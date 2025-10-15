#!/usr/bin/env python3
"""
协作者专用环境设置工具
仅安装数据库访问相关依赖，不包含AI模型功能
"""
import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"🐍 当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True

def install_dependencies():
    """安装最小化依赖"""
    print("📦 安装数据库访问依赖...")
    
    requirements_file = Path("database_only_requirements.txt")
    if not requirements_file.exists():
        print("❌ 找不到依赖文件: database_only_requirements.txt")
        return False
        
    try:
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖安装成功")
            return True
        else:
            print(f"❌ 依赖安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        return False

def setup_database():
    """初始化数据库"""
    print("🗃️ 初始化数据库...")
    
    try:
        # 创建数据目录
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # 检查是否有数据库文件需要导入
        exports_dir = Path("database_exports")
        if exports_dir.exists():
            db_files = list(exports_dir.glob("*.db"))
            json_files = list(exports_dir.glob("*.json"))
            
            if db_files or json_files:
                print("📥 发现可导入的数据库文件:")
                for i, file in enumerate(db_files + json_files):
                    print(f"  {i+1}. {file.name}")
                
                try:
                    choice = input("请选择要导入的文件编号（回车跳过）: ").strip()
                    if choice and choice.isdigit():
                        file_index = int(choice) - 1
                        all_files = db_files + json_files
                        if 0 <= file_index < len(all_files):
                            selected_file = all_files[file_index]
                            
                            if selected_file.suffix == '.db':
                                os.system(f'python database_export.py --action import --input "{selected_file}"')
                            else:
                                os.system(f'python database_export.py --action import-json --input "{selected_file}"')
                            
                            print("✅ 数据库导入完成")
                        else:
                            print("❌ 无效的选择")
                except:
                    print("⏭️ 跳过数据库导入")
        
        # 运行数据库初始化
        from app.database.sqlite_storage import storage
        storage.init_database()
        print("✅ 数据库初始化完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def create_start_script():
    """创建启动脚本"""
    script_content = '''#!/usr/bin/env python3
"""
协作者专用服务启动脚本
仅启动数据库API服务
"""
import subprocess
import sys
import os

def main():
    print("🎭 LoopcruiseTheatre 数据库API服务")
    print("=" * 50)
    
    # 检查依赖
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 依赖缺失: {e}")
        print("请运行: python collaborator_setup.py")
        return
    
    # 启动服务
    print("🚀 启动数据库API服务...")
    print("服务地址: http://localhost:8001")
    print("API文档: http://localhost:8001/docs")
    print("按 Ctrl+C 停止服务")
    
    os.system(f"{sys.executable} database_only_main.py")

if __name__ == "__main__":
    main()
'''
    
    with open("start_database_api.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # 给脚本添加执行权限（Unix系统）
    if os.name != 'nt':
        os.chmod("start_database_api.py", 0o755)
    
    print("✅ 启动脚本创建完成: start_database_api.py")

def main():
    print("🎭 LoopcruiseTheatre 协作者环境设置")
    print("=" * 50)
    print("📝 此工具仅安装数据库访问功能，不包含AI模型")
    print()
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装依赖
    if not install_dependencies():
        return
    
    # 设置数据库
    if not setup_database():
        return
    
    # 创建启动脚本
    create_start_script()
    
    print()
    print("🎉 协作者环境设置完成！")
    print()
    print("📋 接下来的步骤:")
    print("1. 如需导入数据库：python database_export.py --action import --input <数据库文件>")
    print("2. 启动服务：python start_database_api.py")
    print("3. 访问API文档：http://localhost:8001/docs")
    print()
    print("🔧 可用工具:")
    print("- database_export.py: 数据库导入导出")
    print("- start_database_api.py: 启动API服务")
    print("- database_only_main.py: 纯数据库API服务")

if __name__ == "__main__":
    main()
