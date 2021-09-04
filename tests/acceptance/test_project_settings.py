from tests.acceptance import run_gitlabform


class TestProjectSettings:
    def test__builds_for_private_projects(self, gitlab, group, project):
        group_and_project_name = f"{group}/{project}"

        settings = gitlab.get_project_settings(group_and_project_name)
        assert settings["visibility"] == "private"

        config = f"""
        projects_and_groups:
          {group_and_project_name}:
            project_settings:
              visibility: internal
        """

        run_gitlabform(config, group_and_project_name)

        settings = gitlab.get_project_settings(group_and_project_name)
        assert settings["visibility"] == "internal"

    def test__squash_option(self, gitlab, group, project):
        group_and_project_name = f"{group}/{project}"

        settings = gitlab.get_project_settings(group_and_project_name)
        assert settings["squash_option"] == "default_off"

        config = f"""
        projects_and_groups:
          {group_and_project_name}:
            project_settings:
              squash_option: default_on
        """

        run_gitlabform(config, group_and_project_name)

        settings = gitlab.get_project_settings(group_and_project_name)
        assert settings["squash_option"] == "default_on"
