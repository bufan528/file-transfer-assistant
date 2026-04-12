@echo off
chcp 65001 >nul
echo ========================================
echo   文件传输助手 - GitHub 一键推送工具
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查Git状态...
git status >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Git仓库，请确保在项目目录下运行此脚本
    pause
    exit /b 1
)

echo [2/3] 移除旧远程地址并添加新地址...
git remote remove origin 2>nul
git remote add origin https://github.com/bf410/file-transfer-assistant.git

echo.
echo [3/3] 推送到GitHub...
echo.
git push -u origin main

if errorlevel 1 (
    echo.
    echo ============================================
    echo   推送失败！请检查以下事项：
    echo   1. 确保已在 https://github.com/new 创建了 file-transfer-assistant 仓库
    echo   2. 确保你的Git已登录GitHub账号
    echo ============================================
) else (
    echo.
    echo ============================================
    echo   推送成功！
    echo   仓库地址: https://github.com/bf410/file-transfer-assistant
    echo ============================================
)

pause