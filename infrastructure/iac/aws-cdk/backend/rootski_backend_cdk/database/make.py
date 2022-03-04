"""
Script to deploy three CDK apps needed to form the backend.

The 3 stacks have very particular inputs and outputs that must
be orchestrated.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen
from typing import Dict, List, Literal

from rootski_backend_cdk.common.constants import StackNames
from rootski_backend_cdk.common.outputs import get_stack_outputs
from rootski_backend_cdk.common.secrets import get_secret_by_id
from rootski_backend_cdk.database.lightsail.stacks.lightsail_instance import (
    ContextVars as LightsailInstanceContextVars,
)
from rootski_backend_cdk.database.lightsail.stacks.lightsail_instance import (
    StackOutputs as LightsailStackOutputKeys,
)
from rootski_backend_cdk.database.lightsail_dependencies.stacks.db_backups_bucket_stack import (
    StackOutputs as DbBucketStackOutputKeys,
)
from rootski_backend_cdk.database.lightsail_dependencies.stacks.lightsail_iam_user_stack import (
    StackOutputs as IamUserStackOutputKeys,
)
from rootski_backend_cdk.database.lightsail_subdomains.stacks.subdomains import (
    ContextVars as SubdomainsContextVars,
)

AWS_REGION = "us-west-2"

THIS_DIR = Path(__file__).parent


@dataclass
class Config:
    """Constant values used during the deployment process."""

    # lightsail app
    lightsail_instance_outputs_fpath = THIS_DIR / "lightsail-outputs.json"
    lightsail_dependencies_stack_outputs_fpath = THIS_DIR / "lightsail-dependencies-outputs.json"


#########################
# --- Stack Outputs --- #
#########################


@dataclass
class DbBucketStackOutputs:
    """Output keys for the database-backups-bucket stack."""

    rootski_db_backups_s3_bucket_name: str
    rootski_db_backups_s3_bucket_arn: str

    @classmethod
    def from_cloudformation(cls, region: str):
        """Fetch outputs from the database backups stack in the ``region``.

        :param region: see the one-line description.
        """
        outputs: dict = get_stack_outputs(stack_name=StackNames.db_backups_bucket, region=region)

        return cls(
            rootski_db_backups_s3_bucket_arn=outputs[
                DbBucketStackOutputKeys.rootski_db_backups_s3_bucket_arn.value
            ],
            rootski_db_backups_s3_bucket_name=outputs[
                DbBucketStackOutputKeys.rootski_db_backups_s3_bucket_name.value
            ],
        )


@dataclass
class IamUserStackOutputs:
    """Utility class to fetch outputs from an IamUserStack."""

    rootski_iam_user_secret_key_id: str
    rootski_iam_user_secret_key: str

    @classmethod
    def from_cloudformation(cls, region: str = AWS_REGION):
        """Retrieve outputs for the deployed IamUserStack in the given ``region``.

        :param region: See one-line summary.
        """
        outputs: dict = get_stack_outputs(stack_name=StackNames.iam_user, region=region)

        # use the secret ARNs in the stack outputs to fetch the actual secrets from secrets manager
        rootski_iam_user_secret_key_id = get_secret_by_id(
            secret_id=outputs[IamUserStackOutputKeys.rootski_iam_user_secret_key_id__secret_arn.value],
            region=region,
        )
        rootski_iam_user_secret_key = get_secret_by_id(
            secret_id=outputs[IamUserStackOutputKeys.rootski_iam_user_secret_key__secret_arn.value],
            region=region,
        )

        return cls(
            rootski_iam_user_secret_key_id=rootski_iam_user_secret_key_id,
            rootski_iam_user_secret_key=rootski_iam_user_secret_key,
        )


@dataclass
class LightsailInstanceStackOutputs:
    """Utility class to fetch outputs from a LightsailInstanceStack."""

    static_ip: str
    ssh_key_pair_name: str
    lightsail_admin_username: str

    @classmethod
    def from_cloudformation(cls, region: str = AWS_REGION):
        """Fetch stack values from the stack deployed in the given region.

        :param region: See one-line summary
        """
        outputs: dict = get_stack_outputs(stack_name=StackNames.lightsail_instance, region=region)

        return cls(
            static_ip=outputs[LightsailStackOutputKeys.static_ip.value],
            ssh_key_pair_name=outputs[LightsailStackOutputKeys.ssh_key_pair_name.value],
            lightsail_admin_username=outputs[LightsailStackOutputKeys.lightsail_admin_username.value],
        )


############################
# --- Helper Functions --- #
############################

TCdkCommand = Literal["diff", "deploy", "destroy"]


def run_cdk_command(
    cdk_cmd: TCdkCommand,
    app_py_fpath: Path,
    context_vars: Dict[str, str],
    stack_names: List[str] = None,
    region: str = AWS_REGION,
) -> int:
    """Run ``cdk diff|deploy|destroy``.

    :param cdk_cmd: subcommand of the AWS ``cdk`` command to run
    :param app_py_fpath: location of ``app.py`` for the CDK app to act on
    :param context_vars: key-value pairs that are used with ``note.try_get_context(key)`` calls
    :param stack_names: list of stack names registered in ``app.py::app`` to deploy
    :param region: AWS region to deploy the stacks to
    :return: exit status code of the ``cdk <subcommand>``
    """
    if not stack_names:
        stack_names = ["'*'"]

    cmd = [
        "cdk",
        cdk_cmd,
        ",".join(stack_names),
        "--app",
        f"'python {str(app_py_fpath)}'",
        "--region",
        region,
    ]

    if cdk_cmd == "deploy":
        cmd.extend(["--require-approval", "never"])

    for k, val in context_vars.items():
        cmd.extend(["--context", f"{k}={val}"])
    status_code = run_shell_cmd(cmd)
    return status_code


def deploy_cdk_app(
    app_py_fpath: Path,
    stack_names: List[str],
    context_vars: Dict[str, str] = None,
    region: str = AWS_REGION,
):
    """Run ``cdk deploy`` on a CDK app.

    :param app_py_fpath: location of ``app.py`` for the CDK app to act on
    :param context_vars: key-value pairs that are used with ``note.try_get_context(key)`` calls
    :param stack_names: list of stack names registered in ``app.py::app`` to deploy
    :param region: AWS region to deploy the stacks to

    :raises Exception: if the exit status is non-zero
    """
    if not context_vars:
        context_vars = {}

    status_code = run_cdk_command(
        cdk_cmd="deploy",
        app_py_fpath=app_py_fpath,
        stack_names=stack_names,
        context_vars=context_vars,
        region=region,
    )
    if status_code != 0:
        raise Exception("cdk deploy failed")


def diff_cdk_app(
    app_py_fpath: Path,
    stack_names: List[str],
    context_vars: Dict[str, str] = None,
    region: str = AWS_REGION,
):
    """Run ``cdk diff`` on a CDK app.

    :param app_py_fpath: location of ``app.py`` for the CDK app to act on
    :param context_vars: key-value pairs that are used with ``note.try_get_context(key)`` calls
    :param stack_names: list of stack names registered in ``app.py::app`` to deploy
    :param region: AWS region to deploy the stacks to
    """
    if not context_vars:
        context_vars = {}

    run_cdk_command(
        cdk_cmd="diff",
        app_py_fpath=app_py_fpath,
        stack_names=stack_names,
        context_vars=context_vars,
        region=region,
    )


def log_subprocess_output(pipe):
    """Log the output of a subprocess real-time as it executes.

    :param pipe: a subprocess output pipe.
    """
    # b'\n'-separated lines
    for line in iter(pipe.readline, b""):
        print(line.decode().strip(), sep="")


def run_shell_cmd(cmd: List[str]) -> int:
    """Execute a bash command as a subprocess.

    :param cmd: Command as a list of arguments
    :return: exit status code of the command
    """
    env_vars = dict(os.environ) | {"SYSTEMD": "1"}
    with Popen(cmd, stdout=PIPE, stderr=STDOUT, env=env_vars) as process:
        with process.stdout:
            log_subprocess_output(process.stdout)
        exit_code = process.wait()  # 0 means success
        return exit_code


################
# --- Main --- #
################


def main():
    """Deploy each of the three apps needed for the rootski database."""
    os.environ["AWS_PROFILE"] = "rootski"

    # create DB backup S3 bucket and IAM user
    deploy_cdk_app(
        app_py_fpath=THIS_DIR / "lightsail_dependencies/app.py",
        stack_names=['"*"'],
    )
    iam_user_stack_outputs = IamUserStackOutputs.from_cloudformation()

    # create the lightsail instance with the IAM user credentials in the user-data.sh script
    deploy_cdk_app(
        app_py_fpath=THIS_DIR / "lightsail/app.py",
        stack_names=['"*"'],
        context_vars={
            LightsailInstanceContextVars.iam_access_key_id.value: iam_user_stack_outputs.rootski_iam_user_secret_key_id,
            LightsailInstanceContextVars.iam_access_key.value: iam_user_stack_outputs.rootski_iam_user_secret_key,
        },
    )
    lightsail_instance_stack_outputs = LightsailInstanceStackOutputs.from_cloudformation()

    # create the subdomains and route53 rules pointing to the lightsail static ip
    deploy_cdk_app(
        app_py_fpath=THIS_DIR / "lightsail_subdomains/app.py",
        stack_names=['"*"'],
        context_vars={
            SubdomainsContextVars.rootski_lightsail_intance_static_ip: lightsail_instance_stack_outputs.static_ip,
        },
    )


if __name__ == "__main__":
    main()
