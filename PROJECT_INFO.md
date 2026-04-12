# 文件传输助手项目 - 重要信息

## GitHub账号信息
- **GitHub用户名**: `bufan528` （不是 bf410）
- **Git全局配置名**: `bufan410425-commits`
- **Git全局邮箱**: `bufan410425@gmail.com`
- **仓库地址**: https://github.com/bufan528/file-transfer-assistant

## 推送流程（牢记）

### 1. 本地提交代码
```powershell
cd "d:\文件传输助手"
git add .
git commit -m "更新说明"
```

### 2. 设置远程仓库（注意用 bufan528）
```powershell
git remote remove origin
git remote add origin https://github.com/bufan528/file-transfer-assistant.git
```

### 3. 推送
```powershell
git push -u origin main
```

## 常见问题
1. **Repository not found** → 用户名写错了，应该是 `bufan528` 不是 `bf410`
2. **Permission denied** → 仓库还没创建，先去 https://github.com/new 创建
3. **remote: Repository not found** → 确认仓库名和用户名都正确

## 项目结构
```
d:\文件传输助手\
├── main.py           # 主程序入口
├── ui.py             # UI界面
├── storage.py        # 数据存储
├── file_handler.py   # 文件处理
├── config.json       # 配置文件
├── requirements.txt  # 依赖
├── .gitignore        # Git忽略文件
└── 推送到GitHub.bat  # 一键推送脚本
```

## 打包APK
访问 https://build.flet.dev/ 用GitHub登录后选择仓库打包