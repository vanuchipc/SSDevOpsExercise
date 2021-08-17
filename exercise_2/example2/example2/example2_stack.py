import aws_cdk
from aws_cdk import (
    core as cdk,
    aws_lambda,
    aws_autoscaling,
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


class Example2Stack(cdk.Stack):

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
                f'pip install -r ../exercise_1/fortune_handler/requirements.txt -t ../exercise_1/fortune_handler'.split()
            )

        # Fortune Handler lambda creation
        fortune_handler_lambda = aws_lambda.Function(
            scope=self,
            id="Fortune Handler",
            code=aws_lambda.Code.asset("../exercise_1/fortune_handler"),
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

        # EC2 code and info used:
        # https: // docs.aws.amazon.com / AWSEC2 / latest / UserGuide / concepts.html
        # Primarily used this example for ASG and converted to Python: https://bobbyhadz.com/blog/aws-cdk-application-load-balancer

        # Python File I/O example used for reading single file:
        # https://www.w3resource.com/python-exercises/file/python-io-exercise-6.php
        # https://www.programiz.com/python-programming/methods/string/join
        # This solution is not scaleable but it should work for this specific instance of only using a single file. In a professional environment it seems I'd use S3 and potentially AWS Amplify,
        # but those can also incur costs and extra complexity here that I felt would make it unnecessarily difficult for a project where everything was already new to me.
        frontend_resource=' '.join(file_read("./frontend/index.html"))

        # Create user data script
        # https://www.programiz.com/python-programming/string-interpolation
        user_data = aws_ec2.UserData.for_linux()
        user_data.add_commands(
            'sudo su',
            'yum install -y httpd',
            'systemctl start httpd',
            'systemctl enable httpd',
            f'echo "{frontend_resource}" > /var/www/html/index.html',
        )

        # Creating Auto Scaling Group
        # https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html
        myASG = aws_autoscaling.AutoScalingGroup(
            scope=self,
            id="ASG",
            vpc=myVPC,
            instance_type=aws_ec2.InstanceType.of(aws_ec2.InstanceClass.BURSTABLE2, aws_ec2.InstanceSize.MICRO),
            machine_image=aws_ec2.AmazonLinuxImage(generation=aws_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            user_data=user_data,
            min_capacity=2,
            max_capacity=3
        )

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

        # Add lambda listener target
        myListener.add_targets(
            id="lambda-target",
            path_pattern="/fortune",
            priority=1,
            targets=[fortune_handler_lambda_target]
        )

        # Add EC2 listener target
        myListener.add_targets(
            id="default-target",
            port=80,
            targets=[myASG]
        )

        # Make ASG scale based on requests per minute
        myASG.scale_on_request_count(
            id='requests-per-minute',
            target_requests_per_minute=60
        )

# Python File I/O example used for reading single file:
# https://www.w3resource.com/python-exercises/file/python-io-exercise-6.php
# This solution is not scaleable but it should work for this specific instance of only using a single file. In a professional environment it seems I'd use S3 and potentially AWS Amplify,
# but those can also incur costs and extra complexity here that I felt would make it unnecessarily difficult for a project where everything was already new to me.
def file_read(fname):
    with open(fname, "r") as myfile:
        data = myfile.readlines()
        return data