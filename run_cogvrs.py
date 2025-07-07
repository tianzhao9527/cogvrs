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
        
        # 优化配置 - 提高生存率和文明发展
        config = {
            'window_width': 1600,  # 增加默认窗口大小以支持更多智能体的显示
            'window_height': 1000,
            'target_fps': 30,
            'initial_agents': 100,  # 设置为100个初始智能体
            'world': {
                'size': (100, 100),
                'resource_density': 0.2,  # 大幅提高资源密度
                'max_agents': 200,  # 增加最大承载量以支持更多智能体
                'resource_regeneration_rate': 0.8  # 新增资源再生率
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
            },
            # 新增部落配置
            'civilization': {
                'enable_tribes': True,
                'tribe_formation_threshold': 8,  # 8个以上智能体可形成部落
                'tribe_communication_range': 150,  # 部落间通信范围
                'cultural_evolution_rate': 0.1  # 文化进化速率
            },
            # 优化环境压力
            'environment': {
                'reduce_climate_severity': True,  # 减少气候严酷程度
                'stable_climate_probability': 0.7  # 70%概率保持稳定气候
            }
        }
        
        print("🧠 Welcome to Cogvrs - Cognitive Universe Simulation!")
        print("🚀 Starting simulation...")
        print("\nControls:")
        print("  Space - Pause/Resume")
        print("  M - Toggle Multi-Scale/Legacy Rendering")
        print("  G - Toggle Grid")
        print("  T - Toggle Agent Trajectories")
        print("  C - Toggle Agent Connections")
        print("  P - Toggle Perception Radius")
        print("  B - Toggle Tribe Visualization")
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