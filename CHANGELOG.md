# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [1.0.0] - 2024-07-14

### 新增
- 🚀 初始版本发布
- 🎯 支持尾号连续相同字符靓号检测（ends_consecutive_3/4/5）
- 🔐 助记词生成和保存功能
- 🖥️ GPU加速支持（CUDA）
- 📊 实时统计信息显示
- 💾 自动保存结果到JSON文件
- 🎨 彩色终端输出
- ⚡ 批量地址生成
- 🔧 配置管理器
- 🧪 完整的测试套件

### 支持的靓号模式
- `ends_consecutive_N`: 尾号连续N个相同字符
- `consecutive_N`: 连续N个相同数字
- `repeat_X_N`: 包含至少N个数字X
- `custom_XXX`: 自定义模式

### 技术特性
- GPU加速（支持CUDA）
- 多线程处理
- 内存优化
- 错误处理
- 进度显示

## [1.2.0] - 2026-02-08

### 新增
- 🧅 Tor v3 .onion靓号生成器 (`onion_finder.py`)
  - ed25519密钥派生（PyNaCl）
  - GPU加速RNG（CuPy）
  - `--prefix` 前缀精确匹配（仅匹配开头）
  - `--patterns` 通用模式匹配（前缀/后缀/包含）
  - 支持 `consecutive_N`、`ends_consecutive_N`、`repeat_C_N`、`custom_STR` 特殊模式
  - 内置RFC 4648 base32编码（无外部依赖）
  - 结果自动保存为JSON
  - tqdm进度条 + colorama彩色输出

## [1.1.0] - 2026-02-07

### 新增
- 🔑 tronpy集成，保证地址与TronLink完全一致
- ⚡ coincurve (libsecp256k1) 快速CPU路径
- 🖥️ GPU RNG加速（CuPy生成随机种子）
- 📊 流式迭代器 + 增量tqdm进度更新

### 修复
- 🐛 地址派生使用Keccak-256替代SHA3-256（修复TronLink地址不匹配）
- 🐛 公钥哈希前去除0x04前缀
- 🐛 进度条不动问题（改为流式批量更新）
- 🐛 CuPy 11 `Device.name` AttributeError（改用 `getDeviceProperties`）

### 改进
- 🔧 `python310_conda.bat` 增强
  - PATH检查、conda环境激活检测
  - CUDA/GPU自动检测（nvidia-smi）
  - cudatoolkit版本检测并匹配CuPy版本
  - 重试逻辑（最多3次）
  - 带时间戳的日志记录（install.log）

### 依赖更新
- 新增: coincurve, tronpy, pynacl
- 移除: base32hex（已用内置实现替代）

## [未发布]

### 计划功能
- 🔄 多GPU支持
- 🌐 Web界面
- 📱 移动端支持
- 🔗 多链支持
- 📈 性能优化
- 🔐 GPU端完整加密管线（secp256k1/SHA3/RIPEMD/Base58） 