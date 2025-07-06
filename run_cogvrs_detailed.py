#!/usr/bin/env python3
"""
Cogvrs Detailed Launcher
增强版启动脚本，包含详细的状态输出和日志记录

Author: Ben Hsu & Claude
"""

import sys
import os
import logging
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_detailed_logging():
    """设置详细的日志系统"""
    # 创建logs目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 设置日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/cogvrs_session_{timestamp}.log"
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file

def print_welcome_message():
    """打印欢迎信息"""
    print("=" * 80)
    print("🧠 COGVRS - COGNITIVE UNIVERSE SIMULATION PLATFORM")
    print("=" * 80)
    print("🔬 Digital Universe Laboratory | AI Consciousness Exploration")
    print("👨‍💻 Author: Ben Hsu & Claude")
    print("🌐 Website: cogvrs.com")
    print("=" * 80)
    print()
    
    print("🚀 SIMULATION FEATURES:")
    print("   • 15 AI agents with neural networks")
    print("   • Memory systems (working, long-term, spatial)")
    print("   • Behavior-driven decision making") 
    print("   • Social interactions and learning")
    print("   • Reproduction and evolution")
    print("   • Real-time physics simulation")
    print()
    
    print("🎮 CONTROLS:")
    print("   • Space Bar    - Pause/Resume simulation")
    print("   • G Key        - Toggle grid display")
    print("   • T Key        - Toggle agent trajectories")
    print("   • C Key        - Toggle agent connections")
    print("   • P Key        - Toggle perception radius")
    print("   • R Key        - Reset trajectories")
    print("   • GUI Buttons  - Add agents, adjust speed")
    print()
    
    print("📊 STATUS OUTPUT:")
    print("   • Real-time statistics every 5 seconds")
    print("   • Agent behavior analysis")
    print("   • World resource monitoring")
    print("   • Performance metrics")
    print()

def main():
    """主函数"""
    print_welcome_message()
    
    # 设置详细日志
    log_file = setup_detailed_logging()
    logger = logging.getLogger(__name__)
    
    print(f"📝 Session log: {log_file}")
    print("=" * 80)
    print()
    
    try:
        from cogvrs_core.visualization.gui import CogvrsGUI
        
        # 增强配置
        config = {
            'window_width': 1200,
            'window_height': 800,
            'target_fps': 24,  # 降低FPS减少闪烁
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
                'target_fps': 24,
                'real_time': True
            }
        }
        
        logger.info("🎯 Cogvrs simulation starting...")
        logger.info(f"📊 Configuration: {config}")
        
        print("🎬 Starting Cogvrs GUI...")
        print("💡 Watch the console for real-time status updates!")
        print("🖼️  The GUI window should appear momentarily...")
        print()
        
        # 启动GUI
        gui = CogvrsGUI(config)
        gui.run()
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Please install required packages:")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Error starting Cogvrs: {e}")
        print(f"❌ Unexpected error: {e}")
        print("📝 Check the log file for details")
        sys.exit(1)
    
    finally:
        print()
        print("=" * 80)
        print("🎯 Cogvrs simulation ended")
        print(f"📝 Session log saved: {log_file}")
        print("=" * 80)

if __name__ == "__main__":
    main()