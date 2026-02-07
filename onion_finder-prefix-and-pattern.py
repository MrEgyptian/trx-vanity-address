#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tor v3 .onion靓号生成器
使用GPU加速RNG + 多进程ed25519密钥派生
"""

import hashlib
import base64
import os
import time
import json
from typing import List, Tuple
from dataclasses import dataclass
from datetime import datetime
import argparse
import sys

try:
    import numpy as np
    from tqdm import tqdm
    from colorama import init, Fore, Style
    init(autoreset=True)

    # 尝试导入CuPy
    try:
        import cupy as cp
        CUPY_AVAILABLE = True
    except ImportError:
        CUPY_AVAILABLE = False
        print("⚠️  CuPy不可用，将使用CPU模式")

    from nacl.signing import SigningKey

except ImportError as e:
    print(f"缺少依赖包: {e}")
    print("请运行: pip install pynacl numpy tqdm colorama")
    sys.exit(1)

ONION_CHECKSUM_PREFIX = b".onion checksum"
ONION_VERSION = b"\x03"

# Base32 alphabet (RFC 4648)
_B32_ALPHABET = "abcdefghijklmnopqrstuvwxyz234567"


def _base32_encode(data: bytes) -> str:
    """Fast base32 encode without padding."""
    result = []
    bits = 0
    buffer = 0
    for byte in data:
        buffer = (buffer << 8) | byte
        bits += 8
        while bits >= 5:
            bits -= 5
            result.append(_B32_ALPHABET[(buffer >> bits) & 0x1F])
    if bits > 0:
        result.append(_B32_ALPHABET[(buffer << (5 - bits)) & 0x1F])
    return "".join(result)


@dataclass
class VanityOnion:
    """靓号.onion数据类"""
    onion: str
    public_key: str
    private_key_seed: str
    pattern: str = ""
    score: int = 0
    timestamp: float = 0.0


class OnionVanityGenerator:
    """Tor v3 .onion靓号生成器"""

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
            print(f"{Fore.GREEN}✓ GPU加速已启用{Style.RESET_ALL}")
            if gpu_info:
                print(f"{Fore.CYAN}GPU信息: {gpu_info}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠ GPU不可用，使用CPU模式{Style.RESET_ALL}")

    def _check_gpu_availability(self) -> bool:
        if not CUPY_AVAILABLE:
            return False
        try:
            cp.cuda.Device(0)
            return True
        except:
            return False

    def _get_gpu_info(self):
        if not CUPY_AVAILABLE:
            return None
        try:
            dev = cp.cuda.Device(0)
            attrs = dev.attributes
            props = cp.cuda.runtime.getDeviceProperties(0)
            name = props["name"].decode()
            mp = attrs.get("MultiProcessorCount", "未知")
            mem = dev.mem_info[1] // (1024 ** 2)
            cc = f"{props['major']}.{props['minor']}"
            return f"{name} | SM数: {mp} | 总内存: {mem}MB | Compute Capability: {cc}"
        except Exception as e:
            return f"无法获取GPU信息: {e}"

    @staticmethod
    def _onion_address_from_pubkey(pubkey: bytes) -> str:
        checksum = hashlib.sha3_256(ONION_CHECKSUM_PREFIX + pubkey + ONION_VERSION).digest()[:2]
        raw = pubkey + checksum + ONION_VERSION
        return _base32_encode(raw) + ".onion"

    @staticmethod
    def _seed_to_keypair(seed: bytes) -> Tuple[bytes, bytes]:
        """从seed生成公钥，返回 (pubkey, seed)"""
        sk = SigningKey(seed)
        return sk.verify_key.encode(), seed

    def _generate_seeds_gpu(self, batch_size: int) -> List[bytes]:
        if not self.use_gpu or not CUPY_AVAILABLE:
            blob = os.urandom(batch_size * 32)
            return [blob[i*32:(i+1)*32] for i in range(batch_size)]
        random_bytes = cp.random.randint(0, 256, size=(batch_size, 32), dtype=cp.uint8)
        random_bytes = cp.asnumpy(random_bytes)
        return [bytes(row) for row in random_bytes]

    def _check_vanity_pattern(self, onion: str, prefix_patterns: List[str],
                               general_patterns: List[str], case_sensitive: bool) -> Tuple[bool, str, int]:
        # Strip .onion suffix for matching
        addr = onion.replace('.onion', '')
        check = addr if case_sensitive else addr.lower()

        # Check prefix match
        prefix_match = None  # (label, score)
        for pattern in prefix_patterns:
            target = pattern if case_sensitive else pattern.lower()
            if check.startswith(target):
                prefix_match = (f"prefix:{pattern}", len(pattern) * 10)
                break

        # Check general pattern match
        general_match = None  # (label, score)
        for pattern in general_patterns:
            matched, label, score = self._matches_special_pattern(check, pattern)
            if matched:
                general_match = (label, score)
                break
            # Literal string matching: prefix > suffix > contains
            target = pattern if case_sensitive else pattern.lower()
            if check.startswith(target):
                general_match = (f"prefix:{pattern}", len(pattern) * 10)
                break
            elif check.endswith(target):
                general_match = (f"suffix:{pattern}", len(pattern) * 8)
                break
            elif target in check:
                general_match = (f"contains:{pattern}", len(pattern) * 5)
                break

        # Both specified → AND logic (both must match)
        if prefix_patterns and general_patterns:
            if prefix_match and general_match:
                label = f"{prefix_match[0]} + {general_match[0]}"
                score = prefix_match[1] + general_match[1]
                return True, label, score
            return False, "", 0

        # Only one specified → just that one needs to match
        if prefix_match:
            return True, prefix_match[0], prefix_match[1]
        if general_match:
            return True, general_match[0], general_match[1]
        return False, "", 0

    def _matches_special_pattern(self, addr: str, pattern: str) -> Tuple[bool, str, int]:
        """Handle special pattern syntax: consecutive_, ends_consecutive_, repeat_, custom_"""
        if pattern.startswith('ends_consecutive_'):
            # Tail ends with N identical chars, e.g. ends_consecutive_5
            count = int(pattern.split('_')[-1])
            tail = addr[-count:]
            if len(tail) == count and len(set(tail)) == 1:
                return True, f"ends_consecutive:{count}({tail[0]})", count * 12
            return False, "", 0

        if pattern.startswith('consecutive_'):
            # Any run of N identical chars anywhere, e.g. consecutive_5
            count = int(pattern.split('_')[1])
            if self._has_consecutive_chars(addr, count):
                run_char, run_len = self._longest_consecutive_run(addr)
                return True, f"consecutive:{run_len}({run_char})", run_len * 10
            return False, "", 0

        if pattern.startswith('repeat_'):
            # Char appears >= N times, e.g. repeat_a_6
            parts = pattern.split('_')
            char = parts[1]
            count = int(parts[2])
            actual = addr.count(char)
            if actual >= count:
                return True, f"repeat:{char}x{actual}", actual * 5
            return False, "", 0

        if pattern.startswith('custom_'):
            # Substring match, e.g. custom_dead
            custom = pattern.split('_', 1)[1]
            if custom in addr:
                return True, f"custom:{custom}", len(custom) * 5
            return False, "", 0

        return False, "", 0

    @staticmethod
    def _has_consecutive_chars(addr: str, count: int) -> bool:
        """Check if address has a run of >= count identical characters."""
        for i in range(len(addr) - count + 1):
            if len(set(addr[i:i+count])) == 1:
                return True
        return False

    @staticmethod
    def _longest_consecutive_run(addr: str) -> Tuple[str, int]:
        """Return (char, length) of the longest consecutive run."""
        best_char, best_len = addr[0], 1
        cur_char, cur_len = addr[0], 1
        for c in addr[1:]:
            if c == cur_char:
                cur_len += 1
            else:
                if cur_len > best_len:
                    best_char, best_len = cur_char, cur_len
                cur_char, cur_len = c, 1
        if cur_len > best_len:
            best_char, best_len = cur_char, cur_len
        return best_char, best_len

    def generate_batch_iter(self, batch_size: int = 10000):
        """批量生成.onion地址（迭代器）"""
        seeds = self._generate_seeds_gpu(batch_size)
        for seed in seeds:
            pk, seed_out = self._seed_to_keypair(seed)
            onion = self._onion_address_from_pubkey(pk)
            yield (
                onion,
                base64.b64encode(pk).decode("ascii"),
                base64.b64encode(seed_out).decode("ascii"),
            )

    def find_vanity_addresses(self,
                              prefix_patterns: List[str] = None,
                              general_patterns: List[str] = None,
                              max_addresses: int = 1,
                              batch_size: int = 10000,
                              case_sensitive: bool = False,
                              save_to_file: bool = True) -> List[VanityOnion]:
        """寻找靓号.onion地址"""
        prefix_patterns = prefix_patterns or []
        general_patterns = general_patterns or []
        print(f"{Fore.CYAN}开始寻找Tor v3靓号.onion地址...{Style.RESET_ALL}")
        if prefix_patterns:
            print(f"前缀模式 (仅匹配开头): {prefix_patterns}")
        if general_patterns:
            print(f"通用模式 (匹配任意位置): {general_patterns}")
        print(f"最大地址数: {max_addresses}")
        print(f"批次大小: {batch_size}")
        print(f"大小写敏感: {case_sensitive}")
        print("-" * 50)

        found_count = 0
        total_generated = 0

        with tqdm(total=None, desc="已检查", unit="addr", dynamic_ncols=True) as pbar:
            mode_msg = self.use_gpu and f"{Fore.GREEN}使用GPU生成密钥...{Style.RESET_ALL}" or f"{Fore.YELLOW}使用CPU生成密钥...{Style.RESET_ALL}"
            tqdm.write(mode_msg)
            while found_count < max_addresses:
                address_iter = self.generate_batch_iter(batch_size)

                update_interval = max(1000, batch_size // 100)
                pending_updates = 0
                for onion, pub_key_b64, seed_b64 in address_iter:
                    total_generated += 1
                    is_vanity, pattern, score = self._check_vanity_pattern(onion, prefix_patterns, general_patterns, case_sensitive)
                    pending_updates += 1

                    if is_vanity:
                        vanity = VanityOnion(
                            onion=onion,
                            public_key=pub_key_b64,
                            private_key_seed=seed_b64,
                            pattern=pattern,
                            score=score,
                            timestamp=time.time()
                        )

                        self.found_addresses.append(vanity)
                        found_count += 1

                        tqdm.write(f"\n{Fore.GREEN}找到靓号!{Style.RESET_ALL}")
                        tqdm.write(f"Onion: {Fore.YELLOW}{onion}{Style.RESET_ALL}")
                        tqdm.write(f"模式: {pattern}")
                        tqdm.write(f"分数: {score}")
                        tqdm.write(f"Public Key: {pub_key_b64}")
                        tqdm.write(f"Private Seed: {seed_b64}")
                        tqdm.write("-" * 30)

                        if found_count >= max_addresses:
                            break

                    if pending_updates >= update_interval:
                        pbar.update(pending_updates)
                        pending_updates = 0

                if pending_updates > 0:
                    pbar.update(pending_updates)

                self.stats['total_generated'] = total_generated
                self.stats['found_vanity'] = found_count

                elapsed = time.time() - self.stats['start_time']
                rate = found_count / elapsed if elapsed > 0 else 0
                remaining = max_addresses - found_count
                eta = remaining / rate if rate > 0 else 0
                pbar.set_description(f"已检查 {total_generated:,}")
                pbar.set_postfix({
                    "elapsed": self._format_duration(elapsed),
                    "eta": self._format_duration(eta),
                    "found": f"{found_count}/{max_addresses}"
                })

        if save_to_file:
            self.save_results()

        return self.found_addresses

    def save_results(self, filename: str = None):
        """保存结果到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"onion_vanity_{timestamp}.json"

        results = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'addresses': [
                {
                    'onion': addr.onion,
                    'public_key': addr.public_key,
                    'private_key_seed': addr.private_key_seed,
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

    def _format_duration(self, seconds: float) -> str:
        """格式化时长显示"""
        seconds = max(0, int(seconds))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

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


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Tor v3 .onion靓号生成器')
    parser.add_argument('--prefix', type=str, default=None,
                        help='前缀匹配 (e.g., deepx)')
    parser.add_argument('--patterns', nargs='+', default=None,
                        help='靓号模式列表 (包含匹配)')
    parser.add_argument('--max-addresses', type=int, default=1,
                        help='最大找到的靓号数量')
    parser.add_argument('--batch-size', type=int, default=10000,
                        help='每批次生成的地址数量')
    parser.add_argument('--no-gpu', action='store_true',
                        help='禁用GPU加速')
    parser.add_argument('--case-sensitive', action='store_true',
                        help='大小写敏感匹配')

    args = parser.parse_args()

    # 分离 prefix 和 patterns
    prefix_patterns = []
    general_patterns = []
    if args.prefix:
        prefix_patterns.append(args.prefix)
    if args.patterns:
        general_patterns.extend(args.patterns)
    if not prefix_patterns and not general_patterns:
        parser.error('必须指定 --prefix 或 --patterns')

    generator = OnionVanityGenerator(use_gpu=not args.no_gpu)

    try:
        found = generator.find_vanity_addresses(
            prefix_patterns=prefix_patterns,
            general_patterns=general_patterns,
            max_addresses=args.max_addresses,
            batch_size=args.batch_size,
            case_sensitive=args.case_sensitive,
            save_to_file=True
        )

        generator.print_stats()

        if found:
            print(f"\n{Fore.CYAN}找到的靓号.onion地址:{Style.RESET_ALL}")
            for i, addr in enumerate(found, 1):
                print(f"\n{i}. {Fore.YELLOW}{addr.onion}{Style.RESET_ALL}")
                print(f"   模式: {addr.pattern}")
                print(f"   分数: {addr.score}")
                print(f"   Public Key: {addr.public_key}")
                print(f"   Private Seed: {addr.private_key_seed}")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}用户中断程序{Style.RESET_ALL}")
        generator.print_stats()
    except Exception as e:
        print(f"\n{Fore.RED}错误: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
