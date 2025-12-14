# Nova Act CDK Examples

This directory contains ready-to-use examples for deploying Nova Act on various AWS compute services. Each service directory includes a complete CDK construct example, Docker configuration, and test scripts.

## 🚨 Prerequisites (Required Before Starting)

Before using any example, ensure you have:

1. **AWS CLI** configured with appropriate permissions
2. **Node.js** installed (version 18 or later)
3. **Docker** installed and running (for containerized examples)
4. **Nova Act API Key** - Get yours at [nova.amazon.com/act](https://nova.amazon.com/act)

## 📁 Available Service Examples

| Service | Directory | Use Case | Authentication | Key Files |
|---------|-----------|----------|----------------|-----------|
| **🚀 Lambda** | [`lambda/`](./lambda/) | Event-driven automation, 15-min max execution | IAM Role | `lambda-stack.ts`, `lambda-app.ts` |
| **🐳 Fargate** | [`fargate/`](./fargate/) | Serverless containers, private subnets | IAM Role | `fargate-stack.ts`, `fargate-app.ts` |
| **🏗️ ECS** | [`ecs/`](./ecs/) | Container orchestration with EC2 backing | IAM Role | `ecs-stack.ts`, `ecs-app.ts` |
| **🤖 AgentCore** | [`agentcore/`](./agentcore/) | Native agent runtime with browser sessions | IAM Role | `agentcore-stack.ts`, `handler.py` |

> **📖 Each service directory contains a detailed README with specific deployment instructions and architecture details.**

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   cd cdk/
   npm ci
   ```

2. **Set environment variables**:
   ```bash
   export CDK_DEFAULT_ACCOUNT="your-account-id"
   export CDK_DEFAULT_REGION="your-region"
   export NOVA_ACT_API_KEY="your-api-key"
   ```

3. **Bootstrap CDK** (first-time only):
   ```bash
   npx cdk bootstrap
   ```

4. **Deploy a service**:
   ```bash
   cd [service-directory]/
   npx cdk deploy --app "npx ts-node [service]-app.ts"
   ```

## 🔐 Authentication

**All examples use IAM Role authentication** - no API keys required:
- **Lambda**: Execution role provides Nova Act service access
- **Fargate**: Task role with comprehensive AWS permissions
- **ECS**: Task role with Nova Act service permissions
- **AgentCore**: Runtime role with Bedrock and browser session access

## 🧪 Testing & Validation

### Full Deployment Tests
Each service includes comprehensive test scripts:
```bash
cd [service-directory]/
./test-[service]-deploy.sh
```

These scripts perform complete **deploy → invoke → teardown** cycles:
- **Fargate**: Deploys stack, waits for service stability, checks logs, destroys
- **AgentCore**: Deploys, invokes runtime with test payload, destroys
- **ECS**: Deploys, runs task, monitors completion, destroys
- **Lambda**: Deploys, invokes function, destroys

## 🏗️ Architecture Patterns

### Container-Based Services
- **Lambda**: Container image with Playwright pre-installed
- **Fargate**: Private subnets with VPC endpoints and NAT gateway
- **ECS**: EC2-backed cluster with auto-scaling and encrypted volumes
- **AgentCore**: ARM64 container with OpenTelemetry integration

### Security Features
- **VPC Flow Logs** for network monitoring
- **Encrypted EBS volumes** where applicable
- **VPC Endpoints** for secure AWS service access
- **Least privilege IAM roles** with service-specific permissions
- **CDK-Nag compliance** with documented suppressions

## 📋 Common Configuration

All examples include:
- **Browser Arguments**: `--disable-gpu --disable-dev-shm-usage --no-sandbox --single-process`
- **Headless Mode**: Enabled for server environments
- **Playwright**: Pre-installed in containers with system browsers
- **CloudWatch Logs**: Configured for monitoring and debugging
- **Platform**: Linux AMD64 (ARM64 for AgentCore)

## ⚠️ Production Readiness

| Service | Production Ready | Notes |
|---------|------------------|-------|
| **Lambda** | ✅ Yes | 15-minute execution limit |
| **Fargate** | ✅ Yes | Fully managed, secure |
| **ECS** | ✅ Yes | Requires capacity management |
| **AgentCore** | ✅ Yes | Native AWS integration |

## 🆘 Need Help?

1. **Check prerequisites** - Most issues stem from missing environment variables
2. **Review service-specific README** - Each directory has detailed troubleshooting
3. **Run test scripts** - Validate deployment before customization
4. **Check AWS permissions** - Ensure your credentials have required access

---

**Ready to deploy?** Choose your service from the table above and follow the detailed instructions in that service's directory.