# @see: https://www.pulumi.com/blog/lambda-urls-launch/
import json

import pulumi
import pulumi_aws as aws
import pulumi_aws_native as aws_native
from pulumi_command import local

from productizer.utils.settings import get_setting

lambda_role = aws_native.iam.Role(
    "lambda_role",
    assume_role_policy_document=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "lambda.amazonaws.com",
                    },
                    "Effect": "Allow",
                    "Sid": "",
                },
            ],
        }
    ),
)

lambda_role_attachment = aws.iam.RolePolicyAttachment(
    "lambda_role_attachment",
    role=pulumi.Output.concat(lambda_role.role_name),  # type: ignore
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
)

"""
Packakge the lambda function, layerify dependencies.
"""
dependenciesLayer = aws.lambda_.LayerVersion(
    "dependenciesLayer-v1",
    layer_name="dependencies-layer",
    code=pulumi.asset.AssetArchive({"./python": pulumi.FileArchive("./.lambda/layer/")}),
    compatible_runtimes=[aws.lambda_.Runtime.PYTHON3D9],
)

"""
Create the lambda function
"""
productizerer_function = aws.lambda_.Function(
    "testbed-test-productizer",
    runtime="python3.9",
    role=lambda_role.arn,
    handler="productizer.main.handler",
    code=pulumi.AssetArchive(
        {
            "./productizer": pulumi.FileArchive("../src/productizer"),
        }
    ),
    layers=[dependenciesLayer.arn],
    timeout=15,
    tags={"Name": "testbed-test-productizer", "Environment": pulumi.get_stack(), "Project": "Virtual Finland"},
)

lambda_url = aws_native.lambda_.Url(
    "testbed-test-productizer-url",
    target_function_arn=productizerer_function.arn,
    auth_type=aws_native.lambda_.UrlAuthType.NONE,
)

add_permissions = local.Command(
    "add_permissions",
    create=pulumi.Output.concat(
        "aws lambda add-permission --function-name ",
        productizerer_function.name,
        " --action lambda:InvokeFunctionUrl --principal '*' --function-url-auth-type NONE --statement-id FunctionURLAllowPublicAccess",
    ),
    opts=pulumi.ResourceOptions(delete_before_replace=True),
    environment={
        "AWS_DEFAULT_REGION": get_setting("POETRY_AWS_REGION"),
        "AWS_ACCESS_KEY_ID": get_setting("POETRY_AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": get_setting("POETRY_AWS_SECRET_ACCESS_KEY"),
    },
)

pulumi.export("url", lambda_url.function_url)
