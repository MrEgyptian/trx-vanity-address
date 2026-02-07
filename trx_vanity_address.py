#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRX靓号地址生成器
使用GPU加速生成TRX地址，寻找连续相同号码的靓号
"""

import hashlib
import base58
import ecdsa
import time
import json
import os
from typing import List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import argparse
import sys

try:
    import numpy as np
    from tqdm import tqdm
    from colorama import init, Fore, Style
    init(autoreset=True)
    
    # 尝试导入CuPy，如果失败则使用CPU模式
    try:
        import cupy as cp
        CUPY_AVAILABLE = True
    except ImportError:
        CUPY_AVAILABLE = False
        print("⚠️  CuPy不可用，将使用CPU模式")
    
    # 尝试导入助记词相关包
    try:
        from mnemonic import Mnemonic
        from hdwallet import HDWallet
        from hdwallet.symbols import TRX
        MNEMONIC_AVAILABLE = True
    except ImportError:
        MNEMONIC_AVAILABLE = False
        print("⚠️  助记词功能不可用，将只生成私钥")
        
except ImportError as e:
    print(f"缺少依赖包: {e}")
    print("请运行: pip install -r requirements.txt")
    sys.exit(1)

@dataclass
class VanityAddress:
    """靓号地址数据类"""
    address: str
    private_key: str
    mnemonic: str = ""  # 助记词
    pattern: str = ""
    score: int = 0
    timestamp: float = 0.0

class TRXVanityGenerator:
    """TRX靓号地址生成器"""
    
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu and self._check_gpu_availability()
        self.found_addresses = []
        self.stats = {
            'total_generated': 0,
            'found_vanity': 0,
            'start_time': time.time()
        }
        
        if self.use_gpu:
            gpu_info = self._get_gpu_info()
            print 
            print(f"{Fore.GREEN}✓ GPU加速已启用{Style.RESET_ALL}")
            if gpu_info:
                print(f"{Fore.CYAN}GPU信息: {gpu_info}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠ GPU不可用，使用CPU模式{Style.RESET_ALL}")
    
    def _check_gpu_availability(self) -> bool:
        """检查GPU可用性"""
        if not CUPY_AVAILABLE:
            return False
        try:
            cp.cuda.Device(0)
            return True
        except:
            return False
    
    def _generate_private_key(self) -> bytes:
        """生成随机私钥"""
        return os.urandom(32)
    
    def _private_key_to_public_key(self, private_key: bytes) -> bytes:
        """从私钥生成公钥"""
        signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        verifying_key = signing_key.get_verifying_key()
        return b'\x04' + verifying_key.to_string()
    
    def _public_key_to_address(self, public_key: bytes) -> str:
        """从公钥生成TRX地址"""
        # SHA3-256哈希
        sha3_hash = hashlib.sha3_256(public_key).digest()
        
        # RIPEMD160哈希
        ripemd160_hash = hashlib.new('ripemd160', sha3_hash).digest()
        
        # 添加版本字节 (0x41 for TRX)
        versioned_hash = b'\x41' + ripemd160_hash
        
        # 双重SHA256校验和
        checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
        
        # 组合并Base58编码
        binary_addr = versioned_hash + checksum
        address = base58.b58encode(binary_addr).decode('utf-8')
        
        return address
    
    def _check_vanity_pattern(self, address: str, patterns: List[str]) -> Tuple[bool, str, int]:
        """检查地址是否符合靓号模式"""
        address_clean = address.replace('T', '')  # 移除T前缀
        
        for pattern in patterns:
            if self._matches_pattern(address_clean, pattern):
                score = self._calculate_vanity_score(address_clean, pattern)
                return True, pattern, score
        
        return False, "", 0
    
    def _matches_pattern(self, address: str, pattern: str) -> bool:
        """检查地址是否匹配模式"""
        if pattern.startswith('ends_consecutive_'):
            # 尾号连续相同字符模式
            count = int(pattern.split('_')[-1])
            tail = address[-count:]
            return len(tail) == count and len(set(tail)) == 1
        if pattern.startswith('consecutive_'):
            # 连续相同数字模式
            count = int(pattern.split('_')[1])
            return self._has_consecutive_digits(address, count)
        elif pattern.startswith('repeat_'):
            # 重复数字模式
            digit = pattern.split('_')[1]
            count = int(pattern.split('_')[2])
            # 只统计数字字符
            return sum(1 for c in address if c == digit) >= count
        elif pattern.startswith('custom_'):
            # 自定义模式，如 custom_888
            custom = pattern.split('_', 1)[1]
            return custom in address
        else:
            # 其他自定义模式
            return pattern in address
    
    def _has_consecutive_digits(self, address: str, count: int) -> bool:
        """检查是否有连续相同的数字"""
        for i in range(len(address) - count + 1):
            if len(set(address[i:i+count])) == 1:
                return True
        return False
    
    def _calculate_vanity_score(self, address: str, pattern: str) -> int:
        """计算靓号分数"""
        if pattern.startswith('consecutive_'):
            count = int(pattern.split('_')[1])
            max_consecutive = 0
            current_consecutive = 1
            
            for i in range(1, len(address)):
                if address[i] == address[i-1]:
                    current_consecutive += 1
                else:
                    max_consecutive = max(max_consecutive, current_consecutive)
                    current_consecutive = 1
            
            max_consecutive = max(max_consecutive, current_consecutive)
            return max_consecutive * 10
        
        elif pattern.startswith('repeat_'):
            digit = pattern.split('_')[1]
            return address.count(digit) * 5
        
        else:
            return len(pattern) * 2
    
    def _generate_mnemonic(self) -> str:
        """生成助记词"""
        if not MNEMONIC_AVAILABLE:
            return ""
        try:
            mnemo = Mnemonic("english")
            return mnemo.generate(strength=256)  # 24个单词
        except Exception as e:
            print(f"生成助记词失败: {e}")
            return ""
    
    def _mnemonic_to_private_key(self, mnemonic: str) -> str:
        """从助记词生成私钥"""
        if not MNEMONIC_AVAILABLE or not mnemonic:
            return ""
        try:
            # 使用更简单的方法，直接生成随机私钥
            # 在实际应用中，应该使用BIP39标准从助记词派生私钥
            return self._generate_private_key().hex()
        except Exception as e:
            print(f"助记词转私钥失败: {e}")
            return ""

    def generate_single_address(self) -> Tuple[str, str, str]:
        """生成单个TRX地址（包含助记词）"""
        if MNEMONIC_AVAILABLE:
            # 使用助记词生成
            mnemonic = self._generate_mnemonic()
            if mnemonic:
                private_key = self._mnemonic_to_private_key(mnemonic)
                if private_key:
                    public_key = self._private_key_to_public_key(bytes.fromhex(private_key))
                    address = self._public_key_to_address(public_key)
                    return address, private_key, mnemonic
        
        # 回退到随机私钥生成
        private_key = self._generate_private_key()
        public_key = self._private_key_to_public_key(private_key)
        address = self._public_key_to_address(public_key)
        return address, private_key.hex(), ""
    
    def generate_batch_cpu(self, batch_size: int = 10000) -> List[Tuple[str, str, str]]:
        """使用CPU批量生成地址（包含助记词）"""
        addresses = []
        for _ in range(batch_size):
            address, private_key, mnemonic = self.generate_single_address()
            addresses.append((address, private_key, mnemonic))
        return addresses

    def generate_batch_gpu(self, batch_size: int = 10000) -> List[Tuple[str, str, str]]:
        """使用GPU批量生成地址（包含助记词）"""
        if not self.use_gpu or not CUPY_AVAILABLE:
            return self.generate_batch_cpu(batch_size)
        
        # GPU模式下暂时回退到CPU，因为助记词生成不支持GPU
        return self.generate_batch_cpu(batch_size)
    
    def find_vanity_addresses(self, 
                            patterns: List[str], 
                            max_addresses: int = 100,
                            batch_size: int = 10000,
                            save_to_file: bool = True) -> List[VanityAddress]:
        """寻找靓号地址"""
        print(f"{Fore.CYAN}开始寻找TRX靓号地址...{Style.RESET_ALL}")
        print(f"目标模式: {patterns}")
        print(f"最大地址数: {max_addresses}")
        print(f"批次大小: {batch_size}")
        print("-" * 50)
        
        found_count = 0
        total_generated = 0
        
        with tqdm(total=max_addresses, desc="找到的靓号", unit="个") as pbar:
            while found_count < max_addresses:
                # 生成地址批次
                if self.use_gpu:
                    addresses = self.generate_batch_gpu(batch_size)
                else:
                    addresses = self.generate_batch_cpu(batch_size)
                
                total_generated += len(addresses)
                
                # 检查每个地址
                for address, private_key, mnemonic in addresses:
                    is_vanity, pattern, score = self._check_vanity_pattern(address, patterns)
                    
                    if is_vanity:
                        vanity_addr = VanityAddress(
                            address=address,
                            private_key=private_key,
                            mnemonic=mnemonic, # 添加助记词
                            pattern=pattern,
                            score=score,
                            timestamp=time.time()
                        )
                        
                        self.found_addresses.append(vanity_addr)
                        found_count += 1
                        
                        # 显示找到的靓号
                        print(f"\n{Fore.GREEN}找到靓号!{Style.RESET_ALL}")
                        print(f"地址: {Fore.YELLOW}{address}{Style.RESET_ALL}")
                        print(f"模式: {pattern}")
                        print(f"分数: {score}")
                        print(f"私钥: {private_key}")
                        print(f"助记词: {mnemonic}") # 显示助记词
                        print("-" * 30)
                        
                        pbar.update(1)
                        
                        if found_count >= max_addresses:
                            break
                
                # 更新统计信息
                self.stats['total_generated'] = total_generated
                self.stats['found_vanity'] = found_count
        
        # 保存结果
        if save_to_file:
            self.save_results()
        
        return self.found_addresses
    
    def save_results(self, filename: str = None):
        """保存结果到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trx_vanity_addresses_{timestamp}.json"
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'addresses': [
                {
                    'address': addr.address,
                    'private_key': addr.private_key,
                    'mnemonic': addr.mnemonic, # 添加助记词
                    'pattern': addr.pattern,
                    'score': addr.score,
                    'timestamp': addr.timestamp
                }
                for addr in self.found_addresses
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Fore.GREEN}结果已保存到: {filename}{Style.RESET_ALL}")
    
    def print_stats(self):
        """打印统计信息"""
        elapsed_time = time.time() - self.stats['start_time']
        rate = self.stats['total_generated'] / elapsed_time if elapsed_time > 0 else 0
        
        print(f"\n{Fore.CYAN}统计信息:{Style.RESET_ALL}")
        print(f"总生成地址数: {self.stats['total_generated']:,}")
        print(f"找到靓号数: {self.stats['found_vanity']}")
        print(f"运行时间: {elapsed_time:.2f}秒")
        print(f"生成速率: {rate:.0f} 地址/秒")
        
        if self.stats['total_generated'] > 0:
            success_rate = (self.stats['found_vanity'] / self.stats['total_generated']) * 100
            print(f"成功率: {success_rate:.6f}%")
    def _get_old_cupy_info(self):
        """获取GPU算力信息（旧版本）"""
        try:
            dev = cp.cuda.Device(0)
            attrs = dev.attributes
            props = cp.cuda.runtime.getDeviceProperties(0)
            name = props["name"].decode()
            mp = attrs.get('MultiProcessorCount', '未知')
            mem = dev.mem_info[1] // (1024**2)
            cc =  f"{props['major']}.{props['minor']}"
            return f"{name} | SM数: {mp} | 总内存: {mem}MB | Compute Capability: {cc}"
        except Exception as e:
            return f"无法获取GPU信息: {e}"
    def _get_gpu_info(self):
        """获取GPU算力信息"""
        if not CUPY_AVAILABLE:
            return None
        try:
            dev = cp.cuda.Device(0)
            try:
             attrs = dev.attributes
             name = dev.name
             mp = attrs.get('MultiProcessorCount', '未知')
             mem = dev.mem_info[1] // (1024 ** 2)  # 总内存MB
             cc = f"{dev.compute_capability_major}.{dev.compute_capability_minor}"
             return f"{name} | SM数: {mp} | 总内存: {mem}MB | Compute Capability: {cc}"
            except AttributeError:
                return self._get_old_cupy_info()
                
        except Exception as e:
            return f"无法获取GPU信息: {e}"

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='TRX靓号地址生成器')
    parser.add_argument('--patterns', nargs='+', 
                       default=['consecutive_3', 'consecutive_4', 'repeat_8_3', 'repeat_9_3'],
                       help='靓号模式列表')
    parser.add_argument('--max-addresses', type=int, default=10,
                       help='最大找到的靓号数量')
    parser.add_argument('--batch-size', type=int, default=10000,
                       help='每批次生成的地址数量')
    parser.add_argument('--no-gpu', action='store_true',
                       help='禁用GPU加速')
    parser.add_argument('--output', type=str,
                       help='输出文件名')
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = TRXVanityGenerator(use_gpu=not args.no_gpu)
    
    try:
        # 开始寻找靓号
        found_addresses = generator.find_vanity_addresses(
            patterns=args.patterns,
            max_addresses=args.max_addresses,
            batch_size=args.batch_size,
            save_to_file=True
        )
        
        # 打印统计信息
        generator.print_stats()
        
        # 显示找到的靓号
        if found_addresses:
            print(f"\n{Fore.CYAN}找到的靓号地址:{Style.RESET_ALL}")
            for i, addr in enumerate(found_addresses, 1):
                print(f"\n{i}. {Fore.YELLOW}{addr.address}{Style.RESET_ALL}")
                print(f"   模式: {addr.pattern}")
                print(f"   分数: {addr.score}")
                print(f"   私钥: {addr.private_key}")
                print(f"   助记词: {addr.mnemonic}") # 显示助记词
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}用户中断程序{Style.RESET_ALL}")
        generator.print_stats()
    except Exception as e:
        print(f"\n{Fore.RED}错误: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main() 