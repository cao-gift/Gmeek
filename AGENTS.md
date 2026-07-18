# AGENTS.md

## 项目概述

Gmeek 是围绕 GitHub Issues、GitHub Pages 和 GitHub Actions 的 Python 静态博客生成器。它从指定仓库读取 Issues，经 GitHub Markdown API 将 Markdown 转为 HTML，再用 Jinja2 渲染，输出到 `docs/`。

本仓库是 `cao-gift/Gmeek`（fork 自 `Meekdai/Gmeek`）。生产博客仓库通过 `config.json` 的 `GMEEK_VERSION` 克隆本仓库对应标签/提交进行构建。这里不是 Web 服务；核心逻辑集中在 `Gmeek.py`。

跨仓库总览见工作区 `F:\blog\AGENTS.md`；生产站点配置与插件见 `F:\blog\cao-gift.github.io/AGENTS.md`。

## 仓库结构

- `Gmeek.py`：CLI 与全部核心生成逻辑
- `templates/`
  - `base.html`：公共骨架、主题、robots、PWA 注册
  - `plist.html`：首页与分页列表
  - `post.html`：文章页、评论、代码复制
  - `tag.html`：标签筛选与搜索（消费 `postList.json`）
  - `archive.html`：按年归档
  - `footer.html`：公共页脚
- `plugins/`：可选浏览器端增强（目录、统计、灯箱等）；具体博客可改用站点仓库 `static/plugins`
- `.github/workflows/static.yml`：仅部署本仓库到 GitHub Pages，不执行博客构建
- `img/`：文档图片
- `requirements.txt`：运行时依赖（未锁版本）：PyGithub、requests、xpinyin、feedgen、Jinja2、transliterate

## 入口与参数

```powershell
python Gmeek.py <github_token> <owner/repository> [--issue_number <number>] [--preview]
```

- 当前工作目录必须有 `config.json`
- `--issue_number`：指定时走增量 `runOne`（在 `blogBase.json` 存在且 `schemaVersion` 一致时）
- `--preview`：将请求的 open Issue（含草稿/定时）纳入 noindex 预览构建
- `GMEEK_CACHE_DIR`：Markdown HTML 与图片尺寸等磁盘缓存目录
- `GITHUB_WORKSPACE`：Actions 中用于回写前端 `README.md`（非 schedule、非 preview）

## 配置与 schema

`config.json` 与内置默认配置合并。默认中含 `schemaVersion`（当前生成器为 **2**）。若磁盘上 `blogBase.json` 的 `schemaVersion` 不一致，强制 `runAll()`。

重要默认/常用字段：

- 展示：`title`、`displayTitle`、`subTitle`、`avatarUrl`、`homeUrl`、`themeMode`、`dayTheme`、`nightTheme`
- 内容：`singlePage`、`urlMode`（`pinyin` / `issue` / `ru_translit`）、`draftLabel`、`onePageListNum`
- 功能：`needComment`、`imageCaptcha`、`showPostSource`、`archivePage`、`relatedPostsNum`、`readingWordsPerMinute`
- PWA：`pwa`、`pwaRecentPosts`、`pwaAssets`、`pwaIcon`、`pwaIconSizes`、`themeColor`、`backgroundColor`
- 注入：`script`、`style`、`head`、`allHead`、`indexScript`、`indexStyle`、`primerCSS`、`exlink`、`bottomText`
- 其他：`i18n`（CN/EN/RU）、`UTC`、`rssSplit`、`filingNum`、`startSite`、`yearColorList`、`author`

改变 `blogBase` 或 `postList.json` 结构时，应提升 `schemaVersion`。

## 发布条件

`issuePublication` / `shouldIncludeIssue`：

- 公开：`open` + 至少一个 Label + 非 `draftLabel` + `publishAt` 非未来且解析有效
- 预览：`--preview` 且 Issue 编号匹配、open、至少一个 Label → `isPreview`，页面 `noindex,nofollow`
- Issue 正文末尾 `##{json}` 可提供 `timestamp`、`updatedAt`、`publishAt`、`author`、`style`、`script`、`head`、`ogImage` 等

## 数据流

1. 解析参数，初始化仓库与标签，合并配置
2. 判断全量或增量：
   - 全量 `runAll()`：`cleanFile()` 重建目录 → 遍历 open Issues → 过滤发布条件 → 写 backup、转 HTML、渲染
   - 增量 `runOne(n)`：先 `removePost(n)`，再按条件决定是否重新加入；删除 Issue（404/410）只移除不重建
3. `preparePostRelationships()`：上一篇/下一篇、相关文章
4. 渲染文章、单页、列表、标签、归档
5. `createFeedXml`、`createRobotsTxt`、`createSitemapXml`；非预览且 `pwa=1` 时 `createPwaFiles`
6. `writeBuildState`：写 `blogBase.json`；写精简 `docs/postList.json`（搜索字段 + `labelColorDict`）；条件更新 README

### 运行时输入与产物（勿当本仓库源码长期手改）

- 输入：`config.json`、可选 `static/`、可选已有 `blogBase.json`
- 产物：`backup/`、`docs/`、`blogBase.json`；Actions 中还可能写前端 `README.md`

全量构建会删除并重建 `backup/` 与 `docs/`。

## 核心能力摘要

- Markdown 渲染结果磁盘缓存；图片尺寸探测与缓存；图片保护属性处理
- 字数与阅读时长；相关文章与前后篇
- 归档页、robots、sitemap、RSS
- PWA manifest + service worker（预缓存首页、manifest、近期文章与配置的 `pwaAssets`）
- 草稿标签与 `publishAt` 定时发布；关闭/删除/不可发布时的增量下线
- 搜索索引字段示例：`postTitle`、`postUrl`、`labels`、`description`、`searchText`、`createdDate`、`updatedDate`、`dateLabelColor`、`author`、`readingTime`

## 开发规范

- 改动聚焦需求，保持轻量、低依赖
- 修改 `Gmeek.py` 时遵循现有风格，避免无关全文件格式化
- 保持 UTF-8 与中/英/俄 i18n 行为
- 模板须兼容 Jinja2 与纯静态输出；无前端打包器
- 新增输出或 HTML 字段时正确转义 Issue/配置来源值；仅在明确允许处输出原始 HTML
- 不要提交密钥、真实 Token、个人生产配置或生成后的博客内容到本仓库
- 改模板时兼顾桌面/移动与主题模式，并考虑生产站自定义插件的注入方式
- 改 `postList.json` 字段时同步生产逻辑与所有消费方（尤其 `templates/tag.html`），并评估 `schemaVersion`

## 验证方式

无自动化测试套件。最小检查：

```powershell
python -c "import ast, pathlib; ast.parse(pathlib.Path('Gmeek.py').read_text(encoding='utf-8')); print('ast ok')"
python -c "import github, requests, xpinyin, feedgen, jinja2, transliterate; print('imports ok')"
```

生成器或模板改动应使用一次性测试仓库与测试配置，不要用生产凭据。至少检查：

- `docs/index.html`、至少一篇 `docs/post/*.html`
- `docs/tag.html`、`docs/archive.html`（若开启）
- `docs/postList.json`、`docs/rss.xml`
- `docs/robots.txt`、`docs/sitemap.xml`
- PWA 开启时的 `manifest.webmanifest`、`sw.js`

涉及发布条件、下线、草稿、定时、置顶、搜索索引或元数据时，分别验证 `runAll` 与 `runOne`，并在需要时验证 `--preview`。

## 部署说明

本仓库 `static.yml` 只部署仓库自身内容到 GitHub Pages，**不会**调用 `Gmeek.py` 构建博客。生产博客的生成与部署在目标博客仓库（如 `cao-gift.github.io`）的 Actions 中完成。修改生成器后需推送到生产实际克隆的远程，并更新博客侧 `GMEEK_VERSION` 或等待 `last` 指向包含改动的标签。
