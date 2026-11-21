# 上传 GitHub 与本地维护

[返回总览](../README.md)

这是文档仓库，不需要前端、不需要 npm，不需要 GitHub Pages。GitHub 可直接显示 Markdown 和 Mermaid，依据见 [GitHub 官方图表文档](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)。

## 上传步骤

1. 解压交付包，进入含 `README.md` 的 `cs-roadmap-ai-era` 目录。
2. 在自己的 GitHub 账号新建空仓库，建议名 `cs-roadmap-ai-era`，按需要选择可见性。
3. 在该目录执行下面的命令；把远程地址替换成实际仓库地址。

```bash
git init
git add .
git commit -m "Add AI-era CS learning and career roadmaps"
git branch -M main
git remote add origin https://github.com/YOUR_ACCOUNT/cs-roadmap-ai-era.git
git push -u origin main
```

账号、仓库可见性和 Git 身份由维护者设置。交付包中没有凭证、远程地址或虚构 Git 身份；上述命令尚未代为执行。

## 修改与重新生成

```bash
python tools/build.py
python tools/validate.py
```

要求 Python 3.10+，只用标准库。源数据位于 `data/`。`README.md`、分类索引、`roadmaps/`、`docs/all-routes.md`、`docs/ai-era.md`、`docs/future.md`、`docs/sources.md` 由生成器管理，应修改源数据或生成器后再构建。

`docs/foundation.md`、其他手写说明、模板与维护规则可直接编辑。

## 核验范围

校验脚本检查条目唯一性、必填字段、资源引用、Markdown 本地链接、代码围栏以及本仓库生成的 Mermaid 节点/边结构。它不自动访问外部链接，不判断职业预测，不证明教学效果。

本轮未创建远程 GitHub 仓库，也未在 GitHub 逐张渲染所有 Mermaid 图；图采用简单的 `flowchart`、文本节点和连线，已做结构检查。上传后应抽查共同主干和若干路线的图表显示。
