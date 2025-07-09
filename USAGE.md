# Cogvrs 使用说明

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

### 2. 运行方式

#### 快速启动(推荐新手)
```bash
# 激活虚拟环境
source venv/bin/activate

# 快速模式 - 20个智能体，60 FPS，低质量
python3 quick_start.py --fast
```

#### 命令行参数启动
```bash
# 正常模式
python3 quick_start.py

# 自定义参数
python3 quick_start.py --agents 100 --fps 30 --quality high --world-size 120

# 查看所有参数
python3 quick_start.py --help
```

#### 交互式配置启动
```bash
# 图形界面配置(如果有tkinter)
python3 quick_start.py --interactive

# 或者直接运行配置器
python3 config_launcher.py
```

## 控制说明

### 键盘控制
- **Space** - 暂停/恢复模拟
- **M** - 切换多尺度/传统渲染
- **G** - 切换网格显示
- **T** - 切换智能体轨迹
- **C** - 切换智能体连接
- **P** - 切换感知半径
- **B** - 切换部落可视化
- **R** - 重置轨迹

### 鼠标控制
- **滚轮** - 缩放
- **左键拖拽** - 移动视角
- **右键点击** - 选择智能体

### GUI界面
- **左侧面板** - 模拟控制和统计信息
- **右侧标签页** - 部落、灾难、日志信息
- **底部状态栏** - 实时性能信息

## 功能特性

### 🧠 智能体系统
- AI智能体探索和学习
- 社会互动和繁殖
- 资源收集和竞争
- 适应性行为进化

### 🏛️ 文明系统
- 自动部落形成
- 部落间贸易和冲突
- 文化演化
- 社会结构发展

### 🌍 环境系统
- 动态资源管理
- 气候变化模拟
- 自然灾害事件
- 生态系统平衡

### 📊 可视化系统
- 多尺度渲染
- 实时性能监控
- 详细统计信息
- 交互式界面

## 配置选项

### 预设模式
- **快速测试** (10智能体) - 快速测试，运行流畅
- **正常模式** (50智能体) - 平衡的性能和功能
- **中等规模** (100智能体) - 更复杂的互动
- **大规模** (200智能体) - 完整模拟(可能较慢)

### 性能设置
- **低质量** - 最佳性能，基础视觉效果
- **正常质量** - 平衡性能和质量
- **高质量** - 最佳视觉效果，可能影响性能

### 高级设置
- **世界大小** - 50x50 到 200x200
- **资源密度** - 0.1 到 0.5
- **多尺度渲染** - 开启/关闭

## 性能优化建议

### 低端设备
```bash
python3 quick_start.py --agents 10 --fps 24 --quality low --world-size 50
```

### 中端设备
```bash
python3 quick_start.py --agents 50 --fps 30 --quality normal --world-size 100
```

### 高端设备
```bash
python3 quick_start.py --agents 200 --fps 60 --quality high --world-size 150
```

## 故障排除

### 常见问题

1. **缺少依赖包**
   ```bash
   pip install numpy pygame pygame-gui matplotlib scipy
   ```

2. **虚拟环境问题**
   ```bash
   deactivate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **性能问题**
   - 减少智能体数量
   - 降低FPS目标
   - 使用低质量模式
   - 减小世界大小

4. **显示问题**
   - 确保pygame正确安装
   - 检查显卡驱动
   - 尝试不同的渲染质量

### 日志和调试
- 日志文件位置：控制台输出
- 调试模式：查看右侧日志标签页
- 错误报告：检查终端输出

## 开发者信息

**项目**: Cogvrs - Cognitive Universe Simulation Platform  
**作者**: Ben Hsu & Claude  
**版本**: 1.0.0  
**许可**: MIT  

更多信息请查看 `Project_Plan.md` 和 `CLAUDE.md`