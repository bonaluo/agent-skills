---
name: doc-manage
description: Structured document management and indexing system. Suitable for creating, maintaining, and managing project documents, using index.doc.md as the directory index, each document type stored in corresponding subdirectory, supporting multi-level directory structure. / 结构化文档管理与索引系统。适用于创建、维护和管理项目文档，使用 index.doc.md 作为目录索引，每种文档类型存放在对应子目录中，支持多级目录结构。
metadata:
  version: 20260417.0000
  update-url: https://github.com/bonaluo/agent-skills@doc-manage
---

# Doc Manage

结构化文档管理与索引系统。

## 概述

本技能定义了一套规范的文档组织方式，通过统一的目录结构和索引文件实现文档的有序管理。

## 目录结构规范

```
项目根目录/
└── docs/                          # 文档根目录
    ├── index.doc.md               # 文档总索引
    ├── prd/                       # 产品需求文档
    │   ├── index.doc.md           # PRD 索引
    │   └── 20260401-登录功能/     # 按功能/日期组织的子目录
    │       ├── index.doc.md       # 子目录索引
    │       └── 功能设计.md        # 具体文档
    ├── design/                    # 技术设计文档
    ├── meeting/                   # 会议纪要
    └── guide/                    # 使用指南
```

## 文档索引文件规范

### 根目录索引 (docs/index.doc.md)

每个 `index.doc.md` 文件包含两部分：目录索引和子项索引。

```markdown
---
title: 文档总索引
description: 项目文档目录
---

# 文档总索引

## 内容索引

- [PRD 产品需求文档](#prd-产品需求文档)
- [技术设计文档](#技术设计文档)
- [会议纪要](#会议纪要)

## PRD 产品需求文档

- [登录功能 PRD](prd/20260401-登录功能/功能设计.doc.md)

## 技术设计文档

- [认证模块设计](design/auth-design.doc.md)

## 会议纪要

- [2024年4月评审会](meeting/20240401-review.doc.md)
```

### 文档内容索引规范

每个文档头部必须包含内容索引：

```markdown
---
title: 功能设计文档
description: 登录功能技术设计
---

# 登录功能技术设计

## 内容索引

- [需求概述](#需求概述)
- [技术方案](#技术方案)
- [数据库设计](#数据库设计)
- [接口设计](#接口设计)
- [安全性考虑](#安全性考虑)

## 需求概述

...
```

## 使用场景

| 场景 | 目录 | 示例 |
|------|------|------|
| 产品需求 | `docs/prd/` | `prd/20260401-登录功能/功能设计.doc.md` |
| 技术设计 | `docs/design/` | `design/auth-service.doc.md` |
| 会议纪要 | `docs/meeting/` | `meeting/20240401-weekly.doc.md` |
| 使用指南 | `docs/guide/` | `guide/deployment.doc.md` |
| API 文档 | `docs/api/` | `api/user-service.doc.md` |

## 创建新文档工作流

1. **确定文档类型**：选择对应的子目录（prd/design/meeting/guide 等）
2. **创建日期目录**：如需按时间组织，创建 `YYYYMMDD-名称/` 格式目录
3. **创建索引文件**：在对应目录创建 `index.doc.md`
4. **创建文档**：创建实际文档，添加内容索引
5. **更新索引**：在父目录的 `index.doc.md` 中添加链接

## 示例：创建新 PRD

1. 创建目录：`docs/prd/20260401-新功能/`
2. 创建 `docs/prd/20260401-新功能/index.doc.md`
3. 创建 `docs/prd/20260401-新功能/需求文档.doc.md`
4. 更新 `docs/prd/index.doc.md`，添加新文档链接
5. 更新 `docs/index.doc.md`，同步 PRD 索引
