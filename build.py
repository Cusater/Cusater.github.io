# -*- coding: utf-8 -*-
"""
build.py —— 把 posts/ 目录下的 Markdown 文章编译成独立的 HTML 文章页 + 更新首页数据

用法：
    python build.py

每次新增 / 修改文章后，运行一次本脚本，再刷新网页即可。

文章格式见 posts/ 目录下的 .md 文件：文件头用 --- 包裹元信息（title/date/tags/excerpt），
下面是正文。正文支持：
    标题 # ## ###       引用 >              无序列表 - / *
    有序列表 1.         代码块 ```          分隔线 ---
    粗体 **文字**       斜体 *文字* / _文字_  行内代码 `文字`
    链接 [文字](网址)   图片 ![说明](图片地址)

生成的产物：
    articles/文章名.html   每篇文章一个独立页面（自动引用 ../style.css）
    posts-data.js          首页文章列表数据（由 index.html 读取）
"""

import os
import re
import json

BASE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BASE, 'posts')
OUT_DIR = os.path.join(BASE, 'articles')
DATA_OUT = os.path.join(BASE, 'posts-data.js')

# ==================== front matter 解析 ====================
def parse_front_matter(text):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?', text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).split('\n'):
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key, value = key.strip(), value.strip()
        if value.startswith('[') and value.endswith(']'):
            # [a, b, c] 数组形式
            value = [x.strip() for x in value[1:-1].split(',') if x.strip()]
        elif value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        meta[key] = value
    return meta, text[m.end():]

# ==================== HTML 转义（防注入） ====================
def esc(s):
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;'))

# ==================== 行内语法 ====================
def inline(s):
    s = esc(s)
    s = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)',
               r'<img src="\2" alt="\1" style="max-width:100%;border-radius:8px;">', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)',
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    # 斜体，避免与粗体冲突
    s = re.sub(r'(^|[^*])\*([^*\n]+)\*(?!\*)', r'\1<em>\2</em>', s)
    s = re.sub(r'(^|[^_])_([^_\n]+)_(?!_)', r'\1<em>\2</em>', s)
    return s

# ==================== Markdown → HTML ====================
def render_markdown(md):
    lines = md.replace('\r\n', '\n').split('\n')
    html = []
    i = 0
    in_code = False
    code_buf = []
    list_type = None  # 'ul' | 'ol'
    quote_buf = []

    def flush_quote():
        if quote_buf:
            html.append('<blockquote>' + ''.join('<p>' + inline(l) + '</p>' for l in quote_buf) + '</blockquote>')
            quote_buf.clear()

    def flush_list():
        nonlocal list_type
        if list_type:
            html.append('</' + list_type + '>')
            list_type = None

    while i < len(lines):
        line = lines[i]
        t = line.strip()

        # 代码块
        if t.startswith('```'):
            if not in_code:
                in_code = True
                code_buf = []
            else:
                in_code = False
                html.append('<pre><code>' + esc('\n'.join(code_buf)) + '</code></pre>')
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # 空行
        if t == '':
            flush_quote()
            flush_list()
            i += 1
            continue

        # 标题
        h = re.match(r'^(#{1,3})\s+(.*)$', t)
        if h:
            flush_quote()
            flush_list()
            level = len(h.group(1))
            html.append('<h%d>%s</h%d>' % (level, inline(h.group(2)), level))
            i += 1
            continue

        # 引用
        if t.startswith('>'):
            flush_list()
            quote_buf.append(re.sub(r'^>\s?', '', t))
            i += 1
            continue

        # 无序列表
        ul = re.match(r'^[-*]\s+(.*)$', t)
        if ul:
            flush_quote()
            if list_type != 'ul':
                flush_list()
                html.append('<ul>')
                list_type = 'ul'
            html.append('<li>' + inline(ul.group(1)) + '</li>')
            i += 1
            continue

        # 有序列表
        ol = re.match(r'^\d+\.\s+(.*)$', t)
        if ol:
            flush_quote()
            if list_type != 'ol':
                flush_list()
                html.append('<ol>')
                list_type = 'ol'
            html.append('<li>' + inline(ol.group(1)) + '</li>')
            i += 1
            continue

        # 分隔线
        if re.match(r'^(-{3,}|\*{3,})$', t):
            flush_quote()
            flush_list()
            html.append('<hr>')
            i += 1
            continue

        # 普通段落（合并连续行）
        flush_quote()
        flush_list()
        para = [t]
        i += 1
        while i < len(lines):
            nt = lines[i].strip()
            if (nt == '' or re.match(r'^(#{1,3})\s+', nt) or nt.startswith('>')
                    or re.match(r'^[-*]\s+', nt) or re.match(r'^\d+\.\s+', nt)
                    or nt.startswith('```') or re.match(r'^(-{3,}|\*{3,})$', nt)):
                break
            para.append(nt)
            i += 1
        html.append('<p>' + inline('<br>'.join(para)) + '</p>')

    flush_quote()
    flush_list()
    if in_code:
        html.append('<pre><code>' + esc('\n'.join(code_buf)) + '</code></pre>')
    return '\n'.join(html)

# ==================== 文章页 HTML 模板 ====================
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Cusater的博客</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>

    <header class="site-header">
        <div class="header-inner">
            <a class="site-title" href="../index.html" title="回到首页">
                我的个人博客
            </a>
            <nav>
                <ul class="nav-links">
                    <li><a href="../index.html">文章</a></li>
                    <li><a href="../index.html#/about">关于</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <main class="main-content">
        <article class="article-detail">
            <a class="back-link" href="../index.html">
                <span class="arrow-icon">←</span> 返回文章列表
            </a>
            <p class="article-date">{date}</p>
            <h1 class="article-title">{title}</h1>
            <div class="article-tags">
                {tags_html}
            </div>
            <hr class="article-divider">
            <div class="article-body">
                {content}
            </div>
        </article>
    </main>

    <footer class="site-footer">
        <p>© 2026 Edit by Cusater <span class="footer-heart">♥</span></p>
    </footer>
</body>
</html>
"""

def slugify(name):
    """把文件名去掉 .md 后缀作为页面名（保留中文，直观）"""
    return name[:-3] if name.endswith('.md') else name

def make_tags_html(tags):
    return ''.join('<span class="article-tag">#%s</span>' % esc(t) for t in tags)

def build_article_page(article, out_file):
    page = PAGE_TEMPLATE.format(
        title=esc(article['title']),
        date=esc(article['date']),
        tags_html=make_tags_html(article['tags']),
        content=article['content'],
    )
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(page)

# ==================== 首页数据 ====================
def build_data_js(articles):
    lines = [
        '// 本文件由 build.py 自动生成，请勿手动修改。',
        '// 编辑文章请修改 posts/ 目录下的 .md 文件，然后运行：python build.py',
        '',
        'const articles = ' + json.dumps(articles, ensure_ascii=False, indent=4) + ';',
        '',
    ]
    with open(DATA_OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

# ==================== 主流程 ====================
def main():
    if not os.path.isdir(POSTS_DIR):
        print('未找到 posts 目录，请确认目录结构正确')
        return
    os.makedirs(OUT_DIR, exist_ok=True)

    files = sorted(f for f in os.listdir(POSTS_DIR) if f.endswith('.md'))

    records = []
    for name in files:
        with open(os.path.join(POSTS_DIR, name), 'r', encoding='utf-8') as f:
            raw = f.read()
        meta, body = parse_front_matter(raw)
        tags = meta.get('tags', [])
        if isinstance(tags, str):
            tags = [x.strip() for x in tags.split(',') if x.strip()]
        records.append({
            'file': name,
            'title': meta.get('title', name[:-3]),
            'date': meta.get('date', ''),
            'tags': tags,
            'excerpt': meta.get('excerpt', ''),
            'content': render_markdown(body.strip()),
        })

    # 按日期排序（同日期按文件名），重新分配 id 并生成文章页
    records.sort(key=lambda a: (a['date'], a['file']))
    articles = []
    for idx, a in enumerate(records, 1):
        slug = slugify(a['file'])
        link = 'articles/' + slug + '.html'
        build_article_page(a, os.path.join(OUT_DIR, slug + '.html'))
        articles.append({
            'id': idx,
            'title': a['title'],
            'date': a['date'],
            'tags': a['tags'],
            'excerpt': a['excerpt'],
            'link': link,
        })

    build_data_js(articles)
    print('✔ 已生成 %d 篇文章页面到 articles/ 目录' % len(articles))
    for a in articles:
        print('   - %s (%s)' % (a['title'], a['link']))
    print('✔ 已更新 ' + DATA_OUT)

if __name__ == '__main__':
    main()
