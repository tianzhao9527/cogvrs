"""
部落管理器 - 管理智能体部落形成和发展
支持部落间通信和文明演化

Author: Ben Hsu & Claude
"""

import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from ..core.physics_engine import Vector2D
from ..utils.event_logger import (
    EventType, EventSeverity, log_tribe_event, log_event, get_event_logger
)
from .warfare_system import WarfareSystem


class CivilizationLevel(Enum):
    """文明等级"""
    NOMADIC = "nomadic"          # 游牧阶段
    SETTLEMENT = "settlement"    # 定居阶段
    VILLAGE = "village"          # 村庄阶段
    TOWN = "town"               # 城镇阶段
    CITY = "city"               # 城市阶段


@dataclass
class CulturalTrait:
    """文化特征"""
    name: str
    strength: float      # 特征强度 0-1
    origin_time: float   # 起源时间
    spread_rate: float   # 传播速率


@dataclass
class Tribe:
    """部落类"""
    tribe_id: str
    name: str
    members: List        # 部落成员
    leader: Optional     # 部落首领
    territory_center: Vector2D
    territory_radius: float
    
    # 社会结构
    civilization_level: CivilizationLevel
    population: int
    
    # 文化属性
    cultural_traits: List[CulturalTrait]
    collective_knowledge: Dict[str, float]  # 集体知识
    traditions: List[str]  # 传统
    
    # 经济属性
    resources: Dict[str, float]  # 部落资源
    technology_level: float      # 科技水平
    
    # 外交属性
    allied_tribes: Set[str]      # 盟友部落
    enemy_tribes: Set[str]       # 敌对部落
    
    # 视觉属性
    color: Tuple[int, int, int]  # 部落颜色 (RGB)
    
    # 统计数据
    formation_time: float
    total_offspring: int
    avg_lifespan: float
    
    def __post_init__(self):
        if not self.cultural_traits:
            self.cultural_traits = []
        if not self.collective_knowledge:
            self.collective_knowledge = {}
        if not self.traditions:
            self.traditions = []
        if not self.resources:
            self.resources = {'food': 0, 'materials': 0, 'knowledge': 0}
        if not self.allied_tribes:
            self.allied_tribes = set()
        if not self.enemy_tribes:
            self.enemy_tribes = set()


class TribeManager:
    """部落管理器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # 部落形成参数 - 调整以促进地域扩散
        self.formation_threshold = self.config.get('tribe_formation_threshold', 6)  # 降低形成门槛
        self.min_density = 3  # 最小密度要求
        self.formation_range = 25  # 减小形成范围，促进分散
        
        # 通信参数
        self.communication_range = self.config.get('tribe_communication_range', 150)
        self.cultural_evolution_rate = self.config.get('cultural_evolution_rate', 0.1)
        
        # 部落数据
        self.tribes: Dict[str, Tribe] = {}
        self.next_tribe_id = 1
        
        # 文明发展参数
        self.civilization_thresholds = {
            CivilizationLevel.NOMADIC: 5,
            CivilizationLevel.SETTLEMENT: 12,
            CivilizationLevel.VILLAGE: 25,
            CivilizationLevel.TOWN: 50,
            CivilizationLevel.CITY: 100
        }
        
        # 部落名称库
        self.tribe_names = [
            "Azure", "Crimson", "Golden", "Silver", "Emerald", "Sapphire", "Ruby", "Diamond",
            "Storm", "Thunder", "Lightning", "Wind", "Earth", "Fire", "Water", "Ice",
            "Dawn", "Dusk", "Star", "Moon", "Sun", "Sky", "Forest", "Mountain",
            "River", "Ocean", "Desert", "Valley", "Peak", "Grove", "Meadow", "Stone"
        ]
        
        # 部落颜色库 (RGB格式)
        self.tribe_colors = [
            (255, 100, 100),   # 红色系
            (100, 255, 100),   # 绿色系  
            (100, 100, 255),   # 蓝色系
            (255, 255, 100),   # 黄色系
            (255, 100, 255),   # 紫色系
            (100, 255, 255),   # 青色系
            (255, 150, 100),   # 橙色系
            (150, 255, 150),   # 浅绿系
            (150, 150, 255),   # 浅蓝系
            (255, 200, 150),   # 桃色系
            (200, 150, 255),   # 淡紫系
            (150, 255, 200),   # 薄荷系
        ]
        self.color_index = 0  # 颜色分配索引
        
        # 初始化战争系统
        self.warfare_system = WarfareSystem({
            'enable_warfare': True,
            'conflict_probability': 0.002,  # 增加冲突概率
            'battle_duration': 20  # 缩短战斗时间
        })
        
        print(f"🏘️ 部落管理器初始化完成")
        print(f"   形成门槛: {self.formation_threshold} 个体")
        print(f"   通信范围: {self.communication_range}")
        print(f"   战争系统: 已启用")
    
    def update(self, agents: List, dt: float):
        """更新部落系统"""
        # 1. 检测新部落形成
        self._detect_tribe_formation(agents)
        
        # 2. 更新现有部落
        self._update_existing_tribes(agents, dt)
        
        # 3. 处理部落间交互
        self._handle_inter_tribe_interactions(dt)
        
        # 4. 文明发展检查
        self._check_civilization_advancement()
        
        # 5. 处理部落迁移和领土扩张
        self._handle_tribal_migration(dt)
        
        # 6. 更新战争系统
        self.warfare_system.update(self.tribes, dt)
    
    def _detect_tribe_formation(self, agents: List):
        """检测部落形成"""
        # 找到未加入部落的智能体
        unassigned_agents = [agent for agent in agents 
                           if not hasattr(agent, 'tribe_id') or agent.tribe_id is None]
        
        if len(unassigned_agents) < self.formation_threshold:
            return
        
        # 使用聚类算法检测密集群体
        clusters = self._cluster_agents(unassigned_agents)
        
        for cluster in clusters:
            if len(cluster) >= self.formation_threshold:
                self._form_new_tribe(cluster)
    
    def _cluster_agents(self, agents: List) -> List[List]:
        """对智能体进行聚类"""
        clusters = []
        processed = set()  # 存储已处理的agent_id
        
        for agent in agents:
            if agent.agent_id in processed:
                continue
            
            # 创建新聚类
            cluster = [agent]
            processed.add(agent.agent_id)
            
            # 查找附近的智能体
            for other_agent in agents:
                if other_agent.agent_id in processed:
                    continue
                
                distance = agent.position.distance_to(other_agent.position)
                if distance <= self.formation_range:
                    cluster.append(other_agent)
                    processed.add(other_agent.agent_id)
            
            # 检查聚类密度
            if len(cluster) >= self.min_density:
                clusters.append(cluster)
        
        return clusters
    
    def _form_new_tribe(self, members: List):
        """形成新部落"""
        tribe_id = f"tribe_{self.next_tribe_id:03d}"
        self.next_tribe_id += 1
        
        # 选择部落名称
        name_base = np.random.choice(self.tribe_names)
        tribe_name = f"{name_base} Tribe"
        
        # 计算部落中心
        center_x = np.mean([member.position.x for member in members])
        center_y = np.mean([member.position.y for member in members])
        territory_center = Vector2D(center_x, center_y)
        
        # 计算领土半径
        max_distance = max([territory_center.distance_to(member.position) for member in members])
        territory_radius = max(20, max_distance * 1.5)
        
        # 选择首领（能量最高的个体）
        leader = max(members, key=lambda x: x.energy)
        
        # 分配部落颜色
        tribe_color = self.tribe_colors[self.color_index % len(self.tribe_colors)]
        self.color_index += 1
        
        # 创建部落
        tribe = Tribe(
            tribe_id=tribe_id,
            name=tribe_name,
            members=members,
            leader=leader,
            territory_center=territory_center,
            territory_radius=territory_radius,
            civilization_level=CivilizationLevel.NOMADIC,
            population=len(members),
            cultural_traits=[],
            collective_knowledge={'survival': 0.3, 'cooperation': 0.2, 'exploration': 0.1},
            traditions=[],
            resources={'food': len(members) * 5, 'materials': len(members) * 2, 'knowledge': len(members)},
            technology_level=0.1,
            allied_tribes=set(),
            enemy_tribes=set(),
            color=tribe_color,
            formation_time=time.time(),
            total_offspring=sum(getattr(m, 'offspring_count', 0) for m in members),
            avg_lifespan=np.mean([getattr(m, 'age', 0) for m in members])
        )
        
        # 给成员分配部落ID和颜色
        for member in members:
            member.tribe_id = tribe_id
            member.tribe_name = tribe_name
            member.tribe_color = tribe_color
            # 标记首领身份
            member.is_tribe_leader = (member == leader)
        
        self.tribes[tribe_id] = tribe
        
        print(f"🏘️ 新部落形成: {tribe_name} (ID: {tribe_id})")
        print(f"   成员数: {len(members)}, 首领: {leader.agent_id}")
        print(f"   领土中心: ({territory_center.x:.1f}, {territory_center.y:.1f})")
        
        # 记录部落形成事件
        log_tribe_event(
            event_type=EventType.TRIBE_FORMATION,
            tribe_name=tribe_name,
            description=f"新部落{tribe_name}在({territory_center.x:.1f}, {territory_center.y:.1f})形成，成员数{len(members)}",
            data={
                'tribe_id': tribe_id,
                'tribe_name': tribe_name,
                'member_count': len(members),
                'leader_id': leader.agent_id,
                'territory_center': (territory_center.x, territory_center.y),
                'territory_radius': territory_radius,
                'color': tribe_color,
                'member_ids': [m.agent_id for m in members],
                'civilization_level': tribe.civilization_level.value
            },
            location=(territory_center.x, territory_center.y),
            participants=[m.agent_id for m in members],
            impact_score=len(members) * 2.0
        )
        
        # 记录部落形成事件（如果GUI可用）
        if hasattr(self, 'gui_callback') and self.gui_callback:
            self.gui_callback('tribe', f'新部落形成: {tribe_name}', {
                'tribe_id': tribe_id,
                'tribe_name': tribe_name,
                'member_count': len(members),
                'leader_id': leader.agent_id,
                'territory_center': (territory_center.x, territory_center.y),
                'territory_radius': territory_radius,
                'color': tribe_color,
                'member_ids': [m.agent_id for m in members]
            })
    
    def _update_existing_tribes(self, agents: List, dt: float):
        """更新现有部落"""
        tribes_to_remove = []
        
        for tribe_id, tribe in self.tribes.items():
            # 更新成员列表（移除死亡成员）
            alive_members = [agent for agent in agents 
                           if hasattr(agent, 'tribe_id') and agent.tribe_id == tribe_id]
            
            if len(alive_members) < 3:
                # 部落解散
                tribes_to_remove.append(tribe_id)
                print(f"💔 部落解散: {tribe.name} (成员不足)")
                
                # 记录部落解散事件
                log_tribe_event(
                    event_type=EventType.TRIBE_DISSOLUTION,
                    tribe_name=tribe.name,
                    description=f"部落{tribe.name}因成员不足而解散，最终成员数{len(alive_members)}",
                    data={
                        'tribe_id': tribe_id,
                        'tribe_name': tribe.name,
                        'final_member_count': len(alive_members),
                        'dissolution_reason': '成员不足',
                        'tribe_age': time.time() - tribe.formation_time,
                        'total_offspring': tribe.total_offspring,
                        'civilization_level': tribe.civilization_level.value
                    },
                    location=(tribe.territory_center.x, tribe.territory_center.y),
                    participants=[m.agent_id for m in alive_members],
                    impact_score=5.0
                )
                continue
            
            tribe.members = alive_members
            tribe.population = len(alive_members)
            
            # 更新首领（如果现任首领死亡）
            if tribe.leader not in alive_members:
                # 清除旧首领标记
                for member in alive_members:
                    member.is_tribe_leader = False
                
                # 选出新首领并标记
                new_leader = max(alive_members, key=lambda x: x.energy)
                old_leader_id = tribe.leader.agent_id if tribe.leader else "未知"
                tribe.leader = new_leader
                tribe.leader.is_tribe_leader = True
                print(f"👑 {tribe.name} 选出新首领: {tribe.leader.agent_id}")
                
                # 记录领导权变更事件
                log_tribe_event(
                    event_type=EventType.TRIBE_LEADERSHIP_CHANGE,
                    tribe_name=tribe.name,
                    description=f"部落{tribe.name}选出新首领{new_leader.agent_id}，替换前任首领{old_leader_id}",
                    data={
                        'tribe_id': tribe_id,
                        'tribe_name': tribe.name,
                        'new_leader_id': new_leader.agent_id,
                        'old_leader_id': old_leader_id,
                        'new_leader_energy': new_leader.energy,
                        'member_count': len(alive_members)
                    },
                    location=(tribe.territory_center.x, tribe.territory_center.y),
                    participants=[new_leader.agent_id],
                    impact_score=3.0
                )
            else:
                # 确保当前首领有正确的标记
                for member in alive_members:
                    member.is_tribe_leader = (member == tribe.leader)
            
            # 更新统计数据
            tribe.total_offspring = sum(getattr(m, 'offspring_count', 0) for m in alive_members)
            tribe.avg_lifespan = np.mean([getattr(m, 'age', 0) for m in alive_members])
            
            # 文化演化
            self._evolve_culture(tribe, dt)
            
            # 积累资源
            self._accumulate_resources(tribe, dt)
        
        # 移除解散的部落
        for tribe_id in tribes_to_remove:
            del self.tribes[tribe_id]
    
    def _evolve_culture(self, tribe: Tribe, dt: float):
        """文化演化"""
        # 基于部落行为发展文化特征
        cultural_growth = self.cultural_evolution_rate * dt
        
        # 增长集体知识
        for knowledge_type in tribe.collective_knowledge:
            tribe.collective_knowledge[knowledge_type] += cultural_growth * np.random.uniform(0.5, 1.5)
            tribe.collective_knowledge[knowledge_type] = min(1.0, tribe.collective_knowledge[knowledge_type])
        
        # 随机发展新的文化特征
        if np.random.random() < 0.01:  # 1% 概率发展新特征
            trait_names = ['art', 'music', 'storytelling', 'rituals', 'craftsmanship', 'warfare', 'trade']
            if len(tribe.cultural_traits) < 5:  # 最多5个特征
                new_trait_name = np.random.choice(trait_names)
                if not any(trait.name == new_trait_name for trait in tribe.cultural_traits):
                    new_trait = CulturalTrait(
                        name=new_trait_name,
                        strength=0.1,
                        origin_time=time.time(),
                        spread_rate=np.random.uniform(0.01, 0.05)
                    )
                    tribe.cultural_traits.append(new_trait)
                    print(f"🎨 {tribe.name} 发展了新文化: {new_trait_name}")
                    
                    # 记录文化发展事件
                    log_tribe_event(
                        event_type=EventType.TRIBE_CULTURAL_DEVELOPMENT,
                        tribe_name=tribe.name,
                        description=f"部落{tribe.name}发展了新文化特征：{new_trait_name}",
                        data={
                            'tribe_id': tribe.tribe_id,
                            'tribe_name': tribe.name,
                            'cultural_trait': new_trait_name,
                            'trait_strength': new_trait.strength,
                            'spread_rate': new_trait.spread_rate,
                            'total_traits': len(tribe.cultural_traits)
                        },
                        location=(tribe.territory_center.x, tribe.territory_center.y),
                        participants=[m.agent_id for m in tribe.members],
                        impact_score=2.0
                    )
    
    def _accumulate_resources(self, tribe: Tribe, dt: float):
        """积累资源"""
        # 基于部落规模和科技水平积累资源
        population_factor = tribe.population / 10
        tech_factor = 1 + tribe.technology_level
        
        tribe.resources['food'] += population_factor * tech_factor * dt * 0.5
        tribe.resources['materials'] += population_factor * tech_factor * dt * 0.3
        tribe.resources['knowledge'] += len(tribe.cultural_traits) * dt * 0.1
        
        # 科技发展
        if tribe.resources['knowledge'] > 10:
            tribe.technology_level += 0.01 * dt
            tribe.technology_level = min(1.0, tribe.technology_level)
    
    def _handle_inter_tribe_interactions(self, dt: float):
        """处理部落间交互"""
        tribe_list = list(self.tribes.values())
        
        for i, tribe_a in enumerate(tribe_list):
            for tribe_b in tribe_list[i+1:]:
                distance = tribe_a.territory_center.distance_to(tribe_b.territory_center)
                
                if distance <= self.communication_range:
                    self._handle_tribe_contact(tribe_a, tribe_b, distance, dt)
    
    def _handle_tribe_contact(self, tribe_a: Tribe, tribe_b: Tribe, distance: float, dt: float):
        """处理两个部落的接触"""
        # 基于距离和文化相似性决定交互类型
        cultural_similarity = self._calculate_cultural_similarity(tribe_a, tribe_b)
        
        # 交互概率基于距离
        interaction_probability = max(0, 1.0 - distance / self.communication_range) * dt * 0.1
        
        if np.random.random() < interaction_probability:
            if cultural_similarity > 0.6:
                # 文化相似，倾向于合作
                self._handle_cooperation(tribe_a, tribe_b)
            elif cultural_similarity < 0.3:
                # 文化差异大，可能冲突
                self._handle_conflict(tribe_a, tribe_b)
            else:
                # 中等相似性，贸易交流
                self._handle_trade(tribe_a, tribe_b)
    
    def _calculate_cultural_similarity(self, tribe_a: Tribe, tribe_b: Tribe) -> float:
        """计算文化相似性"""
        # 基于共同文化特征计算相似性
        traits_a = set(trait.name for trait in tribe_a.cultural_traits)
        traits_b = set(trait.name for trait in tribe_b.cultural_traits)
        
        if not traits_a and not traits_b:
            return 0.5  # 都没有特征，中等相似性
        
        common_traits = traits_a.intersection(traits_b)
        total_traits = traits_a.union(traits_b)
        
        return len(common_traits) / len(total_traits) if total_traits else 0.5
    
    def _handle_cooperation(self, tribe_a: Tribe, tribe_b: Tribe):
        """处理部落合作"""
        if tribe_b.tribe_id not in tribe_a.allied_tribes:
            tribe_a.allied_tribes.add(tribe_b.tribe_id)
            tribe_b.allied_tribes.add(tribe_a.tribe_id)
            
            # 移除敌对关系
            tribe_a.enemy_tribes.discard(tribe_b.tribe_id)
            tribe_b.enemy_tribes.discard(tribe_a.tribe_id)
            
            print(f"🤝 部落结盟: {tribe_a.name} ↔ {tribe_b.name}")
            
            # 记录结盟事件
            log_tribe_event(
                event_type=EventType.TRIBE_ALLIANCE,
                tribe_name=f"{tribe_a.name} & {tribe_b.name}",
                description=f"部落{tribe_a.name}与{tribe_b.name}结成同盟",
                data={
                    'tribe_a_id': tribe_a.tribe_id,
                    'tribe_a_name': tribe_a.name,
                    'tribe_b_id': tribe_b.tribe_id,
                    'tribe_b_name': tribe_b.name,
                    'alliance_type': 'cultural_cooperation',
                    'tribe_a_population': tribe_a.population,
                    'tribe_b_population': tribe_b.population
                },
                location=(
                    (tribe_a.territory_center.x + tribe_b.territory_center.x) / 2,
                    (tribe_a.territory_center.y + tribe_b.territory_center.y) / 2
                ),
                participants=[tribe_a.tribe_id, tribe_b.tribe_id],
                impact_score=4.0
            )
            
            # 文化交流
            self._cultural_exchange(tribe_a, tribe_b)
    
    def _handle_conflict(self, tribe_a: Tribe, tribe_b: Tribe):
        """处理部落冲突"""
        if tribe_b.tribe_id not in tribe_a.enemy_tribes:
            tribe_a.enemy_tribes.add(tribe_b.tribe_id)
            tribe_b.enemy_tribes.add(tribe_a.tribe_id)
            
            # 移除盟友关系
            tribe_a.allied_tribes.discard(tribe_b.tribe_id)
            tribe_b.allied_tribes.discard(tribe_a.tribe_id)
            
            print(f"⚔️ 部落冲突: {tribe_a.name} ↔ {tribe_b.name}")
            
            # 记录冲突事件
            log_tribe_event(
                event_type=EventType.TRIBE_CONFLICT,
                tribe_name=f"{tribe_a.name} vs {tribe_b.name}",
                description=f"部落{tribe_a.name}与{tribe_b.name}发生冲突",
                data={
                    'tribe_a_id': tribe_a.tribe_id,
                    'tribe_a_name': tribe_a.name,
                    'tribe_b_id': tribe_b.tribe_id,
                    'tribe_b_name': tribe_b.name,
                    'conflict_type': 'cultural_difference',
                    'tribe_a_population': tribe_a.population,
                    'tribe_b_population': tribe_b.population
                },
                location=(
                    (tribe_a.territory_center.x + tribe_b.territory_center.x) / 2,
                    (tribe_a.territory_center.y + tribe_b.territory_center.y) / 2
                ),
                participants=[tribe_a.tribe_id, tribe_b.tribe_id],
                impact_score=3.0
            )
    
    def _handle_trade(self, tribe_a: Tribe, tribe_b: Tribe):
        """处理部落贸易"""
        # 简单的资源交换
        trade_amount = min(tribe_a.resources['food'], tribe_b.resources['materials']) * 0.1
        
        if trade_amount > 0:
            tribe_a.resources['materials'] += trade_amount
            tribe_a.resources['food'] -= trade_amount
            tribe_b.resources['food'] += trade_amount
            tribe_b.resources['materials'] -= trade_amount
            
            print(f"💰 部落贸易: {tribe_a.name} ↔ {tribe_b.name} (交易量: {trade_amount:.1f})")
            
            # 记录贸易事件
            log_tribe_event(
                event_type=EventType.TRIBE_TRADE,
                tribe_name=f"{tribe_a.name} & {tribe_b.name}",
                description=f"部落{tribe_a.name}与{tribe_b.name}进行贸易，交易量{trade_amount:.1f}",
                data={
                    'tribe_a_id': tribe_a.tribe_id,
                    'tribe_a_name': tribe_a.name,
                    'tribe_b_id': tribe_b.tribe_id,
                    'tribe_b_name': tribe_b.name,
                    'trade_amount': trade_amount,
                    'trade_type': 'food_materials_exchange'
                },
                location=(
                    (tribe_a.territory_center.x + tribe_b.territory_center.x) / 2,
                    (tribe_a.territory_center.y + tribe_b.territory_center.y) / 2
                ),
                participants=[tribe_a.tribe_id, tribe_b.tribe_id],
                impact_score=1.0
            )
    
    def _cultural_exchange(self, tribe_a: Tribe, tribe_b: Tribe):
        """文化交流"""
        # 交换文化特征
        for trait in tribe_a.cultural_traits:
            if not any(t.name == trait.name for t in tribe_b.cultural_traits):
                if np.random.random() < trait.spread_rate:
                    new_trait = CulturalTrait(
                        name=trait.name,
                        strength=trait.strength * 0.5,  # 传播时强度减半
                        origin_time=time.time(),
                        spread_rate=trait.spread_rate
                    )
                    tribe_b.cultural_traits.append(new_trait)
                    print(f"🌍 文化传播: {trait.name} ({tribe_a.name} → {tribe_b.name})")
    
    def _check_civilization_advancement(self):
        """检查文明发展"""
        for tribe in self.tribes.values():
            current_level = tribe.civilization_level
            
            # 检查是否可以晋升到下一个文明等级
            for level, threshold in self.civilization_thresholds.items():
                if (tribe.population >= threshold and 
                    level.value != current_level.value and
                    self._get_level_rank(level) > self._get_level_rank(current_level)):
                    
                    old_level = tribe.civilization_level
                    tribe.civilization_level = level
                    print(f"🏛️ 文明进步: {tribe.name} 达到 {level.value} 阶段")
                    
                    # 记录文明进步事件
                    log_tribe_event(
                        event_type=EventType.TRIBE_CIVILIZATION_ADVANCEMENT,
                        tribe_name=tribe.name,
                        description=f"部落{tribe.name}文明等级从{old_level.value}晋升到{level.value}",
                        data={
                            'tribe_id': tribe.tribe_id,
                            'tribe_name': tribe.name,
                            'old_level': old_level.value,
                            'new_level': level.value,
                            'population': tribe.population,
                            'technology_level': tribe.technology_level,
                            'cultural_traits': len(tribe.cultural_traits)
                        },
                        location=(tribe.territory_center.x, tribe.territory_center.y),
                        participants=[m.agent_id for m in tribe.members],
                        impact_score=10.0
                    )
                    break
    
    def _get_level_rank(self, level: CivilizationLevel) -> int:
        """获取文明等级排名"""
        level_ranks = {
            CivilizationLevel.NOMADIC: 1,
            CivilizationLevel.SETTLEMENT: 2,
            CivilizationLevel.VILLAGE: 3,
            CivilizationLevel.TOWN: 4,
            CivilizationLevel.CITY: 5
        }
        return level_ranks.get(level, 0)
    
    def _handle_tribal_migration(self, dt: float):
        """处理部落迁移和领土扩张"""
        for tribe in self.tribes.values():
            # 检查迁移条件
            migration_probability = 0.001 * dt  # 每秒0.1%的迁移概率
            
            # 大部落有更高的迁移倾向
            if tribe.population > 15:
                migration_probability *= 2.0
            
            # 资源不足时增加迁移概率
            if tribe.resources['food'] < tribe.population * 2:
                migration_probability *= 3.0
            
            if np.random.random() < migration_probability:
                self._execute_tribal_migration(tribe)
    
    def _execute_tribal_migration(self, tribe: Tribe):
        """执行部落迁移"""
        # 选择新的领土中心 - 远离当前位置
        world_width, world_height = 100, 100  # 使用世界尺寸
        
        # 计算理想迁移距离（现有领土半径的2-4倍）
        migration_distance = tribe.territory_radius * np.random.uniform(2.0, 4.0)
        
        # 随机选择迁移方向
        angle = np.random.uniform(0, 2 * np.pi)
        new_center_x = tribe.territory_center.x + migration_distance * np.cos(angle)
        new_center_y = tribe.territory_center.y + migration_distance * np.sin(angle)
        
        # 确保新位置在世界边界内
        new_center_x = np.clip(new_center_x, tribe.territory_radius, world_width - tribe.territory_radius)
        new_center_y = np.clip(new_center_y, tribe.territory_radius, world_height - tribe.territory_radius)
        
        old_center = (tribe.territory_center.x, tribe.territory_center.y)
        tribe.territory_center = Vector2D(new_center_x, new_center_y)
        
        # 更新成员位置到新领土附近
        for member in tribe.members:
            # 在新领土中心周围重新分布成员
            offset_distance = np.random.uniform(0, tribe.territory_radius * 0.8)
            offset_angle = np.random.uniform(0, 2 * np.pi)
            
            new_x = new_center_x + offset_distance * np.cos(offset_angle)
            new_y = new_center_y + offset_distance * np.sin(offset_angle)
            
            # 确保成员位置在世界边界内
            new_x = np.clip(new_x, 0, world_width - 1)
            new_y = np.clip(new_y, 0, world_height - 1)
            
            member.position = Vector2D(new_x, new_y)
        
        print(f"🏃 部落迁移: {tribe.name} 从 ({old_center[0]:.1f}, {old_center[1]:.1f}) 迁移到 ({new_center_x:.1f}, {new_center_y:.1f})")
        
        # 记录迁移事件
        log_tribe_event(
            event_type=EventType.TRIBE_MIGRATION,
            tribe_name=tribe.name,
            description=f"部落{tribe.name}为寻找更好资源迁移到新领土",
            data={
                'tribe_id': tribe.tribe_id,
                'tribe_name': tribe.name,
                'old_territory': old_center,
                'new_territory': (new_center_x, new_center_y),
                'migration_distance': migration_distance,
                'population': tribe.population,
                'migration_reason': 'resource_seeking' if tribe.resources['food'] < tribe.population * 2 else 'expansion'
            },
            location=(new_center_x, new_center_y),
            participants=[m.agent_id for m in tribe.members],
            impact_score=3.0
        )
    
    def get_tribes_info(self) -> Dict:
        """获取所有部落信息"""
        return {
            'total_tribes': len(self.tribes),
            'tribes': {
                tribe_id: {
                    'name': tribe.name,
                    'population': tribe.population,
                    'civilization_level': tribe.civilization_level.value,
                    'territory_center': (tribe.territory_center.x, tribe.territory_center.y),
                    'territory_radius': tribe.territory_radius,
                    'allies': len(tribe.allied_tribes),
                    'enemies': len(tribe.enemy_tribes),
                    'cultural_traits': len(tribe.cultural_traits),
                    'technology_level': tribe.technology_level,
                    'formation_time': tribe.formation_time
                }
                for tribe_id, tribe in self.tribes.items()
            }
        }
    
    def get_visualization_data(self) -> List[Dict]:
        """获取可视化数据"""
        visualization_data = []
        
        for tribe in self.tribes.values():
            visualization_data.append({
                'tribe_id': tribe.tribe_id,
                'name': tribe.name,
                'center': (tribe.territory_center.x, tribe.territory_center.y),
                'radius': tribe.territory_radius,
                'population': tribe.population,
                'civilization_level': tribe.civilization_level.value,
                'color': tribe.color,
                'allies': list(tribe.allied_tribes),
                'enemies': list(tribe.enemy_tribes),
                'members': [(m.position.x, m.position.y) for m in tribe.members]
            })
        
        return visualization_data
    
    def get_tribe_interactions(self) -> List[Dict]:
        """获取部落间交互的可视化数据"""
        interactions = []
        
        for tribe_a in self.tribes.values():
            for tribe_b in self.tribes.values():
                if tribe_a.tribe_id >= tribe_b.tribe_id:  # 避免重复
                    continue
                
                distance = tribe_a.territory_center.distance_to(tribe_b.territory_center)
                if distance <= self.communication_range:
                    # 判断关系类型
                    if tribe_b.tribe_id in tribe_a.allied_tribes:
                        relation_type = 'alliance'
                        color = (100, 255, 100)  # 绿色 - 同盟
                    elif tribe_b.tribe_id in tribe_a.enemy_tribes:
                        relation_type = 'conflict'
                        color = (255, 100, 100)  # 红色 - 冲突
                    else:
                        relation_type = 'neutral'
                        color = (200, 200, 200)  # 灰色 - 中性
                    
                    interactions.append({
                        'tribe_a': tribe_a.tribe_id,
                        'tribe_b': tribe_b.tribe_id,
                        'center_a': (tribe_a.territory_center.x, tribe_a.territory_center.y),
                        'center_b': (tribe_b.territory_center.x, tribe_b.territory_center.y),
                        'relation_type': relation_type,
                        'color': color,
                        'distance': distance
                    })
        
        return interactions