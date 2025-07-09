#!/usr/bin/env python3
"""
Cogvrs命令行配置界面
当tkinter不可用时的备选方案

Author: Ben Hsu & Claude
"""

from typing import Dict, Optional

def get_user_input(prompt: str, default: str = "", input_type: type = str):
    """获取用户输入"""
    while True:
        try:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
            
            if input_type == int:
                return int(user_input)
            elif input_type == float:
                return float(user_input)
            else:
                return user_input
        except ValueError:
            print(f"❌ Invalid input. Please enter a valid {input_type.__name__}.")
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Configuration cancelled or not in interactive mode.")
            # 在非交互式环境中返回默认值
            if input_type == int:
                return int(default) if default.isdigit() else 0
            elif input_type == float:
                try:
                    return float(default)
                except ValueError:
                    return 0.0
            else:
                return default

def show_cli_config() -> Optional[Dict]:
    """显示命令行配置界面"""
    print("\n" + "="*60)
    print("🧠 COGVRS - CONFIGURATION SETUP")
    print("="*60)
    print("Configure your simulation parameters for optimal performance.")
    print()
    
    # 预设选项
    print("📊 AGENT COUNT PRESETS:")
    print("  1. Fast Test (10 agents) - Quick testing")
    print("  2. Normal (50 agents) - Balanced performance")
    print("  3. Medium (100 agents) - More complex interactions")
    print("  4. Large (200 agents) - Full simulation")
    print("  5. Custom - Specify your own count")
    print()
    
    # 选择预设
    preset_choice = get_user_input("Select preset (1-5)", "2", int)
    if preset_choice is None:
        return None
    
    preset_configs = {
        1: ("Fast Test", 10),
        2: ("Normal", 50), 
        3: ("Medium", 100),
        4: ("Large", 200),
        5: ("Custom", 0)
    }
    
    if preset_choice in preset_configs:
        preset_name, agent_count = preset_configs[preset_choice]
        print(f"✅ Selected: {preset_name}")
        
        if preset_choice == 5:  # Custom
            agent_count = get_user_input("Enter custom agent count (1-500)", "50", int)
            if agent_count is None or agent_count < 1 or agent_count > 500:
                print("❌ Invalid agent count. Using default: 50")
                agent_count = 50
    else:
        print("❌ Invalid choice. Using default: Normal (50 agents)")
        agent_count = 50
    
    print()
    print("⚡ PERFORMANCE SETTINGS:")
    
    # FPS设置
    fps = get_user_input("Target FPS (10-60)", "30", int)
    if fps is None or fps < 10 or fps > 60:
        fps = 30
    
    # 渲染质量
    print("\n🎨 RENDERING QUALITY:")
    print("  1. Low - Best performance, basic visuals")
    print("  2. Normal - Balanced performance and quality")
    print("  3. High - Best visuals, may impact performance")
    
    quality_choice = get_user_input("Select quality (1-3)", "2", int)
    quality_map = {1: "low", 2: "normal", 3: "high"}
    rendering_quality = quality_map.get(quality_choice, "normal")
    
    # 多尺度渲染
    print()
    multi_scale_input = get_user_input("Enable Multi-Scale Rendering? (y/n)", "y", str)
    multi_scale = multi_scale_input.lower() in ['y', 'yes', '1', 'true']
    
    # 世界大小
    print("\n🌍 WORLD SIZE:")
    print("  1. Small (50x50) - Fast simulation")
    print("  2. Normal (100x100) - Balanced")
    print("  3. Large (150x150) - More space")
    print("  4. Huge (200x200) - Maximum space")
    
    size_choice = get_user_input("Select world size (1-4)", "2", int)
    size_map = {1: (50, 50), 2: (100, 100), 3: (150, 150), 4: (200, 200)}
    world_size = size_map.get(size_choice, (100, 100))
    
    # 资源密度
    print()
    resource_density = get_user_input("Resource density (0.1-0.5)", "0.2", float)
    if resource_density is None or resource_density < 0.1 or resource_density > 0.5:
        resource_density = 0.2
    
    # 显示最终配置
    print("\n" + "="*60)
    print("📋 FINAL CONFIGURATION:")
    print("="*60)
    print(f"📊 Initial Agents: {agent_count}")
    print(f"🎯 Target FPS: {fps}")
    print(f"🎨 Rendering Quality: {rendering_quality.title()}")
    print(f"🔄 Multi-Scale Rendering: {'Enabled' if multi_scale else 'Disabled'}")
    print(f"🌍 World Size: {world_size[0]}x{world_size[1]}")
    print(f"🌱 Resource Density: {resource_density:.2f}")
    print("="*60)
    
    # 确认
    confirm = get_user_input("Start simulation with these settings? (y/n)", "y", str)
    if confirm is None or confirm.lower() not in ['y', 'yes', '1', 'true']:
        print("❌ Configuration cancelled.")
        return None
    
    return {
        'initial_agents': agent_count,
        'target_fps': fps,
        'rendering_quality': rendering_quality,
        'enable_multi_scale': multi_scale,
        'world_size': world_size,
        'resource_density': resource_density
    }

if __name__ == "__main__":
    # 测试CLI配置
    result = show_cli_config()
    if result:
        print("\n✅ Configuration completed:", result)
    else:
        print("\n❌ Configuration cancelled.")