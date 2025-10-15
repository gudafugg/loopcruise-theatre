# 🧠 对话处理逻辑详解

## 📊 **数据结构解析**

### **对话消息完整结构**
```json
{
  "id": "64f24c32-60e9-4933-b87c-d4e71992d4ff",
  "session_id": "052c4bfc-bb8f-41a0-9b8f-db3fcbf088d5", 
  "content": "[小白说]: 旺旺旺旺。",
  "role": "dialogue",
  "timestamp": "2025-10-15 17:00:57.670880",
  "metadata": "{\"speaker\": \"小白\", \"scene\": \"主人公醒来时\", \"sequence\": 1, \"script_title\": \"《迷失》\"}"
}
```

## 🔍 **Metadata 字段详解**

### **核心字段含义**

| 字段 | 数据类型 | 含义 | 示例 |
|------|----------|------|------|
| **speaker** | `string` | 说话者角色名 | `"汤尚"`, `"周二"`, `"绑架犯"` |
| **scene** | `string` | 对话发生的场景 | `"地下室初次相遇"`, `"医院醒来"` |
| **sequence** | `integer` | 对话在剧本中的顺序 | `1`, `2`, `3`... |
| **script_title** | `string` | 所属剧本名称 | `"《迷失》"` |

### **字段详细说明**

#### 1. **speaker（角色）**
- **作用**: 标识对话的说话者
- **数据来源**: 从剧本文本中手工提取
- **《迷失》中的角色**:
  - `"周二"` - 主人公，多重人格之一
  - `"汤尚"` - 被绑架的少年，知情者
  - `"绑架犯"` - 戴猪八戒面具的反派
  - `"妈妈"` - 主人公的母亲  
  - `"小白"` - 主人公的宠物狗

#### 2. **scene（场景）**
- **作用**: 描述对话发生的具体情境
- **用途**: 帮助AI理解对话的上下文环境
- **《迷失》中的场景**:
  - `"主人公醒来时"` - 故事开始
  - `"地下室初次相遇"` - 周二与汤尚初见
  - `"自我介绍"` - 角色介绍环节
  - `"解释绑架情况"` - 汤尚说明被绑经过
  - `"送饭时刻"` - 绑架犯出现
  - `"透露重要信息"` - 关于家庭秘密
  - `"医院醒来"` - 故事结尾

#### 3. **sequence（序号）**
- **作用**: 保持对话的时间顺序
- **重要性**: 确保AI Agent能理解剧情发展
- **范围**: 1-18（《迷失》共18条对话）

#### 4. **script_title（剧本标题）**
- **作用**: 区分不同剧本的对话
- **扩展性**: 支持导入多个剧本到同一数据库

## 🔄 **对话处理流程**

### **1. 数据导入流程**
```python
# simple_script_importer.py 中的处理逻辑

def extract_dialogues():
    """从剧本中提取结构化对话"""
    dialogues = [
        {
            "speaker": "汤尚",                    # 角色识别
            "content": "你醒了？",                # 纯对话内容
            "scene": "地下室初次相遇"              # 场景标注
        }
    ]
    return dialogues

def import_to_database():
    for i, dialogue in enumerate(dialogues):
        # 构建存储内容
        content = "[{}说]: {}".format(dialogue["speaker"], dialogue["content"])
        
        # 构建元数据
        metadata = {
            "speaker": dialogue["speaker"],
            "scene": dialogue["scene"], 
            "sequence": i + 1,                    # 自动编号
            "script_title": "《迷失》"
        }
        
        # 存储到数据库
        store_message(content, "dialogue", json.dumps(metadata))
```

### **2. 数据查询流程**
```python
# script_api.py 中的查询逻辑

def get_speaker_dialogues(speaker_name):
    """按角色查询对话"""
    # SQL查询：匹配内容格式 [角色说]: 
    query = "SELECT * FROM messages WHERE content LIKE '[{}说]: %'".format(speaker_name)
    
    # 数据处理：提取纯对话内容
    for msg in results:
        content = msg["content"].split("]: ", 1)[1]  # 去掉[角色说]: 前缀
        metadata = json.loads(msg["metadata"])       # 解析元数据
        
        return {
            "speaker": metadata["speaker"],
            "content": content,                       # 纯净的对话文本
            "scene": metadata["scene"],
            "sequence": metadata["sequence"]
        }
```

### **3. 搜索匹配逻辑**
```python
def search_dialogues(query):
    """内容搜索逻辑"""
    # 1. 模糊匹配对话内容
    sql = "SELECT * WHERE content LIKE '%{}%'".format(query)
    
    # 2. 高亮匹配文本  
    for dialogue in results:
        highlight = dialogue["content"].replace(query, "**{}**".format(query))
        dialogue["match_highlight"] = highlight
    
    # 3. 按relevance排序
    return sorted(results, key=lambda x: x["sequence"])
```

## 🎭 **角色对话分析**

### **汤尚角色分析**（基于metadata）
```python
# 获取汤尚的所有对话
tangs_dialogues = api.get_speaker_dialogues("汤尚")

# 分析结果：
{
    "total": 10,  # 汤尚说了10句话
    "scenes": [
        "地下室初次相遇",   # 首次出场
        "自我介绍",         # 主动介绍
        "解释绑架情况",     # 信息提供者
        "安慰周二",         # 心理支持
        "透露重要信息",     # 剧情推进
        "叫醒周二准备逃跑"  # 行动发起者
    ],
    "character_traits": "冷静、善良、知情、行动力强"
}
```

### **场景转换分析**
```python
# 追踪剧情发展
scene_flow = [
    {"sequence": 1, "scene": "主人公醒来时", "speaker": "小白"},
    {"sequence": 2, "scene": "地下室初次相遇", "speaker": "汤尚"},  
    {"sequence": 14, "scene": "叫醒周二准备逃跑", "speaker": "汤尚"},
    {"sequence": 18, "scene": "医院醒来", "speaker": "妈妈"}
]
# 体现了：正常生活 → 被绑架 → 逃脱 → 获救 的完整故事线
```

## 🤖 **AI Agent 利用方式**

### **1. 角色扮演训练**
```python
# 训练AI扮演汤尚
tangs_data = api.get_speaker_dialogues("汤尚")
for dialogue in tangs_data["dialogues"]:
    training_data = {
        "input": f"在{dialogue['scene']}场景下，作为汤尚你会说什么？",
        "output": dialogue["content"],
        "context": dialogue["scene"]
    }
```

### **2. 剧情续写**
```python
# 基于已有对话生成新剧情
last_scene = api.search_dialogues("逃跑")
context = {
    "current_scene": "逃跑过程中",
    "active_characters": ["周二", "汤尚", "绑架犯"],
    "story_tension": "高度紧张"
}

# AI可以基于这些元数据继续创作
```

### **3. 情感分析**
```python
def analyze_emotions(speaker):
    dialogues = api.get_speaker_dialogues(speaker)
    
    emotions = []
    for d in dialogues["dialogues"]:
        # 基于scene和content分析情感
        if "安慰" in d["scene"]:
            emotion = "关怀"
        elif "恐吓" in d["content"]:
            emotion = "威胁"
        elif "谢谢" in d["content"]:
            emotion = "感激"
            
        emotions.append({
            "sequence": d["sequence"],
            "scene": d["scene"], 
            "emotion": emotion
        })
    
    return emotions
```

## 📈 **数据统计功能**

### **剧本统计分析**
```python
stats = api.get_stats()
# 返回：
{
    "total_dialogues": 18,
    "total_speakers": 5, 
    "total_scenes": 15,
    "speakers": ["周二", "汤尚", "绑架犯", "妈妈", "小白"],
    "dialogue_distribution": {
        "汤尚": 10,    # 汤尚最活跃
        "周二": 4,     # 主人公相对被动
        "绑架犯": 2,   # 寡言的反派
        "妈妈": 1,     # 只在结尾出现
        "小白": 1      # 引发事件的关键
    }
}
```

## 💡 **扩展应用场景**

### **1. 对话生成**
利用metadata训练生成模型，让AI学会在特定场景下生成符合角色特点的对话

### **2. 剧本分析**
通过sequence分析剧情节奏，通过scene分析场景转换，通过speaker分析角色关系

### **3. 教育应用** 
将对话数据用于语言学习、戏剧教学、创意写作等领域

### **4. 游戏开发**
基于角色对话数据创建互动式剧情游戏或聊天机器人

现在您完全理解了对话处理的所有细节！🎭✨
