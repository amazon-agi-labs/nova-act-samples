import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as autoscaling from 'aws-cdk-lib/aws-autoscaling';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

interface NovaActEcsStackProps extends cdk.StackProps {
  instanceType?: ec2.InstanceType;
  desiredCapacity?: number;
  containerImage?: ecs.ContainerImage;
  apiKey: string;
}

export class NovaActEcsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: NovaActEcsStackProps) {
    super(scope, id, props);

    const vpc = this.createVpc();
    const cluster = this.createCluster(vpc, props.instanceType, props.desiredCapacity);
    const taskDefinition = this.createTaskDefinition();
    
    this.configureContainer(taskDefinition, props.containerImage, props.apiKey);
  }

  private createVpc(): ec2.Vpc {
    const vpc = new ec2.Vpc(this, 'Vpc', {
      maxAzs: 2,
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
      ],
    });

    // Enable VPC Flow Logs
    const flowLogGroup = new logs.LogGroup(this, 'VpcFlowLogGroup', {
      retention: logs.RetentionDays.ONE_WEEK,
    });

    new ec2.FlowLog(this, 'VpcFlowLog', {
      resourceType: ec2.FlowLogResourceType.fromVpc(vpc),
      destination: ec2.FlowLogDestination.toCloudWatchLogs(flowLogGroup),
    });

    this.addVpcEndpoints(vpc);
    this.createSecurityGroup(vpc);
    
    return vpc;
  }

  private addVpcEndpoints(vpc: ec2.Vpc): void {
    vpc.addGatewayEndpoint('S3Endpoint', {
      service: ec2.GatewayVpcEndpointAwsService.S3,
    });

    vpc.addInterfaceEndpoint('EcrEndpoint', {
      service: ec2.InterfaceVpcEndpointAwsService.ECR,
    });

    vpc.addInterfaceEndpoint('EcrDkrEndpoint', {
      service: ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
    });

    vpc.addInterfaceEndpoint('LogsEndpoint', {
      service: ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
    });
  }

  private createSecurityGroup(vpc: ec2.Vpc): ec2.SecurityGroup {
    const sg = new ec2.SecurityGroup(this, 'SecurityGroup', {
      vpc,
      description: 'Security group for Nova Act ECS',
      allowAllOutbound: true,
    });

    sg.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(443),
      'Allow HTTPS for SSM'
    );

    return sg;
  }

  private createCluster(
    vpc: ec2.Vpc, 
    instanceType = ec2.InstanceType.of(ec2.InstanceClass.M5, ec2.InstanceSize.LARGE),
    desiredCapacity = 1
  ): ecs.Cluster {
    const cluster = new ecs.Cluster(this, 'Cluster', { 
      vpc,
      containerInsights: true,
    });

    cluster.addCapacity('AutoScalingGroup', {
      instanceType,
      desiredCapacity,
      minCapacity: 1,
      maxCapacity: 3,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      blockDevices: [{
        deviceName: '/dev/xvda',
        volume: autoscaling.BlockDeviceVolume.ebs(30, {
          encrypted: true,
        }),
      }],
    });

    return cluster;
  }

  private createTaskDefinition(): ecs.Ec2TaskDefinition {
    return new ecs.Ec2TaskDefinition(this, 'TaskDefinition');
  }

  private configureContainer(
    taskDefinition: ecs.Ec2TaskDefinition,
    containerImage: ecs.ContainerImage | undefined,
    apiKey: string
  ): void {
    const environment = this.createEnvironmentVariables(apiKey);

    const image = containerImage || ecs.ContainerImage.fromAsset('.', {
      platform: cdk.aws_ecr_assets.Platform.LINUX_AMD64,
    });

    taskDefinition.addContainer('AppContainer', {
      image,
      memoryLimitMiB: 2048,
      environment,
      logging: ecs.LogDrivers.awsLogs({
        logGroup: new logs.LogGroup(this, 'AppLogs'),
        streamPrefix: 'ecs',
      }),
    });
  }

  private createEnvironmentVariables(apiKey: string): { [key: string]: string } {
    return {
      NOVA_ACT_BROWSER_ARGS: '--disable-gpu --disable-dev-shm-usage --no-sandbox',
      NOVA_ACT_HEADLESS: 'true',
      NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL: '1',
      NOVA_ACT_API_KEY: apiKey,
    };
  }
}