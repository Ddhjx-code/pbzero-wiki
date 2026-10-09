# 部署注意事项

## 永远不要用 `vercel deploy --prebuilt` 部署本仓库

本站是 `output: "export"` 静态导出。`vercel build` 生成的
`.vercel/output/config.json` 里 **没有任何 `/` 到 `/index.html` 的映射**
（14 条路由全靠 `handle: filesystem` 兜底），用它做 prebuilt 上传后，
Vercel 会把 `404.html` 当作首页返回：

```
https://pbzero.wiki/     -> 404   (26,719B = 404 页)
https://pbzero.wiki/guide -> 200   ← 内容页全部正常，只有首页挂
```

改用远端构建（`vercel --prod`，不带 `--prebuilt`）即恢复，平台会补自己的路由：

```
https://pbzero.wiki/     -> 200   (42,076B, ad-slot=1)
```

## 广告变量的类型要求

`NEXT_PUBLIC_ADSTERRA_SCRIPT_URL` 原先是 **sensitive** 类型，而 sensitive 变量
不会下发给构建，`NEXT_PUBLIC_` 前缀的编译期内联因此拿到空串，
`AdBanner` 的 `if (!src) return null` 就让广告位从预渲染 HTML 里静默消失。

已改为 **encrypted**（构建期可读）。这个值本来就会被打进客户端 JS、发给每个
浏览器，sensitive 类型对它没有任何实际保护意义。

## 本地验证方式

`npm run build` 产出的 `.next/server/app/index.html` 不含广告位属正常现象
（本地没有该环境变量）。要看真实结果用：

```bash
vercel pull --yes --environment=production   # encrypted 类型可解出真值
vercel build --prod
```

## 404 判定的陷阱

Next 会把 not-found 边界写进每个页面的 RSC payload，所以页面正文里总能搜到
"Error 404" 字样。**判断某 URL 是否真的 404 只能看 HTTP 状态码**，
不能用文本匹配。
