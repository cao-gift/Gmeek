# AGENTS.md

## 项目概述

Gmeek 是一个围绕 GitHub Issues、GitHub Pages 和 GitHub Actions 构建的 Python 静态博客生成器。它从指定的 GitHub 仓库读取 Issues，通过 GitHub Markdown API 将 Markdown 转换为 HTML，再使用 Jinja2 渲染页面，最终把静态网站写入 `docs/`。

本项目不是 Web 服务应用。主要实现集中在一个 Python 脚本中，页面层由 Jinja2 模板和可选的浏览器端 JavaScript 插件组成。

## 仓库结构

- `Gmeek.py`：命令行入口和全部核心生成逻辑。
- `templates/`：生成静态网站所使用的 Jinja2 模板。
  - `base.html`：公共 HTML 骨架、主题处理和共享区块。
  - `plist.html`：首页和分页文章列表。
  - `post.html`：文章页面、评论和代码复制功能。
  - `tag.html`：浏览器端标签筛选与搜索。
  - `footer.html`：公共页脚。
- `plugins/`：可选的浏览器端增强功能，例如文章目录、访问统计和图片灯箱。
- `.github/workflows/`：GitHub Pages 部署配置。
- `img/`：README 图片和其他文档资源。
- `requirements.txt`：Python 运行时依赖。

## 入口与数据流

命令行入口是 `Gmeek.py`：

```powershell
python Gmeek.py <github_token> <owner/repository> [--issue_number <number>]
```

整体生成流程如下：

1. 解析 GitHub Token、仓库名称和可选的 Issue 编号。
2. 读取仓库标签，并将 `config.json` 与内置默认配置合并。
3. 通过 `runAll()` 获取所有 Issues，或通过 `runOne()` 获取单个处于打开状态的 Issue。
4. 将 Issue 正文保存到 `backup/`，并通过 GitHub API 转换 Markdown。
5. 使用 `templates/` 中的模板渲染页面并写入 `docs/`。
6. 生成 `docs/rss.xml`、`docs/postList.json` 和持久化状态文件 `blogBase.json`。

生成后的网站入口页面是 `docs/index.html`。它属于输出产物，当前源码仓库中不保存该文件。

## 运行时输入与生成文件

`Gmeek.py` 要求用户提供 `config.json`。当前源码仓库不包含该文件，因此在没有有效配置和 GitHub 凭据的情况下，生成器无法正常运行。

除非任务明确要求修改，否则应将以下路径视为运行时输入或生成产物：

- `config.json`：用户配置，也是必需的运行时输入。
- `static/`：可选的用户静态资源，生成时会复制到 `docs/`。
- `backup/`：自动生成的 Markdown 备份。
- `docs/`：自动生成的静态网站。
- `blogBase.json`：用于增量构建的自动生成状态文件。

运行生成器时必须谨慎：全量构建会删除并重新创建 `backup/` 和 `docs/`；当设置了 `GITHUB_WORKSPACE` 且当前不是定时任务时，正常运行还会重写 `README.md`。

## 开发规范

- 修改应聚焦当前需求，并保持项目轻量、低依赖的设计。
- 修改 `Gmeek.py` 时遵循现有 Python 风格，避免对整个文件进行无关格式化。
- 保持 UTF-8 处理方式，以及现有中文、英文和俄文国际化行为。
- 模板逻辑必须兼容 Jinja2 和生成后的纯静态 HTML；项目没有前端打包器或前端框架。
- 新增输出路径或 HTML 内容时，应正确转义或清理来自 Issue 标题、正文、标签及 `config.json` 的值。
- 不要通过直接编辑生成文件来实现源码行为，应修改 `Gmeek.py`、模板或插件。
- 不要向仓库提交密钥、真实 GitHub Token、个人配置或生成后的博客内容。
- 修改模板时，同时考虑桌面端、移动端和全部主题模式。
- 修改 `postList.json` 字段时，应同时更新 `Gmeek.py` 中的数据生产逻辑及所有消费方，尤其是 `templates/tag.html`。

## 验证方式

当前项目没有自动化测试套件。根据改动范围选择最小且安全的检查方式：

```powershell
python -m py_compile Gmeek.py
```

在已安装依赖的环境中，可以检查依赖导入：

```powershell
python -c "import github, requests, xpinyin, feedgen, jinja2, transliterate"
```

对于生成器或模板改动，应使用一次性的测试仓库和测试配置进行验证，不要使用生产凭据。至少检查以下产物：

- `docs/index.html`
- 至少一个生成的 `docs/post/*.html` 文章页面
- `docs/tag.html`
- `docs/postList.json`
- `docs/rss.xml`

如果改动涉及共享状态或文章元数据，还应分别验证全量生成和单 Issue 增量生成是否符合预期。

## 部署说明

当前 `.github/workflows/static.yml` 工作流只负责将仓库内容部署到 GitHub Pages，并不会调用 `Gmeek.py`。不要假设当前源码仓库包含 README 所述的 Issue 触发生成工作流；处理自动化相关任务时，应检查目标博客仓库或模板仓库中的实际配置。
