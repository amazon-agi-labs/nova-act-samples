#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { NovaActLambdaStack } from './lambda-stack';

function getEnvironment(): cdk.Environment {
  const account = process.env.CDK_DEFAULT_ACCOUNT;
  const region = process.env.CDK_DEFAULT_REGION;

  if (!account || !region) {
    throw new Error('CDK_DEFAULT_ACCOUNT and CDK_DEFAULT_REGION must be set');
  }

  return { account, region };
}

const app = new cdk.App();
new NovaActLambdaStack(app, 'NovaActLambdaStack', {
  env: getEnvironment(),
});
