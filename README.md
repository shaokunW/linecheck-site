# LineCheck website

Public product information and privacy policy for LineCheck.

- Homepage: https://shaokunw.github.io/linecheck-site/
- Privacy: https://shaokunw.github.io/linecheck-site/privacy.html
- Support: wangsk15@outlook.com

Deploy the main branch root using GitHub Pages. This repository contains only the static website, not extension source or user records.

## SEO and release checks

The site is plain HTML and CSS: its content, navigation, translations, and metadata are available without JavaScript. English and Simplified Chinese homepages and guides have reciprocal `hreflang` links and self-referencing canonical URLs. The sitemap lists the five indexable pages; the custom 404 is excluded and marked `noindex`. JSON-LD describes the actual pages and guide breadcrumbs, without invented reviews or ratings. Social cards use the existing icon.

Run before publishing:

```sh
python3 scripts/check_seo.py
```

GitHub Actions runs the same check on pushes and pull requests. GitHub Pages currently publishes the root of `main`; a passing branch check is not evidence that a deployment has completed. Check the Pages build and live URLs after merging. When adding a page, add its canonical URL to `sitemap.xml`, link it from relevant content, and keep translation links reciprocal. Do not change `lastmod` simply because a build ran; this sitemap intentionally omits it.

### 搜索引擎后台：仍需账号操作

1. 在 [Google Search Console](https://search.google.com/search-console/) 添加 **网址前缀**资源 `https://shaokunw.github.io/linecheck-site/`。这个 GitHub 子域名不属于可由本项目修改 DNS 的自有域名，因此使用网址前缀验证。
2. 按后台实际提供的方式，将 HTML 验证文件放在本站根目录，或把后台提供的验证 meta 标签加入英文首页。必须使用账号生成的真实值，发布后再完成验证。保留验证文件或标签。
3. 提交站点地图 `https://shaokunw.github.io/linecheck-site/sitemap.xml`。在网址检查工具中检查英文和中文首页及指南，并对需要的页面请求编入索引。
4. 在 [Bing Webmaster Tools](https://www.bing.com/webmasters/) 验证同一网站（或按其流程导入已验证的 Search Console 资源），提交相同站点地图。
5. 后续根据后台实际的收录、查询词、展示、点击、移动端和页面体验数据调整内容。发布、提交和被收录是三个不同状态；这些文件不能证明搜索引擎已收录网站或提高排名。

### robots.txt 的位置限制

搜索引擎读取的是 `https://shaokunw.github.io/robots.txt`，不是 `/linecheck-site/robots.txt`。本次审计根目录 robots 返回 404；没有 robots 文件不等于禁止抓取。不要在项目子目录放一个文件后宣称已配置抓取策略。若以后需要 robots 规则，应由控制该主机根目录的仓库提供，并避免影响同一主机的其他项目。当前可在站长工具直接提交 sitemap。

### Cloudflare 免费方案能做什么

当前网站使用 GitHub Pages，没有自有域名或已配置的 Cloudflare zone。保留现有网址即可完成本次站内优化。

- Cloudflare Pages 提供免费额度，可以托管这个静态站点；免费托管并不等于赠送自有域名，也不代表自动改善排名。
- 对接入 Cloudflare 的域名，免费版 **Crawler Hints** 可以通过 IndexNow 通知支持的搜索引擎内容变化。这不代表完成 Google Search Console 提交，也不保证收录。
- 如果已有自有域名，可以再规划 DNS、HTTPS、缓存及主域名重定向。先核对现有邮件等 DNS 记录，不应为 SEO 直接替换整套 DNS。
- 没有必要仅为 SEO 增加一份使用不同网址的重复站点。若迁移，必须同时更新 canonical、语言链接、sitemap、分享链接、404 返回链接、校验脚本中的 BASE，以及扩展的官网/隐私链接；规划旧地址到新地址的逐页重定向。GitHub 项目页对子路径重定向的能力有限，需要单独验证。
- 迁移主机或添加任何统计脚本前，复核现有隐私政策中关于 GitHub 托管和没有统计脚本的描述。当前改动未接入统计服务。

### 内容和产品事实

指南以公开源码支持的行为为准。开发工作区里尚未发布的版本、语言和快捷键不应提前写成线上功能。已核实 [Chrome Web Store 的公开产品链接](https://chromewebstore.google.com/detail/linecheck/pcfmhpdkaplkchannpbidjinmlknlein)，首页提供商店安装按钮，指南同时保留免费源码安装路径。商店语言列表已包含德语；商店说明中的旧快捷键与开发工作区存在差异，指南因此引导用户查看和配置实际快捷键。FAQ 是给用户阅读的真实说明，没有添加不适用于此产品的 FAQ 富结果声明。

不要使用虚构评价、关键词堆砌、批量重复落地页或伪造兼容性声明。优先根据实际使用问题完善指南。此仓库不负责更新 Chrome Web Store 后台的商品资料。

### Official references

- [Google: SEO starter guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [Google: Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Google: Localized page versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Google: robots.txt location and scope](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)
- [Cloudflare: SEO support](https://developers.cloudflare.com/fundamentals/performance/improve-seo/)
- [Cloudflare: Crawler Hints and Free plan availability](https://developers.cloudflare.com/cache/advanced-configuration/crawler-hints/)
- [Cloudflare Pages: Free plan limits](https://developers.cloudflare.com/pages/platform/limits/)

### IndexNow：无需 Cloudflare 的抓取通知

本站发布 `indexnow-key.txt` 作为 IndexNow 的网址归属验证文件；它不是账号密码或 Cloudflare API token。提交使用 `keyLocation`，将验证范围限定在 `/linecheck-site/`，不会提交同一 GitHub 主机下的其他项目。

```sh
# 预览将提交的网址，不发送请求
python3 scripts/submit_indexnow.py
# 仅在 Pages 发布完成后执行；先核对线上 key 与 sitemap，再发送通知
python3 scripts/submit_indexnow.py --submit
```

返回 HTTP 200 表示服务收到网址；202 表示收到网址但仍在验证 key。都不代表已收录，也不是 Google 提交。发生 429 时不要连续重试。只有内容发生实际变化并发布完成后才需要再次通知。参见 [IndexNow 官方协议](https://www.indexnow.org/documentation)。
