# Jarvis Agent Learning Log - Day 01

## 开发环境与第一个 Agent 原型

日期：2026-07-08

------------------------------------------------------------------------

## 一、学习目标

建立个人 AI Agent 项目的基础开发环境，并完成第一个可运行 Jarvis 程序。

目标：

- 掌握 AI 项目工程初始化流程

- 理解 Python 项目结构

- 建立 Git 版本管理习惯

- 完成第一个 Agent 雏形

  Agent =

  ```
  LLM
  +
  Memory
  +
  Tools
  +
  Planning
  +
  Action
  ```

------------------------------------------------------------------------

## 二、开发环境

### 操作系统

Windows 10

### Python 环境

工具：

Miniconda

创建环境：

``` bash
conda create -n jarvis python=3.11
```

（创建环境时要退出vps,否则出错）

conda activate XXX

当前环境：

-   Conda 环境：jarvis
-   Python：3.11.15

### IDE

Visual Studio Code 1.126.0

安装扩展：

-   Python (Microsoft)
-   Python Debugger
-   Python Environments

### Git

版本：

git version 2.54.0.windows.1

初始化：

``` bash
git init
```

------------------------------------------------------------------------

## 三、项目结构

项目路径：

F:`\AIProject`{=tex}`\Jarvis`{=tex}

结构：

    Jarvis/
    
    ├── app/
    ├── tools/
    ├── memory/
    ├── knowledge/
    ├── prompts/
    ├── tests/
    ├── README.md
    ├── requirements.txt
    └── .env

目录用途：

  目录        用途
----------- ---------------
  app         核心程序
  tools       外部能力
  memory      记忆系统
  knowledge   知识库
  prompts     Agent行为定义
  tests       测试

------------------------------------------------------------------------

## 四、第一个 Jarvis 程序

文件：

app/main.py

实现流程：

    用户输入
     ↓
    Python程序处理
     ↓
    输出回复

基础 Agent Loop：

    Observe
     ↓
    Process
     ↓
    Response

------------------------------------------------------------------------

## 五、Git版本记录

第一次提交：

    d27d6e9

提交信息：

    Day1 create first Jarvis core

------------------------------------------------------------------------

## 六、遇到的问题与解决

### 1. VS Code 多窗口导致解释器不同步

原因：

VS Code 工作区独立保存 Python 解释器配置。

解决：

打开项目目录后重新选择：

Python 3.11.15 ('jarvis')

经验：

项目环境绑定到 Workspace。

------------------------------------------------------------------------

### 2. Conda环境与VS Code终端不一致

现象：

    (base)

解决：

``` powershell
conda activate jarvis
```

确认：

``` powershell
python --version
```

结果：

    Python 3.11.15

------------------------------------------------------------------------

### 3. Git首次提交失败

错误：

    Author identity unknown

原因：

Git未配置用户身份。

解决：

``` bash
git config --global user.name "Name"
git config --global user.email "Email"
```

------------------------------------------------------------------------

## 七、Day 1 知识总结

软件工程流程：

    创建环境
     ↓
    建立项目
     ↓
    编写代码
     ↓
    运行测试
     ↓
    Git保存版本

Agent基础认知：

普通程序：

    输入
     ↓
    规则
     ↓
    输出

Agent：

    输入
     ↓
    理解
     ↓
    规划
     ↓
    行动
     ↓
    反馈

------------------------------------------------------------------------

## 八、下一课 Day 2

主题：

让 Jarvis 获得真正的大脑。

内容：

1.  OpenAI API基础
2.  API Key管理
3.  .env安全配置
4.  第一次调用大模型
5.  将固定回复升级为模型生成回复

目标：

    用户
     ↓
    Jarvis
     ↓
    OpenAI模型
     ↓
    智能回答

------------------------------------------------------------------------

## 当前项目状态

Jarvis v0.0.1

完成：

-   环境搭建
-   项目初始化
-   Git版本管理
-   第一个Jarvis程序
