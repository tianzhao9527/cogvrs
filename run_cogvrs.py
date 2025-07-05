#!/usr/bin/env python3
"""
Cogvrs Launcher
简单的启动脚本，用于快速运行Cogvrs可视化界面

Author: Ben Hsu & Claude
"""

import sys
import os
import logging

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    # 设置基础日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        from cogvrs_core.visualization.gui import CogvrsGUI
        
        # 简单配置
        config = {
            'window_width': 1200,
            'window_height': 800,
            'target_fps': 30,
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
        
        print("🧠 Welcome to Cogvrs - Cognitive Universe Simulation!")
        print("🚀 Starting simulation...")
        print("\nControls:")
        print("  Space - Pause/Resume")
        print("  G - Toggle Grid")
        print("  T - Toggle Agent Trajectories")
        print("  C - Toggle Agent Connections")
        print("  P - Toggle Perception Radius")
        print("  R - Reset Trajectories")
        print("\nWatch as AI agents:")
        print("  • Explore their environment")
        print("  • Search for resources")
        print("  • Interact socially")
        print("  • Learn and adapt")
        print("  • Reproduce and evolve")
        print("\n" + "="*50)
        
        # 启动GUI
        gui = CogvrsGUI(config)
        gui.run()
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Please install required packages:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error starting Cogvrs: {e}")
        logging.exception("Startup error")
        sys.exit(1)


if __name__ == "__main__":
    main()