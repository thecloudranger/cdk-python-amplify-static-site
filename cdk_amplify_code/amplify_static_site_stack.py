import os
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_amplify_alpha as amplify,
    aws_codecommit as codecommit,
    CfnOutput,
    aws_codebuild as codebuild,
    custom_resources,
)


class AmplifyStaticSiteStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a CodeCommit repository with initial content from src folder
        repo = codecommit.Repository(
            self,
            "StaticSiteRepo",
            repository_name="static-site-repo",
            description="Repository for the static website",
            code=codecommit.Code.from_directory(
                "src"
            ),  # Initialize from local src folder
        )

        # Create an Amplify App with the required build steps
        amplify_app = amplify.App(
            self,
            "StaticSiteAmplifyApp",
            source_code_provider=amplify.CodeCommitSourceCodeProvider(repository=repo),
            environment_variables={"AMPLIFY_MONOREPO_APP_ROOT": "/"},
            build_spec=codebuild.BuildSpec.from_object_to_yaml(
                {
                    "version": "1.0",
                    "frontend": {
                        "phases": {
                            "build": {"commands": ["echo 'Building static site'"]}
                        },
                        "artifacts": {"baseDirectory": "/", "files": ["**/*"]},
                        "env": {"AMPLIFY_MONOREPO_APP_ROOT": "/"},
                    },
                }
            ),
        )

        # Add a branch to the Amplify app
        main_branch = amplify_app.add_branch("main")

        # Enable auto-build for the main branch
        main_branch.auto_build = True

        #
        # Triggering Amplify build and deployment right after app creation
        #
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.custom_resources/AwsCustomResource.html
        myBuildTrigger = custom_resources.AwsCustomResource(
            self,
            "Amplify_Build_Trigger",
            policy=custom_resources.AwsCustomResourcePolicy.from_sdk_calls(
                resources=custom_resources.AwsCustomResourcePolicy.ANY_RESOURCE
            ),
            on_create=custom_resources.AwsSdkCall(
                service="Amplify",
                action="startJob",
                physical_resource_id=custom_resources.PhysicalResourceId.of(
                    "app-build-trigger"
                ),
                parameters={
                    "appId": amplify_app.app_id,
                    "branchName": main_branch.branch_name,
                    "jobType": "RELEASE",
                    "jobReason": "Auto Start build",
                },
            ),
        )

        # Output the Amplify app URL
        CfnOutput(
            self,
            "AmplifyAppURL",
            value=f"https://main.{amplify_app.default_domain}",
            description="URL of the Amplify app",
        )

        # Output the CodeCommit repository clone URL
        CfnOutput(
            self,
            "CodeCommitRepoURL",
            value=repo.repository_clone_url_http,
            description="CodeCommit repository clone URL",
        )
