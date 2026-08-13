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

#请不要乱动代码！！！否则博客写起来会很麻烦！！！真的！！！

import os
import re
import json

BASE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BASE, 'posts')
OUT_DIR = os.path.join(BASE, 'articles')
DATA_OUT = os.path.join(BASE, 'posts-data.js')

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
def esc(s):
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;'))

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
        if t == '':
            flush_quote()
            flush_list()
            i += 1
            continue
        h = re.match(r'^(#{1,3})\s+(.*)$', t)
        if h:
            flush_quote()
            flush_list()
            level = len(h.group(1))
            html.append('<h%d>%s</h%d>' % (level, inline(h.group(2)), level))
            i += 1
            continue
        if t.startswith('>'):
            flush_list()
            quote_buf.append(re.sub(r'^>\s?', '', t))
            i += 1
            continue
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
        if re.match(r'^(-{3,}|\*{3,})$', t):
            flush_quote()
            flush_list()
            html.append('<hr>')
            i += 1
            continue
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
        html.append('<p>' + '<br>'.join(inline(l) for l in para) + '</p>')

    flush_quote()
    flush_list()
    if in_code:
        html.append('<pre><code>' + esc('\n'.join(code_buf)) + '</code></pre>')
    return '\n'.join(html)
#176行的Cusater可以改 194行“我的个人博客”可以改
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Cusater的博客</title>
    <link rel="stylesheet" href="../style.css">
    <script>
        (function() {{
            try {{
                var saved = localStorage.getItem('theme');
                if (saved === 'dark') {{
                    document.documentElement.setAttribute('data-theme', 'dark');
                }}
            }} catch (e) {{}}
        }})();
    </script>
</head>
<body>

    <header class="site-header">
        <div class="header-inner">
            <a class="site-title" href="../index.html" title="回到首页">
                我的个人博客
            </a>
            <div class="header-right">
                <nav>
                    <ul class="nav-links">
                        <li><a href="../index.html">文章</a></li>
                        <li><a href="../index.html#/archives">归档</a></li>
                        <li><a href="../index.html#/about">关于</a></li>
                    </ul>
                </nav>
                <button id="theme-toggle" class="theme-toggle" type="button" title="切换主题" aria-label="切换主题">
                    <span class="icon-moon">D</span>
                    <span class="icon-sun">L</span>
                </button>
            </div>
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
            {nav_html}
        </article>
    </main>

    <footer class="site-footer">
        <p>© 2026 Edit by Cusater <span class="footer-heart">♥</span></p>
    </footer>
    <script>
        (function() {{
            var btn = document.getElementById('theme-toggle');
            function applyTheme(theme) {{
                if (theme === 'dark') {{
                    document.documentElement.setAttribute('data-theme', 'dark');
                }} else {{
                    document.documentElement.removeAttribute('data-theme');
                }}
            }}
            btn.addEventListener('click', function() {{
                var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
                var next = isDark ? 'light' : 'dark';
                applyTheme(next);
                try {{ localStorage.setItem('theme', next); }} catch (e) {{}}
            }});
        }})();
    </script>
</body>
</html>
"""

def slugify(name):
    return name[:-3] if name.endswith('.md') else name

def make_tags_html(tags):
    return ''.join('<span class="article-tag">#%s</span>' % esc(t) for t in tags)

def build_article_page(article, out_file, prev=None, nxt=None):
    nav_parts = ['<nav class="article-nav">']
    if prev:
        prev_slug = slugify(prev['file'])
        nav_parts.append(
            '<a class="nav-item nav-prev" href="%s.html">'
            '<span class="nav-arrow">←</span>'
            '<span class="nav-text"><span class="nav-label">上一篇</span>'
            '<span class="nav-title">%s</span></span></a>'
            % (esc(prev_slug), esc(prev['title']))
        )
    else:
        nav_parts.append('<span class="nav-item nav-placeholder"></span>')
    if nxt:
        nxt_slug = slugify(nxt['file'])
        nav_parts.append(
            '<a class="nav-item nav-next" href="%s.html">'
            '<span class="nav-text"><span class="nav-label">下一篇</span>'
            '<span class="nav-title">%s</span></span>'
            '<span class="nav-arrow">→</span></a>'
            % (esc(nxt_slug), esc(nxt['title']))
        )
    else:
        nav_parts.append('<span class="nav-item nav-placeholder"></span>')
    nav_parts.append('</nav>')
    nav_html = ''.join(nav_parts)

    page = PAGE_TEMPLATE.format(
        title=esc(article['title']),
        date=esc(article['date']),
        tags_html=make_tags_html(article['tags']),
        content=article['content'],
        nav_html=nav_html,
    )
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(page)
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
    records.sort(key=lambda a: (a['date'], a['file']), reverse=True)
    articles = []
    for idx, a in enumerate(records, 1):
        slug = slugify(a['file'])
        link = 'articles/' + slug + '.html'
        articles.append({
            'id': idx,
            'title': a['title'],
            'date': a['date'],
            'tags': a['tags'],
            'excerpt': a['excerpt'],
            'link': link,
        })
    total = len(records)
    for i, a in enumerate(records):
        slug = slugify(a['file'])
        out_file = os.path.join(OUT_DIR, slug + '.html')
        prev = records[i - 1] if i - 1 >= 0 else None
        nxt = records[i + 1] if i + 1 < total else None
        build_article_page(a, out_file, prev, nxt)

    build_data_js(articles)
    print('已生成 %d 篇文章页面到 articles/ 目录' % len(articles))
    for a in articles:
        print('   - %s (%s)' % (a['title'], a['link']))
    print('已更新 ' + DATA_OUT)

if __name__ == '__main__':
    main()
