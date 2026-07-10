# Jarvis 学习记录 - Day02

**日期：** 2026-07-09

---

# 今日目标

完成 Jarvis 项目基础框架搭建，使项目具备：

- 配置管理（Config）
- 日志系统（Logger）
- 工程化目录结构
- Git 版本管理
- 为 Day03 接入大模型做好准备

---

# 今日完成内容

## 一、项目结构重构

项目由原来的简单结构调整为：

```
Jarvis/
│
├── core/
│   ├── __init__.py
│   ├── assistant.py
│   ├── config.py
│   └── logger.py
│
├── memory/
│   ├── __init__.py
│   └── history.py
│
├── tools/
│   └── __init__.py
│
├── prompts/
│
├── tests/
│
├── main.py
├── README.md
├── requirements.txt
└── .env
```

理解了 Package 与模块之间的关系。

---

## 二、实现 Config 类

学习内容：

- class
- object
- __init__()
- 属性封装

实现：

```python
self.name
self.version
self.api_key
self.model
self.base_url
```

学习了：

```python
os.getenv()
```

读取环境变量。

---

## 三、学习 .env 配置

安装：

```
python-dotenv
```

配置：

```
APP_NAME=Jarvis
APP_VERSION=0.1.0

OPENAI_API_KEY=test-key
MODEL=gpt-4.1-mini
BASE_URL=https://api.openai.com/v1
```

理解：

为什么真实项目不会把 API Key 写进代码。

---

## 四、实现 Logger

学习 Python logging 模块。

封装：

```
Logger
```

使用：

```python
self.logger.info(...)
```

代替：

```python
print(...)
```

理解：

日志比 print 更适合工程开发。

---

## 五、Jarvis 初始化流程

目前启动流程：

```
main.py
    │
    ▼
Jarvis()
    │
    ├── Config
    ├── Logger
    └── initialize()
```

运行结果：

```
INFO - Jarvis 初始化完成
INFO - 使用模型: gpt-4.1-mini
INFO - 你好，我是 Jarvis!
INFO - Jarvis 正在运行...
INFO - 当前版本: 0.1.0
```

---

# 今日 Debug

今天解决了多个真实开发问题。

## 1.Logger 没有 info()

错误：

```
AttributeError:
'Logger' object has no attribute 'info'
```

原因：

函数缩进错误。

经验：

Python 中缩进决定代码归属。

---

## 2..gitignore 放错位置

原因：

.gitignore 必须位于项目根目录。

否则不会生效。

---

## 3.__pycache__

理解：

Python 自动生成的字节码缓存。

作用：

提高程序启动速度。

因此需要加入：

```
__pycache__/
*.pyc
```

---

## 4..env 为什么不能上传

理解：

API Key 属于敏感信息。

正确做法：

```
.gitignore
```

忽略：

```
.env
```

---

## 5.Git 中文乱码

解决：

```
git config --global core.quotepath false
```

---

## 6.LF 与 CRLF

理解：

Windows：

```
CRLF
```

Linux/macOS：

```
LF
```

Git Warning 不影响程序运行。

---

## 7.Git Rename Detection

今天最大的收获。

Git 出现：

```
rename .env => core/__init__.py
```

最终学习了：

Git 的 Rename Detection 只是显示方式。

最后重新整理暂存区并重新 Commit。

---

# Git 操作

今天学习：

```
git status
git add
git commit
git log
git show
git diff
git restore
git rm --cached
```

理解：

Git 包含：

- Working Tree
- Index（暂存区）
- Commit

---

# 今日 Commit

```
c5df2b1
Day02 build Jarvis core framework
```

Git 历史：

```
c5df2b1 Day02 build Jarvis core framework
d27d6e9 Day1 create first Jarvis core
```

---

# 今日收获

今天最大的收获不是写了多少代码。

而是理解了：

- 工程化项目结构
- Config 与代码分离
- Logger 封装
- .env 管理配置
- Git 工作流程
- Debug 思路
- Python Package

这些内容将成为后续所有 AI 项目的基础。

---

# 当前项目架构

```
main.py
    │
    ▼
 Jarvis
    │
 ┌──┴──────────────┐
 │                 │
 ▼                 ▼
Config          Logger
 │
 ▼
.env
```

Day03 将新增：

```
Jarvis
│
├── Config
├── Logger
├── LLMClient
├── Memory
└── Tools
```

---

# Day03 计划

目标：

让 Jarvis 第一次真正调用大模型。

计划：

1. 安装 OpenAI SDK
2. 编写 LLMClient
3. 调用 Chat Completions API
4. 实现 Streaming 输出
5. 接入 Jarvis 主程序

最终效果：

```
You:
> 你好

Jarvis:
你好！我是 Jarvis，很高兴认识你。
```

---

# 今日评价

完成度：

⭐⭐⭐⭐⭐（100%）

今天不仅完成了代码开发，更完成了第一次真正的软件工程实践。

这是 Jarvis 项目正式进入 AI 开发阶段前最重要的一天。