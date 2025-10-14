# AI Agent集成指南

## 概述

已为您的LoopcruiseTheatre项目集成了基于Ollama的本地AI Agent系统。该系统完全开源、免费，支持本地部署，可以理解剧本内容并根据用户输入生成相关的剧情文本。

## 🎯 功能特性

✅ **完全本地部署** - 无需网络连接，保护数据隐私  
✅ **开源免费** - 基于Ollama和开源LLM模型  
✅ **流式响应** - 实时生成对话内容  
✅ **剧本理解** - 智能解析剧本结构和角色设定  
✅ **上下文感知** - 根据剧情背景生成符合设定的内容  
✅ **多模型支持** - 支持Qwen2.5、Llama3等多种模型  

## 🏗️ 系统架构

```
Frontend (React/TypeScript)
         ↓ HTTP + SSE
Backend (FastAPI)
    ├── Stream API (SSE流式传输)
    ├── Agent API (AI对话接口)
    └── AI Agent Layer
              ↓ HTTP
        Ollama Service (本地LLM服务)
              ↓
        Local Models (qwen2.5:7b等)
```

## 📁 新增文件结构

```
server/
├── app/
│   ├── agents/                 # AI Agent模块
│   │   ├── __init__.py
│   │   ├── base_agent.py      # Agent基类定义
│   │   └── ollama_agent.py    # Ollama Agent实现
│   └── api/
│       └── agent.py           # Agent API接口
├── ollama_setup.md           # Ollama安装指南
└── test_agent_integration.py # 集成测试脚本
```

## 🚀 快速开始

### 1. 安装Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# 下载中文模型（推荐）
ollama pull qwen2.5:7b
```

### 2. 启动服务

```bash
# 启动Ollama（在后台运行）
ollama serve &

# 启动FastAPI服务
cd server
uvicorn app.main:app --reload --port 8000
```

### 3. 测试集成

```bash
# 运行集成测试
python test_agent_integration.py
```

## 🔧 API接口说明

### 1. 加载剧本
```http
POST /api/v1/agent/load_script
Content-Type: application/json

{
  "session_id": "sess_xxx",
  "script_text": "你的完整剧本内容...",
  "model_name": "qwen2.5:7b"
}
```

### 2. AI对话
```http
POST /api/v1/agent/chat
Content-Type: application/json

{
  "session_id": "sess_xxx", 
  "message": "用户输入的文本",
  "stream": true
}
```

### 3. 获取状态
```http
GET /api/v1/agent/status/{session_id}
```

### 4. SSE事件监听
```javascript
const eventSource = new EventSource(`/api/v1/stream/sse?session_id=${sessionId}`);

eventSource.addEventListener('npc', (event) => {
  const data = JSON.parse(event.data);
  console.log(`[${data.speaker_id}]: ${data.text}`);
});

eventSource.addEventListener('ai_stream', (event) => {
  const data = JSON.parse(event.data);
  console.log('AI流式输出:', data.chunk);
});
```

## 📝 使用流程示例

```javascript
// 1. 创建会话
const sessionResponse = await fetch('/api/v1/stream/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ hello: true })
});
const { session_id } = await sessionResponse.json();

// 2. 加载剧本
await fetch('/api/v1/agent/load_script', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id,
    script_text: `
      标题：神秘岛屿探险
      角色：
      - 船长：经验丰富的探险家
      - 助手：年轻好奇的船员
      
      剧情：在海上发现了一个神秘岛屿...
    `
  })
});

// 3. 开始对话
await fetch('/api/v1/agent/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id,
    message: "我们登上岛屿后看到了什么？",
    stream: true
  })
});

// 4. 监听AI响应（通过SSE）
const eventSource = new EventSource(`/api/v1/stream/sse?session_id=${session_id}`);
// ... 处理事件
```

## 🎨 前端集成建议

### 添加Agent控制组件

建议在前端添加以下组件：

1. **剧本上传组件** - 允许用户上传或粘贴剧本文本
2. **AI对话框** - 显示AI生成的角色对话
3. **加载状态指示器** - 显示AI思考和生成进度
4. **模型选择器** - 允许用户选择不同的AI模型

### 示例React组件

```tsx
// src/components/AIAgent.tsx
import { useState, useEffect } from 'react';

export const AIAgent = ({ sessionId }: { sessionId: string }) => {
  const [script, setScript] = useState('');
  const [message, setMessage] = useState('');
  const [isLoaded, setIsLoaded] = useState(false);

  const loadScript = async () => {
    await fetch('/api/v1/agent/load_script', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, script_text: script })
    });
    setIsLoaded(true);
  };

  const sendMessage = async () => {
    await fetch('/api/v1/agent/chat', {
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        session_id: sessionId, 
        message, 
        stream: true 
      })
    });
    setMessage('');
  };

  return (
    <div className="ai-agent">
      <textarea
        value={script}
        onChange={(e) => setScript(e.target.value)}
        placeholder="粘贴你的剧本内容..."
        rows={10}
      />
      <button onClick={loadScript}>加载剧本</button>
      
      {isLoaded && (
        <div>
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="输入你想说的话..."
          />
          <button onClick={sendMessage}>发送</button>
        </div>
      )}
    </div>
  );
};
```

## 🔧 高级配置

### 1. 模型性能调优

```python
# 在ollama_agent.py中调整参数
"options": {
    "temperature": 0.8,      # 创造性 (0-1)
    "top_p": 0.9,           # 核采样
    "max_tokens": 500,      # 最大输出长度
    "repeat_penalty": 1.1   # 重复惩罚
}
```

### 2. 自定义提示词

修改 `ollama_agent.py` 中的 `_build_prompt` 方法来自定义AI的行为：

```python
def _build_prompt(self, user_input: UserInput) -> str:
    # 添加你的自定义提示词逻辑
    return f"""
    你是一个专业的互动小说AI助手...
    {your_custom_instructions}
    """
```

### 3. 多模型切换

```python
# 支持动态切换模型
agent = OllamaAgent(model_name="llama3.1:8b")
# 或
agent = OllamaAgent(model_name="chatglm3:6b")
```

## 🐛 故障排除

### 常见问题

1. **Ollama连接失败**
   ```bash
   # 检查Ollama服务状态
   curl http://localhost:11434/api/tags
   
   # 重启Ollama
   pkill ollama && ollama serve
   ```

2. **内存不足**
   - 使用更小的模型（如qwen2.5:1.5b）
   - 关闭其他应用程序

3. **响应速度慢**
   - 确保有足够内存
   - 考虑使用GPU加速
   - 减少max_tokens设置

### 日志调试

```python
# 在ollama_agent.py中启用详细日志
from loguru import logger
logger.add("agent.log", level="DEBUG")
```

## 🎯 扩展建议

### 1. 其他开源方案

如果Ollama不满足需求，还可以考虑：

- **Hugging Face Transformers** - 直接使用Python加载模型
- **LangChain + LocalAI** - 更复杂的Agent工作流
- **AutoGPT本地版** - 基于开源LLM的自主Agent

### 2. 功能增强

- 添加角色情感分析
- 支持多轮对话记忆
- 集成语音合成(TTS)
- 添加剧情分支选择

### 3. 性能优化

- 使用向量数据库存储剧本
- 实现模型缓存机制
- 添加请求队列管理

## 📞 技术支持

如需进一步定制或优化，可以：

1. 查看详细的API文档：`http://localhost:8000/docs`
2. 运行测试脚本验证功能：`python test_agent_integration.py`
3. 查看Ollama官方文档：https://ollama.ai/

---

🎉 **恭喜！** 您现在拥有了一个完全本地化、开源免费的AI剧情生成系统！
