# TRX靓号地址生成器 & Tor v3 .onion靓号生成器

使用GPU加速的靓号地址生成工具集，支持TRX（波场）靓号地址和Tor v3 .onion靓号域名生成。

## 功能特点

### TRX靓号生成器 (`trx_vanity_address.py`)
- 🚀 **GPU加速**: 使用CUDA GPU加速RNG，大幅提升生成速度
- 🎯 **多种靓号模式**: 支持连续相同数字、重复数字、自定义模式等
- 🔑 **tronpy集成**: 地址派生与TronLink完全一致
- ⚡ **coincurve加速**: 使用libsecp256k1实现快速CPU路径
- 📊 **实时统计**: 流式进度条、生成速率、成功率等
- 💾 **结果保存**: 自动保存找到的靓号地址到JSON文件
- 🎨 **彩色输出**: 使用颜色区分不同类型的信息

### Tor v3 .onion靓号生成器 (`onion_finder.py`)
- 🧅 **Tor v3支持**: 生成56字符的v3 .onion地址
- 🔐 **ed25519密钥**: 基于PyNaCl的ed25519密钥派生
- 🎯 **精确匹配**: `--prefix`仅匹配开头，`--patterns`支持前缀/后缀/包含
- 🖥️ **GPU RNG**: CuPy加速随机数生成
- 📊 **特殊模式**: 支持`consecutive_N`、`ends_consecutive_N`、`repeat_C_N`、`custom_STR`

## 支持的靓号模式

### TRX & Onion通用模式

| 模式 | 格式 | 说明 | 示例 |
|------|------|------|------|
| 连续相同字符 | `consecutive_N` | 任意位置连续N个相同字符 | `consecutive_5` → `aaaaa` |
| 尾号连续 | `ends_consecutive_N` | 末尾连续N个相同字符 | `ends_consecutive_4` → `...xxxx` |
| 重复字符 | `repeat_X_N` | 字符X出现至少N次 | `repeat_8_3` → 至少3个8 |
| 自定义子串 | `custom_XXX` | 包含指定子串 | `custom_888` → 包含888 |

### Onion专属模式

| 模式 | 说明 |
|------|------|
| `--prefix STR` | 地址必须以STR开头（精确前缀匹配） |
| `--patterns STR` | 字面量匹配（前缀>后缀>包含，按优先级） |

## 安装依赖

```bash
pip install -r requirements.txt
```

### 核心依赖

| 包 | 用途 |
|---|---|
| pycryptodome | Keccak-256哈希（TRX地址派生） |
| coincurve | libsecp256k1快速ECDSA（TRX） |
| tronpy | TRX地址生成（确保与TronLink一致） |
| pynacl | ed25519密钥派生（.onion） |
| cupy | GPU加速RNG（可选） |
| ecdsa | ECDSA后备方案 |
| base58 | Base58Check编码 |
| numpy, tqdm, colorama | 数组处理、进度条、彩色输出 |

### 系统要求

- Python ≥3.7, <3.11
- CUDA支持的GPU（推荐，非必需）
- 至少4GB内存

## 使用方法

### TRX靓号生成器

```bash
# 使用默认设置寻找靓号
python trx_vanity_address.py

# 指定靓号模式
python trx_vanity_address.py --patterns consecutive_4 repeat_8_3 custom_888

# 设置最大找到的靓号数量
python trx_vanity_address.py --max-addresses 20

# 调整批次大小
python trx_vanity_address.py --batch-size 20000

# 禁用GPU加速（使用CPU）
python trx_vanity_address.py --no-gpu

# 组合使用多个选项
python trx_vanity_address.py \
    --patterns consecutive_4 consecutive_5 repeat_9_3 \
    --max-addresses 15 \
    --batch-size 15000
```

### Tor v3 .onion靓号生成器

```bash
# 前缀匹配（地址必须以deep开头）
python onion_finder.py --prefix deep

# 通用模式匹配
python onion_finder.py --patterns facebook torsite

# 前缀 + 通用模式组合
python onion_finder.py --prefix deep --patterns consecutive_3

# 特殊模式
python onion_finder.py --patterns consecutive_5          # 连续5个相同字符
python onion_finder.py --patterns ends_consecutive_4     # 末尾4个相同字符
python onion_finder.py --patterns repeat_a_8             # 字符a出现≥8次
python onion_finder.py --patterns custom_dead            # 包含dead子串

# 高级选项
python onion_finder.py --prefix deep \
    --max-addresses 3 \
    --batch-size 50000 \
    --case-sensitive \
    --no-gpu
```

## 命令行参数

### TRX生成器

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--patterns` | 靓号模式列表 | `consecutive_3 consecutive_4 repeat_8_3 repeat_9_3` |
| `--max-addresses` | 最大找到的靓号数量 | 10 |
| `--batch-size` | 每批次生成的地址数量 | 10000 |
| `--no-gpu` | 禁用GPU加速 | False |
| `--output` | 输出文件名 | 自动生成 |

### Onion生成器

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--prefix` | 前缀精确匹配（仅开头） | 无 |
| `--patterns` | 通用模式列表（含特殊模式） | 无 |
| `--max-addresses` | 最大找到的靓号数量 | 1 |
| `--batch-size` | 每批次生成的地址数量 | 10000 |
| `--no-gpu` | 禁用GPU加速 | False |
| `--case-sensitive` | 大小写敏感匹配 | False |

## 输出格式

程序会生成JSON文件，包含以下信息：

### TRX输出示例

```json
{
  "timestamp": "2026-02-08T12:00:00",
  "stats": {
    "total_generated": 1000000,
    "found_vanity": 5,
    "start_time": 1704110400.0
  },
  "addresses": [
    {
      "address": "TXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "private_key": "abcdef1234567890...",
      "pattern": "consecutive_4",
      "score": 40,
      "timestamp": 1704110400.0
    }
  ]
}
```

### Onion输出示例

```json
{
  "timestamp": "2026-02-08T12:00:00",
  "stats": {
    "total_generated": 500000,
    "found_vanity": 1,
    "start_time": 1704110400.0
  },
  "addresses": [
    {
      "onion": "deepxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.onion",
      "public_key": "base64...",
      "private_key_seed": "base64...",
      "pattern": "prefix:deep",
      "score": 40,
      "timestamp": 1704110400.0
    }
  ]
}
```

## 性能优化建议

1. **GPU设置**: 确保使用支持CUDA的GPU以获得最佳性能
2. **批次大小**: 根据GPU内存调整批次大小，通常10000-50000之间
3. **模式选择**: 选择更具体的模式可以提高成功率
4. **内存管理**: 长时间运行时注意内存使用情况
5. **coincurve**: 安装coincurve可显著提升TRX生成的CPU路径性能

## 安全注意事项

- ⚠️ **私钥安全**: 生成的私钥/种子非常重要，请妥善保管
- 🔒 **离线使用**: 建议在离线环境中使用
- 💾 **备份**: 定期备份找到的靓号地址
- 🚫 **不要分享**: 不要分享私钥/种子信息

## 故障排除

### 常见问题

1. **GPU不可用**
   ```
   错误: CUDA not available
   解决: 使用 --no-gpu 参数切换到CPU模式
   ```

2. **内存不足**
   ```
   错误: Out of memory
   解决: 减小 --batch-size 参数值
   ```

3. **依赖包缺失**
   ```
   错误: ModuleNotFoundError
   解决: 运行 pip install -r requirements.txt
   ```

4. **TRX地址与TronLink不一致**
   ```
   解决: 确保已安装tronpy (pip install tronpy)
   ```

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md) 