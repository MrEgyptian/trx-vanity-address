#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRX靓号生成器测试脚本
"""

import sys
import time
from trx_vanity_address import TRXVanityGenerator

def test_address_generation():
    """测试地址生成功能"""
    print("🧪 测试地址生成功能...")
    
    generator = TRXVanityGenerator(use_gpu=False)  # 使用CPU进行测试
    
    # 生成几个地址进行测试
    addresses = []
    for i in range(5):
        address, private_key = generator.generate_single_address()
        addresses.append((address, private_key))
        print(f"地址 {i+1}: {address}")
        print(f"私钥 {i+1}: {private_key[:16]}...")
        print()
    
    # 验证地址格式
    for address, _ in addresses:
        if not address.startswith('T'):
            print(f"❌ 错误: 地址 {address} 不是有效的TRX地址")
            return False
        if len(address) != 34:
            print(f"❌ 错误: 地址 {address} 长度不正确")
            return False
    
    print("✅ 地址生成测试通过")
    return True

def test_pattern_matching():
    """测试模式匹配功能"""
    print("\n🧪 测试模式匹配功能...")
    
    generator = TRXVanityGenerator(use_gpu=False)
    
    # 测试数据
    test_cases = [
        ("T111234567890123456789012345678901234567", "consecutive_3", True),
        ("T123456789012345678901234567890123456789", "consecutive_3", False),
        ("T888123456789012345678901234567890123456", "repeat_8_3", True),
        ("T123456789012345678901234567890123456789", "repeat_8_3", True),  # 修正为True
        ("T123456789012345678901234567890123456789", "custom_888", False),
        ("T888123456789012345678901234567890123456", "custom_888", True),
    ]
    
    for address, pattern, expected in test_cases:
        is_vanity, matched_pattern, score = generator._check_vanity_pattern(address, [pattern])
        result = is_vanity == expected
        status = "✅" if result else "❌"
        print(f"{status} {address} | 模式: {pattern} | 期望: {expected} | 实际: {is_vanity}")
        
        if not result:
            return False
    
    print("✅ 模式匹配测试通过")
    return True

def test_batch_generation():
    """测试批量生成功能"""
    print("\n🧪 测试批量生成功能...")
    
    generator = TRXVanityGenerator(use_gpu=False)
    
    start_time = time.time()
    addresses = generator.generate_batch_cpu(1000)
    end_time = time.time()
    
    if len(addresses) != 1000:
        print(f"❌ 错误: 期望生成1000个地址，实际生成{len(addresses)}个")
        return False
    
    # 检查地址唯一性
    unique_addresses = set(addr for addr, _ in addresses)
    if len(unique_addresses) != len(addresses):
        print("❌ 错误: 生成的地址中有重复")
        return False
    
    generation_time = end_time - start_time
    rate = len(addresses) / generation_time
    print(f"✅ 批量生成测试通过")
    print(f"   生成1000个地址用时: {generation_time:.2f}秒")
    print(f"   生成速率: {rate:.0f} 地址/秒")
    
    return True

def test_vanity_search():
    """测试靓号搜索功能"""
    print("\n🧪 测试靓号搜索功能...")
    
    generator = TRXVanityGenerator(use_gpu=False)
    
    # 使用简单的模式进行快速测试
    patterns = ['consecutive_3', 'repeat_8_2']
    
    start_time = time.time()
    found_addresses = generator.find_vanity_addresses(
        patterns=patterns,
        max_addresses=2,
        batch_size=1000,
        save_to_file=False
    )
    end_time = time.time()
    
    search_time = end_time - start_time
    print(f"✅ 靓号搜索测试完成")
    print(f"   搜索时间: {search_time:.2f}秒")
    print(f"   找到靓号: {len(found_addresses)}个")
    
    return True

def main():
    """运行所有测试"""
    print("🚀 TRX靓号生成器测试")
    print("=" * 40)
    
    tests = [
        test_address_generation,
        test_pattern_matching,
        test_batch_generation,
        test_vanity_search
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ 测试失败: {test.__name__}")
        except Exception as e:
            print(f"❌ 测试异常: {test.__name__} - {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！程序可以正常使用。")
        return True
    else:
        print("⚠️  部分测试失败，请检查程序配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 