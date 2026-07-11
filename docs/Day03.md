
# Jarvis 学习开发日志 Day03

日期：2026-07-10

主题：

> **接入大语言模型，让 Jarvis 第一次拥有真正的对话能力**

---

# 一、今日目标

今天计划完成：

1. 安装并理解 OpenAI SDK
2. 编写 `core/llm.py`
3. 调用 OpenAI Compatible API
4. 接入 OpenRouter + Tencent Hunyuan 模型
5. 实现 Jarvis 与大模型第一次真实通信
6. 将 LLM 能力接入 Jarvis Assistant

---

# 二、今日完成内容

## 1. OpenAI SDK 环境确认

确认当前虚拟环境：

```text
jarvis
```

已经安装：

```text
openai 2.45.0
```

验证：

```powershell
pip show openai
```

结果：

```text
Name: openai
Version: 2.45.0
```

说明：

Jarvis 已具备调用 OpenAI Compatible API 的基础环境。

---

# 三、配置系统升级

继续使用 Day02 建立的配置架构：

```text
.env
    |
    ▼
core/config.py
    |
    ▼
Jarvis
```

---

## `.env` 配置

新增：

```env
OPENAI_API_KEY=xxxx

BASE_URL=https://openrouter.ai/api/v1

MODEL_NAME=tencent/hy3:free
```

作用：

* API Key 与代码分离
* 支持不同模型切换
* 支持不同 OpenAI Compatible 服务商

---

## Config 类

保持：

```python
self.openai_api_key = os.getenv("OPENAI_API_KEY")

self.model_name = os.getenv(
    "MODEL_NAME",
    "gpt-4.1-mini"
)

self.base_url = os.getenv(
    "BASE_URL",
    "https://api.openai.com/v1"
)
```

---

# 四、新增 LLM 模块

创建：

```text
core/
└── llm.py
```

职责：

> 专门负责与大语言模型通信。

设计思想：

Assistant 不关心：

* API 请求细节
* HTTP
* 模型供应商

只调用：

```python
ask_llm()
```

即可。

---

架构：

```text
assistant.py

      |
      ▼

core.llm.ask_llm()

      |
      ▼

OpenAI SDK

      |
      ▼

OpenRouter API

      |
      ▼

Tencent Hunyuan
```

---

# 五、第一次调用 OpenAI Compatible API

成功发送请求：

```text
POST

https://openrouter.ai/api/v1/chat/completions
```

返回：

```text
HTTP/1.1 200 OK
```

说明：

* API Key 正确
* Base URL 正确
* Model 正确
* SDK 工作正常

---

# 六、创建测试程序

创建：

```text
test_llm.py
```

用于验证：

```python
reply = ask_llm(
    "你好，请介绍一下自己"
)
```

成功返回：

```text
你好！我是混元，是由腾讯开发的大模型……
```

完成：

> Jarvis 第一次调用大模型。

---

# 七、Assistant 接入 LLM

修改：

```text
core/assistant.py
```

新增：

```python
from core.llm import ask_llm
```

增加：

```python
def chat(self):
    user_input = input("You: ")

    reply = ask_llm(user_input)

    print(f"Jarvis: {reply}")
```

---

# 八、Jarvis 第一次真实对话

运行：

```powershell
python main.py
```

输入：

```text
You: 你好
```

成功返回：

```text
Jarvis:
你好！很高兴见到你。有什么我可以帮你的吗？
```

---

# 九、今日项目结构变化

当前：

```text
Jarvis/

├── main.py
├── README.md
├── requirements.txt
│
├── core/
│   ├── assistant.py
│   ├── config.py
│   ├── logger.py
│   ├── llm.py        ⭐ 新增
│   └── __init__.py
│
├── memory/
│   └── history.py
│
├── tools/
│
├── tests/
│   └── test_llm.py
│
└── docs/
    ├── Day01.md
    ├── Day02.md
    └── Day03.md
```

---

# 十、今日重要工程思想

## 1. 配置驱动开发

不要：

```python
api_key="xxxx"
```

写死在代码里。

应该：

```text
.env

↓

Config

↓

Application
```

优势：

* 安全
* 易维护
* 易切换模型

---

## 2. 模块职责分离

当前：

```text
Config
负责配置

Logger
负责日志

LLM
负责模型调用

Assistant
负责交互流程
```

每个模块只负责自己的事情。

---

## 3. 增量开发

今天没有一次写完整 Agent。

而是：

```text
API连接
    ↓
测试调用
    ↓
Assistant接入
    ↓
用户输入
    ↓
模型回复
```

每一步都保持可运行。

---

# 十一、Git 状态

Day03 完成后计划提交：

```bash
git add .

git commit -m "Day03 integrate LLM module and first interactive chat"

git push
```

目标 Git 历史：

```text
d27d6e9
Day01 create first Jarvis core

c5df2b1
Day02 project refactor

xxxxxxx
Day03 integrate LLM module and first interactive chat
```

---

# 十二、今日里程碑

## 🏆 Milestone: Jarvis v0.0.3

完成：

✅ 项目工程化基础
✅ GitHub 远程仓库
✅ 配置管理
✅ 日志系统
✅ OpenAI SDK 接入
✅ OpenRouter API 接入
✅ Tencent Hunyuan 模型调用
✅ Jarvis 第一次真实对话

---

# 十三、下一阶段计划 Day04

主题：

> **让 Jarvis 像真正 AI 助手一样持续交流**

计划：

1. 实现多轮聊天循环
2. 增加退出机制
3. 实现 Streaming 流式输出
4. 优化用户交互体验
5. 开始设计 Conversation Memory

目标：

从：

```text
You:
你好

Jarvis:
你好！
```

升级为：

```text
You:
你好

Jarvis:
你好，我是 Jarvis...

You:
你还记得刚才吗？

Jarvis:
当然……
```

---

# Day03 总结

今天是 Jarvis 项目的一个关键节点。

从今天开始：

Jarvis 不再只是一个 Python 工程框架。

它第一次连接到了真实的大语言模型，并具备了理解和回应用户输入的能力。

下一阶段，我们将开始让它拥有：

* 连续交流能力
* 记忆能力
* 工具能力
* Agent 能力

---

**End of Day03**

🚀 Jarvis Project Status:

> "The brain has been connected."
