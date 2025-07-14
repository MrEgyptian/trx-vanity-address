#!/bin/bash

# GitHub发布脚本

echo "🚀 准备发布TRX靓号生成器到GitHub"
echo "=================================="

# 检查Git状态
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ 有未提交的更改，请先提交所有更改"
    git status
    exit 1
fi

# 检查是否在main分支
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "⚠️  当前分支: $current_branch，建议在main分支发布"
    read -p "是否继续? (y/n): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 获取GitHub仓库URL
echo "📝 请输入GitHub仓库URL (例如: https://github.com/username/trx-vanity-address.git):"
read -r repo_url

if [ -z "$repo_url" ]; then
    echo "❌ 仓库URL不能为空"
    exit 1
fi

# 添加远程仓库
echo "🔗 添加远程仓库..."
git remote add origin "$repo_url"

# 推送到GitHub
echo "📤 推送到GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ 成功推送到GitHub!"
    echo ""
    echo "🎉 发布完成！"
    echo "📋 下一步操作："
    echo "1. 访问 $repo_url"
    echo "2. 创建Release标签"
    echo "3. 添加项目描述"
    echo "4. 设置项目主题"
    echo ""
    echo "🔗 项目链接: $repo_url"
else
    echo "❌ 推送失败，请检查："
    echo "1. 仓库URL是否正确"
    echo "2. 是否有推送权限"
    echo "3. 网络连接是否正常"
    exit 1
fi 