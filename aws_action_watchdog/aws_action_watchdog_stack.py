from aws_cdk import cdk, aws_lambda as lambda_, aws_iam as iam, aws_s3 as s3, aws_sns as sns, aws_cloudwatch as cloudwatch, aws_events as events, aws_events_targets as targets, aws_cloudwatch_actions as actions


class AwsActionWatchdogStack(cdk.Stack):

    def __init__(self, app: cdk.App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        jsonFileBucket = s3.Bucket(self, 'jsonFileBucket')
        newActionTopic = sns.Topic(self, 'newActions')
        lambdaErrorSnsTopic = sns.Topic(self, 'lambdaError')

        bucketResource = jsonFileBucket.node.find_child('Resource')
        bucketResource.add_override('DeletionPolicy', 'Delete')

        with open("aws_action_watchdog/lambda-handler.js", encoding="utf8") as fp:
            handler_code = fp.read()

        handler_code = handler_code.replace('{{S3BucketName}}', jsonFileBucket.bucket_name)
        handler_code = handler_code.replace('{{SnsTopicArn}}', newActionTopic.topic_arn)

        actionWatchdogLambda = lambda_.Function(self, 'watchdog_Lambda',
                                                runtime=lambda_.Runtime.NODE_J_S810,
                                                timeout=15,
                                                code=lambda_.Code.inline(
                                                    handler_code),
                                                handler='index.handler')

        schedule = events.Rule(self, 'lambdaScheduleEvent', schedule_expression='rate(24 hours)')
        schedule.add_target(target=targets.LambdaFunction(actionWatchdogLambda))

        alarm = actionWatchdogLambda.metric_all_errors().new_alarm(
            self,
            'lambdaErrorAlarm',
            threshold=0,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GreaterThanThreshold,
            treat_missing_data=cloudwatch.TreatMissingData.Missing,
            alarm_name='Lambda Error',
            datapoints_to_alarm=1,
        )

        alarm.add_alarm_action(actions.SnsAction(lambdaErrorSnsTopic))

        newActionTopic.grant_publish(actionWatchdogLambda)
        jsonFileBucket.grant_read_write(actionWatchdogLambda)
