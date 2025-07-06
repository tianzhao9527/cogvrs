#!/usr/bin/env python3
"""
Simple Cogvrs Runner
简单的Cogvrs运行器，避免语法错误

Author: Ben Hsu & Claude
"""

import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    print("=" * 80)
    print("🧠 COGVRS - COGNITIVE UNIVERSE SIMULATION")
    print("=" * 80)
    print("🚀 Starting simulation...")
    print("📊 Will show status updates every 5 seconds")
    print("🎮 Use GUI controls to interact with simulation")
    print("=" * 80)
    
    try:
        from cogvrs_core.visualization.gui import CogvrsGUI
        
        # 简化配置，降低FPS减少闪烁
        config = {
            'window_width': 1200,
            'window_height': 800,
            'target_fps': 20,  # 进一步降低FPS
            'initial_agents': 12,
            'world': {
                'size': (100, 100),
                'resource_density': 0.15,
                'max_agents': 40
            },
            'physics': {
                'friction': 0.1,
                'boundary_type': 'toroidal',
                'energy_conservation': True
            },
            'time': {
                'dt': 0.1,
                'target_fps': 20,
                'real_time': True
            }
        }
        
        # 启动GUI
        gui = CogvrsGUI(config)
        gui.run()
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Please run: source venv/bin/activate && pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    print("🎯 Simulation ended")

if __name__ == "__main__":
    main()