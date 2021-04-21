from math import ceil
from time import time
from json import dump
from re import findall
from requests import get
from subprocess import run
from datetime import datetime

org_name = "Magisk-Modules-Repo"
api_url = "https://api.github.com"
module_prop = f"https://cdn.jsdelivr.net/gh/{org_name}/{{}}@{{}}/module.prop"


def time_formatter(seconds: int) -> str:
    result = ""
    v_m = 0
    remainder = seconds
    r_ange_s = {"days": (24 * 60 * 60), "hours": (60 * 60), "minutes": 60, "seconds": 1}
    for age in r_ange_s:
        divisor = r_ange_s[age]
        v_m, remainder = divmod(remainder, divisor)
        v_m = int(v_m)
        if v_m != 0:
            result += f" {v_m} {age} "
    return result


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
    run(["git", "add", "modules.json", "by_id.json", "modules_list.json"])
    run(["git", "commit", "-m", f"Automated Sync: {now}"])
    run(["git", "push"])
    print("Pushed to remote")


def get_api_data():
    print("Getting data from Official API...")
    data = get(f"{api_url}/orgs/{org_name}").json()
    total_repos = data["public_repos"]
    pages_req = ceil(total_repos / 10)
    api_data = []
    for i in range(1, pages_req):
        rec = get(f"{api_url}/orgs/{org_name}/repos?per_page=100&page={i}").json()
        api_data += rec
    return api_data


def save_file(filename, details):
    with open(filename, "w+") as f:
        dump(details, f, indent=4)
    print(f"Done generating {filename}")
    return


def gen_modules_json(repos, filename):
    """
    generate modules.json file
    """
    print(f"Genarating {filename}")
    details = []
    # iterate for all repos in organisation
    for repo in repos:
        name = repo["name"]
        # we don't need 'submission' repo in file
        if name == "submission":
            continue
        branch = repo["default_branch"]
        url = repo["clone_url"].replace(".git", "")
        language = repo["language"]
        last_updated = repo["pushed_at"]
        tmp_dict = {
            "name": name,
            "branch": branch,
            "url": url,
            "language": language,
            "last_updated": last_updated,
            "properties": {},
        }
        build_props = read_prop(module_prop.format(name, branch))
        for prop in build_props:
            tmp_dict["properties"][prop[0]] = prop[1]
        details.append(tmp_dict)
    save_file(filename, details)


def gen_id_json(repos, filename):
    """
    generate by_id.json file
    """
    print(f"Genarating {filename}")
    details = {}
    # iterate for all repos in organisation
    for repo in repos:
        name = repo["name"]
        # we don't need 'submission' repo in file
        if name == "submission":
            continue
        branch = repo["default_branch"]
        url = repo["clone_url"].replace(".git", "")
        language = repo["language"]
        last_updated = repo["pushed_at"]
        tmp_dict = {
            "branch": branch,
            "url": url,
            "language": language,
            "last_updated": last_updated,
            "properties": {},
        }
        build_props = read_prop(module_prop.format(name, branch))
        for prop in build_props:
            tmp_dict["properties"][prop[0]] = prop[1]
        id_prop = tmp_dict["properties"]["id"]
        details[id_prop] = tmp_dict

    save_file(filename, details)


def gen_modules_list(repos, filename):
    """
    generate modules_list.json file
    """
    print(f"Genarating {filename}")
    details = {}
    # iterate for all repos in organisation
    for repo in repos:
        name = repo["name"]
        # we don't need 'submission' repo in file
        if name == "submission":
            continue
        details.append(name)

    save_file(filename, details)


def purge_jsdeliver():
    print("Sending purge request on jsdelivr.net")
    tvar1 = get("https://purge.jsdelivr.net/gh/DivideTrackers/magisk-modules-tracker@latest/modules.json")
    tvar2 = get("https://purge.jsdelivr.net/gh/DivideTrackers/magisk-modules-tracker@latest/by_id.json")
    tvar3 = get("https://purge.jsdelivr.net/gh/DivideTrackers/magisk-modules-tracker@latest/modules_list.json")
    
    if tvar1.status_code == 200 and tvar2.status_code == 200 and tvar3.status_code == 200:
        return True
    return False


def main():
    """
    main script
    """
    start = time()
    rep_data = get_api_data()
    gen_modules_json(rep_data, "modules.json")
    gen_id_json(rep_data, "by_id.json")
    gen_modules_list(rep_data, "modules_list.json")
    push_files()
    purge_jsdeliver()
    total_time = time_formatter(int(time() - start))
    print(f"Completed in {total_time}")


if __name__ == "__main__":
    main()
