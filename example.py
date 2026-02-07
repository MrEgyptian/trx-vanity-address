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
        'consecutive_5',  # 连续5个相同数字
        'consecutive_6',  # 连续6个相同数字
        'consecutive_8',  # 连续8个相同数字
        'consecutive_9',  # 连续9个相同数字
        'consecutive_10',  # 连续10个相同数字
        'consecutive_7',  # 连续7个相同数字
        'custom_ahmed',      # 包含ahmed
        'custom_MrEgyptian',    # 包含MrEgyptian
        'custom_MrAhmed',       # 包含MrAhmed
        'custom_Egyptian',     # 包含Egyptian
        'custom_Ahmed',       # 包含Ahmed
        'custom_Pharaoh',       # 包含Pharaoh
        'custom_Queen',        # 包含Queen
        'custom_mrEgyptian',       # 包含mrEgyptian
        'custom_mrAhmed',         # 包含mrAhmed
        'custom_egyptian',       # 包含egyptian
        'custom_ahmed',         # 包含ahmed
        'custom_pharaoh',       # 包含pharaoh
        'custom_queen',        # 包含queen
        'custom_mregyptian',       # 包含mregyptian
        'custom_mrahmed',         # 包含mrahmed
        'custom_egyptian',       # 包含egyptian
        'custom_egypt',         # 包含egypt
        
        
    ]
    
    print("开始寻找TRX靓号地址...")
    print("目标模式:")
    for pattern in patterns:
        print(f"  - {pattern}")
    print()
    
    # 寻找靓号地址
    found_addresses = generator.find_vanity_addresses(
        patterns=patterns,
        max_addresses=20,      # 找到5个靓号就停止
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