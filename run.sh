#!/bin/bash

# TRX靓号生成器快速启动脚本

echo "🚀 TRX靓号地址生成器"
echo "=================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖是否安装
echo "📦 检查依赖包..."
if ! python3 -c "import cupy, numpy, tqdm, colorama" 2>/dev/null; then
    echo "⚠️  缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖包安装失败"
        exit 1
    fi
fi

echo "✅ 依赖检查完成"

# 显示使用说明
echo ""
echo "使用方法:"
echo "1. 基本使用: python3 trx_vanity_address.py"
echo "2. 指定模式: python3 trx_vanity_address.py --patterns consecutive_4 repeat_8_3"
echo "3. 调整数量: python3 trx_vanity_address.py --max-addresses 20"
echo "4. 禁用GPU: python3 trx_vanity_address.py --no-gpu"
echo "5. 运行示例: python3 example.py"
echo ""

# 询问用户是否立即运行
read -p "是否立即运行程序? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🎯 启动TRX靓号生成器..."
    python3 trx_vanity_address.py
else
    echo "💡 您可以使用以下命令运行程序:"
    echo "   python3 trx_vanity_address.py"
fi 