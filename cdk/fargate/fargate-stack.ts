import { Construct } from "constructs";
import * as cdk from "aws-cdk-lib";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as iam from "aws-cdk-lib/aws-iam";
import * as logs from "aws-cdk-lib/aws-logs";
import { NagSuppressions } from "cdk-nag";

export interface NovaActVpcProps extends ec2.VpcProps {
  addSecurityGroup?: boolean;
}

export class NovaActVpc extends ec2.Vpc {
  public readonly ssmEndpoint: ec2.InterfaceVpcEndpoint;
  public readonly securityGroup?: ec2.SecurityGroup;

  constructor(scope: Construct, id: string, props: NovaActVpcProps = {}) {
    const { addSecurityGroup, ...vpcProps } = props;

    super(scope, id, {
      maxAzs: 2,
      subnetConfiguration: [
        {
          name: "PrivateSubnet",
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
        {
          name: "PublicSubnet",
          subnetType: ec2.SubnetType.PUBLIC,
        },
      ],
      // Add VPC Flow Logs for security compliance (AwsSolutions-VPC7)
      flowLogs: {
        'VpcFlowLog': {
          destination: ec2.FlowLogDestination.toCloudWatchLogs(
            new logs.LogGroup(scope, `${id}FlowLogGroup`, {
              retention: logs.RetentionDays.ONE_WEEK,
            })
          ),
        }
      },
      ...vpcProps,
    });

    this.ssmEndpoint = this.createVpcEndpoints();
    
    if (addSecurityGroup) {
      this.securityGroup = this.createSecurityGroup();
    }
  }

  private createVpcEndpoints(): ec2.InterfaceVpcEndpoint {
    const ssmEndpoint = this.addInterfaceEndpoint("SSMEndpoint", {
      service: ec2.InterfaceVpcEndpointAwsService.SSM,
    });

    this.addInterfaceEndpoint("EC2MessagesEndpoint", {
      service: ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES,
    });

    this.addInterfaceEndpoint("SSMMessagesEndpoint", {
      service: ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
    });

    return ssmEndpoint;
  }

  private createSecurityGroup(): ec2.SecurityGroup {
    const securityGroup = new ec2.SecurityGroup(this, "SecurityGroup", {
      vpc: this,
      description: "Security Group for Nova Act Fargate",
      allowAllOutbound: false,
    });

    this.configureSecurityGroupRules(securityGroup);
    return securityGroup;
  }

  private configureSecurityGroupRules(securityGroup: ec2.SecurityGroup): void {
    securityGroup.connections.allowFrom(
      this.ssmEndpoint,
      ec2.Port.tcp(443),
      "Allow SSM traffic from VPC endpoint"
    );

    securityGroup.addEgressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80), "Allow HTTP out");
    securityGroup.addEgressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443), "Allow HTTPS out");
    securityGroup.addEgressRule(ec2.Peer.anyIpv4(), ec2.Port.udp(53), "Allow DNS out");
  }
}

export interface NovaActFargateProps {
  containerImage: ecs.ContainerImage;
  cpu?: number;
  memoryLimitMiB?: number;
  vpc?: NovaActVpc;
  environment?: { [key: string]: string };
  taskRole?: iam.IRole;
  executionRole?: iam.IRole;
  apiKey: string;
}

export class NovaActFargate extends Construct {
  public readonly vpc: NovaActVpc;
  public readonly cluster: ecs.Cluster;
  public readonly taskDefinition: ecs.FargateTaskDefinition;

  constructor(scope: Construct, id: string, props: NovaActFargateProps) {
    super(scope, id);

    this.vpc = this.getOrCreateVpc(props.vpc);
    this.cluster = this.createCluster();
    this.taskDefinition = this.createTaskDefinition(props);
    this.addContainer(this.taskDefinition, props);
  }

  private getOrCreateVpc(vpc?: NovaActVpc): NovaActVpc {
    return vpc || new NovaActVpc(this, "Vpc", { addSecurityGroup: true });
  }

  private createCluster(): ecs.Cluster {
    return new ecs.Cluster(this, "Cluster", { 
      vpc: this.vpc,
      containerInsights: true // Fix for AwsSolutions-ECS4
    });
  }

  private createTaskDefinition(props: NovaActFargateProps): ecs.FargateTaskDefinition {
    return new ecs.FargateTaskDefinition(this, "TaskDefinition", {
      cpu: props.cpu || 2048,
      memoryLimitMiB: props.memoryLimitMiB || 4096,
      taskRole: props.taskRole,
      executionRole: props.executionRole,
    });
  }

  private addContainer(taskDefinition: ecs.FargateTaskDefinition, props: NovaActFargateProps): void {
    const environment = this.createEnvironmentVariables(props.apiKey, props.environment);

    taskDefinition.addContainer("AppContainer", {
      image: props.containerImage,
      logging: this.createLogDriver(),
      environment,
    });

    // Suppress CDK-Nag violation for environment variables
    // Nova Act requires environment variables for configuration
    NagSuppressions.addResourceSuppressions(taskDefinition, [
      {
        id: 'AwsSolutions-ECS2',
        reason: 'Nova Act requires environment variables for browser configuration and API key management. These are necessary for proper operation.'
      }
    ]);
  }

  private createEnvironmentVariables(apiKey: string, additionalEnv: { [key: string]: string } = {}): { [key: string]: string } {
    return {
      NOVA_ACT_BROWSER_ARGS: "--disable-gpu --disable-dev-shm-usage --no-sandbox --single-process",
      NOVA_ACT_HEADLESS: "true",
      NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL: "1",
      NOVA_ACT_API_KEY: apiKey,
      ...additionalEnv,
    };
  }

  private createLogDriver(): ecs.LogDriver {
    return ecs.LogDrivers.awsLogs({
      logGroup: new logs.LogGroup(this, "AppLogs"),
      mode: ecs.AwsLogDriverMode.NON_BLOCKING,
      streamPrefix: "fargate",
    });
  }
}

export interface NovaActFargateStackProps extends cdk.StackProps {
  apiKey: string;
}

export class NovaActFargateStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: NovaActFargateStackProps) {
    super(scope, id, props);

    new NovaActFargate(this, 'NovaActService', {
      containerImage: ecs.ContainerImage.fromAsset('.', {
        platform: cdk.aws_ecr_assets.Platform.LINUX_AMD64
      }),
      apiKey: props.apiKey,
    });
  }
}