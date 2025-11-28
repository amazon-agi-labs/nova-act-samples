#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { NovaActFargateStack } from './fargate-stack';

const app = new cdk.App();
new NovaActFargateStack(app, 'NovaActFargateStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
