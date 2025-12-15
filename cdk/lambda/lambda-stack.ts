import { Construct } from "constructs";
import { Duration, Stack } from "aws-cdk-lib";
import * as cdk from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as iam from "aws-cdk-lib/aws-iam";
import * as ecr_assets from "aws-cdk-lib/aws-ecr-assets";

type NovaActLambdaProps = {
  dockerfilePath: string;
  memorySize?: number;
  timeout?: Duration;
  environment?: { [key: string]: string };
  role?: iam.IRole;
  apiKey: string;
};

interface NovaActLambdaStackProps extends cdk.StackProps {
  apiKey: string;
}

function createNovaActEnvironment(apiKey: string, additionalEnvironment: { [key: string]: string } = {}): { [key: string]: string } {
  return {
    NOVA_ACT_BROWSER_ARGS: "--disable-gpu --disable-dev-shm-usage --no-sandbox --single-process",
    NOVA_ACT_HEADLESS: "true",
    NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL: "1",
    NOVA_ACT_API_KEY: apiKey,
    ...additionalEnvironment,
  };
}

function createContainerImage(scope: Construct, dockerfilePath: string): ecr_assets.DockerImageAsset {
  return new ecr_assets.DockerImageAsset(scope, "ContainerImage", {
    directory: dockerfilePath,
    platform: ecr_assets.Platform.LINUX_AMD64,
  });
}

export class NovaActLambda extends Construct {
  public readonly function: lambda.Function;
  public readonly containerImage: ecr_assets.DockerImageAsset;

  constructor(
    scope: Construct,
    id: string,
    {
      dockerfilePath,
      memorySize = 3008,
      timeout = Duration.minutes(15),
      environment = {},
      role,
      apiKey,
    }: NovaActLambdaProps
  ) {
    super(scope, id);

    this.containerImage = createContainerImage(this, dockerfilePath);
    
    const environmentVariables = createNovaActEnvironment(apiKey, environment);
    
    const executionRole = role || new iam.Role(this, "ExecutionRole", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    this.function = new lambda.Function(this, "Function", {
      code: lambda.Code.fromEcrImage(this.containerImage.repository, {
        tagOrDigest: this.containerImage.assetHash,
      }),
      handler: lambda.Handler.FROM_IMAGE,
      runtime: lambda.Runtime.FROM_IMAGE,
      memorySize,
      timeout,
      environment: environmentVariables,
      role: executionRole,
    });

    if (!role) {
      // Add policies after function creation to avoid circular dependency
      (executionRole as iam.Role).addToPolicy(new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream", 
          "logs:PutLogEvents"
        ],
        resources: [`arn:aws:logs:${Stack.of(this).region}:${Stack.of(this).account}:log-group:/aws/lambda/*`]
      }));
    }
  }
}

export class NovaActLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: NovaActLambdaStackProps) {
    super(scope, id, props);

    new NovaActLambda(this, 'NovaActLambda', {
      dockerfilePath: '.',
      apiKey: props.apiKey,
    });
  }
}