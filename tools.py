## 依旧屎山代码
from datetime import datetime
import os
import subprocess
import sys
today_str = datetime.now().strftime("%Y-%m-%d")

# 如果posts文件夹不存在就自动创建
if not os.path.exists("posts"):
    os.makedirs("posts")

print("请选择功能：")
print("创建文章（1）")
print("更新所有文章（2）")
print("推送到GitHub（3）")

try:
    idinp = int(input("请输入："))
except ValueError:
    print("输入错误，请输入数字！")
    exit()

if idinp == 1:
    title = input("请输入文章标题：")
    tags = input("请输入文章标签（空格分隔）：")
    excerpt = input("请输入文章摘要：")
    invalid_chars = r'\/:*?"<>|'
    safe_title = "".join([c for c in title if c not in invalid_chars])

    file_path = f"posts/{today_str}-{safe_title}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"""---
title: {title}
date: {today_str}
tags: {tags}
excerpt: {excerpt}
---

""")
    print(f"✅文章创建成功！路径：{file_path}")

elif idinp == 2:
    subprocess.run([sys.executable, "build.py"])

elif idinp == 3:
    print("\n===== 开始推送到GitHub =====")
    def run_git(cmd):
        """执行git命令，打印输出，出错抛出异常"""
        print(f"> {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌命令出错：{result.stderr}")
            return False
        return True
    ok1 = run_git(["git", "add", "."])
    if not ok1:
        exit()
    commit_msg = f"auto update posts {today_str}"
    ok2 = run_git(["git", "commit", "-m", commit_msg])
    if not ok2:
        print("⚠️没有检测到文件改动，无需提交")
    else:
        ok3 = run_git(["git", "push"])
        if ok3:
            print("✅全部推送完成！")
        else:
            print("❌git push失败，请检查网络/仓库权限")

else:
    print("无效的选项")

