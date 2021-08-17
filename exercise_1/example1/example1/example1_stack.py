import aws_cdk
from aws_cdk import (
    core as cdk,
    aws_lambda,
    aws_ec2,
    aws_elasticloadbalancingv2,
    aws_elasticloadbalancingv2_targets
)
import os
import subprocess

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class Example1Stack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Virtual Private Cloud Code and info used:
        # https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html
        # https://bobbyhadz.com/blog/aws-cdk-application-load-balancer

        myVPC = aws_ec2.Vpc(
            scope=self,
            id="VPC",
            nat_gateways=1
        )

        # Lambda code and info used:
        # https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
        # https://sbstjn.com/blog/aws-cdk-lambda-loadbalancer-vpc-certificate/
        # https://gitlab.com/josef.stach/aws-cdk-lambda-asset/-/blob/master/aws_cdk_lambda_asset/zip_asset_code.py
        # https://sbstjn.com/blog/aws-cdk-lambda-loadbalancer-vpc-certificate/

        # Install Lambda dependencies
        if not os.environ.get('SKIP_PIP'):
            subprocess.check_call(
                f'pip install -r ./fortune_handler/requirements.txt -t ./fortune_handler'.split()
            )

        # Fortune Handler lambda creation
        fortune_handler_lambda = aws_lambda.Function(
            scope=self,
            id="Fortune Handler",
            code=aws_lambda.Code.asset("./fortune_handler"),
            handler="app.lambda_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            vpc=myVPC
        )

        # ALB Creation and info used:
        # https://sbstjn.com/blog/aws-cdk-lambda-loadbalancer-vpc-certificate/
        # https://bobbyhadz.com/blog/aws-cdk-application-load-balancer
        # https://gitlab.com/josef.stach/aws-cdk-lambda-asset/-/blob/master/aws_cdk_lambda_asset/zip_asset_code.py
        # https://docs.aws.amazon.com/lambda/latest/dg/welcome.html

        fortune_handler_lambda_target = aws_elasticloadbalancingv2_targets.LambdaTarget(fortune_handler_lambda)

        # Setting up Application Load Balancer to be Internet facing (public)
        myALB = aws_elasticloadbalancingv2.ApplicationLoadBalancer(
            scope=self,
            id="ALB",
            vpc=myVPC,
            internet_facing=True
        )

        # Add ALB listener
        myListener = myALB.add_listener(
            'Listener',
            port=80,
            open=True
        )

        # Add ALB listener target
        myListener.add_targets(
            id="default-target",
            targets=[fortune_handler_lambda_target]
        )