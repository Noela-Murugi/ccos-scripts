"""
This script pulls the members of the "Community Team Tracking" Asana
project, formats it a bit, then pushes it to a databag
"databags/community_team_list.json" in creativecommons/creativecommons.github.io-source
"""

# Standard Lib
import os
import json

# Third party
import asana
from github import Github

ASANA_CLIENT = asana.Client.access_token(os.environ["ADMIN_ASANA_TOKEN"])
ASANA_PROJECT_GID = "1172465506923661"

GITHUB_CLIENT = Github(os.environ["ADMIN_GITHUB_TOKEN"])

def generate_databag():
    """
    databag schema
    {
        "team_members": [
            {
                "name": "",
                "projects": [
                    "",
                    ""
                ]
            },
            ...
        ]
    }
    """

    databag = {
        "projects": []
    }

    members = ASANA_CLIENT.tasks.find_by_section(
        ASANA_PROJECT_GID,
        opt_fields=["name", "custom_fields"]
    )
    print("    Team members pulled.")

    print("    Processing team members...")
    for member in members:
        if member["name"] == "": continue # Sometimes blank names come up
        role = get_custom_field(member, "Role")
        project_name = get_custom_field(member, "Project Name")
        seen_projects = []
        
        if project_name not in seen_projects:
            databag["projects"].append({
                "name": project_name,
                "members": []
            })
            seen_projects.append(project_name)

        for project in databag["projects"]:
            if project["name"] == project_name:
                project["members"].append({
                    "name": member["name"],
                    "role": role
                })

    print("    Done.")

    return databag

def format_project(role, project, repos):
    """
    Formats data about member roles into a nice pretty string
    """
    return "{} for the {} project{}".format(
        role,
        project,
        format_repo(repos)
    )

def format_repo(repos):
    """
    The formatting for the repo part of the project string needs a
    little extra doing, this function does that doing.
    """
    base = ", has privileges for the {} {}"
    if repos is None:
        return ""
    else:
        return base.format(
            repos,
            "repository" if len(repos.split(",")) == 1 else "repositories"
        )

def get_custom_field(task, field_name):
    """
    Gets the value of a custom field
    """
    for field in task["custom_fields"]:
        if field["name"] == "Repo(s)" and field_name == "Repo(s)":
            return field["text_value"]
        elif field["name"] == field_name:
            return field["enum_value"]["name"]

def push_to_repo(databag):    
    """
    Pushes the generated databag to GitHub
    """
    oss_repo = GITHUB_CLIENT.get_repo("creativecommons/creativecommons.github.io-source")
    update = oss_repo.update_file(
        path="databags/community_team_list.json",
        message="Update Community Team List Databag",
        content=json.dumps(databag, sort_keys=True, indent=4),
        sha=oss_repo.get_contents("databags/community_team_list.json").sha,
        branch="master"
    )
    return update

print("Pulling from Asana and generating databag...")
databag = generate_databag()
print("Pull successful.")

print("Pushing page content to open source repo...")
push_data = push_to_repo(databag)
print("Pushed successfully. Commit Info: {}".format(push_data))