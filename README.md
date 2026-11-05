# qx-multiclash

一份规则源，同时给 Quantumult X / Clash / Surge 用。

## 原理

不存在「一个原生格式被所有客户端直读」的规则文件——各家语法不同。
能复用的部分只有**规则语义**（域名后缀、IP 段、geoip），
所以做法是：**统一用一种语法维护，构建时转译成各端产物**。

本仓库选 Clash/Surge 语法作为源，因为它的生态最全（blackmatrix7、ACL4SSR 都是 Clash 优先）。

## 目录

```
src/                     ← 你唯一需要改的地方
├── cn.list              国内域名（Clash 语法）
├── proxy.list           需要代理的
└── bypass.list          银行/支付，强制直连
scripts/build.py         转译器
dist/qx/*.list           产物：Quantumult X
dist/clash/*.yaml        产物：Clash rule-provider
templates/qx.conf        QX 配置模板
templates/clash.yaml     Clash 配置模板
```

仓库：https://github.com/jeson998/qx-multiclash

> **本仓库必须保持 Public。** Quantumult X 与 Clash 拉取 `raw.githubusercontent.com`
> 时不携带任何凭证，私有仓库的规则链接会直接失效。

## 用法

```bash
python scripts/build.py
```

改完 `src/` 提交，GitHub Actions 每天自动重建 `dist/`；
客户端只引用 `dist/` 的链接，`update-interval` 到期自动生效。

## 客户端接入

`templates/qx.conf` 与 `templates/clash.yaml` 里的 URL 已指向本仓库 `main/dist/`，
导入即可用，无需替换占位符。

规则直链：

| 客户端 | 地址 |
|---|---|
| Quantumult X | `https://raw.githubusercontent.com/jeson998/qx-multiclash/main/dist/qx/cn.list` |
| Clash / mihomo | `https://raw.githubusercontent.com/jeson998/qx-multiclash/main/dist/clash/cn.yaml` |

`proxy`、`bypass` 同理，替换文件名即可。

## 安全边界

公开仓库意味着内容任何人可见，因此：

- **禁止**提交节点订阅 URL、token、机场链接、账号信息
- 本地私有配置放 `local/`（已在 `.gitignore` 中排除）
- 节点订阅请在客户端本地填写，不要写进 `templates/` 后提交
- 若确需托管订阅，改用 Sub-Store 自部署并加访问令牌，不要混进本仓库

## 语法对照

| 语义 | 源文件（Clash/Surge） | 产物（Quantumult X） |
|---|---|---|
| 域名后缀 | `DOMAIN-SUFFIX,x.com,PROXY` | `host-suffix, x.com, proxy` |
| 域名关键字 | `DOMAIN-KEYWORD,google,PROXY` | `host-keyword, google, proxy` |
| 完整域名 | `DOMAIN,x.com,PROXY` | `host, x.com, proxy` |
| IP 段 | `IP-CIDR,1.1.1.0/24,DIRECT` | `ip-cidr, 1.1.1.0/24, direct` |
| IP 段不解析 | `IP-CIDR,1.1.1.0/24,DIRECT,no-resolve` | `ip-cidr, 1.1.1.0/24, direct, no-resolve` |
| IPv6 段 | `IP-CIDR6,...` | `ip6-cidr, ...` |
| 国家 IP | `GEOIP,CN,DIRECT` | `geoip, cn, direct` |
| 最终兜底 | `MATCH,PROXY` | `final, proxy` |

`PROCESS-NAME`（按进程分流）只有 Clash 支持，QX 无对应写法，转换时会被注释掉。

## 注意

- `force-policy=` 是按**整个远程文件**生效的，所以不同策略必须拆成不同文件
- QX 无法按 App 分流，银行类只能靠域名/IP 命中
- 上游国内大集合建议直接引 QX 版（仓库已按 QX 语法提供），不必自己转
