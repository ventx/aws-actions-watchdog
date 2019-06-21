#!/usr/bin/env python3

from aws_cdk import cdk

from aws_action_watchdog.aws_action_watchdog_stack import AwsActionWatchdogStack


app = cdk.App()
AwsActionWatchdogStack(app, "aws-action-watchdog-cdk")

app.run()
