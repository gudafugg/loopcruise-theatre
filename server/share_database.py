#!/usr/bin/env python3
"""
数据库分享工具 - 为协作者准备数据库文件
"""
import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_collaborator_package():
    """创建协作者专用包"""
    print("🎭 准备协作者数据库访问包...")
    
    # 创建临时目录
    package_dir = Path("collaborator_package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # 复制必要文件
    files_to_copy = [
        "database_only_requirements.txt",
        "collaborator_setup.py", 
        "database_only_main.py",
        "database_export.py",
        "app/"  # 整个app目录
    ]
    
    print("📁 复制必要文件...")
    for file in files_to_copy:
        src = Path(file)
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, package_dir / src.name)
            else:
                shutil.copy2(src, package_dir / src.name) 
            print("  ✅ {}".format(file))
        else:
            print("  ❌ 缺少文件: {}".format(file))
    
    # 导出数据库
    print("🗃️ 导出数据库...")
    db_path = Path("data/conversations.db")
    if db_path.exists():
        # 创建数据目录
        (package_dir / "database_exports").mkdir(exist_ok=True)
        
        # 导出数据库文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_db = package_dir / "database_exports" / "conversations_shared_{}.db".format(timestamp)
        shutil.copy2(db_path, exported_db)
        print("  ✅ 数据库已导出: {}".format(exported_db.name))
        
        # 也导出JSON格式
        os.system('python database_export.py --action export-json --output "{}/database_exports/conversations_shared_{}.json"'.format(package_dir, timestamp))
        print("  ✅ JSON数据已导出: conversations_shared_{}.json".format(timestamp))
    else:
        print("  ⚠️ 未找到数据库文件，将创建空数据库结构")
    
    # 创建README文件
    readme_content = """# 协作者数据库访问包

此包包含访问 LoopcruiseTheatre 数据库所需的所有文件。

## 🚀 快速开始

1. **安装环境**
   ```bash
   python collaborator_setup.py
   ```

2. **启动服务**
   ```bash
   python start_database_api.py
   ```

3. **访问API**
   - 服务地址: http://localhost:8001
   - API文档: http://localhost:8001/docs

## 📁 文件说明

- `collaborator_setup.py` - 环境安装脚本
- `database_only_main.py` - 数据库API服务
- `database_export.py` - 数据导入导出工具
- `database_only_requirements.txt` - 精简依赖列表
- `app/` - 核心应用代码
- `database_exports/` - 共享的数据库文件

## 📊 数据访问

导入数据库文件：
```bash
python database_export.py --action import --input database_exports/conversations_shared_*.db
```

查看完整指南：参考项目根目录的 `COLLABORATOR_GUIDE.md`

---
生成时间: {}
"""
    
    with open(package_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    print("📝 README.md 已创建")
    
    # 创建压缩包
    print("📦 创建压缩包...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = "collaborator_database_package_{}.zip".format(timestamp)
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(package_dir)
                zipf.write(file_path, arc_name)
    
    # 清理临时目录
    shutil.rmtree(package_dir)
    
    print("✅ 协作者包已创建: {}".format(zip_name))
    print()
    print("🎯 发送给协作者的步骤:")
    print("1. 发送文件: {}".format(zip_name))
    print("2. 解压缩后运行: python collaborator_setup.py")
    print("3. 启动服务: python start_database_api.py")
    print()
    
    return zip_name

def main():
    import sys
    
    print("🤝 协作者数据库分享工具")
    print("=" * 50)
    
    if not Path("data/conversations.db").exists():
        print("⚠️ 提醒: 当前没有数据库文件，将创建空的数据库结构")
        print("如果你希望分享现有数据，请先启动主服务生成一些对话数据")
        print()
    
    # 支持命令行参数 --yes 或 -y 自动确认
    if len(sys.argv) > 1 and sys.argv[1] in ['--yes', '-y']:
        choice = 'y'
    else:
        try:
            choice = input("是否继续创建协作者包? (y/N): ")
        except EOFError:
            choice = 'y'  # 非交互环境默认继续
    
    if choice.lower() != 'y':
        print("已取消")
        return
    
    package_name = create_collaborator_package()
    
    print("🎉 完成！协作者现在可以:")
    print("✅ 独立运行数据库API服务")
    print("✅ 访问和搜索对话历史")
    print("✅ 导入导出数据库文件")
    print("✅ 在自己的AI Agent中集成数据访问")

if __name__ == "__main__":
    main()
