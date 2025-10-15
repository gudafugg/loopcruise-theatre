# 🤝 协作者数据库访问指南

> **专为协作者设计的精简环境配置**  
> 仅包含数据库访问功能，不需要AI模型和Agent环境

## 🎯 **环境说明**

协作者环境特点：
- ✅ **轻量级**: 只安装数据库相关依赖
- ✅ **独立性**: 使用自己的AI模型和Agent
- ✅ **数据共享**: 可访问和同步对话历史数据
- ✅ **快速部署**: 3分钟完成环境配置

## 🚀 **快速开始**

### **方式1: 一键安装（推荐）**

```bash
# 1. 克隆项目
git clone <project-url>
cd loopcruise-theatre/server

# 2. 运行协作者专用安装
python collaborator_setup.py

# 3. 启动数据库API服务
python start_database_api.py
```

### **方式2: 手动安装**

```bash
# 1. 安装精简依赖
pip install -r database_only_requirements.txt

# 2. 初始化数据库
python -c "from app.database.sqlite_storage import storage; storage.init_database()"

# 3. 启动服务
python database_only_main.py
```

## 📊 **服务访问**

启动成功后，可访问：

```bash
# API服务地址
http://localhost:8001

# API文档
http://localhost:8001/docs

# 健康检查
http://localhost:8001/health
```

## 🔄 **数据同步**

### **从主环境获取数据**

```bash
# 方式1: 导入数据库文件（推荐）
python database_export.py --action import --input conversations_backup.db

# 方式2: 导入JSON数据
python database_export.py --action import-json --input conversations_data.json
```

### **导出自己的数据**

```bash
# 导出数据库文件
python database_export.py --action export --output my_conversations.db

# 导出JSON格式
python database_export.py --action export-json --output my_conversations.json

# 查看所有导出文件
python database_export.py --action list
```

## 📁 **项目结构**

协作者环境的核心文件：

```
server/
├── database_only_requirements.txt    # 精简依赖列表
├── collaborator_setup.py            # 协作者安装工具
├── database_only_main.py            # 纯数据库API服务
├── database_export.py               # 数据导入导出工具
├── start_database_api.py            # 服务启动脚本
├── data/                            # 数据库文件目录
│   └── conversations.db             # SQLite数据库
└── database_exports/                # 数据导出目录
    ├── conversations_backup_*.db    # 数据库备份
    └── conversations_data_*.json    # JSON导出文件
```

## 🛠️ **可用API接口**

### **对话历史查询**

```http
GET /api/v1/conversation/sessions/{user_id}    # 获取用户会话列表
GET /api/v1/conversation/messages/{session_id} # 获取会话消息
GET /api/v1/conversation/search               # 搜索对话内容
GET /api/v1/conversation/stats                # 获取统计信息
```

### **数据管理**

```http
DELETE /api/v1/conversation/sessions/{session_id}  # 删除会话
POST /api/v1/conversation/export                   # 导出数据
POST /api/v1/conversation/cleanup                  # 清理旧数据
```

## 🔧 **常用命令**

### **服务管理**

```bash
# 启动数据库API服务
python start_database_api.py

# 直接启动（指定端口）
python database_only_main.py

# 检查服务状态
curl http://localhost:8001/health
```

### **数据库管理**

```bash
# 备份数据库
python database_export.py --action export

# 恢复数据库
python database_export.py --action import --input backup.db

# 查看数据库统计
curl http://localhost:8001/api/v1/conversation/stats
```

## 🚨 **故障排除**

### **常见问题**

1. **依赖安装失败**
   ```bash
   # 升级pip
   python -m pip install --upgrade pip
   
   # 重新安装
   pip install -r database_only_requirements.txt
   ```

2. **数据库文件不存在**
   ```bash
   # 手动创建数据库
   python -c "from app.database.sqlite_storage import storage; storage.init_database()"
   ```

3. **端口冲突**
   ```bash
   # 使用其他端口启动
   python -c "import uvicorn; from database_only_main import app; uvicorn.run(app, port=8002)"
   ```

4. **导入数据失败**
   ```bash
   # 检查文件格式和路径
   python database_export.py --action list
   ```

## 📝 **开发集成**

### **在你的AI Agent中使用**

```python
import requests

# 获取对话历史
def get_conversation_history(session_id):
    response = requests.get(f"http://localhost:8001/api/v1/conversation/messages/{session_id}")
    return response.json()

# 搜索相关对话
def search_conversations(query):
    response = requests.get(f"http://localhost:8001/api/v1/conversation/search?query={query}")
    return response.json()

# 获取用户会话
def get_user_sessions(user_id):
    response = requests.get(f"http://localhost:8001/api/v1/conversation/sessions/{user_id}")
    return response.json()
```

### **数据格式说明**

```json
{
  "sessions": [
    {
      "id": "session_id",
      "user_id": "user_001",
      "script_content": "剧本内容",
      "created_at": "2024-01-01T00:00:00",
      "message_count": 10
    }
  ],
  "messages": [
    {
      "id": "message_id", 
      "session_id": "session_id",
      "content": "对话内容",
      "role": "user|assistant",
      "timestamp": "2024-01-01T00:00:00"
    }
  ]
}
```

## 🎉 **完成！**

现在你可以：
1. ✅ 访问完整的对话历史数据
2. ✅ 与主环境同步数据库
3. ✅ 在自己的AI Agent中集成数据访问
4. ✅ 独立开发而不依赖主环境的AI模型

如有问题，请查看API文档：http://localhost:8001/docs
