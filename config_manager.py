#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRX靓号生成器配置管理器
"""

import json
import os
from typing import Dict, List, Any

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"警告: 无法加载配置文件 {self.config_file}: {e}")
        
        # 返回默认配置
        return {
            "patterns": {
                "consecutive_3": "连续3个相同数字",
                "consecutive_4": "连续4个相同数字",
                "consecutive_5": "连续5个相同数字",
                "repeat_8_3": "包含至少3个数字8",
                "repeat_9_3": "包含至少3个数字9",
                "repeat_6_4": "包含至少4个数字6",
                "repeat_7_4": "包含至少4个数字7",
                "custom_888": "包含888",
                "custom_999": "包含999",
                "custom_666": "包含666",
                "custom_777": "包含777"
            },
            "default_settings": {
                "max_addresses": 10,
                "batch_size": 10000,
                "use_gpu": True,
                "save_results": True
            },
            "advanced_patterns": {
                "palindrome": "回文数字",
                "ascending": "递增数字",
                "descending": "递减数字"
            }
        }
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已保存到 {self.config_file}")
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
    
    def get_patterns(self) -> Dict[str, str]:
        """获取所有模式"""
        return self.config.get("patterns", {})
    
    def get_pattern_description(self, pattern: str) -> str:
        """获取模式描述"""
        patterns = self.get_patterns()
        return patterns.get(pattern, "未知模式")
    
    def add_pattern(self, pattern: str, description: str):
        """添加新模式"""
        self.config["patterns"][pattern] = description
        self.save_config()
        print(f"✅ 已添加模式: {pattern} - {description}")
    
    def remove_pattern(self, pattern: str):
        """删除模式"""
        if pattern in self.config["patterns"]:
            del self.config["patterns"][pattern]
            self.save_config()
            print(f"✅ 已删除模式: {pattern}")
        else:
            print(f"❌ 模式 {pattern} 不存在")
    
    def get_default_settings(self) -> Dict[str, Any]:
        """获取默认设置"""
        return self.config.get("default_settings", {})
    
    def update_default_settings(self, settings: Dict[str, Any]):
        """更新默认设置"""
        self.config["default_settings"].update(settings)
        self.save_config()
        print("✅ 默认设置已更新")
    
    def list_patterns(self):
        """列出所有模式"""
        patterns = self.get_patterns()
        print("\n📋 可用的靓号模式:")
        print("-" * 50)
        
        for pattern, description in patterns.items():
            print(f"  {pattern:<20} - {description}")
        
        print(f"\n总计: {len(patterns)} 个模式")
    
    def validate_pattern(self, pattern: str) -> bool:
        """验证模式格式"""
        if pattern.startswith('ends_consecutive_'):
            try:
                count = int(pattern.split('_')[-1])
                return 1 <= count <= 10
            except:
                return False
        if pattern.startswith('consecutive_'):
            try:
                count = int(pattern.split('_')[1])
                return 1 <= count <= 10
            except:
                return False
        elif pattern.startswith('repeat_'):
            try:
                parts = pattern.split('_')
                if len(parts) != 3:
                    return False
                digit = parts[1]
                count = int(parts[2])
                return digit.isdigit() and 0 <= int(digit) <= 9 and 1 <= count <= 10
            except:
                return False
        elif pattern.startswith('custom_'):
            return len(pattern.split('_')[1]) > 0
        else:
            return len(pattern) > 0
    
    def create_custom_pattern(self, name: str, digits: str, count: int):
        """创建自定义重复数字模式"""
        if not digits.isdigit() or len(digits) != 1:
            print("❌ 错误: 数字必须是单个0-9的数字")
            return
        
        digit = int(digits)
        pattern = f"repeat_{digit}_{count}"
        description = f"包含至少{count}个数字{digit}"
        
        self.add_pattern(pattern, description)
    
    def create_consecutive_pattern(self, count: int):
        """创建连续数字模式"""
        if not 1 <= count <= 10:
            print("❌ 错误: 连续数字数量必须在1-10之间")
            return
        
        pattern = f"consecutive_{count}"
        description = f"连续{count}个相同数字"
        
        self.add_pattern(pattern, description)

    def create_ends_consecutive_pattern(self, count: int):
        """创建尾号连续字符模式"""
        if not 1 <= count <= 10:
            print("❌ 错误: 尾号连续字符数量必须在1-10之间")
            return
        pattern = f"ends_consecutive_{count}"
        description = f"尾号连续{count}个相同字符"
        self.add_pattern(pattern, description)

def main():
    """配置管理器主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TRX靓号生成器配置管理器')
    parser.add_argument('--list', action='store_true', help='列出所有模式')
    parser.add_argument('--add', nargs=2, metavar=('PATTERN', 'DESCRIPTION'), help='添加新模式')
    parser.add_argument('--remove', metavar='PATTERN', help='删除模式')
    parser.add_argument('--custom-repeat', nargs=2, metavar=('DIGIT', 'COUNT'), help='创建重复数字模式')
    parser.add_argument('--consecutive', type=int, metavar='COUNT', help='创建连续数字模式')
    parser.add_argument('--ends-consecutive', type=int, metavar='COUNT', help='创建尾号连续字符模式')
    
    args = parser.parse_args()
    
    config = ConfigManager()
    
    if args.list:
        config.list_patterns()
    elif args.add:
        pattern, description = args.add
        if config.validate_pattern(pattern):
            config.add_pattern(pattern, description)
        else:
            print(f"❌ 无效的模式格式: {pattern}")
    elif args.remove:
        config.remove_pattern(args.remove)
    elif args.custom_repeat:
        digit, count = args.custom_repeat
        try:
            count = int(count)
            config.create_custom_pattern(f"custom_{digit}", digit, count)
        except ValueError:
            print("❌ 错误: 数量必须是整数")
    elif args.consecutive:
        config.create_consecutive_pattern(args.consecutive)
    elif args.ends_consecutive:
        config.create_ends_consecutive_pattern(args.ends_consecutive)
    else:
        print("TRX靓号生成器配置管理器")
        print("=" * 40)
        print("使用方法:")
        print("  python config_manager.py --list                    # 列出所有模式")
        print("  python config_manager.py --add PATTERN DESC        # 添加新模式")
        print("  python config_manager.py --remove PATTERN          # 删除模式")
        print("  python config_manager.py --custom-repeat DIGIT COUNT  # 创建重复数字模式")
        print("  python config_manager.py --consecutive COUNT       # 创建连续数字模式")
        print("  python config_manager.py --ends-consecutive COUNT    # 创建尾号连续字符模式")

if __name__ == "__main__":
    main() 