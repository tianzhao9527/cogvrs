#!/usr/bin/env python3
"""
Simple Status Output Functions
解决语法错误的简单状态输出
"""

def print_simulation_status(agents, time_manager, world):
    """打印详细的模拟状态"""
    alive_agents = [a for a in agents if a.alive]
    time_stats = time_manager.get_time_stats()
    world_state = world.get_world_state()
    
    print()
    print(f"🕰  Step {time_stats['current_step']:>6} | FPS: {time_stats['actual_fps']:5.1f} | Agents: {len(alive_agents):>2}")
    
    if alive_agents:
        # 计算智能体统计数据
        ages = [a.age for a in alive_agents]
        energies = [a.energy for a in alive_agents]
        healths = [a.health for a in alive_agents]
        offspring_counts = [a.offspring_count for a in alive_agents]
        
        print(f"🧠 Age: {min(ages):4.0f}-{max(ages):4.0f} (avg:{sum(ages)/len(ages):5.1f})")
        print(f"⚡ Energy: {min(energies):5.1f}-{max(energies):5.1f} (avg:{sum(energies)/len(energies):5.1f})")
        print(f"❤️ Health: {min(healths):5.1f}-{max(healths):5.1f} (avg:{sum(healths)/len(healths):5.1f})")
        print(f"👼 Offspring: total={sum(offspring_counts):>3} | max={max(offspring_counts):>2}")
        
        # 显示最活跃的智能体
        most_active = max(alive_agents, key=lambda a: a.social_interactions)
        oldest = max(alive_agents, key=lambda a: a.age)
        
        print(f"🏆 Most Social: Agent#{most_active.id} ({most_active.social_interactions} interactions)")
        print(f"👴 Oldest: Agent#{oldest.id} (age {oldest.age:.0f}, energy {oldest.energy:.1f})")
    
    print(f"🌍 World: {world_state['num_resources']} resources, total value {world_state['total_resources']:.0f}")
    print("-" * 60)