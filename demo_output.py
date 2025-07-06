#!/usr/bin/env python3
"""
Cogvrs Demo Output
展示Cogvrs运行状态的演示脚本

Author: Ben Hsu & Claude
"""

import sys
import os
import time
import signal

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def signal_handler(sig, frame):
    print('\n🛑 Demo interrupted by user')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def simulate_cogvrs_output():
    """模拟Cogvrs运行时的状态输出"""
    print("=" * 80)
    print("🧠 COGVRS - COGNITIVE UNIVERSE SIMULATION PLATFORM")
    print("=" * 80)
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
    
    print("📊 STATUS OUTPUT EVERY 5 SECONDS:")
    print("=" * 80)
    
    # 模拟运行状态
    for step in range(1, 600, 150):  # 模拟约30秒的运行
        print()
        print(f"Step {step:>6} | FPS: {24.0:5.1f} | Agents: {15:>2}")
        print(f"Age: {step/10:4.0f}-{step/5:4.0f} (avg:{step/7:5.1f})")
        print(f"Energy: {80.0:5.1f}-{120.0:5.1f} (avg:{100.0:5.1f})")
        print(f"Total Offspring: {step//100}")
        print(f"Resources: {25}")
        print("-" * 60)
        
        if step == 150:
            print("🎉 New agent born! Population growing...")
        elif step == 300:
            print("🤝 Social interactions increasing...")
        elif step == 450:
            print("🧬 Evolution detected - neural networks adapting...")
            
        time.sleep(2)  # 模拟5秒间隔
    
    print()
    print("=" * 80)
    print("🎯 DEMO COMPLETE")
    print("💡 The actual Cogvrs GUI shows:")
    print("   • Real-time 2D visualization of agents")
    print("   • Interactive control panel")
    print("   • Live statistics and metrics")
    print("   • Agent trajectory visualization")
    print("   • Resource distribution display")
    print("=" * 80)

def main():
    """主函数"""
    print("🎬 This is a demo of Cogvrs status output")
    print("⏰ Watch for 5-second status updates...")
    print("🛑 Press Ctrl+C to stop the demo")
    print()
    
    try:
        simulate_cogvrs_output()
    except KeyboardInterrupt:
        print('\n🛑 Demo stopped by user')
    
    print("\n🚀 To run the actual simulation:")
    print("   source venv/bin/activate")
    print("   python3 run_simple.py")

if __name__ == "__main__":
    main()