#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { NovaActEcsStack } from './ecs-stack';

const app = new cdk.App();

// Option 3: IAM role-based (recommended for production)
new NovaActEcsStack(app, 'NovaActEcsStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
