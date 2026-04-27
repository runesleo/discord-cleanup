# discord-cleanup

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()

[English](./README.md)

批量退出不再需要的 Discord 服务器。零依赖、单文件、**默认仅预览（dry-run）**。

作者曾在一轮空投热潮里加了 166 个服务器（ZK、Arb、OP、Starknet、NFT、节点、GameFi…），未读 @ 超过三万条；用这个脚本在两分钟内收敛到 16 个。

## 快速开始

```bash
git clone https://github.com/runesleo/discord-cleanup.git
cd discord-cleanup

# 设置 Discord Token（见下文「获取 Token」）
export DISCORD_TOKEN="your_token_here"

# 查看当前服务器列表
python discord_cleanup.py list --category

# 预览清理（dry-run，不会真的退出）
python discord_cleanup.py cleanup

# 编辑 whitelist.json，把想保留的服务器 ID 加进去

# 执行清理
python discord_cleanup.py cleanup --execute
```

无需 `pip install`、`requirements.txt` 或虚拟环境，只要本机有 Python。

## 命令

```bash
python discord_cleanup.py list
python discord_cleanup.py list --category
python discord_cleanup.py cleanup
python discord_cleanup.py cleanup --execute
python discord_cleanup.py leave <server_id> [<server_id> ...]
```

## 工作流程

1. 拉取全部服务器并按类别分组  
2. 生成 `whitelist.json`（你拥有的服务器会自动加入白名单）  
3. **默认 dry-run**：只打印计划，不操作  
4. 编辑 `whitelist.json` 保留重要服务器  
5. `--execute` 退出其余服务器，并需输入 `yes` 确认  

## 获取 Token

1. 浏览器打开 [Discord](https://discord.com/app)  
2. `F12` → **Network**，在应用里点任意操作  
3. 找到发往 `discord.com` 的请求，复制请求头里的 `Authorization`  

```bash
export DISCORD_TOKEN="your_token_here"
```

> **安全：** Token 等同于完整账号权限。勿提交仓库、勿泄露。若泄露请立即改密码以作废旧 Token。

## 安全机制

- 默认 dry-run，除非显式 `--execute`  
- 必须输入 `yes` 才会执行  
- 自己创建的服务器受保护、不会误退  
- 内置速率限制等待  

## 相关项目

- [x-reader](https://github.com/runesleo/x-reader) — 多平台内容抓取  
- [claude-code-workflow](https://github.com/runesleo/claude-code-workflow) — Claude Code 工作流模板  

## 许可

MIT  

## 关于作者

*Leo ([@runes_leo](https://x.com/runes_leo)) — AI × Crypto 独立构建者。*
