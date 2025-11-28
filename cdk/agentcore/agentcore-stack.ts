#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as bedrockAgentCore from 'aws-cdk-lib/aws-bedrockagentcore';
import * as ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import { Construct } from 'constructs';

interface AgentCoreStackProps extends cdk.StackProps {
  agentName?: string;
  description?: string;
}

/**
 * Standalone AgentCore Stack for Nova Act deployment
 * No external dependencies - ready for customer use
 */
export class AgentCoreStack extends cdk.Stack {
  public readonly agentCore: bedrockAgentCore.CfnRuntime;
  public readonly containerImage: ecr_assets.DockerImageAsset;

  constructor(scope: Construct, id: string, props: AgentCoreStackProps) {
    super(scope, id, props);

    this.containerImage = new ecr_assets.DockerImageAsset(this, 'ContainerImage', {
      directory: '.',
      platform: ecr_assets.Platform.LINUX_ARM64,
    });

    const agentCoreRole = this.createAgentCoreRole();
    const environmentVariables = this.createEnvironmentVariables();

    this.agentCore = new bedrockAgentCore.CfnRuntime(this, 'AgentCoreRuntime', {
      agentRuntimeName: props.agentName || 'NovaActAgent',
      description: props.description || 'Nova Act Agent running on AgentCore Runtime',
      roleArn: agentCoreRole.roleArn,
      agentRuntimeArtifact: {
        containerConfiguration: {
          containerUri: this.containerImage.imageUri
        }
      },
      networkConfiguration: {
        networkMode: 'PUBLIC'
      },
      environmentVariables: environmentVariables
    });
  }

  private createAgentCoreRole(): iam.Role {
    return new iam.Role(this, 'AgentCoreRole', {
      assumedBy: new iam.ServicePrincipal('bedrock-agentcore.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonAPIGatewayInvokeFullAccess'),
      ],
      inlinePolicies: {
        ECRAccess: this.createECRPolicy(),
        CloudWatchAccess: this.createCloudWatchPolicy(),
        XRayAccess: this.createXRayPolicy(),
        BedrockAgentCoreAccess: this.createBedrockAgentCorePolicy(),
        S3Access: this.createS3Policy(),
      }
    });
  }

  private createECRPolicy(): iam.PolicyDocument {
    return new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'ecr:GetAuthorizationToken',
            'ecr:BatchGetImage',
            'ecr:GetDownloadUrlForLayer'
          ],
          resources: ['*']
        })
      ]
    });
  }

  private createCloudWatchPolicy(): iam.PolicyDocument {
    return new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'logs:CreateLogGroup',
            'logs:CreateLogStream',
            'logs:PutLogEvents',
            'logs:DescribeLogStreams',
            'logs:DescribeLogGroups',
            'cloudwatch:PutMetricData'
          ],
          resources: ['*']
        })
      ]
    });
  }

  private createXRayPolicy(): iam.PolicyDocument {
    return new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'xray:PutTraceSegments',
            'xray:PutTelemetryRecords',
            'xray:GetSamplingRules',
            'xray:GetSamplingTargets'
          ],
          resources: ['*']
        })
      ]
    });
  }

  private createBedrockAgentCorePolicy(): iam.PolicyDocument {
    return new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'bedrock-agentcore:GetBrowserSession',
            'bedrock-agentcore:StartBrowserSession',
            'bedrock-agentcore:StopBrowserSession',
            'bedrock-agentcore:UpdateBrowserStream',
            'bedrock-agentcore:DeleteBrowser',
            'bedrock-agentcore:GetBrowser',
            'bedrock-agentcore:ConnectBrowserAutomationStream',
            'bedrock-agentcore:ListBrowsers',
            'bedrock-agentcore:ListBrowserSessions',
            'bedrock-agentcore:CreateBrowser',
            'bedrock-agentcore:ConnectBrowserLiveViewStream'
          ],
          resources: ['*']
        })
      ]
    });
  }

  private createS3Policy(): iam.PolicyDocument {
    return new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            's3:GetObject',
            's3:PutObject',
            's3:DeleteObject'
          ],
          resources: ['arn:aws:s3:::nova-act-*/*']
        }),
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: ['s3:ListBucket'],
          resources: ['arn:aws:s3:::nova-act-*']
        })
      ]
    });
  }

  private createEnvironmentVariables(): { [key: string]: string } {
    return {
      NOVA_ACT_BROWSER_ARGS: '--disable-gpu --disable-dev-shm-usage --no-sandbox --single-process',
      NOVA_ACT_HEADLESS: 'true',
      OTEL_SDK_DISABLED: 'true',
    };
  }
}
