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
        # 尝试显示启动配置对话框，如果失败则使用CLI
        print("🚀 Launching Cogvrs Configuration...")
        
        user_config = None
        try:
            from cogvrs_core.utils.startup_dialog import show_startup_dialog
            user_config = show_startup_dialog()
        except ImportError as e:
            if '_tkinter' in str(e):
                print("ℹ️  GUI not available (tkinter missing), using command line interface...")
                from cogvrs_core.utils.cli_config import show_cli_config
                user_config = show_cli_config()
            else:
                raise e
        except Exception as e:
            print(f"⚠️  GUI configuration failed: {e}")
            print("🔄 Falling back to command line interface...")
            from cogvrs_core.utils.cli_config import show_cli_config
            user_config = show_cli_config()
        
        if user_config is None:
            print("❌ User cancelled configuration. Exiting...")
            return
        
        print(f"✅ Configuration selected:")
        print(f"   📊 Initial Agents: {user_config['initial_agents']}")
        print(f"   🎯 Target FPS: {user_config['target_fps']}")
        print(f"   🎨 Rendering Quality: {user_config['rendering_quality']}")
        print(f"   🌍 World Size: {user_config['world_size']}")
        print(f"   🌱 Resource Density: {user_config['resource_density']:.2f}")
        
        from cogvrs_core.visualization.optimized_gui import OptimizedCogvrsGUI
        
        # 根据用户配置生成最终配置
        config = {
            'window_width': 1600,
            'window_height': 1000,
            'target_fps': user_config['target_fps'],
            'initial_agents': user_config['initial_agents'],
            'enable_multi_scale': user_config['enable_multi_scale'],
            'world': {
                'size': user_config['world_size'],
                'resource_density': user_config['resource_density'],
                'max_agents': max(user_config['initial_agents'] * 20, 1000),  # 动态设置最大数量
                'resource_regeneration_rate': 0.8
            },
            'physics': {
                'friction': 0.1,
                'boundary_type': 'toroidal',
                'energy_conservation': True
            },
            'time': {
                'dt': 0.1,
                'target_fps': user_config['target_fps'],
                'real_time': True
            },
            'civilization': {
                'enable_tribes': True,
                'tribe_formation_threshold': max(5, user_config['initial_agents'] // 10),  # 动态调整部落门槛
                'tribe_communication_range': 150,
                'cultural_evolution_rate': 0.1
            },
            'environment': {
                'reduce_climate_severity': True,
                'stable_climate_probability': 0.7
            },
            'rendering': {
                'quality': user_config['rendering_quality'],
                'skip_frames': 0 if user_config['rendering_quality'] == 'high' else 
                              1 if user_config['rendering_quality'] == 'normal' else 2
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
        
        # 启动优化GUI
        gui = OptimizedCogvrsGUI(config)
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