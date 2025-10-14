# Ollama 本地AI模型部署指南

## 1. 安装Ollama

### macOS/Linux 
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
访问 https://ollama.ai/download 下载安装包

## 2. 下载推荐的中文模型

```bash
# 下载Qwen2.5 7B模型（推荐，中文效果好，8GB内存可运行）
ollama pull qwen2.5:7b

# 可选：下载其他模型
ollama pull llama3.1:8b      # 英文较好
ollama pull chatglm3:6b      # 中文对话模型
ollama pull baichuan2:7b     # 中文模型
```

## 3. 启动Ollama服务

```bash
# 启动Ollama服务（默认端口11434）
ollama serve

# 后台运行
nohup ollama serve > ollama.log 2>&1 &
```

## 4. 测试模型

```bash
# 命令行测试
ollama run qwen2.5:7b

# 测试对话
>>> 你好，请介绍一下自己
>>> exit
```

## 5. API测试

```bash
# 测试API接口
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:7b",
    "prompt": "请用中文回答：什么是人工智能？",
    "stream": false
  }'
```

## 6. 模型配置说明

### 内存需求
- qwen2.5:7b → 需要约8GB RAM
- llama3.1:8b → 需要约10GB RAM  
- chatglm3:6b → 需要约6GB RAM

### 性能调优
```bash
# 设置GPU使用（如果有NVIDIA显卡）
export CUDA_VISIBLE_DEVICES=0

# 设置并发数
export OLLAMA_NUM_PARALLEL=2

# 设置模型缓存目录
export OLLAMA_MODELS=/path/to/models
```

## 7. 故障排除

### 常见问题

1. **端口占用**
```bash
# 检查端口
lsof -i :11434
# 杀死进程
kill -9 <PID>
```

2. **内存不足**
- 尝试使用更小的模型
- 关闭其他程序释放内存

3. **模型下载慢**
```bash
# 设置镜像源（中国用户）
export OLLAMA_HOST=0.0.0.0:11434
```

### 日志查看
```bash
# 查看Ollama日志
tail -f ollama.log

# 查看系统日志
journalctl -u ollama
```

## 8. 生产环境部署

### Docker部署
```bash
# 拉取Ollama镜像
docker pull ollama/ollama

# 运行容器
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama

# 下载模型
docker exec -it ollama ollama pull qwen2.5:7b
```

### 性能监控
```bash
# 监控资源使用
docker stats ollama

# 查看模型状态
curl http://localhost:11434/api/tags
```
