# Exercise 2 – Elastic Infrastructure

Deploy the [provided web site](frontend/) on an EC2-based web server. The web application calls the API from the first exercise. The web application should scale elastically based on load (using reasonable metrics of your choosing). Consider how to increase the application's observability. Deploy all infrastructure using an Infrastructure as Code tool (CloudFormation/CDK or Terraform are strongly preferred). EC2 instances should bootstrap themselves without manual intervention.

### I have never done problems like these, and have very little to no experience using AWS and CDK, but I was able to put together a working solution that I hope fulfills all of the requirements, although I didn't really know what to do in terms of increasing observability.
### I had to use a lot of the AWS documentation available online as well as other examples found online.
### I chose Python because I feel like it's a really important language that I need more practice with and would like to work with more.
### These problems were completed on a Windows machine with PyCharm as my IDE.
### Helpful links for working with AWS and CDK:
- https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html
- https://docs.aws.amazon.com/cdk/latest/guide/work-with-cdk-python.html
- https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
- https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancers.html
- https://docs.aws.amazon.com/ec2/?id=docs_gateway
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html
- https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html

### Creating IAM Administrator user to be used instead of root account:
- https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html

## Prerequisites (Links for Windows):
- Python3: https://www.python.org/downloads/windows/
- Node >= 14: https://nodejs.org/en/download/
- AWS CDK: https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html
- AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html & https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html
- Chocolatey (not required but definitely helps): https://chocolatey.org/install

## Setup
Configure AWS credentials and install CDK globally. Bootstrap CDK for your AWS account.

```shell
cdk bootstrap aws://ACCOUNTNUMBER/REGION
```

Install the Python dependencies via:

To manually create a virtualenv:

```
$ py -m venv .venv
```

Activate virtualenv on Windows:

```
% .venv\Scripts\activate.bat
```

Install required dependencies:

```
$ pip install -r requirements.txt
```

Synthesize the CloudFormation template for this code.

```
$ cdk synth
```

## Deployment
Follow the above steps and run `cdk deploy`.

## Teardown
Follow the above steps and run `cdk destroy`.