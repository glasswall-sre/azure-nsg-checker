<div align="center" style="text-align:center">

# Azure NSG Checker

The Azure NSG Checker is a CRON AWS Lambda service that checks to see if your Azure NSG rules are up to date with the current O365 and GSUITE SMTP rules. This is a very specific Glasswall SRE but feel free to use this in your own projects.

<img align="center" src="https://sonarcloud.io/api/project_badges/measure?project=azure_nsg_checker&metric=alert_status">
<img align="center" src="https://sonarcloud.io/api/project_badges/measure?project=azure_nsg_checker&metric=sqale_rating">
<img align="center" src="https://sonarcloud.io/api/project_badges/measure?project=azure_nsg_checker&metric=reliability_rating">
<img align="center" src="https://codecov.io/gh/glasswall-sre/azure_nsg_checker/branch/master/graph/badge.svg">
<img align="center" src="https://img.shields.io/github/license/glasswall-sre/azure_nsg_checker">
<img align="center" src="https://img.shields.io/github/workflow/status/glasswall-sre/azure_nsg_checker/CI">

</div>

## Design 

### Cloud Technology 

The system uses a scheduled AWS lambda to periodically connect to an Azure Network security group, list all Inbound NSG rules that have **O365** or **GSUITE** rules in their name. It then takes that set and compares it to the current O365 and GSUITE SMTP egress IPs to make sure the current NSG rules are up to date.

### IaC

The Lambda is deployed using [Serverless](https://www.serverless.com/framework/docs/). Serverless acts as the infrastructure as code and deploys the Lambda to a defined AWS account.

## User guide

### Pre-requisites

### Setup

There is some initial setup in AWS, Azure and on the deployment environment that is required before you can run the serverless deployment. 

#### Azure 

* Azure App with **Reader** permissions on the Azure Network security group you want to check.

#### AWS 

* User with permissions:
    - lambda:*

* AWS Secret Manager with a secret that contains the Azure Apps details in the format:

``` json
{
  "client_id": "<INSERT_GUID>",
  "tenant_id": "<INSERT_GUID>",
  "key": "<INSERT_KEY>"
}
```

#### Deployment environment 

The deployment environment is where you will be deploying this from. Either a CI pipeline or a local machine.

* Install [serverless](https://www.serverless.com/framework/docs/getting-started/)
* Install the serverless plugin for python

``` 
serverless plugin install --name serverless-python-requirements
```

* Docker to build the Lambda Python Zip file. 

### Configuration

The configuration below is for deploying the serverless. Comments in the yaml describe what 

``` yaml
service: azure-nsg-checker

provider:
  name: aws
  runtime: python3.8
  region: eu-west-2
  stage: prod
  # Reader permissions to access the Azure App secret during runtime
  iamRoleStatements:

    - Effect: "Allow"

      Action:

        - secretsmanager:GetSecretValue

      Resource: "arn:aws:secretsmanager:eu-west-2:433250546572:secret:<SECRET_NAME>"

functions:
  nsg-watcher:
    handler: handler.run
    events:

      - schedule:

          # How often you want to run the function for.
          name: azure-nsg-checker-cron
          description: "Runs the Azure NSG Checker CRON Job"
          rate: rate(2 minutes)

    environment:
      # O365 Exchange URI to retrieve the SMTP CIDR Ips
      O365_URL: https://endpoints.office.com/endpoints/Worldwide?ServiceAreas=Exchange&ClientRequestId=
      # Comma separated list of Gsuites netblocks for their egress SMTP rules
      GSUITE_NETBLOCKS: "_netblocks.google.com, _netblocks2.google.com, _netblocks3.google.com"
      # Azure Subscription ID for where the Azure NSG is location
      AZURE_SUBSCRIPTION: 359ee0f2-2ad9-4d4f-9187-aa466416a520
      # Azure App's Secret Name in AWS Secret Manager
      AZURE_APP_SECRET_NAME: azure_nsg_watcher
      #Azure Network security group resource group
      AZURE_NSG_RGP: rgp-uks-gwc-prod-vnet
      #Azure Network security group name 
      AZURE_NSG_NAME: nsg-uks-gwc-k8s-subnet-uksprod1
      # AWS Secret Region for where the secret is located.
      AWS_SECRET_REGION: eu-west-2

plugins:

  +  serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: non-linux
```

### Deployment

``` 
serverless deploy
```
