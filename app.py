#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_amplify_code.amplify_static_site_stack import AmplifyStaticSiteStack


app = cdk.App()

AmplifyStaticSiteStack(
    app,
    "AmplifyStaticSiteStack",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION"),
    ),
)
app.synth()
