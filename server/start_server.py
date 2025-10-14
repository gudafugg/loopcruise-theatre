#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LoopcruiseTheatre服务启动脚本
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_ollama():
    """检查Ollama服务是否运行"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = [model["name"] for model in response.json().get("models", [])]
            print(f"✅ Ollama服务正常运行，可用模型: {models}")
            return True
    except requests.RequestException:
        print("❌ Ollama服务未运行")
        print("请先启动Ollama:")
        print("  1. 安装: curl -fsSL https://ollama.ai/install.sh | sh")
        print("  2. 下载模型: ollama pull qwen2.5:7b")
        print("  3. 启动服务: ollama serve")
        return False

def install_dependencies():
    """安装Python依赖"""
    print("📦 检查Python依赖...")
    try:
        import aiohttp
        import fastapi
        import uvicorn
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装依赖:")
        print("  pip install aiohttp fastapi uvicorn")
        return False

def start_fastapi():
    """启动FastAPI服务"""
    print("🚀 启动FastAPI服务...")
    try:
        # 确保在正确的目录
        server_dir = Path(__file__).parent
        
        # 启动uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        print("服务将在 http://localhost:8000 启动")
        print("API文档: http://localhost:8000/docs")
        print("\n按 Ctrl+C 停止服务\n")
        
        # 切换到正确目录并启动
        subprocess.run(cmd, cwd=server_dir, check=True)
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 找不到uvicorn，请安装: pip install uvicorn")
        return False
    
    return True

def main():
    """主函数"""
    print("🎭 LoopcruiseTheatre AI Agent 服务启动器")
    print("=" * 50)
    
    # 检查依赖
    if not install_dependencies():
        return
    
    # 检查Ollama
    if not check_ollama():
        print("\n⚠️  可以先启动FastAPI服务进行测试，但AI功能需要Ollama")
        response = input("\n是否继续启动FastAPI服务? (y/N): ")
        if response.lower() != 'y':
            return
    
    # 启动FastAPI
    start_fastapi()

if __name__ == "__main__":
    main()
