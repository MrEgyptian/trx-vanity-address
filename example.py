#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRX靓号生成器使用示例
"""

from trx_vanity_address import TRXVanityGenerator
import json

def main():
    """示例：寻找包含连续相同数字的TRX靓号"""
    
    # 创建生成器
    generator = TRXVanityGenerator(use_gpu=True)
    
    # 定义靓号模式
    patterns = [
        'consecutive_3',  # 连续3个相同数字
        'consecutive_4',  # 连续4个相同数字
        'repeat_8_3',     # 包含至少3个数字8
        'repeat_9_3',     # 包含至少3个数字9
        'custom_888',     # 包含888
        'custom_999'      # 包含999
    ]
    
    print("开始寻找TRX靓号地址...")
    print("目标模式:")
    for pattern in patterns:
        print(f"  - {pattern}")
    print()
    
    # 寻找靓号地址
    found_addresses = generator.find_vanity_addresses(
        patterns=patterns,
        max_addresses=5,      # 找到5个靓号就停止
        batch_size=5000,      # 每批次生成5000个地址
        save_to_file=True
    )
    
    # 显示结果
    if found_addresses:
        print("\n找到的靓号地址:")
        for i, addr in enumerate(found_addresses, 1):
            print(f"\n{i}. 地址: {addr.address}")
            print(f"   模式: {addr.pattern}")
            print(f"   分数: {addr.score}")
            print(f"   私钥: {addr.private_key}")
    else:
        print("未找到符合条件的靓号地址")
    
    # 打印统计信息
    generator.print_stats()

if __name__ == "__main__":
    main() 