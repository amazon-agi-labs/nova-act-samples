#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { NovaActEcsStack } from './ecs-stack';

/**
 * Standalone ECS CDK App
 * Customers can copy this directory and deploy immediately
 */

function getEnvironment(): cdk.Environment {
  const account = getAccountId();
  const region = getRegion();
  
  return { account, region };
}

function getAccountId(): string {
  const accountEnvVars = ['CDK_DEFAULT_ACCOUNT', 'AWS_ACCOUNT_ID'];
  const account = accountEnvVars.map(envVar => process.env[envVar]).find(Boolean);
  
  if (!account) {
    throw new Error(`AWS Account ID required. Set one of: ${accountEnvVars.join(', ')}`);
  }
  
  return account;
}

function getRegion(): string {
  const regionEnvVars = ['CDK_DEFAULT_REGION', 'AWS_DEFAULT_REGION', 'AWS_REGION'];
  const region = regionEnvVars.map(envVar => process.env[envVar]).find(Boolean);
  
  if (!region) {
    throw new Error(`AWS Region required. Set one of: ${regionEnvVars.join(', ')}`);
  }
  
  return region;
}

function getApiKey(): string {
  const apiKey = process.env['NOVA_ACT_API_KEY'];
  
  if (!apiKey) {
    throw new Error('Nova Act API key required. Set NOVA_ACT_API_KEY environment variable.');
  }
  
  return apiKey;
}

const app = new cdk.App();
const env = getEnvironment();
const apiKey = getApiKey();

new NovaActEcsStack(app, 'NovaActEcsStack', {
  env,
  apiKey
});