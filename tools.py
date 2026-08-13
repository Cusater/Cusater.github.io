## 依旧屎山代码
from datetime import datetime
import os
import subprocess
import sys
today_str = datetime.now().strftime("%Y-%m-%d")
if not os.path.exists("posts"):
    os.makedirs("posts")

def list_articles():
    """列出 posts/ 下所有文章，返回 [(序号, 文件名, 标题, 日期)]"""
    if not os.path.exists("posts"):
        return []
    files = sorted(
        (f for f in os.listdir("posts") if f.endswith(".md")),
        reverse=True,
    )
    result = []
    for idx, name in enumerate(files, 1):
        title = name[:-3]  # 文件名作为标题展示
        date = ""
        try:
            with open(os.path.join("posts", name), "r", encoding="utf-8") as f:
                text = f.read()
            # 尝试从 front matter 提取真实标题和日期
            if text.startswith("---"):
                end = text.find("\n---", 3)
                if end != -1:
                    for line in text[3:end].split("\n"):
                        if line.startswith("title:"):
                            title = line.split(":", 1)[1].strip()
                        elif line.startswith("date:"):
                            date = line.split(":", 1)[1].strip()
        except Exception:
            pass
        result.append((idx, name, title, date))
    return result

def delete_article():
    articles = list_articles()
    if not articles:
        print("posts 目录下没有文章，无法删除")
        return

    print("\n===== 文章列表 =====")
    for idx, name, title, date in articles:
        date_str = f" ({date})" if date else ""
        print(f"  [{idx}] {title}{date_str}")
    print(f"  [0] 取消删除")

    try:
        choice = int(input("\n请输入要删除的文章编号："))
    except ValueError:
        print("输入错误，请输入数字！")
        return

    if choice == 0:
        print("已取消删除")
        return
    if choice < 0 or choice > len(articles):
        print("编号超出范围！")
        return

    _, md_name, title, _ = articles[choice - 1]
    md_path = os.path.join("posts", md_name)
    html_name = md_name[:-3] + ".html"
    html_path = os.path.join("articles", html_name)

    confirm = input(f"确定要删除「{title}」吗？（y/n）")
    if confirm != "y":
        print("已取消删除")
        return

    deleted_md = False
    deleted_html = False
    if os.path.exists(md_path):
        os.remove(md_path)
        deleted_md = True
        print(f"已删除 Markdown：{md_path}")
    else:
        print(f"未找到 Markdown 文件：{md_path}")

    if os.path.exists(html_path):
        os.remove(html_path)
        deleted_html = True
        print(f"已删除 HTML 页面：{html_path}")
    else:
        print(f"ℹ未找到对应 HTML 页面：{html_path}（首次构建前属正常）")

    if deleted_md or deleted_html:
        print(f"「{title}」删除完成！")
        rebuild = input("是否立即重新构建首页文章列表？（y/n）")
        if rebuild == "y":
            subprocess.run([sys.executable, "build.py"])

def main():
    print("请选择功能：")
    print("创建文章（1）")
    print("更新所有文章（2）")
    print("推送到GitHub（3）")
    print("删除文章（4）")

    try:
        idinp = int(input("请输入："))
    except ValueError:
        print("输入错误，请输入数字！")
        return

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
        print(f"文章创建成功！路径：{file_path}")

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
                print(f"命令出错：{result.stderr}")
                return False
            return True
        ok1 = run_git(["git", "add", "."])
        if not ok1:
            return
        commit_msg = f"auto update posts {today_str}"
        ok2 = run_git(["git", "commit", "-m", commit_msg])
        if not ok2:
            print("没有检测到文件改动，无需提交")
        else:
            ok3 = run_git(["git", "push"])
            if ok3:
                print("全部推送完成！")
            else:
                print("git push失败，请检查网络/仓库权限")

    elif idinp == 4:
        delete_article()

    else:
        print("无效的选项")

while True:
    main()
    while True:
        ask = input("是否继续运行：（y/n）")
        if ask in ("y", "n"):
            break
        print("输入无效，请输入 y 或 n")
    if ask != "y":
        print("已退出程序")
        break
