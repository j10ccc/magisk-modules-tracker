from math import ceil
from time import time
from json import dump
from re import findall
from requests import get
from subprocess import run
from datetime import datetime

org_name = "Magisk-Modules-Repo"
api_url = "https://api.github.com"
module_prop = f"https://raw.githubusercontent.com/{org_name}/{{}}/{{}}/module.prop"


def read_prop(url):
    """
    read the prop file
    """
    data = get(url).text
    properties = findall(r"(\w+)\=(.*)", data)
    return properties


def push_files():
    """
    push files back to repo
    git add - git commit - git push
    """
    now = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    run(["git", "config", "user.name", '"Divkix"'])
    run(["git", "config", "user.email", '"techdroidroot@gmail.com"'])
    run(["git", "add", "modules.json"])
    run(["git", "commit", "-m", f"Automated Sync: {now}"])
    run(["git", "push"])
    print("Pushed to remote")


def get_api_data():
    print("Getting data from official api...")
    data = get(f"{api_url}/orgs/{org_name}").json()
    total_repos = data["public_repos"]
    pages_req = ceil(total_repos / 10)
    api_data = []
    for i in range(1, pages_req):
        rec = get(f"{api_url}/orgs/{org_name}/repos?per_page=100&page={i}").json()
        api_data += rec
    return api_data


def gen_file():
    """
    get data from all the repos
    """
    start = time()
    print("Generating the json file...")
    repos = get_api_data()
    details = []
    # iterate for all repos in organisation
    for repo in repos:
        name = repo["name"]
        branch = repo["default_branch"]
        url = repo["clone_url"].replace(".git", "")
        language = repo["language"]
        last_update = repo["updated_at"]
        tmp_dict = {
            "name": name,
            "branch": branch,
            "url": url,
            "language": language,
            "last_update": last_update,
            "properties": {},
        }
        build_props = read_prop(module_prop.format(name, branch))
        for prop in build_props:
            tmp_dict["properties"][prop[0]] = prop[1]
        details.append(tmp_dict)
        print(f"Added {name}")

    print(f"Total Repos: {len(details)}")

    # Save file
    with open("modules.json", "w+") as f:
        dump(details, f, indent=4)
    print("Done generating file...")
    total_time = time() - start
    print(f"Completed in {round(total_time, 2)}")


def main():
    """
    main script
    """
    gen_file()
    push_files()


if __name__ == "__main__":
    main()
