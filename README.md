
# Cusater 的博客框架

> 从零搭建的个人博客框架 —— 纯 Python + HTML/CSS/JS，零依赖、自动化，一键部署到 GitHub Pages。

无需安装 Node.js、npm，无需 `pip install`，**一台装了 Python 3.8+ 的电脑就能跑**。

---

##  特性

| 特性 | 说明 |
|------|------|
|  **零依赖** | Python 只用标准库，前端纯原生 HTML/CSS/JS，没有任何第三方框架 |
|  **自动化工具** | `tools.py` 一键创建文章 / 构建页面 / 推送到 GitHub |
|  **双主题** | 明亮/暗黑主题，刷新不闪烁（localStorage 同步） |
|  **响应式** | 手机、平板、桌面端自适应 |
|  **文章搜索** | 按标题/摘要/标签/日期关键词搜索，结果高亮匹配 |
|  **归档页面** | 按年份分组，按日期降序排列 |
|  **上下篇导航** | 文章页底部一键跳转相邻文章 |
|  **打印友好** | 打印样式已配置，导出 PDF 干净整洁 |
|  **单页体验** | Hash 路由实现文章/归档/关于页无刷新切换 |
|  **静态部署** | 直接部署到 GitHub Pages / Vercel / Netlify / Cloudflare Pages |

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 构建工具 | **Python 3**（标准库） | 解析 Markdown front matter → 自研解析器渲染 HTML → 生成文章页和首页数据 → 自动 Git |
| 页面结构 | **HTML5** | 文章模板 + 首页 SPA（含路由/搜索/归档/关于） |
| 视觉样式 | **CSS3** | CSS 变量驱动主题、响应式布局、过渡动画 |
| 交互逻辑 | **原生 JavaScript** | Hash 路由、搜索过滤、主题切换、归档渲染 |

自研 Markdown 解析器支持：
- 标题 `# / ## / ###`
- 引用 `>`
- 无序 / 有序列表 `- / * / 1.`
- 代码块 ` ``` `、行内代码 `` ` ``
- 分隔线 `--- / ***`
- 粗体 `**文字**`、斜体 `*文字*` / `_文字_`
- 链接 `[文字](URL)`、图片 `![说明](URL)`

---

##  目录结构

```
blog/
├── posts/                  # 你的 Markdown 文章放在这里
│   └── YYYY-MM-DD-标题.md  # 文件名由 tools.py 自动创建（不要手动改）
├── articles/               # build.py 自动生成的文章 HTML（不要手改）
├── avatar.jpg              # 你的头像（换成自己的同名文件）
├── build.py                # 构建脚本：posts/ → articles/ + posts-data.js
├── tools.py                # 工具入口：创建文章 / 构建 / 部署一条龙
├── index.html              # 首页（含 SPA 路由 + 关于页内容）
├── style.css               # 全站样式（CSS 变量驱动，易自定义）
├── posts-data.js           # build.py 自动生成的首页文章数据（不要手改）
└── README.md               # 本文件
```

---

##  快速开始

### 1. 环境检查

只需要 Python 3.8+：

```bash
python --version
```

没装？去 [python.org](https://www.python.org/downloads/) 下载就行。

### 2. 克隆 / 下载模板

```bash
# 克隆示例仓库（建议先 Fork 到自己账号，再 clone 自己的地址）
git clone https://github.com/Cusater/Cusater.github.io.git
cd Cusater.github.io
```

或者直接 **Download ZIP** 解压。

> 💡 提示：如果你用 GitHub Pages 的"用户名仓库"（`<用户名>.github.io`），也可以直接从本模板仓库 Fork，然后改仓库名为 `<你的用户名>.github.io`。

### 3. 替换成你自己的信息

> 🔔 以下所有要改的内容都集中在 **`index.html`** 一个文件里，搜类名/注释就能找到。

#### ① 头像
把仓库根目录的 `avatar.jpg` 换成你自己的头像照片（**文件名和后缀保持 `avatar.jpg`**，正方形效果最好）。

#### ② 关于页（`renderAboutPage` 函数）
打开 `index.html`，搜索 `renderAboutPage`，按下面几项改：
- `<img class="about-avatar">` 的 `alt` 文本改成"你的名字的头像"
- `<h2 class="about-name">` 换成你的昵称 / 真实姓名
- `<div class="about-text">` 里的个人介绍（爱好、经历等，支持 `<br>`、`<h3>` 等 HTML 标签，`index.html` 里有示例）
- `<div class="about-skills">` 下的 `<span class="about-skill-tag">` 技能 / 兴趣标签，增删都行

#### ③ 博客标题、GitHub 导航、页脚
在 `index.html` 里搜索并修改：
- `.site-title`：博客主标题（默认是"我的个人博客"）
- `#nav-github` 的 `href`：顶部导航 GitHub 图标/文字链接，改成你自己的主页
- `.site-footer` 里的 `© 2026 Edit by XXX`：页脚署名

### 4. 创建第一篇文章

```bash
python tools.py
# 输入 1（创建文章）
# 按提示输入 标题 / 标签（空格分隔）/ 摘要
```

脚本会在 `posts/` 下创建一个 Markdown 文件，直接打开写正文（支持标准 Markdown 语法，见上文）。

### 5. 构建页面

```bash
python tools.py
# 输入 2（更新所有文章）
```

脚本会自动：
- 把 `posts/` 下所有 `.md` 渲染成独立 HTML 页面放到 `articles/`
- 更新首页文章列表数据 `posts-data.js`

### 6. 本地预览

**最简单**：双击 `index.html` 直接在浏览器打开。

**推荐**（避免某些浏览器对本地文件的限制）：

```bash
python -m http.server 8000
```

然后访问 http://localhost:8000

---

## 🌐 部署到 GitHub Pages

GitHub Pages 有两种仓库类型，**访问地址和仓库名规则不同**，别搞混：

| 类型 | 仓库名要求 | 访问地址 | 适用场景 |
|------|-----------|----------|----------|
| **用户名仓库（推荐）** | 必须是 `<你的用户名>.github.io` | `https://<你的用户名>.github.io`（根域名，没有 `/仓库名`） | 作为个人主博客，一个账号只能有一个 |
| **项目仓库** | 任意名字，比如 `my-blog` | `https://<你的用户名>.github.io/<仓库名>` | 测试、或者有多套博客/项目站 |

本模板（Cusater 的仓库）属于**用户名仓库**，生成的文章链接、CSS/JS 都是相对路径，**两种仓库都能直接用**，不需要改代码。

### 首次部署（只需一次）

```bash
# ① 如果你还没初始化 Git
git init
git branch -M main

# ② 关联远程仓库（改成你自己的地址！）
git remote add origin https://github.com/你的用户名/你的仓库名.git

# ③ 初次提交 & 推送
git add .
git commit -m "init my blog"
git push -u origin main
```

然后在 **GitHub 仓库页面** 开启 Pages：

**Settings → Pages → Build and deployment → Source** 选：
- Branch: `main`
- Folder: `/ (root)`（项目根目录，不是 /docs）

保存，等 1~2 分钟，对应地址就能访问了（两种仓库见上表）。

### 日常更新文章

```bash
python tools.py
→ 输入 1（创建文章 / 或自己在 posts/ 里写 md）
→ 输入 2（构建页面，生成 articles/ 和 posts-data.js）
→ 输入 3（自动 git add + commit + push 推上去）

# 想删文章：
python tools.py → 输入 4（删除文章后可选是否立即重建）
```

GitHub Pages 会在 push 后的 1 分钟内自动重新部署生效。

---

## 🧰 tools.py 菜单说明

运行 `python tools.py` 会看到四个选项：

| 选项 | 功能 | 说明 |
|------|------|------|
| 1 | 创建文章 | 引导输入标题/标签/摘要，自动在 `posts/` 生成带 front matter 的 `.md` 文件 |
| 2 | 更新所有文章 | 调用 `build.py`，重新渲染所有文章页 + 更新首页数据 + 重算上下篇导航 |
| 3 | 推送到 GitHub | 自动执行 `git add .` → `git commit` → `git push`，任何一步出错会停止并提示 |
| 4 | 删除文章 | 列出文章选编号，二次确认后同时删除 md + html，可选是否立即重建首页列表 |

每次操作完成后会询问是否继续运行，方便连续执行（比如先 2 再 3，或先 4 再 2）。

---

##  自定义指南

### 换主题色

打开 `style.css`：

```css
:root {
    --text-accent: #2c5f7c;        /* 强调色：链接、标签高亮、按钮 */
    --text-accent-hover: #1a4058;  /* 强调色悬停 */
    --bg-accent-soft: #eaf2f7;     /* 强调色浅背景 */
}
html[data-theme="dark"] {
    --text-accent: #6fb3d0;        /* 暗黑主题强调色 */
    --text-accent-hover: #8fc7de;
    --bg-accent-soft: #1f2d38;
}
```

改这几个变量就行，全站自动生效。

### 改配色风格（奶油/纯白/深色底等）

`--bg-page`（页面底）、`--bg-card`（卡片底）、`--bg-header`（头底）、`--text-primary`（主文字）这些变量都在 `:root` 和 `html[data-theme="dark"]` 里，按喜好调。

### 自定义文章链接样式

`.article-body a`（默认态）和 `.article-body a:hover`（悬停态）在 `style.css` 里找，可以调下划线粗细、颜色、有无背景高亮。

### 扩展 Markdown 语法

`build.py` 中的 `render_markdown()` 函数，每个块级语法一个 `if`。参考现有结构加表格（`| a | b |`）、任务列表（`- [x]`）之类的语法不复杂。

### 扩展 tools.py 功能

想加批量删除文章、统计字数、检查死链、生成 RSS 等功能，直接在 `main()` 的 `if idinp == X` 后面加新分支即可，循环结构已经准备好了。

---

##  文章 Markdown 格式规范

每个 `.md` 文件开头必须有 front matter（`tools.py` 会自动帮你填好）：

```markdown
---
title: 文章标题
date: 2026-08-13
tags: 标签1, 标签2
excerpt: 出现在首页卡片上的一句话摘要
---

正文从这里开始写，正常 Markdown 语法。

## 二级标题

普通段落可以直接写。
连续两行没空行的话会合并成一段，中间换行。

空一行就是新段落。

> 这是一段引用
> 可以多行

- 无序列表项 1
- 无序列表项 2
  - 子项（缩进）

1. 有序列表项 1
2. 有序列表项 2

`行内代码` 用反引号

```
代码块
用三个反引号
```

这是 [链接文字](https://example.com)，这是 ![图片说明](图片URL)。
```

---

##  常见问题

**Q: 双击 index.html 打开，样式 / 图片 / 文章页跳转有问题？**
A: 用 `python -m http.server 8000` 起本地服务再访问，因为部分浏览器对 `file://` 协议有限制。部署到 GitHub Pages 就正常了。

**Q: 推送到 GitHub 显示没有变更？**
A: 说明你确实没改文件，`tools.py` 的"3"会如实告诉你，不用怕。

**Q: 想删除某篇文章？**
A: 直接把 `posts/` 下对应的 `.md` 文件删掉，然后运行 `tools.py` 选 2 重新构建，首页和 articles/ 会自动清理（手动把 `articles/` 下对应 HTML 删掉更干净）。

**Q: 文章页找不到 404？**
A: 先确保跑过 `tools.py` 选 2 构建过。如果是部署到 `<用户名>.github.io` 这种根仓库（不是项目仓库），没问题。如果是项目仓库（路径带仓库名），文章内引用的相对路径也都对得上，因为生成时用的是相对路径。

---

##  许可证

MIT License — 随便用，随便改。如果你愿意，保留一句"基于 Cusater 的博客框架"我会很开心，但不强制。

---

##  贡献

觉得好用？欢迎：
-  点个 Star
-  遇到问题提 Issue
- 有好想法也可以直接 PR
## 相关链接
- [Cusater 的博客框架仓库](https://github.com/Cusater/blogframe)
- [我的博客](https://cusater.github.io/)
写作愉快 📝
