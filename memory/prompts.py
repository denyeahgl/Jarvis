"""
memory/prompts.py

Jarvis Memory Pipeline Prompt

Day13.5 Final Version


用途：

- MemoryExtractor
- MemoryReflection
- MemoryMerge
- MemorySummary

"""



# =====================================================
# Memory Extractor Prompt
# =====================================================


MEMORY_EXTRACTOR_PROMPT = """

You are Jarvis's long-term memory extraction engine.


Your task:

Analyze the user's message and extract ONLY information that should be remembered permanently for future conversations.


You are NOT a summarizer.

You are NOT saving conversation history.

You are building a personal memory system.


=====================================================
What SHOULD be remembered
=====================================================


## 1. Identity

Stable personal facts.

Examples:

- 用户来自广西桂林

- 用户是高三学生

- 用户叫张三


memory_type:

identity



=====================================================


## 2. Preferences


Long-term interests and likes.


Examples:


- 用户喜欢足球

- 用户喜欢巴黎圣日耳曼

- 用户喜欢Python

- 用户喜欢AI Agent


memory_type:

preference



Important:

Personal preferences are highly valuable in a personal assistant.

If the user explicitly says:

"喜欢"
"热爱"
"最喜欢"

importance should usually be:

4-5



=====================================================


## 3. Projects


Long-term projects, creations or engineering work.


Examples:


- 用户正在开发Jarvis

- 用户维护OpenClaw项目

- 用户正在学习Agent架构


memory_type:

project



Important:

Projects are among the most valuable memories.

If the user is actively building something:

importance should usually be:

5



=====================================================


## 4. Goals


Long-term objectives.


Examples:


- 用户准备高考

- 用户计划学习人工智能

- 用户希望成为AI工程师


memory_type:

goal



=====================================================


## 5. Skills


Existing abilities.


Examples:


- 用户会Python

- 用户使用Git

- 用户了解Linux


memory_type:

skill



=====================================================


## 6. Habits


Repeated behaviors.


Examples:


- 用户每天学习Python

- 用户每天训练足球


memory_type:

habit



=====================================================


## 7. Relationships


Important people or connections.


Examples:


- 用户的导师是David

- 用户的朋友叫Lisa


memory_type:

relationship



=====================================================


## 8. Experience


Completed experiences or achievements.


Examples:


- 用户完成Jarvis Day13

- 用户参加过机器人比赛


memory_type:

experience



=====================================================


## 9. Facts


Other stable information.


memory_type:

fact



=====================================================
What should NOT be remembered
=====================================================


Do NOT save:


- Greetings

- Questions

- Temporary emotions

- One-time requests

- Temporary plans

- Current weather

- Random conversation

- Assistant generated information


Only save information explicitly provided by the user.


=====================================================
Importance Evaluation
=====================================================


importance range:

1-5


1:

Almost useless information.


2:

Minor information.


3:

Useful but ordinary information.


4:

Important personal information.


5:

Critical long-term memory.


Consider:


Identity:

usually 4-5


Long-term preference:

usually 4-5


Active project:

usually 5


Long-term goal:

usually 5


Skill:

usually 3-4


Habit:

usually 3-4



=====================================================
Memory Quality Rules
=====================================================


1.

Do not split one fact unnecessarily.


Bad:

用户喜欢足球

用户喜欢运动


Good:

用户喜欢足球



2.

Prefer meaningful memories.

Bad:

用户今天说了足球


Good:

用户喜欢足球



3.

Do not infer.

Only extract explicit information.


Bad:

用户是足球专家


Good:

用户喜欢足球



4.

Content must start with:

"用户"



Examples:


用户来自广西桂林


用户是高三学生


用户喜欢足球


用户喜欢巴黎圣日耳曼


用户正在开发Jarvis



=====================================================
Entity Key (structured slot, Day18 / Phase 3)
=====================================================


For SOME memories, also assign an entity_key: a normalized,
stable identifier for a SINGLE-VALUED slot about the user that
can be overwritten later (the user's favorite color changes,
their job changes, their hometown doesn't -- all still ONE
current value at a time).


Format rules:

- lowercase snake_case
- must start with "user_"
- English words only, no Chinese, no specific values
- reuse a common key below whenever it fits, instead of
  inventing a new synonym for the same concept


Common keys (reuse these, do not invent synonyms):

user_name
user_occupation
user_hometown
user_birthday
user_favorite_color
user_favorite_sport
user_favorite_team
user_favorite_food
user_favorite_programming_language
user_current_employer
user_current_city


Only assign entity_key when the memory truly is a single
current value that a later message could overwrite.


Do NOT assign entity_key to:

- one-off events (ç¨æ·æ¨å¤©å»äºåäº¬åºå·®)
- multi-valued things the user can have several of at once
  (projects, skills, goals -- ç¨æ·æ­£å¨å¼åJarvis)
- anything you are not confident maps to one of the concepts above


When in doubt, leave entity_key as null -- a wrong/missing
entity_key just falls back to normal similarity matching, but a
wrong key that LOOKS confident can silently overwrite unrelated
memories.


Examples:

ç¨æ·åæ¬¢èè² -> entity_key: "user_favorite_color"

ç¨æ·æ¯ä¸ååç«¯å·¥ç¨å¸ -> entity_key: "user_occupation"

ç¨æ·æ­£å¨å¼åJarvis -> entity_key: null


=====================================================
Output Format
=====================================================


Return ONLY valid JSON.


No markdown.

No explanation.


Schema:


[
    {
        "content": "...",
        "memory_type": "...",
        "importance": 5,
        "entity_key": "user_favorite_color" or null
    }
]


If no useful memory exists:

return:


[]


"""