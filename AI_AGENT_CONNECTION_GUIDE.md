# 🤖 AI Agent 连接《迷失》剧本数据库指南

> **为AI Agent开发者提供的完整数据访问接口文档**

## 🎯 **概览**

《迷失》剧本对话数据已成功存储到SQLite数据库中，提供了完整的REST API接口供AI Agent访问。

### **📊 数据统计**
- **剧本名称**: 《迷失》
- **总对话数**: 18条
- **角色数量**: 5个（周二、汤尚、绑架犯、妈妈、小白）  
- **场景数量**: 15个不同场景
- **数据格式**: JSON，支持元数据查询

## 🚀 **快速接入**

### **API服务地址**
```
http://localhost:8003
```

### **API文档**
```
http://localhost:8003/docs
```

## 📡 **核心API接口**

### **1. 获取所有对话**
```http
GET /dialogues
```
**参数**:
- `limit` (可选): 限制返回数量

**响应示例**:
```json
{
  "total": 18,
  "dialogues": [
    {
      "id": "unique-id",
      "speaker": "汤尚", 
      "content": "你醒了？",
      "scene": "地下室初次相遇",
      "sequence": 2,
      "timestamp": "2025-10-15 17:00:57"
    }
  ]
}
```

### **2. 按角色获取对话**
```http
GET /speaker/{speaker_name}
```
**示例**:
```bash
curl http://localhost:8003/speaker/汤尚
curl http://localhost:8003/speaker/周二
curl http://localhost:8003/speaker/绑架犯
```

### **3. 按场景获取对话**
```http
GET /scene/{scene_name} 
```
**示例**:
```bash
curl http://localhost:8003/scene/地下室初次相遇
curl http://localhost:8003/scene/医院醒来
```

### **4. 搜索对话内容**
```http
GET /search?q={keyword}
```
**示例**:
```bash
curl "http://localhost:8003/search?q=绑架"
curl "http://localhost:8003/search?q=逃跑"
```

### **5. 获取角色列表**
```http
GET /speakers
```
**响应**:
```json
{
  "total": 5,
  "speakers": ["周二", "汤尚", "绑架犯", "妈妈", "小白"]
}
```

### **6. 获取场景列表**
```http
GET /scenes
```

### **7. 获取统计信息**
```http
GET /stats
```

## 💻 **AI Agent 集成示例**

### **Python示例**
```python
import requests

class ScriptDialogueAPI:
    def __init__(self, base_url="http://localhost:8003"):
        self.base_url = base_url
    
    def get_all_dialogues(self, limit=None):
        """获取所有对话"""
        params = {"limit": limit} if limit else {}
        response = requests.get(f"{self.base_url}/dialogues", params=params)
        return response.json()
    
    def get_speaker_dialogues(self, speaker):
        """获取指定角色的对话"""
        response = requests.get(f"{self.base_url}/speaker/{speaker}")
        return response.json()
    
    def search_dialogues(self, query, limit=50):
        """搜索对话内容"""
        params = {"q": query, "limit": limit}
        response = requests.get(f"{self.base_url}/search", params=params)
        return response.json()
    
    def get_scene_dialogues(self, scene):
        """获取场景对话"""
        response = requests.get(f"{self.base_url}/scene/{scene}")
        return response.json()
    
    def get_speakers(self):
        """获取所有角色"""
        response = requests.get(f"{self.base_url}/speakers")
        return response.json()

# 使用示例
api = ScriptDialogueAPI()

# 获取汤尚的所有对话
tangs_dialogues = api.get_speaker_dialogues("汤尚")
print(f"汤尚共有 {tangs_dialogues['total']} 条对话")

# 搜索关于绑架的对话
kidnap_dialogues = api.search_dialogues("绑架")
print(f"找到 {kidnap_dialogues['total']} 条相关对话")

# 获取所有角色
speakers = api.get_speakers()
print(f"剧本中的角色: {speakers['speakers']}")
```

### **JavaScript示例**
```javascript
class ScriptDialogueAPI {
    constructor(baseUrl = 'http://localhost:8003') {
        this.baseUrl = baseUrl;
    }
    
    async getAllDialogues(limit = null) {
        const params = limit ? `?limit=${limit}` : '';
        const response = await fetch(`${this.baseUrl}/dialogues${params}`);
        return response.json();
    }
    
    async getSpeakerDialogues(speaker) {
        const response = await fetch(`${this.baseUrl}/speaker/${speaker}`);
        return response.json();
    }
    
    async searchDialogues(query, limit = 50) {
        const response = await fetch(`${this.baseUrl}/search?q=${encodeURIComponent(query)}&limit=${limit}`);
        return response.json();
    }
    
    async getSceneDialogues(scene) {
        const response = await fetch(`${this.baseUrl}/scene/${encodeURIComponent(scene)}`);
        return response.json();
    }
    
    async getSpeakers() {
        const response = await fetch(`${this.baseUrl}/speakers`);
        return response.json();
    }
}

// 使用示例
const api = new ScriptDialogueAPI();

// 获取汤尚的对话
api.getSpeakerDialogues('汤尚').then(data => {
    console.log(`汤尚共有 ${data.total} 条对话`);
});

// 搜索对话
api.searchDialogues('绑架').then(data => {
    console.log(`找到 ${data.total} 条相关对话`);
});
```

## 🎭 **剧本角色分析**

### **主要角色**

1. **周二** - 主人公，多重人格中的一个
   - 特点: 困惑、恐惧、但有感激之心
   - 关键对话: 询问情况、表达愤怒、表达感谢

2. **汤尚** - 另一个被绑架者  
   - 特点: 冷静、善良、知情者
   - 关键对话: 解释情况、安慰主人公、制定逃跑计划

3. **绑架犯** - 反派角色
   - 特点: 寡言、神秘、带着猪八戒面具
   - 关键对话: 简短指令、追赶威胁

4. **妈妈** - 主人公的母亲
   - 特点: 关爱、担心
   - 关键对话: 医院中的关怀

5. **小白** - 主人公的宠物狗
   - 特点: 叫声引起事件

### **关键场景**

- **地下室初次相遇**: 周二醒来与汤尚的初次对话
- **解释绑架情况**: 汤尚详细说明被绑架的经过  
- **透露重要信息**: 关于家庭新成员和赎金威胁
- **逃跑计划**: 汤尚制定逃跑策略
- **医院醒来**: 故事的结尾场景

## 🔧 **高级用法**

### **对话分析功能**
```python
def analyze_character_emotions(api, speaker):
    """分析角色情感变化"""
    dialogues = api.get_speaker_dialogues(speaker)
    
    emotions = []
    for dialogue in dialogues['dialogues']:
        content = dialogue['content']
        scene = dialogue['scene']
        
        # 简单情感分析逻辑
        if any(word in content for word in ['谢谢', '感谢']):
            emotion = '感激'
        elif any(word in content for word in ['对不起', '抱歉']):
            emotion = '愧疚'
        elif any(word in content for word in ['害怕', '恐惧']):
            emotion = '恐惧'
        else:
            emotion = '平静'
            
        emotions.append({
            'sequence': dialogue['sequence'],
            'scene': scene,
            'emotion': emotion,
            'content': content[:50] + '...'
        })
    
    return emotions

# 分析汤尚的情感变化
emotions = analyze_character_emotions(api, "汤尚")
for e in emotions:
    print(f"序号{e['sequence']}: {e['emotion']} - {e['content']}")
```

### **场景转换追踪**
```python
def track_scene_transitions(api):
    """追踪场景转换"""
    all_dialogues = api.get_all_dialogues()
    
    scenes = []
    current_scene = None
    
    for dialogue in all_dialogues['dialogues']:
        scene = dialogue['scene']
        if scene != current_scene:
            scenes.append({
                'sequence': dialogue['sequence'],
                'scene': scene,
                'speaker': dialogue['speaker']
            })
            current_scene = scene
    
    return scenes
```

## 📚 **数据结构说明**

### **对话数据格式**
```json
{
    "id": "唯一标识符",
    "speaker": "角色名称", 
    "content": "对话内容（纯文本）",
    "scene": "场景描述",
    "sequence": 1,
    "timestamp": "2025-10-15 17:00:57"
}
```

### **元数据字段**
- `sequence`: 对话在剧本中的顺序
- `scene`: 对话发生的场景描述
- `speaker`: 说话的角色名称
- `timestamp`: 数据库存储时间

## 🎉 **完整示例：构建对话机器人**

```python
class LostScriptBot:
    def __init__(self):
        self.api = ScriptDialogueAPI()
        self.speakers = self.api.get_speakers()['speakers']
    
    def answer_question(self, question):
        """根据问题回答"""
        
        # 角色相关问题
        for speaker in self.speakers:
            if speaker in question:
                dialogues = self.api.get_speaker_dialogues(speaker)
                return f"{speaker}在剧本中说了{dialogues['total']}句话"
        
        # 关键词搜索
        search_result = self.api.search_dialogues(question, limit=3)
        if search_result['total'] > 0:
            response = f"找到{search_result['total']}条相关对话:\n"
            for dialogue in search_result['dialogues'][:3]:
                response += f"- {dialogue['speaker']}: {dialogue['content'][:100]}...\n"
            return response
        
        return "抱歉，没有找到相关信息"

# 使用示例
bot = LostScriptBot()
print(bot.answer_question("汤尚说了什么"))
print(bot.answer_question("绑架"))
```

## 🚀 **部署和使用**

1. **启动API服务**:
   ```bash
   python script_api.py
   ```

2. **访问API文档**: http://localhost:8003/docs

3. **测试连接**:
   ```bash
   curl http://localhost:8003/speakers
   ```

现在您的AI Agent可以完全访问《迷失》剧本的所有对话数据了！🎭✨
