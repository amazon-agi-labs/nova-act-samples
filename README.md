# Amazon Nova Act Samples

This repository contains sample code and end-to-end solutions demonstrating [Amazon Nova Act](https://nova.amazon.com/act).

## About Amazon Nova Act

Amazon Nova Act is available as an AWS service to build and manage fleets of reliable AI agents for automating production UI workflows at scale. Nova Act completes repetitive UI workflows in the browser and escalates to a human supervisor when appropriate. You can define workflows by combining the flexibility of natural language with Python code. Start by exploring in the web playground at [nova.amazon.com/act](https://nova.amazon.com/act), develop and debug in your IDE, deploy to AWS, and monitor your workflows in the AWS Console, all in just a few steps.

(Preview) Nova Act also integrates with external tools through API calls, remote MCP, or agentic frameworks, such as Strands Agents.

## Repository Structure

```
├── cdk/                 # AWS CDK sample code to deploy Nova Act on AWS
├── examples/            # Lightweight sample code
└── solutions/           # Reference applications
```

## CDK

Ready-to-use [AWS Cloud Development Kit (CDK)](https://docs.aws.amazon.com/cdk/) examples for deploying the Nova Act SDK on various AWS compute services including Lambda, ECS, and AgentCore.

[Get Started with CDK →](cdk/README.md)

## Examples

Lightweight, focused code samples designed for minimal setup. These single files or small projects require only basic dependency installation and SDK authentication configuration, and can be running within minutes.

[Get Started with Examples →](examples/README.md)

## Solutions

Comprehensive, ready-to-deploy applications targeting specific use cases. These complete projects demonstrate Nova Act integration within larger applications, showcasing real-world implementation patterns.

[Get Started with Solutions →](solutions/README.md)

## Additional Resources

- [Amazon Nova Act SDK](https://github.com/aws/nova-act)
- [Amazon Nova Act AWS Documentation](https://docs.aws.amazon.com/nova-act)