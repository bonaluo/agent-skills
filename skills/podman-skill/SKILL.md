---
name: podman-skill
description: 这是一个本地使用podman容器的skill，当使用容器相关的操作时可使用此技能，podman亦可以替代docker使用。
---
---

# podman-skill

这是一个本地使用podman容器的skill，当使用容器相关的操作时可使用此技能，podman亦可以替代docker使用。

## When to use

当你需要使用容器、docker，尤其是一个不需要持久化的中间件时（在没有绑定卷）的情况下，如果本地没有符合要求的组件或者时容器，你应该使用podman创建并使用中间件。

## Instructions

1. 注意使用podman创建容器时你应该优先使用名称为podman-remote-win的链接并使用-c进行指定，比如 `podman -c podman-remote-win ps`
2. 如果本地没有名为 podman-remote-win 的链接时，或者使用时出现报错、超时等情况时，可以不使用-c指定该链接，而是使用默认链接，比如 `podman ps`
`
