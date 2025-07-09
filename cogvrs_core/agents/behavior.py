"""
Cogvrs - Agent Behavior System
智能体行为系统：定义智能体的基本行为和决策模式

Author: Ben Hsu & Claude
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from ..core.physics_engine import Vector2D

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """行动类型"""
    MOVE = "move"
    EAT = "eat"
    REST = "rest"
    EXPLORE = "explore"
    COMMUNICATE = "communicate"
    REPRODUCE = "reproduce"
    ATTACK = "attack"
    COOPERATE = "cooperate"


@dataclass
class Action:
    """行动"""
    type: ActionType
    target: Optional[Vector2D] = None
    target_agent: Optional[Any] = None
    intensity: float = 1.0
    data: Dict = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


@dataclass
class Motivation:
    """动机"""
    name: str
    value: float
    decay_rate: float = 0.01
    threshold: float = 0.7
    
    def update(self, dt: float):
        """更新动机强度"""
        self.value = max(0, self.value - self.decay_rate * dt)
    
    def stimulate(self, amount: float):
        """刺激动机"""
        self.value = min(1.0, self.value + amount)
    
    def is_active(self) -> bool:
        """动机是否活跃"""
        return self.value >= self.threshold


class BehaviorSystem:
    """
    智能体行为系统
    
    Features:
    - 基本需求驱动行为
    - 目标导向决策
    - 环境适应行为
    - 社会交互行为
    - 学习和经验积累
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.mutation_rate = config.get('mutation_rate', 0.1)
        self.reproduction_threshold = config.get('reproduction_threshold', 120)  # 提高繁殖阈值
        self.energy_decay = config.get('energy_decay', 0.02)
        self.social_tendency = config.get('social_tendency', 0.5)
        
        # 基本动机
        self.motivations = {
            'hunger': Motivation('hunger', 0.3, 0.02, 0.6),
            'energy': Motivation('energy', 0.2, 0.01, 0.7),
            'curiosity': Motivation('curiosity', 0.8, 0.005, 0.5),
            'social': Motivation('social', 0.4, 0.008, 0.6),
            'reproduction': Motivation('reproduction', 0.05, 0.005, 0.95),  # 降低繁殖动机
            'safety': Motivation('safety', 0.3, 0.005, 0.8)
        }
        
        # 行为偏好（个性特征）
        self.behavior_preferences = {
            'exploration': np.random.uniform(0.2, 0.8),
            'cooperation': np.random.uniform(0.1, 0.9),
            'aggression': np.random.uniform(0.0, 0.3),
            'curiosity': np.random.uniform(0.3, 0.9),
            'risk_taking': np.random.uniform(0.1, 0.7),
            'social_activity': np.random.uniform(0.2, 0.8)
        }
        
        # 行为历史和统计
        self.action_history: List[Action] = []
        self.successful_actions = 0
        self.total_actions = 0
        
        # 当前状态
        self.current_goal: Optional[Vector2D] = None
        self.current_target_agent: Optional[Any] = None
        self.last_action: Optional[Action] = None
        
        logger.debug(f"Behavior system initialized with preferences: {self.behavior_preferences}")
    
    def decide_action(self, agent_state: Dict, world_info: Dict, 
                     nearby_agents: List, nearby_resources: List) -> Action:
        """决策下一个行动"""
        # 更新动机
        self._update_motivations(agent_state)
        
        # 获取最强动机
        strongest_motivation = max(
            self.motivations.values(), 
            key=lambda m: m.value if m.is_active() else 0
        )
        
        # 基于动机和环境决策
        action = self._choose_action_for_motivation(
            strongest_motivation, agent_state, world_info, 
            nearby_agents, nearby_resources
        )
        
        # 记录行动
        self.action_history.append(action)
        if len(self.action_history) > 100:
            self.action_history.pop(0)
        
        self.last_action = action
        self.total_actions += 1
        
        return action
    
    def _update_motivations(self, agent_state: Dict):
        """更新动机状态"""
        dt = 1.0  # 假设时间步长为1
        
        # 基本动机更新
        for motivation in self.motivations.values():
            motivation.update(dt)
        
        # 根据智能体状态调整动机
        energy_level = agent_state.get('energy', 50) / 100.0
        health_level = agent_state.get('health', 100) / 100.0
        age = agent_state.get('age', 0)
        
        # 饥饿感与能量成反比
        self.motivations['hunger'].value = max(0.1, 1.0 - energy_level)
        
        # 能量需求
        if energy_level < 0.3:
            self.motivations['energy'].stimulate(0.5)
        
        # 安全需求与健康相关
        if health_level < 0.5:
            self.motivations['safety'].stimulate(0.3)
        
        # 繁殖欲望与年龄相关（更严格的条件）
        if (age > 100 and age < 180 and  # 缩小繁殖年龄窗口
            energy_level > 0.85 and      # 提高能量要求
            health_level > 0.8 and       # 增加健康要求
            agent_state.get('offspring_count', 0) < 3):  # 限制后代数量
            # 添加随机性降低繁殖概率
            if np.random.random() < 0.2:  # 20%概率触发
                self.motivations['reproduction'].stimulate(0.05)
        
        # 好奇心随机波动
        if np.random.random() < 0.1:
            self.motivations['curiosity'].stimulate(np.random.uniform(0.1, 0.3))
    
    def _choose_action_for_motivation(self, motivation: Motivation, agent_state: Dict,
                                    world_info: Dict, nearby_agents: List, 
                                    nearby_resources: List) -> Action:
        """为特定动机选择行动"""
        
        if motivation.name == 'hunger' or motivation.name == 'energy':
            return self._handle_resource_need(nearby_resources, agent_state)
        
        elif motivation.name == 'curiosity':
            return self._handle_exploration(agent_state, world_info)
        
        elif motivation.name == 'social':
            return self._handle_social_interaction(nearby_agents, agent_state)
        
        elif motivation.name == 'reproduction':
            return self._handle_reproduction(nearby_agents, agent_state)
        
        elif motivation.name == 'safety':
            return self._handle_safety(nearby_agents, agent_state, world_info)
        
        else:
            # 默认行为：随机移动
            return self._random_movement(agent_state)
    
    def _handle_resource_need(self, nearby_resources: List, agent_state: Dict) -> Action:
        """处理资源需求"""
        if nearby_resources:
            # 选择最近的食物资源
            agent_pos = Vector2D(agent_state['position'][0], agent_state['position'][1])
            closest_resource = min(
                nearby_resources,
                key=lambda r: agent_pos.distance_to(r.position)
            )
            
            # 如果很近，就吃掉它
            if agent_pos.distance_to(closest_resource.position) < 1.5:
                return Action(ActionType.EAT, target=closest_resource.position)
            else:
                # 否则移动向它
                return Action(ActionType.MOVE, target=closest_resource.position)
        else:
            # 没有资源，探索寻找
            return self._handle_exploration(agent_state, {})
    
    def _handle_exploration(self, agent_state: Dict, world_info: Dict) -> Action:
        """处理探索行为"""
        world_size = world_info.get('size', (100, 100))
        exploration_preference = self.behavior_preferences['exploration']
        
        # 基于好奇心程度决定探索范围
        if exploration_preference > 0.7:
            # 高探索欲：随机远距离移动
            target = Vector2D(
                np.random.uniform(0, world_size[0]),
                np.random.uniform(0, world_size[1])
            )
        else:
            # 低探索欲：短距离随机移动
            agent_pos = Vector2D(agent_state['position'][0], agent_state['position'][1])
            random_offset = Vector2D(
                np.random.uniform(-10, 10),
                np.random.uniform(-10, 10)
            )
            target = agent_pos + random_offset
        
        return Action(ActionType.EXPLORE, target=target)
    
    def _handle_social_interaction(self, nearby_agents: List, agent_state: Dict) -> Action:
        """处理社会交互"""
        if not nearby_agents:
            return self._random_movement(agent_state)
        
        social_preference = self.behavior_preferences['social_activity']
        cooperation_preference = self.behavior_preferences['cooperation']
        
        # 选择最近的智能体
        agent_pos = Vector2D(agent_state['position'][0], agent_state['position'][1])
        closest_agent = min(
            nearby_agents,
            key=lambda a: agent_pos.distance_to(Vector2D(a.position.x, a.position.y))
        )
        
        if social_preference > 0.6:
            if cooperation_preference > 0.5:
                # 合作倾向
                return Action(
                    ActionType.COOPERATE, 
                    target_agent=closest_agent,
                    data={'cooperation_type': 'resource_sharing'}
                )
            else:
                # 普通交流
                return Action(
                    ActionType.COMMUNICATE,
                    target_agent=closest_agent,
                    data={'message_type': 'greeting'}
                )
        else:
            # 社交欲望不强，移动到附近但保持距离
            direction = (Vector2D(closest_agent.position.x, closest_agent.position.y) - agent_pos).normalize()
            target = agent_pos + direction * 3  # 保持3单位距离
            return Action(ActionType.MOVE, target=target)
    
    def _handle_reproduction(self, nearby_agents: List, agent_state: Dict) -> Action:
        """处理繁殖行为"""
        if not nearby_agents:
            return self._handle_exploration(agent_state, {})
        
        # 寻找合适的繁殖伙伴
        suitable_partners = [
            agent for agent in nearby_agents
            if agent.energy > self.reproduction_threshold and 
               agent.age > 30 and agent.age < 200
        ]
        
        if suitable_partners:
            partner = np.random.choice(suitable_partners)
            return Action(
                ActionType.REPRODUCE,
                target_agent=partner,
                data={'reproduction_type': 'sexual'}
            )
        else:
            # 没有合适伙伴，寻找
            return self._handle_social_interaction(nearby_agents, agent_state)
    
    def _handle_safety(self, nearby_agents: List, agent_state: Dict, world_info: Dict) -> Action:
        """处理安全需求"""
        agent_pos = Vector2D(agent_state['position'][0], agent_state['position'][1])
        
        # 检查是否有威胁
        threats = [
            agent for agent in nearby_agents
            if hasattr(agent, 'behavior_system') and 
               agent.behavior_system.behavior_preferences.get('aggression', 0) > 0.5
        ]
        
        if threats:
            # 逃离威胁
            threat_pos = Vector2D(threats[0].position.x, threats[0].position.y)
            escape_direction = (agent_pos - threat_pos).normalize()
            escape_target = agent_pos + escape_direction * 10
            
            return Action(ActionType.MOVE, target=escape_target, intensity=1.5)
        else:
            # 寻找安全区域（远离边界）
            world_size = world_info.get('size', (100, 100))
            center = Vector2D(world_size[0] / 2, world_size[1] / 2)
            
            return Action(ActionType.MOVE, target=center)
    
    def _random_movement(self, agent_state: Dict) -> Action:
        """随机移动"""
        agent_pos = Vector2D(agent_state['position'][0], agent_state['position'][1])
        random_target = agent_pos + Vector2D(
            np.random.uniform(-5, 5),
            np.random.uniform(-5, 5)
        )
        
        return Action(ActionType.MOVE, target=random_target)
    
    def process_feedback(self, action: Action, success: bool, reward: float):
        """处理行动反馈"""
        if success:
            self.successful_actions += 1
            
            # 强化成功的行为偏好
            if action.type == ActionType.EXPLORE:
                self.behavior_preferences['exploration'] = min(
                    1.0, self.behavior_preferences['exploration'] + 0.01
                )
            elif action.type in [ActionType.COMMUNICATE, ActionType.COOPERATE]:
                self.behavior_preferences['cooperation'] = min(
                    1.0, self.behavior_preferences['cooperation'] + 0.01
                )
        else:
            # 减弱失败的行为偏好
            if action.type == ActionType.EXPLORE:
                self.behavior_preferences['exploration'] = max(
                    0.1, self.behavior_preferences['exploration'] - 0.005
                )
    
    def mutate_personality(self, mutation_strength: float = 0.1):
        """个性变异"""
        for key in self.behavior_preferences:
            if np.random.random() < self.mutation_rate:
                change = np.random.normal(0, mutation_strength)
                self.behavior_preferences[key] = np.clip(
                    self.behavior_preferences[key] + change, 0.0, 1.0
                )
    
    def get_personality_summary(self) -> Dict:
        """获取个性摘要"""
        dominant_traits = {
            k: v for k, v in self.behavior_preferences.items() 
            if v > 0.6
        }
        
        behavior_type = "balanced"
        if self.behavior_preferences['exploration'] > 0.7:
            behavior_type = "explorer"
        elif self.behavior_preferences['cooperation'] > 0.7:
            behavior_type = "cooperator"
        elif self.behavior_preferences['aggression'] > 0.5:
            behavior_type = "aggressive"
        elif self.behavior_preferences['social_activity'] > 0.7:
            behavior_type = "social"
        
        return {
            'behavior_type': behavior_type,
            'dominant_traits': dominant_traits,
            'success_rate': self.successful_actions / max(1, self.total_actions),
            'most_active_motivation': max(
                self.motivations.items(), 
                key=lambda x: x[1].value
            )[0],
            'total_actions': self.total_actions
        }
    
    def save_state(self) -> Dict:
        """保存行为系统状态"""
        return {
            'config': self.config,
            'behavior_preferences': self.behavior_preferences.copy(),
            'motivations': {
                name: {
                    'value': mot.value,
                    'decay_rate': mot.decay_rate,
                    'threshold': mot.threshold
                }
                for name, mot in self.motivations.items()
            },
            'stats': {
                'successful_actions': self.successful_actions,
                'total_actions': self.total_actions
            },
            'personality_summary': self.get_personality_summary()
        }
    
    def load_state(self, state: Dict):
        """加载行为系统状态"""
        self.config = state.get('config', self.config)
        self.behavior_preferences = state.get('behavior_preferences', self.behavior_preferences)
        
        # 恢复动机
        motivations_data = state.get('motivations', {})
        for name, mot_data in motivations_data.items():
            if name in self.motivations:
                self.motivations[name].value = mot_data['value']
                self.motivations[name].decay_rate = mot_data['decay_rate']
                self.motivations[name].threshold = mot_data['threshold']
        
        # 恢复统计
        stats = state.get('stats', {})
        self.successful_actions = stats.get('successful_actions', 0)
        self.total_actions = stats.get('total_actions', 0)