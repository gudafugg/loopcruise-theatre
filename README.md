# 🎭 LoopcruiseTheatre - 《迷失》剧本数据库平台

**一个集成《迷失》剧本对话数据库的AI戏剧创作平台，为AI Agent提供完整的剧本数据访问接口**

## 🌟 项目亮点

✨ **《迷失》剧本完整数字化** - 18条对话，5个角色，完整存储  
🤖 **AI Agent友好接口** - REST API，支持多种查询方式  
🤝 **协作者友好** - 一键安装包，无需复杂配置  
🚀 **即插即用** - 3分钟完成环境搭建  

## 🎯 核心功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 📚 **剧本数据存储** | ✅ 完成 | 《迷失》18条对话已入库 |
| 🔍 **智能搜索** | ✅ 完成 | 按角色、场景、内容搜索 |
| 🤖 **AI Agent接口** | ✅ 完成 | REST API，完整文档 |
| 🤝 **协作者支持** | ✅ 完成 | 独立安装包，数据共享 |
| 🎭 **剧本分析** | ✅ 完成 | 角色统计，场景分析 |

## 📊 《迷失》剧本数据

- **总对话数**: 18条
- **角色数量**: 5个（周二、汤尚、绑架犯、妈妈、小白）  
- **场景数量**: 15个不同场景
- **故事类型**: 多重人格悬疑剧

## 🚀 快速开始

### 🎯 **方案A: AI Agent开发者（推荐）**
```bash
# 1. 启动剧本对话API
cd server && python script_api.py
# 访问: http://localhost:8003

# 2. 查看API文档
open http://localhost:8003/docs

# 3. 测试接口
curl http://localhost:8003/speakers
curl "http://localhost:8003/search?q=汤尚"
```

### 🤝 **方案B: 协作者环境**
```bash
# 1. 获取协作者包
unzip collaborator_database_package_*.zip

# 2. 一键安装
python collaborator_setup.py

# 3. 启动数据库API
python start_database_api.py
# 访问: http://localhost:8001
```

### 🎭 **方案C: 完整AI服务**
```bash
# 1. 安装依赖（需要AI模型）
pip install aiohttp fastapi uvicorn loguru

# 2. 安装Ollama（macOS）
brew install ollama
ollama pull qwen2.5:7b

# 3. 启动完整服务
python start_server.py
# 访问: http://localhost:8000
```

## 📡 **API接口速览**

```bash
# 获取所有对话
GET http://localhost:8003/dialogues

# 按角色查询（汤尚说了10句话）
GET http://localhost:8003/speaker/汤尚

# 按场景查询
GET http://localhost:8003/scene/地下室初次相遇

# 搜索对话内容
GET http://localhost:8003/search?q=绑架

# 获取统计信息
GET http://localhost:8003/stats
```

## 🤖 **AI Agent集成示例**

### **Python接入**
```python
import requests

class ScriptAPI:
    def __init__(self):
        self.base_url = "http://localhost:8003"
    
    def get_character_dialogues(self, character):
        """获取角色所有对话"""
        response = requests.get(f"{self.base_url}/speaker/{character}")
        return response.json()
    
    def search_plot_elements(self, keyword):
        """搜索剧情要素"""
        response = requests.get(f"{self.base_url}/search?q={keyword}")
        return response.json()

# 使用示例
api = ScriptAPI()
tangs_lines = api.get_character_dialogues("汤尚")
print(f"汤尚共有 {tangs_lines['total']} 条对话")

kidnap_plot = api.search_plot_elements("绑架")
print(f"找到 {kidnap_plot['total']} 条相关剧情")
```

### **JavaScript接入**
```javascript
// 获取剧本统计
fetch('http://localhost:8003/stats')
  .then(res => res.json())
  .then(data => {
    console.log(`《迷失》共有 ${data.total_dialogues} 条对话`);
    console.log(`角色列表: ${data.speakers.join(', ')}`);
  });

// 角色对话分析
fetch('http://localhost:8003/speaker/汤尚')
  .then(res => res.json())
  .then(data => {
    data.dialogues.forEach(d => {
      console.log(`${d.sequence}: [${d.scene}] ${d.content}`);
    });
  });
```

## 📚 **文档指南**

| 文档 | 内容 | 适用人群 |
|------|------|----------|
| [AI_AGENT_CONNECTION_GUIDE.md](AI_AGENT_CONNECTION_GUIDE.md) | AI Agent完整接入指南 | 🤖 AI开发者 |
| [COLLABORATOR_GUIDE.md](COLLABORATOR_GUIDE.md) | 协作者环境配置指南 | 🤝 协作者 |
| [DIALOGUE_LOGIC_GUIDE.md](DIALOGUE_LOGIC_GUIDE.md) | 对话处理逻辑详解 | 📊 数据分析师 |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | 项目结构说明 | 👥 所有人 |

## 🗂️ **精简项目结构**

```
loopcruise-theatre/
├── 📚 AI_AGENT_CONNECTION_GUIDE.md  # AI Agent接入完整指南
├── 🤝 COLLABORATOR_GUIDE.md        # 协作者配置指南  
├── 📊 DIALOGUE_LOGIC_GUIDE.md      # 对话处理逻辑详解
├── 📁 PROJECT_STRUCTURE.md         # 项目结构说明
├── 📖 README.md                    # 本文档
│
└── server/                         # 服务端核心
    ├── 🎭 script_api.py           # 剧本对话API服务 ⭐
    ├── 📥 simple_script_importer.py  # 剧本导入工具
    ├── 🤝 collaborator_setup.py   # 协作者环境配置
    ├── 🔄 database_export.py      # 数据导入导出工具
    ├── 📦 share_database.py       # 协作者包生成器
    ├── 🚀 start_server.py         # 主AI服务启动器
    │
    ├── 📊 data/conversations.db   # SQLite数据库
    └── 🏗️ app/                    # 核心应用代码
```

## 🎭 **《迷失》剧本角色分析**

| 角色 | 对话数 | 角色特点 | 关键场景 |
|------|-------|----------|----------|
| **汤尚** | 10条 | 冷静、善良、知情者 | 地下室初次相遇、透露重要信息 |
| **周二** | 4条 | 困惑、恐惧、感激 | 询问情况、表达感谢 |
| **绑架犯** | 2条 | 寡言、威胁性 | 送饭时刻、追赶逃跑者 |
| **妈妈** | 1条 | 关爱、担心 | 医院醒来 |
| **小白** | 1条 | 引发事件 | 主人公醒来时 |

## ⚡ **快速测试**

```bash
# 1. 测试API服务是否正常
curl http://localhost:8003/stats

# 2. 获取汤尚的所有对话
curl http://localhost:8003/speaker/汤尚

# 3. 搜索绑架相关剧情
curl "http://localhost:8003/search?q=绑架"

# 4. 查看完整API文档
open http://localhost:8003/docs
```

## 📊 **实际数据展示**

### **API测试结果**
```json
// GET /stats 
{
  "script_title": "《迷失》",
  "total_dialogues": 18,
  "total_speakers": 5,
  "speakers": ["周二", "妈妈", "小白", "汤尚", "绑架犯"]
}

// GET /speaker/汤尚
{
  "speaker": "汤尚",
  "total": 10,
  "dialogues": [
    {
      "content": "你醒了？",
      "scene": "地下室初次相遇",
      "sequence": 2
    },
    {
      "content": "我叫汤尚，我从周三那里听说了你们七个人格的事情，你是周二？",
      "scene": "自我介绍", 
      "sequence": 3
    }
    // ... 更多对话
  ]
}
```

## 🛠️ **开发工具**

| 工具 | 功能 | 命令 |
|------|------|------|
| `simple_script_importer.py` | 导入剧本对话 | `python simple_script_importer.py` |
| `script_api.py` | 启动对话API | `python script_api.py` |
| `collaborator_setup.py` | 协作者环境 | `python collaborator_setup.py` |
| `database_export.py` | 数据管理 | `python database_export.py --help` |
| `share_database.py` | 协作者包 | `python share_database.py --yes` |

## 🎯 **应用场景**

- 🤖 **AI对话训练** - 使用剧本数据训练角色AI
- 📖 **剧本分析** - 分析角色关系和剧情结构  
- 🎮 **游戏开发** - 创建基于剧本的互动游戏
- 🎓 **教育应用** - 戏剧教学和语言学习
- 🔬 **学术研究** - 对话分析和文本挖掘

## 📜 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🎉 **总结**

✅ **项目已完成文件清理** - 删除16个重复/无用文件  
✅ **《迷失》剧本数据已入库** - 18条对话完整存储  
✅ **API服务正常运行** - http://localhost:8003  
✅ **协作者包已生成** - 支持独立部署  
✅ **文档体系完整** - 4份详细指南  

**现在可以开始您的AI Agent开发之旅！** 🚀🎭