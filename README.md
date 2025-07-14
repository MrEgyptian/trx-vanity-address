# TRX靓号地址生成器

这是一个使用GPU加速的TRX（波场）靓号地址生成器，可以快速生成包含连续相同数字的TRX地址。

## 功能特点

- 🚀 **GPU加速**: 使用CUDA GPU加速地址生成，大幅提升生成速度
- 🎯 **多种靓号模式**: 支持连续相同数字、重复数字、自定义模式等
- 📊 **实时统计**: 显示生成速率、成功率等统计信息
- 💾 **结果保存**: 自动保存找到的靓号地址到JSON文件
- 🎨 **彩色输出**: 使用颜色区分不同类型的信息
- ⚡ **批量处理**: 支持批量生成和检查地址

## 支持的靓号模式

### 连续相同数字模式
- `consecutive_3`: 连续3个相同数字 (如: 111, 222, 333)
- `consecutive_4`: 连续4个相同数字 (如: 1111, 2222, 3333)
- `consecutive_5`: 连续5个相同数字 (如: 11111, 22222, 33333)

### 重复数字模式
- `repeat_8_3`: 包含至少3个数字8
- `repeat_9_3`: 包含至少3个数字9
- `repeat_6_4`: 包含至少4个数字6
- `repeat_7_4`: 包含至少4个数字7

### 自定义模式
- `custom_888`: 包含888
- `custom_999`: 包含999
- `custom_666`: 包含666
- `custom_777`: 包含777

## 安装依赖

```bash
pip install -r requirements.txt
```

### 系统要求

- Python 3.7+
- CUDA支持的GPU (推荐)
- 至少4GB内存

## 使用方法

### 1. 基本使用

```bash
# 使用默认设置寻找靓号
python trx_vanity_address.py

# 指定靓号模式
python trx_vanity_address.py --patterns consecutive_4 repeat_8_3 custom_888

# 设置最大找到的靓号数量
python trx_vanity_address.py --max-addresses 20

# 调整批次大小
python trx_vanity_address.py --batch-size 20000
```

### 2. 高级选项

```bash
# 禁用GPU加速（使用CPU）
python trx_vanity_address.py --no-gpu

# 指定输出文件名
python trx_vanity_address.py --output my_vanity_addresses.json

# 组合使用多个选项
python trx_vanity_address.py \
    --patterns consecutive_4 consecutive_5 repeat_9_3 \
    --max-addresses 15 \
    --batch-size 15000
```

### 3. 使用示例脚本

```bash
# 运行示例脚本
python example.py
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--patterns` | 靓号模式列表 | `consecutive_3 consecutive_4 repeat_8_3 repeat_9_3` |
| `--max-addresses` | 最大找到的靓号数量 | 10 |
| `--batch-size` | 每批次生成的地址数量 | 10000 |
| `--no-gpu` | 禁用GPU加速 | False |
| `--output` | 输出文件名 | 自动生成 |

## 输出格式

程序会生成一个JSON文件，包含以下信息：

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "stats": {
    "total_generated": 1000000,
    "found_vanity": 5,
    "start_time": 1704110400.0
  },
  "addresses": [
    {
      "address": "T123456789012345678901234567890123456789",
      "private_key": "abcdef1234567890...",
      "pattern": "consecutive_4",
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

## 安全注意事项

- ⚠️ **私钥安全**: 生成的私钥非常重要，请妥善保管
- 🔒 **离线使用**: 建议在离线环境中使用
- 💾 **备份**: 定期备份找到的靓号地址
- 🚫 **不要分享**: 不要分享私钥信息

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

### 性能调优

- 如果GPU内存较小，将批次大小设置为5000-10000
- 如果CPU性能较好，可以禁用GPU使用CPU模式
- 根据目标靓号难度调整最大地址数量

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

- v1.0.0: 初始版本，支持基本靓号生成功能
- 支持GPU加速和多种靓号模式
- 添加统计信息和结果保存功能 