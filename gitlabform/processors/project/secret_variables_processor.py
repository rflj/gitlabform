from logging import debug
from cli_ui import debug as verbose, fatal
from cli_ui import warning

import copy
import textwrap
import yaml

from gitlabform import EXIT_INVALID_INPUT
from gitlabform.gitlab import GitLab
from gitlabform.gitlab.core import NotFoundException
from gitlabform.processors.abstract_processor import AbstractProcessor
from gitlabform.processors.util.difference_logger import hide


class SecretVariablesProcessor(AbstractProcessor):
    def __init__(self, gitlab: GitLab, strict: bool):
        super().__init__("secret_variables", gitlab)
        self.strict = strict

    def _process_configuration(self, project_and_group: str, configuration: dict):
        if (
            self.gitlab.get_project_settings(project_and_group)["builds_access_level"]
            == "disabled"
        ):
            if self.strict:
                fatal(
                    "Builds disabled in this project so I can't set secret variables here.",
                    EXIT_INVALID_INPUT,
                )
            else:
                warning(
                    "Builds disabled in this project so I can't set secret variables here."
                )
            return

        debug(
            "Secret variables BEFORE: %s",
            self.gitlab.get_secret_variables(project_and_group),
        )

        for secret_variable in sorted(configuration["secret_variables"]):

            if configuration["secret_variables"][secret_variable].get("delete", False):
                key = configuration["secret_variables"][secret_variable]["key"]
                verbose(
                    f"Deleting {secret_variable}: {key} in project {project_and_group}"
                )
                self.gitlab.delete_secret_variable(project_and_group, key)
            else:
                verbose(f"Setting secret variable: {secret_variable}")
                try:
                    self.gitlab.put_secret_variable(
                        project_and_group,
                        configuration["secret_variables"][secret_variable],
                    )
                except NotFoundException:
                    self.gitlab.post_secret_variable(
                        project_and_group,
                        configuration["secret_variables"][secret_variable],
                    )

        debug(
            "Secret variables AFTER: %s",
            self.gitlab.get_secret_variables(project_and_group),
        )

    def _print_diff(self, project_and_group: str, configuration):

        current_secret_variables = self.gitlab.get_secret_variables(project_and_group)

        for secret_variable in current_secret_variables:
            secret_variable["value"] = hide(secret_variable["value"])

        verbose(f"Secret variables for {project_and_group} in GitLab:")

        verbose(
            textwrap.indent(
                yaml.dump(current_secret_variables, default_flow_style=False),
                "  ",
            )
        )

        verbose(f"Secret variables in {project_and_group} in configuration:")

        configured_secret_variables = copy.deepcopy(configuration)
        for key in configured_secret_variables.keys():
            configured_secret_variables[key]["value"] = hide(
                configured_secret_variables[key]["value"]
            )

        verbose(
            textwrap.indent(
                yaml.dump(configured_secret_variables, default_flow_style=False),
                "  ",
            )
        )
