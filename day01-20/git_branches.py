import urllib

import requests
import csv
from datetime import datetime, timedelta, timezone
from dateutil import parser


# ========== 配置区 ==========
GITLAB_URL = ""  # 替换成你的 GitLab 地址
PROJECT_ID = 1  # 替换成你的项目 ID
PRIVATE_TOKEN = ""  # 替换成你的访问 Token
DAYS_THRESHOLD = 120  # 未更新天数阈值
BACKUP_FILE = "branches_backup.csv"
DRY_RUN = False  # ✅ True = 只打印要删除的分支，不执行删除
# ============================

headers = {"PRIVATE-TOKEN": PRIVATE_TOKEN}

def get_branches():
    """获取项目的所有分支"""
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/branches"
    branches = []
    page = 1
    while True:
        resp = requests.get(url, headers=headers, params={"per_page": 100, "page": page})
        if resp.status_code != 200:
            raise Exception(f"获取分支失败: {resp.status_code}, {resp.text}")
        data = resp.json()
        if not data:
            break
        branches.extend(data)
        page += 1
    return branches

def backup_branches(branches):
    """保存分支清单到 CSV"""
    with open(BACKUP_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Branch", "Commit Date"])
        for b in branches:
            writer.writerow([b["name"], b["commit"]["committed_date"]])
    print(f"✅ 分支清单已保存到 {BACKUP_FILE}")

def delete_branch(branch_name):
    """删除指定分支"""
    branch_name_encoded = urllib.parse.quote(branch_name, safe="")
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/branches/{branch_name_encoded}"
    resp = requests.delete(url, headers=headers)
    if resp.status_code == 204:
        print(f"🗑️ 已删除分支: {branch_name}")
    else:
        print(f"⚠️ 删除失败 {branch_name}: {resp.status_code} {resp.text}")

def main():
    branches = get_branches()
    backup_branches(branches)

    now = datetime.now(timezone.utc)  # ✅ 替换原来的 datetime.utcnow()
    threshold_date = now - timedelta(days=DAYS_THRESHOLD)

    for b in branches:
        name = b["name"]
        commit_date = parser.parse(b["commit"]["committed_date"])

        # 保留保护分支
        if name.startswith(("main", "master", "develop", "release")):
            print(f"🔒 保留保护分支: {name}")
            continue

        # 删除超过阈值未更新的分支
        if commit_date < threshold_date:
            if DRY_RUN:
                print(f"📝 [Dry Run] 将删除分支: {name} (最后提交 {commit_date})")
            else:
                delete_branch(name)
        else:
            print(f"⏩ 保留活跃分支: {name}")

if __name__ == "__main__":
    main()
