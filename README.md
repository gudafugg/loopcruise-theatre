# LoopcruiseTheatre - AI驱动的互动剧场

一个基于AI Agent的互动剧场应用，支持实时剧情生成和角色对话。

## 🌟 主要特性

- 🎭 **AI剧情生成** - 基于剧本内容智能生成相关剧情
- 🗣️ **实时对话** - 与AI角色进行自然语言交互  
- 🧠 **对话记忆** - AI能记住历史对话，理解剧情发展
- 🌊 **流式响应** - 实时显示AI思考和生成过程
- 💾 **数据存储** - 本地SQLite数据库存储对话历史
- 🔍 **智能检索** - 搜索历史对话，分析对话统计
- 🔒 **本地部署** - 完全离线运行，保护隐私
- 💰 **完全免费** - 基于开源模型，无任何费用
- ⚡ **高性能** - 优化的流式传输架构

## 🏗️ 技术架构

### 前端 (React + TypeScript)
- Vite构建工具
- 实时SSE流式通信
- 响应式UI设计

### 后端 (Python + FastAPI)  
- RESTful API设计
- Server-Sent Events流式传输
- AI Agent集成层

### AI引擎 (Ollama + 开源LLM)
- 本地大语言模型
- 支持多种开源模型
- 智能剧情生成
- 对话记忆和上下文理解

### 数据存储 (SQLite)
- 本地数据库存储
- 对话历史管理
- 会话状态持久化
- 数据分析和导出

## 🚀 快速开始

### 1. 安装AI模型服务

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载推荐的中文模型  
ollama pull qwen2.5:7b

# 启动Ollama服务
ollama serve
```

### 2. 安装依赖

```bash
# 后端依赖
cd server
pip install aiohttp fastapi uvicorn

# 前端依赖 
cd ../web
pnpm install
```

### 3. 启动服务

```bash
# 启动后端 (终端1)
cd server
python start_server.py

# 启动前端 (终端2)
cd web  
pnpm dev
```

### 4. 访问应用

- 前端应用: http://localhost:5173
- API文档: http://localhost:8000/docs
- Ollama服务: http://localhost:11434

## 📖 使用指南

### 基本使用流程

1. **上传剧本** - 输入完整的剧本文本
2. **AI解析** - 系统自动解析角色和情节设定
3. **开始互动** - 与AI角色进行对话
4. **剧情生成** - AI根据上下文和历史生成新的剧情内容
5. **记忆管理** - 系统自动保存对话历史，支持检索和分析

### API使用示例

```javascript
// 1. 创建会话
const session = await fetch('/api/v1/stream/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ hello: true })
});

// 2. 加载剧本
await fetch('/api/v1/agent/load_script', {
  method: 'POST', 
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: sessionId,
    script_text: "你的剧本内容..."
  })
});

// 3. 开始对话
await fetch('/api/v1/agent/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: sessionId,
    message: "用户输入",
    stream: true
  })
});
```

## 📁 项目结构

```
loopcruise-theatre/
├── web/                    # 前端React应用
│   ├── src/
│   │   ├── dialogue/      # 对话系统组件
│   │   └── api/           # API通信层
│   └── package.json
├── server/                # 后端FastAPI应用
│   ├── app/
│   │   ├── agents/        # AI Agent模块
│   │   │   ├── base_agent.py      # Agent基类
│   │   │   ├── ollama_agent.py    # Ollama Agent
│   │   │   └── memory_agent.py    # 带记忆Agent
│   │   ├── database/      # 数据存储模块
│   │   │   ├── models.py          # 数据模型
│   │   │   └── sqlite_storage.py  # SQLite存储
│   │   └── api/           # API接口
│   │       ├── stream.py          # SSE流式传输
│   │       ├── agent.py           # AI Agent接口
│   │       └── conversation.py    # 对话管理接口
│   ├── environment.yml    # Conda环境配置
│   ├── start_server.py    # 服务启动脚本
│   └── test_agent_integration.py  # 集成测试
├── AI_AGENT_GUIDE.md     # AI Agent详细指南
├── CONVERSATION_STORAGE_GUIDE.md # 对话存储系统指南
└── README.md             # 项目说明
```

## 🔧 配置选项

### 支持的AI模型

| 模型 | 大小 | 内存需求 | 特点 |
|------|------|----------|------|
| qwen2.5:7b | 7B | ~8GB | 中文优化，推荐 |
| llama3.1:8b | 8B | ~10GB | 英文较好 |
| chatglm3:6b | 6B | ~6GB | 中文对话 |
| baichuan2:7b | 7B | ~8GB | 中文模型 |

### 性能调优

```python
# 在ollama_agent.py中调整
"options": {
    "temperature": 0.8,    # 创造性 (0-1)
    "top_p": 0.9,         # 核采样  
    "max_tokens": 500,    # 最大输出
    "repeat_penalty": 1.1 # 重复惩罚
}
```

## 🧪 测试

```bash
# 运行完整集成测试
cd server
python test_agent_integration.py

# 单元测试
python -m pytest tests/

# API测试
curl -X GET http://localhost:8000/api/v1/agent/models
```

## 🐛 故障排除

### 常见问题

1. **Ollama连接失败**
   ```bash
   # 检查服务状态
   curl http://localhost:11434/api/tags
   
   # 重启服务
   pkill ollama && ollama serve
   ```

2. **内存不足**
   - 使用更小的模型 (qwen2.5:1.5b)
   - 关闭其他应用程序

3. **依赖安装失败**
   ```bash
   # 使用conda环境
   conda env create -f server/environment.yml
   conda activate loopcruise
   ```

## 🎯 扩展方案

### 其他开源AI方案

如果需要其他开源方案，可以考虑：

1. **Hugging Face Transformers**
   - 直接使用Python加载模型
   - 支持更多模型选择
   - 可以进行微调

2. **LangChain + LocalAI** 
   - 更复杂的Agent工作流
   - 支持工具调用
   - 可扩展性强

3. **AutoGPT本地版**
   - 基于开源LLM
   - 自主任务执行
   - 支持插件系统

### 功能增强建议

- 🎨 **多媒体支持** - 图片、音频生成
- 🧠 **记忆系统** - 长期对话记忆
- 🎭 **情感分析** - 角色情绪识别
- 🌐 **多语言** - 国际化支持
- 📱 **移动端** - React Native适配

## 📜 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

---

🎉 **享受AI驱动的互动剧场体验吧！**