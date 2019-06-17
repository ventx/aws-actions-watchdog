from aws_cdk import cdk, aws_lambda as lambda_, aws_iam as iam, aws_s3 as s3, aws_sns as sns, aws_cloudwatch as cloudwatch

class AwsActionWatchdogStack(cdk.Stack):

    def __init__(self, app: cdk.App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        jsonFileBucket = s3.Bucket(self, 'jsonFileBucket', versioned=True, removal_policy=cdk.DeletionPolicy.Delete)
        newActionTopic = sns.Topic(self, 'newActions')
        lambdaErrorSnsTopic = sns.Topic(self, 'lambdaError')

        with open("aws_action_watchdog/lambda-handler.js", encoding="utf8") as fp:
            handler_code = fp.read()

        handler_code = handler_code.replace('{{S3BucketName}}', jsonFileBucket.bucket_name)
        handler_code = handler_code.replace('{{SnsTopicArn}}', newActionTopic.topic_arn)

        actionWatchdogLambda = lambda_.Function(self, 'watchdog_Lambda2', 
            runtime= lambda_.Runtime.NODE_J_S810,
            code= lambda_.Code.inline(handler_code),
            handler='index.handler')

        lambdaErrorAlarm = cloudwatch.Alarm(self, 'lambdaErrorAlarm', 
            evaluation_periods=5, 
            threshold=0, 
            comparison_operator=cloudwatch.ComparisonOperator.GreaterThanThreshold,
            treat_missing_data=cloudwatch.TreatMissingData.Breaching,
            alarm_name='Lambda Failed',
            metric=cloudwatch.Metric(metric_name= 'Errors', namespace='AWS/Lambda',dimensions= {
                'FunctionName': actionWatchdogLambda.function_name
            }))
        
        newActionTopic.grant_publish(actionWatchdogLambda)
        jsonFileBucket.grant_read_write(actionWatchdogLambda)
        