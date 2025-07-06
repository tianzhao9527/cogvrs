#!/usr/bin/env python3
"""
Cogvrs Enhanced Launcher
增强版Cogvrs启动器 - 包含所有优化功能

Features:
- 优化的屏幕渲染（减少闪烁）
- 彩色边栏状态显示
- 实时数据收集
- 自动HTML报告生成
- 详细状态输出

Author: Ben Hsu & Claude
"""

import sys
import os
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_banner():
    """打印启动横幅"""
    print("=" * 80)
    print("🧠 COGVRS - COGNITIVE UNIVERSE SIMULATION PLATFORM")
    print("=" * 80)
    print("🔬 数字宇宙实验室 | AI意识探索 | 版本 2.0 Enhanced")
    print("👨‍💻 作者: Ben Hsu & Claude")
    print("🌐 网站: cogvrs.com")
    print("📅 启动时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 80)
    print()

def print_features():
    """打印功能介绍"""
    print("🚀 ENHANCED FEATURES:")
    print("   ✅ 优化渲染引擎 - 减少屏幕闪烁")
    print("   ✅ 彩色状态显示 - 实时边栏监控")
    print("   ✅ 智能体分析 - 行为模式识别")
    print("   ✅ 数据收集系统 - 完整会话记录")
    print("   ✅ HTML报告生成 - 可视化分析结果")
    print("   ✅ 性能监控 - 系统状态跟踪")
    print()
    
    print("🧠 AI AGENTS CAPABILITIES:")
    print("   • 神经网络决策系统 (Multi-layer Neural Networks)")
    print("   • 记忆系统 (Working, Long-term, Spatial Memory)")
    print("   • 行为驱动引擎 (Motivation-based Behavior)")
    print("   • 社交互动网络 (Social Interaction Networks)")
    print("   • 生殖进化机制 (Reproduction & Evolution)")
    print("   • 学习适应能力 (Learning & Adaptation)")
    print()

def print_controls():
    """打印控制说明"""
    print("🎮 ENHANCED CONTROLS:")
    print("   ⌨️  键盘控制:")
    print("      • 空格键     - 暂停/继续模拟")
    print("      • G键        - 切换网格显示")
    print("      • T键        - 切换智能体轨迹")
    print("      • C键        - 切换智能体连接")
    print("      • P键        - 切换感知半径")
    print("      • R键        - 重置轨迹记录")
    print()
    print("   🖱️  GUI控制:")
    print("      • 暂停/继续  - 控制模拟进程")
    print("      • 速度滑块   - 调整模拟速度 (0.1x - 5.0x)")
    print("      • 添加智能体 - 动态增加智能体")
    print("      • 重置按钮   - 重新开始模拟")
    print()

def print_observation_guide():
    """打印观察指南"""
    print("📊 OBSERVATION GUIDE:")
    print("   🌍 世界统计:")
    print("      • Step      - 模拟步数 (时间进度)")
    print("      • Agents    - 智能体数量 (种群规模)")
    print("      • Avg Age   - 平均年龄 (种群成熟度)")
    print("      • Avg Energy- 平均能量 (生存状态: 30危险|70健康|100+优秀)")
    print("      • Resources - 资源数量 (环境承载力)")
    print("      • FPS       - 渲染帧率 (性能指标)")
    print()
    print("   🧠 智能体分析:")
    print("      • Most Social - 最活跃社交者 (社会领袖)")
    print("      • Oldest     - 最年长者 (进化成功案例)")
    print("      • Population - 种群趋势 (Growing/Stable/Declining)")
    print("      • Performance- 系统性能 (Good/Fair/Poor)")
    print()
    print("   🔍 行为观察:")
    print("      • 绿色智能体 - 健康状态良好")
    print("      • 黄色智能体 - 中等健康状态")
    print("      • 红色智能体 - 健康状况不佳")
    print("      • 轨迹模式   - 探索、觅食、社交行为")
    print()

def print_startup_tips():
    """打印启动提示"""
    print("💡 STARTUP TIPS:")
    print("   1. 📊 观察边栏的彩色状态信息")
    print("   2. 🎯 注意智能体的移动模式和颜色变化")
    print("   3. 📈 关注种群数量和平均能量的变化趋势")
    print("   4. 🤝 观察智能体间的社交互动")
    print("   5. 🧬 等待繁殖事件(能量>80, 年龄>50)")
    print("   6. 🔄 使用控制按钮调整观察角度")
    print("   7. 📋 运行结束后查看HTML分析报告")
    print()
    print("⚠️  重要提醒:")
    print("   • 首次运行建议观察5-10分钟以观察完整生命周期")
    print("   • 关闭程序时会自动生成HTML可视化报告")
    print("   • 报告保存在 reports/ 目录下")
    print()

def main():
    """主函数"""
    print_banner()
    print_features()
    print_controls()
    print_observation_guide() 
    print_startup_tips()
    
    print("🎬 正在启动增强版Cogvrs模拟器...")
    print("📱 GUI窗口即将打开，请稍候...")
    print("=" * 80)
    print()
    
    try:
        from cogvrs_core.visualization.gui import CogvrsGUI
        
        # 增强配置
        config = {
            'window_width': 1200,
            'window_height': 800,
            'target_fps': 30,  # 优化后的FPS
            'initial_agents': 15,
            'world': {
                'size': (100, 100),
                'resource_density': 0.15,
                'max_agents': 50
            },
            'physics': {
                'friction': 0.1,
                'boundary_type': 'toroidal',
                'energy_conservation': True
            },
            'time': {
                'dt': 0.1,
                'target_fps': 30,
                'real_time': True
            }
        }
        
        print("🎯 配置加载完成")
        print("🧠 初始化15个AI智能体...")
        print("🌍 创建100x100虚拟世界...")
        print("⚡ 启动物理引擎...")
        print("📊 开始数据收集...")
        print()
        print("🚨 注意: 关闭窗口或按Ctrl+C结束模拟")
        print("📈 实时状态更新每5秒输出一次")
        print("=" * 80)
        
        # 启动GUI
        gui = CogvrsGUI(config)
        gui.run()
        
    except ImportError as e:
        print(f"❌ 依赖缺失: {e}")
        print("💡 请安装所需包:")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 用户中断模拟")
    
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        print("📝 请检查日志文件获取详细信息")
        sys.exit(1)
    
    finally:
        print("\n" + "=" * 80)
        print("🎯 Cogvrs Enhanced 模拟结束")
        print("📊 感谢使用数字宇宙实验室!")
        print("🌐 查看生成的HTML报告以获得详细分析")
        print("=" * 80)

if __name__ == "__main__":
    main()