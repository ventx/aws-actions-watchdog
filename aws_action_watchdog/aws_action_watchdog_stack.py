from aws_cdk import cdk, aws_lambda as lambda_, aws_iam as iam, aws_s3 as s3

class AwsActionWatchdogStack(cdk.Stack):

    def __init__(self, app: cdk.App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        jsonFileBucket = s3.Bucket(self, 'jsonFileBucket')

        with open("aws_action_watchdog/lambda-handler.js", encoding="utf8") as fp:
            handler_code = fp.read()

        handler_code = handler_code.replace('{{S3BucketName}}', jsonFileBucket.bucket_name)

        actionWatchdogLambda = lambda_.Function(self, 'watchdog_Lambda2', 
            runtime= lambda_.Runtime.NODE_J_S810,
            code= lambda_.Code.inline(handler_code),
            handler='index.main')

        jsonFileBucket.grant_read_write(actionWatchdogLambda)
        