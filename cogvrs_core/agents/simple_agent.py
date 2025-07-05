"""
Cogvrs - Simple Agent
简单智能体：整合神经网络、记忆和行为的完整智能体

Author: Ben Hsu & Claude
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
import uuid

from ..core.physics_engine import PhysicsObject, Vector2D
from .neural_brain import NeuralBrain
from .memory import MemorySystem
from .behavior import BehaviorSystem, Action, ActionType

logger = logging.getLogger(__name__)


class SimpleAgent(PhysicsObject):
    """
    简单智能体
    
    Features:
    - 神经网络决策大脑
    - 记忆系统
    - 行为系统
    - 学习和适应
    - 社会交互
    - 生命周期管理
    """
    
    def __init__(self, config: Dict, position: Vector2D = None):
        # 物理属性
        super().__init__(
            position=position or Vector2D(
                np.random.uniform(0, config.get('world_size', [100, 100])[0]),
                np.random.uniform(0, config.get('world_size', [100, 100])[1])
            ),
            velocity=Vector2D(0, 0),
            mass=config.get('mass', 1.0),
            radius=config.get('radius', 1.0),
            energy=config.get('initial_energy', 100.0)
        )
        
        # 智能体属性
        self.agent_id = str(uuid.uuid4())[:8]
        self.age = 0
        self.health = 100.0
        self.max_health = 100.0
        self.max_energy = config.get('max_energy', 150.0)
        self.alive = True
        
        # 生物学属性
        self.species = config.get('species', 'homo_digitalis')
        self.generation = config.get('generation', 0)
        self.parent_ids = config.get('parent_ids', [])
        
        # 核心系统
        self.brain = NeuralBrain(config.get('neural_network', {}))
        self.memory = MemorySystem(config.get('memory', {}))
        self.behavior_system = BehaviorSystem(config.get('behavior', {}))
        
        # 感知系统
        self.perception_radius = config.get('perception_radius', 10.0)
        self.communication_radius = config.get('communication_radius', 5.0)
        
        # 统计信息
        self.birth_time = 0
        self.total_distance_traveled = 0.0
        self.resources_consumed = 0
        self.offspring_count = 0
        self.social_interactions = 0
        
        # 学习相关
        self.learning_rate = config.get('learning_rate', 0.01)
        self.last_reward = 0.0
        
        logger.debug(f"Agent {self.agent_id} created at {self.position}")
    
    def update(self, dt: float, world_state: Dict, nearby_agents: List, nearby_resources: List):
        """更新智能体状态"""
        if not self.alive:
            return
        
        # 年龄增长
        self.age += dt
        
        # 基础代谢
        self._apply_metabolism(dt)
        
        # 感知环境
        perception_data = self._perceive_environment(world_state, nearby_agents, nearby_resources)
        
        # 神经网络决策
        neural_input = self._prepare_neural_input(perception_data)
        neural_output = self.brain.predict(neural_input)
        
        # 行为决策
        agent_state = self._get_agent_state()
        action = self.behavior_system.decide_action(
            agent_state, world_state, nearby_agents, nearby_resources
        )
        
        # 执行行动
        success, reward = self._execute_action(action, world_state, nearby_agents, nearby_resources)
        
        # 学习反馈
        self._process_learning(action, success, reward, neural_output)
        
        # 记忆整合
        self._update_memories(perception_data, action, reward)
        
        # 健康状态检查
        self._check_health()
        
        # 记忆巩固
        if self.age % 10 == 0:  # 每10个时间单位整理一次记忆
            self.memory.consolidate_memories()
    
    def _apply_metabolism(self, dt: float):
        """应用基础代谢"""
        # 基础能量消耗
        base_consumption = 0.5 * dt
        movement_consumption = self.velocity.magnitude() * 0.1 * dt
        brain_consumption = self.brain.calculate_complexity() * 0.01 * dt
        
        total_consumption = base_consumption + movement_consumption + brain_consumption
        self.energy = max(0, self.energy - total_consumption)
        
        # 健康与能量相关
        if self.energy < 20:
            self.health -= 1.0 * dt
        elif self.energy > 80:
            self.health = min(self.max_health, self.health + 0.5 * dt)
        
        # 年龄对健康的影响
        if self.age > 200:
            self.health -= (self.age - 200) * 0.01 * dt
    
    def _perceive_environment(self, world_state: Dict, nearby_agents: List, nearby_resources: List) -> Dict:
        """感知环境"""
        perception = {
            'position': (self.position.x, self.position.y),
            'energy_level': self.energy / self.max_energy,
            'health_level': self.health / self.max_health,
            'age': self.age,
            'nearby_agents_count': len(nearby_agents),
            'nearby_resources_count': len(nearby_resources),
            'world_time': world_state.get('time_step', 0),
            'world_size': world_state.get('size', (100, 100))
        }
        
        # 感知最近的资源
        if nearby_resources:
            closest_resource = min(
                nearby_resources,
                key=lambda r: self.position.distance_to(r.position)
            )
            perception['closest_resource_distance'] = self.position.distance_to(closest_resource.position)
            perception['closest_resource_type'] = closest_resource.type
            perception['closest_resource_amount'] = closest_resource.amount
        else:
            perception['closest_resource_distance'] = float('inf')
            perception['closest_resource_type'] = 'none'
            perception['closest_resource_amount'] = 0
        
        # 感知最近的智能体
        if nearby_agents:
            closest_agent = min(
                nearby_agents,
                key=lambda a: self.position.distance_to(Vector2D(a.position.x, a.position.y))
            )
            perception['closest_agent_distance'] = self.position.distance_to(
                Vector2D(closest_agent.position.x, closest_agent.position.y)
            )
            perception['closest_agent_energy'] = closest_agent.energy / closest_agent.max_energy
        else:
            perception['closest_agent_distance'] = float('inf')
            perception['closest_agent_energy'] = 0
        
        return perception
    
    def _prepare_neural_input(self, perception_data: Dict) -> np.ndarray:
        """准备神经网络输入"""
        # 标准化感知数据
        world_size = perception_data['world_size']
        
        neural_input = np.array([
            perception_data['position'][0] / world_size[0],  # 标准化位置
            perception_data['position'][1] / world_size[1],
            perception_data['energy_level'],
            perception_data['health_level'],
            min(1.0, perception_data['age'] / 300),  # 标准化年龄
            min(1.0, perception_data['nearby_agents_count'] / 10),
            min(1.0, perception_data['nearby_resources_count'] / 5),
            min(1.0, perception_data['closest_resource_distance'] / 20),
            min(1.0, perception_data['closest_agent_distance'] / 20),
            perception_data['closest_agent_energy'],
            
            # 添加记忆信息
            *self._get_memory_features(),
            
            # 添加动机信息
            *self._get_motivation_features(),
            
            # 添加一些随机性（创造性）
            np.random.normal(0, 0.1),
            np.random.normal(0, 0.1)
        ])
        
        # 确保输入大小匹配
        expected_size = self.brain.input_size
        if len(neural_input) < expected_size:
            # 用零填充
            neural_input = np.pad(neural_input, (0, expected_size - len(neural_input)))
        elif len(neural_input) > expected_size:
            # 截断
            neural_input = neural_input[:expected_size]
        
        return neural_input
    
    def _get_memory_features(self) -> List[float]:
        """获取记忆特征"""
        memory_summary = self.memory.get_memory_summary()
        return [
            min(1.0, memory_summary['working_memory_size'] / 10),
            min(1.0, memory_summary['long_term_memory_size'] / 100),
            memory_summary['avg_importance'],
            min(1.0, memory_summary['spatial_coverage'] / 20)
        ]
    
    def _get_motivation_features(self) -> List[float]:
        """获取动机特征"""
        motivations = self.behavior_system.motivations
        return [
            motivations['hunger'].value,
            motivations['energy'].value,
            motivations['curiosity'].value,
            motivations['social'].value
        ]
    
    def _execute_action(self, action: Action, world_state: Dict, 
                       nearby_agents: List, nearby_resources: List) -> Tuple[bool, float]:
        """执行行动"""
        success = False
        reward = 0.0
        
        if action.type == ActionType.MOVE:
            success, reward = self._execute_move(action)
        elif action.type == ActionType.EAT:
            success, reward = self._execute_eat(action, nearby_resources)
        elif action.type == ActionType.REST:
            success, reward = self._execute_rest()
        elif action.type == ActionType.COMMUNICATE:
            success, reward = self._execute_communicate(action, nearby_agents)
        elif action.type == ActionType.COOPERATE:
            success, reward = self._execute_cooperate(action, nearby_agents)
        elif action.type == ActionType.REPRODUCE:
            success, reward = self._execute_reproduce(action, nearby_agents)
        elif action.type == ActionType.EXPLORE:
            success, reward = self._execute_explore(action)
        
        # 处理行为反馈
        self.behavior_system.process_feedback(action, success, reward)
        self.last_reward = reward
        
        return success, reward
    
    def _execute_move(self, action: Action) -> Tuple[bool, float]:
        """执行移动"""
        if action.target is None:
            return False, -0.1
        
        # 计算移动方向
        direction = (action.target - self.position).normalize()
        speed = min(2.0, action.intensity * 1.5)
        
        # 更新速度
        old_position = Vector2D(self.position.x, self.position.y)
        self.velocity = direction * speed
        
        # 计算移动距离
        distance_moved = old_position.distance_to(self.position)
        self.total_distance_traveled += distance_moved
        
        # 移动消耗能量
        energy_cost = distance_moved * 0.1
        self.energy = max(0, self.energy - energy_cost)
        
        return True, 0.1  # 移动成功的小奖励
    
    def _execute_eat(self, action: Action, nearby_resources: List) -> Tuple[bool, float]:
        """执行进食"""
        if not nearby_resources or action.target is None:
            return False, -0.2
        
        # 找到目标资源
        target_resource = None
        for resource in nearby_resources:
            if self.position.distance_to(resource.position) < 1.5:
                target_resource = resource
                break
        
        if target_resource and target_resource.amount > 0:
            # 消耗资源
            consumed = target_resource.consume(min(20, target_resource.amount))
            
            # 恢复能量
            energy_gain = consumed * 0.8
            self.energy = min(self.max_energy, self.energy + energy_gain)
            self.resources_consumed += consumed
            
            # 存储空间记忆
            self.memory.store_spatial_memory(
                (target_resource.position.x, target_resource.position.y),
                f"good_resource_{target_resource.type}",
                energy_gain / 20,  # 标准化价值
                self.age
            )
            
            return True, energy_gain / 20  # 根据能量增益给奖励
        
        return False, -0.2
    
    def _execute_rest(self) -> Tuple[bool, float]:
        """执行休息"""
        # 休息恢复健康
        self.health = min(self.max_health, self.health + 2.0)
        self.velocity = Vector2D(0, 0)  # 停止移动
        
        # 休息时进行记忆整理
        self.memory.consolidate_memories()
        
        return True, 0.1
    
    def _execute_communicate(self, action: Action, nearby_agents: List) -> Tuple[bool, float]:
        """执行交流"""
        if action.target_agent is None or action.target_agent not in nearby_agents:
            return False, -0.1
        
        # 简单交流：交换位置信息
        message_data = {
            'sender_id': self.agent_id,
            'position': (self.position.x, self.position.y),
            'energy_level': self.energy / self.max_energy,
            'message_type': action.data.get('message_type', 'greeting')
        }
        
        # 对方接收消息（简化实现）
        if hasattr(action.target_agent, 'receive_message'):
            action.target_agent.receive_message(message_data)
        
        self.social_interactions += 1
        
        # 满足社交需求
        self.behavior_system.motivations['social'].value = max(
            0, self.behavior_system.motivations['social'].value - 0.2
        )
        
        return True, 0.3
    
    def _execute_cooperate(self, action: Action, nearby_agents: List) -> Tuple[bool, float]:
        """执行合作"""
        if action.target_agent is None or action.target_agent not in nearby_agents:
            return False, -0.1
        
        cooperation_type = action.data.get('cooperation_type', 'resource_sharing')
        
        if cooperation_type == 'resource_sharing' and self.energy > 30:
            # 分享能量
            shared_energy = min(10, self.energy * 0.1)
            self.energy -= shared_energy
            
            if hasattr(action.target_agent, 'receive_cooperation'):
                action.target_agent.receive_cooperation(shared_energy, self.agent_id)
            
            return True, 0.5  # 合作有较高奖励
        
        return False, -0.1
    
    def _execute_reproduce(self, action: Action, nearby_agents: List) -> Tuple[bool, float]:
        """执行繁殖"""
        if (action.target_agent is None or 
            action.target_agent not in nearby_agents or
            self.energy < 80):
            return False, -0.3
        
        partner = action.target_agent
        
        # 检查伙伴是否同意繁殖
        if (hasattr(partner, 'energy') and partner.energy > 80 and
            hasattr(partner, 'behavior_system') and
            partner.behavior_system.motivations['reproduction'].is_active()):
            
            # 繁殖成功！
            self.offspring_count += 1
            
            # 繁殖消耗大量能量
            self.energy -= 40
            if hasattr(partner, 'energy'):
                partner.energy -= 30
            
            # 存储繁殖记忆
            self.memory.store_experience(
                f"reproduced_with_{partner.agent_id}",
                importance=0.9,
                emotional_value=0.8,
                timestamp=self.age
            )
            
            return True, 1.0  # 繁殖成功高奖励
        
        return False, -0.3
    
    def _execute_explore(self, action: Action) -> Tuple[bool, float]:
        """执行探索"""
        if action.target is None:
            return False, -0.1
        
        # 探索就是移动到新位置
        success, move_reward = self._execute_move(action)
        
        if success:
            # 探索有额外奖励（满足好奇心）
            self.behavior_system.motivations['curiosity'].value = max(
                0, self.behavior_system.motivations['curiosity'].value - 0.1
            )
            
            # 存储探索记忆
            self.memory.store_spatial_memory(
                (action.target.x, action.target.y),
                "explored_area",
                0.3,
                self.age
            )
            
            return True, move_reward + 0.2
        
        return False, -0.1
    
    def _process_learning(self, action: Action, success: bool, reward: float, neural_output: np.ndarray):
        """处理学习"""
        # 大脑学习
        self.brain.learn_from_feedback(reward)
        
        # 如果有目标行动，可以进行监督学习
        if success and reward > 0.5:
            # 创建目标输出（强化成功的行动）
            target_output = neural_output.copy()
            action_index = self._action_to_index(action.type)
            if action_index is not None:
                target_output[action_index] = min(1.0, target_output[action_index] + 0.1)
                self.brain.learn_from_feedback(reward, target_output)
    
    def _action_to_index(self, action_type: ActionType) -> Optional[int]:
        """将行动类型转换为输出索引"""
        action_map = {
            ActionType.MOVE: 0,
            ActionType.EAT: 1,
            ActionType.REST: 2,
            ActionType.EXPLORE: 3,
            ActionType.COMMUNICATE: 4,
            ActionType.COOPERATE: 5,
            ActionType.REPRODUCE: 6,
            ActionType.ATTACK: 7
        }
        return action_map.get(action_type)
    
    def _update_memories(self, perception_data: Dict, action: Action, reward: float):
        """更新记忆"""
        # 存储重要经验
        if abs(reward) > 0.3:  # 重要事件
            experience = {
                'action': action.type.value,
                'reward': reward,
                'perception': perception_data,
                'context': f"age_{int(self.age)}"
            }
            
            importance = min(1.0, abs(reward))
            emotional_value = reward
            
            self.memory.store_experience(
                experience,
                importance=importance,
                emotional_value=emotional_value,
                timestamp=self.age
            )
    
    def _check_health(self):
        """检查健康状态"""
        if self.health <= 0 or self.energy <= 0:
            self.alive = False
            logger.info(f"Agent {self.agent_id} died at age {self.age}")
        
        # 老年死亡
        if self.age > 300 and np.random.random() < 0.01:
            self.alive = False
            logger.info(f"Agent {self.agent_id} died of old age at {self.age}")
    
    def receive_message(self, message: Dict):
        """接收来自其他智能体的消息"""
        # 存储社交记忆
        self.memory.store_experience(
            f"message_from_{message.get('sender_id', 'unknown')}",
            importance=0.4,
            emotional_value=0.2,
            timestamp=self.age
        )
        
        # 如果消息包含位置信息，存储空间记忆
        if 'position' in message:
            self.memory.store_spatial_memory(
                message['position'],
                f"agent_location_{message.get('sender_id', 'unknown')}",
                0.3,
                self.age
            )
    
    def receive_cooperation(self, energy_amount: float, from_agent_id: str):
        """接收合作（能量分享）"""
        self.energy = min(self.max_energy, self.energy + energy_amount)
        
        # 存储合作记忆
        self.memory.store_experience(
            f"received_cooperation_from_{from_agent_id}",
            importance=0.7,
            emotional_value=0.6,
            timestamp=self.age
        )
    
    def _get_agent_state(self) -> Dict:
        """获取智能体状态"""
        return {
            'position': (self.position.x, self.position.y),
            'energy': self.energy,
            'health': self.health,
            'age': self.age,
            'alive': self.alive
        }
    
    def get_detailed_state(self) -> Dict:
        """获取详细状态信息"""
        return {
            'agent_id': self.agent_id,
            'position': (self.position.x, self.position.y),
            'velocity': (self.velocity.x, self.velocity.y),
            'energy': self.energy,
            'health': self.health,
            'age': self.age,
            'alive': self.alive,
            'generation': self.generation,
            'species': self.species,
            
            # 统计信息
            'total_distance_traveled': self.total_distance_traveled,
            'resources_consumed': self.resources_consumed,
            'offspring_count': self.offspring_count,
            'social_interactions': self.social_interactions,
            
            # 系统状态
            'brain_performance': self.brain.get_performance_metrics(),
            'memory_summary': self.memory.get_memory_summary(),
            'personality': self.behavior_system.get_personality_summary(),
            'last_reward': self.last_reward
        }
    
    def clone(self, mutation_rate: float = 0.1) -> 'SimpleAgent':
        """克隆智能体（用于繁殖）"""
        # 创建新配置
        child_config = {
            'world_size': [100, 100],  # 默认世界大小
            'generation': self.generation + 1,
            'parent_ids': [self.agent_id],
            'species': self.species,
            'neural_network': self.brain.config.copy(),
            'memory': self.memory.config.copy(),
            'behavior': self.behavior_system.config.copy()
        }
        
        # 创建子代智能体
        child = SimpleAgent(child_config, Vector2D(
            self.position.x + np.random.uniform(-2, 2),
            self.position.y + np.random.uniform(-2, 2)
        ))
        
        # 继承大脑（有变异）
        child.brain = self.brain.clone()
        child.brain.mutate(mutation_rate)
        
        # 继承部分行为偏好（有变异）
        for key, value in self.behavior_system.behavior_preferences.items():
            mutation = np.random.normal(0, 0.1) if np.random.random() < mutation_rate else 0
            child.behavior_system.behavior_preferences[key] = np.clip(
                value + mutation, 0.0, 1.0
            )
        
        return child
    
    def save_state(self) -> Dict:
        """保存智能体完整状态"""
        return {
            'agent_id': self.agent_id,
            'position': (self.position.x, self.position.y),
            'velocity': (self.velocity.x, self.velocity.y),
            'physical_state': {
                'mass': self.mass,
                'radius': self.radius,
                'energy': self.energy,
                'health': self.health,
                'age': self.age,
                'alive': self.alive
            },
            'biological_state': {
                'species': self.species,
                'generation': self.generation,
                'parent_ids': self.parent_ids
            },
            'brain_state': self.brain.save_state(),
            'memory_state': self.memory.save_state(),
            'behavior_state': self.behavior_system.save_state(),
            'statistics': {
                'birth_time': self.birth_time,
                'total_distance_traveled': self.total_distance_traveled,
                'resources_consumed': self.resources_consumed,
                'offspring_count': self.offspring_count,
                'social_interactions': self.social_interactions
            }
        }
    
    def load_state(self, state: Dict):
        """加载智能体状态"""
        self.agent_id = state['agent_id']
        self.position = Vector2D(*state['position'])
        self.velocity = Vector2D(*state['velocity'])
        
        # 物理状态
        physical = state['physical_state']
        self.mass = physical['mass']
        self.radius = physical['radius']
        self.energy = physical['energy']
        self.health = physical['health']
        self.age = physical['age']
        self.alive = physical['alive']
        
        # 生物状态
        biological = state['biological_state']
        self.species = biological['species']
        self.generation = biological['generation']
        self.parent_ids = biological['parent_ids']
        
        # 系统状态
        self.brain.load_state(state['brain_state'])
        self.memory.load_state(state['memory_state'])
        self.behavior_system.load_state(state['behavior_state'])
        
        # 统计
        stats = state['statistics']
        self.birth_time = stats['birth_time']
        self.total_distance_traveled = stats['total_distance_traveled']
        self.resources_consumed = stats['resources_consumed']
        self.offspring_count = stats['offspring_count']
        self.social_interactions = stats['social_interactions']