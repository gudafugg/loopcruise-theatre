# 📁 项目结构说明

## 🎯 **核心文件结构（已清理）**

```
loopcruise-theatre/
├── 📚 文档
│   ├── README.md                        # 项目主文档
│   ├── AI_AGENT_CONNECTION_GUIDE.md     # AI Agent接入完整指南
│   ├── COLLABORATOR_GUIDE.md           # 协作者配置指南
│   └── PROJECT_STRUCTURE.md            # 本文档
│
├── 🗂️ server/                          # 服务端核心
│   ├── 🧠 app/                         # 应用核心代码
│   │   ├── agents/                     # AI Agent模块
│   │   │   ├── base_agent.py          # Agent基类
│   │   │   ├── memory_agent.py        # 带记忆的Agent
│   │   │   └── ollama_agent.py        # Ollama AI实现
│   │   ├── api/                       # API路由
│   │   │   ├── agent.py               # Agent相关API
│   │   │   ├── conversation.py        # 对话管理API
│   │   │   ├── play.py                # 剧本相关API
│   │   │   └── stream.py              # 流式响应API
│   │   ├── database/                  # 数据库模块
│   │   │   ├── models.py              # 数据模型
│   │   │   └── sqlite_storage.py      # SQLite存储实现
│   │   └── main.py                    # FastAPI主应用
│   │
│   ├── 🛠️ 工具脚本
│   │   ├── simple_script_importer.py  # 剧本导入工具
│   │   ├── script_api.py              # 剧本对话API服务
│   │   ├── collaborator_setup.py      # 协作者环境配置
│   │   ├── database_export.py         # 数据库导入导出
│   │   ├── database_only_main.py      # 纯数据库API服务
│   │   ├── share_database.py          # 协作者包生成
│   │   └── start_server.py            # 主服务启动器
│   │
│   ├── 📊 数据文件
│   │   ├── data/conversations.db      # SQLite数据库
│   │   ├── database_exports/          # 导出的数据文件
│   │   └── collaborator_*.zip         # 协作者包
│   │
│   └── ⚙️ 配置文件
│       ├── environment.yml            # Conda环境配置
│       └── database_only_requirements.txt  # 精简依赖列表
│
└── 📄 LICENSE                          # 开源许可证
```

## 🗑️ **已删除的重复文件**

- ❌ `script_importer.py` → ✅ `simple_script_importer.py`
- ❌ `dialogue_api.py` → ✅ `script_api.py`  
- ❌ `quick_install.py` → ✅ `collaborator_setup.py`
- ❌ `AI_AGENT_GUIDE.md` → ✅ `AI_AGENT_CONNECTION_GUIDE.md`
- ❌ 多个重复的setup和test文件
- ❌ 冗余的文档指南

## 🎯 **核心功能文件**

| 文件 | 功能 | 用途 |
|------|------|------|
| `simple_script_importer.py` | 剧本导入 | 将《迷失》对话存入数据库 |
| `script_api.py` | 对话API | 为AI Agent提供数据访问接口 |
| `collaborator_setup.py` | 协作者配置 | 一键安装协作者环境 |
| `database_export.py` | 数据管理 | 导入导出数据库文件 |
| `share_database.py` | 包生成器 | 创建协作者分享包 |

## 🚀 **快速使用**

```bash
# 1. 导入剧本对话（已完成）
python simple_script_importer.py

# 2. 启动对话API服务
python script_api.py
# 访问: http://localhost:8003

# 3. 创建协作者包
python share_database.py --yes

# 4. 启动主AI服务（需要Ollama）
python start_server.py
```

现在项目结构清晰，核心功能完整！🎭
