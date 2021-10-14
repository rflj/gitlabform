from logging import debug
from cli_ui import debug as verbose

from gitlabform.gitlab import GitLab
from gitlabform.gitlab.core import NotFoundException
from gitlabform.processors.abstract_processor import AbstractProcessor


class GroupSecretVariablesProcessor(AbstractProcessor):
    def __init__(self, gitlab: GitLab):
        super().__init__("group_secret_variables", gitlab)

    def _process_configuration(self, group: str, configuration: dict):
        debug(
            "Group secret variables BEFORE: %s",
            self.gitlab.get_group_secret_variables(group),
        )

        for secret_variable in sorted(configuration["group_secret_variables"]):

            if configuration["group_secret_variables"][secret_variable].get(
                "delete", False
            ):
                key = configuration["group_secret_variables"][secret_variable]["key"]
                verbose(f"Deleting {secret_variable}: {key} in group {group}")
                self.gitlab.delete_group_secret_variable(group, key)
            else:
                verbose(f"Setting group secret variable: {secret_variable}")
                try:
                    self.gitlab.put_group_secret_variable(
                        group, configuration["group_secret_variables"][secret_variable]
                    )
                except NotFoundException:
                    self.gitlab.post_group_secret_variable(
                        group, configuration["group_secret_variables"][secret_variable]
                    )

        debug(
            "Groups secret variables AFTER: %s",
            self.gitlab.get_group_secret_variables(group),
        )
