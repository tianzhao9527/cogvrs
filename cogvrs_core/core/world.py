"""
Cogvrs - 2D World Environment
2D世界环境：管理虚拟世界的地理、资源和环境条件

Author: Ben Hsu & Claude
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

from .physics_engine import Vector2D, PhysicsEngine

logger = logging.getLogger(__name__)


class TerrainType(Enum):
    """地形类型"""
    EMPTY = 0
    RESOURCE = 1
    OBSTACLE = 2
    SPECIAL = 3


@dataclass
class Resource:
    """资源对象"""
    position: Vector2D
    type: str
    amount: float
    regeneration_rate: float = 0.1
    max_amount: float = 100.0
    
    def regenerate(self, dt: float):
        """资源再生"""
        if self.amount < self.max_amount:
            self.amount = min(self.max_amount, 
                            self.amount + self.regeneration_rate * dt)
    
    def consume(self, amount: float) -> float:
        """消耗资源，返回实际消耗量"""
        consumed = min(self.amount, amount)
        self.amount -= consumed
        return consumed


@dataclass
class EnvironmentalCondition:
    """环境条件"""
    temperature: float = 20.0  # 温度
    humidity: float = 0.5      # 湿度
    radiation: float = 0.0     # 辐射
    toxicity: float = 0.0      # 毒性
    
    def get_survival_factor(self) -> float:
        """计算生存适宜度因子 (0-1)"""
        # 理想条件：温度15-25，湿度0.3-0.7，低辐射和毒性
        temp_factor = 1.0 - abs(self.temperature - 20) / 50
        humid_factor = 1.0 - abs(self.humidity - 0.5) / 0.5
        rad_factor = max(0, 1.0 - self.radiation)
        tox_factor = max(0, 1.0 - self.toxicity)
        
        return max(0, min(1, temp_factor * humid_factor * rad_factor * tox_factor))


class World2D:
    """
    2D世界环境管理器
    
    Features:
    - 地形和资源管理
    - 环境条件模拟
    - 空间查询和导航
    - 动态环境变化
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.size = config.get('size', (100, 100))
        self.resource_density = config.get('resource_density', 0.1)
        self.max_agents = config.get('max_agents', 200)  # 提高默认最大智能体数量
        
        # 初始化世界网格
        self.width, self.height = self.size
        self.terrain_grid = np.zeros((self.width, self.height), dtype=int)
        
        # 资源管理
        self.resources: List[Resource] = []
        self.resource_grid = np.zeros((self.width, self.height))
        
        # 环境条件
        self.environmental_conditions = np.full(
            (self.width, self.height), 
            EnvironmentalCondition(), 
            dtype=object
        )
        
        # 时间和变化
        self.time_step = 0
        self.day_cycle = config.get('day_cycle', 1000)  # 昼夜循环
        
        # 初始化世界
        self._initialize_terrain()
        self._initialize_resources()
        self._initialize_environment()
        
        logger.info(f"World2D initialized: {self.size}")
    
    def _initialize_terrain(self):
        """初始化地形"""
        # 简单地形：大部分为空地，少量障碍
        obstacle_probability = 0.05
        
        for x in range(self.width):
            for y in range(self.height):
                if np.random.random() < obstacle_probability:
                    self.terrain_grid[x, y] = TerrainType.OBSTACLE.value
                else:
                    self.terrain_grid[x, y] = TerrainType.EMPTY.value
    
    def _initialize_resources(self):
        """初始化资源分布"""
        total_tiles = self.width * self.height
        num_resources = int(total_tiles * self.resource_density)
        
        resource_types = ['food', 'energy', 'material']
        
        for _ in range(num_resources):
            # 随机位置
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            
            # 避免在障碍物上放置资源
            if self.terrain_grid[x, y] == TerrainType.OBSTACLE.value:
                continue
            
            # 创建资源
            resource_type = np.random.choice(resource_types)
            resource = Resource(
                position=Vector2D(x, y),
                type=resource_type,
                amount=np.random.uniform(20, 100),
                regeneration_rate=np.random.uniform(0.05, 0.2)
            )
            
            self.resources.append(resource)
            self.terrain_grid[x, y] = TerrainType.RESOURCE.value
            self.resource_grid[x, y] = resource.amount
    
    def _initialize_environment(self):
        """初始化环境条件"""
        for x in range(self.width):
            for y in range(self.height):
                # 添加一些环境变化
                temp_variation = np.random.normal(0, 5)
                humid_variation = np.random.normal(0, 0.1)
                
                self.environmental_conditions[x, y] = EnvironmentalCondition(
                    temperature=20 + temp_variation,
                    humidity=0.5 + humid_variation,
                    radiation=max(0, np.random.normal(0, 0.1)),
                    toxicity=max(0, np.random.normal(0, 0.05))
                )
    
    def update(self, dt: float):
        """更新世界状态"""
        # 更新资源
        for resource in self.resources:
            resource.regenerate(dt)
            x, y = int(resource.position.x), int(resource.position.y)
            if 0 <= x < self.width and 0 <= y < self.height:
                self.resource_grid[x, y] = resource.amount
        
        # 环境变化
        self._update_environment(dt)
        
        # 昼夜循环效应
        self._apply_day_night_cycle()
        
        self.time_step += 1
    
    def _update_environment(self, dt: float):
        """更新环境条件"""
        # 简单的环境动态变化
        for x in range(self.width):
            for y in range(self.height):
                env = self.environmental_conditions[x, y]
                
                # 温度缓慢变化
                env.temperature += np.random.normal(0, 0.1) * dt
                env.temperature = np.clip(env.temperature, -10, 50)
                
                # 湿度变化
                env.humidity += np.random.normal(0, 0.01) * dt
                env.humidity = np.clip(env.humidity, 0, 1)
    
    def _apply_day_night_cycle(self):
        """应用昼夜循环效应"""
        cycle_position = (self.time_step % self.day_cycle) / self.day_cycle
        
        # 计算当前时间（0=午夜，0.5=正午）
        if cycle_position < 0.5:
            # 白天：温度上升
            temp_modifier = 1.0 + 0.2 * np.sin(cycle_position * 2 * np.pi)
        else:
            # 夜晚：温度下降
            temp_modifier = 1.0 - 0.1 * np.sin((cycle_position - 0.5) * 2 * np.pi)
        
        # 应用全局温度修正
        for x in range(self.width):
            for y in range(self.height):
                base_temp = 20.0  # 基础温度
                self.environmental_conditions[x, y].temperature = \
                    base_temp * temp_modifier + np.random.normal(0, 2)
    
    def get_resources_in_radius(self, center: Vector2D, radius: float) -> List[Resource]:
        """获取指定半径内的资源"""
        nearby_resources = []
        
        for resource in self.resources:
            if resource.amount > 0:  # 只考虑有剩余的资源
                distance = center.distance_to(resource.position)
                if distance <= radius:
                    nearby_resources.append(resource)
        
        return nearby_resources
    
    def get_environment_at(self, position: Vector2D) -> EnvironmentalCondition:
        """获取指定位置的环境条件"""
        x, y = int(position.x), int(position.y)
        
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.environmental_conditions[x, y]
        else:
            # 边界外返回恶劣环境
            return EnvironmentalCondition(
                temperature=-10, humidity=0, radiation=1.0, toxicity=1.0
            )
    
    def is_position_valid(self, position: Vector2D) -> bool:
        """检查位置是否有效（不是障碍物）"""
        x, y = int(position.x), int(position.y)
        
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        return self.terrain_grid[x, y] != TerrainType.OBSTACLE.value
    
    def find_path(self, start: Vector2D, goal: Vector2D, max_distance: int = 20) -> List[Vector2D]:
        """简单路径查找（A*算法的简化版本）"""
        # 如果目标太远，返回直线方向
        if start.distance_to(goal) > max_distance:
            direction = (goal - start).normalize()
            return [start + direction * max_distance]
        
        # 简单实现：返回直线路径，避开障碍物
        path = []
        current = start
        step_size = 1.0
        
        while current.distance_to(goal) > step_size:
            direction = (goal - current).normalize()
            next_pos = current + direction * step_size
            
            if self.is_position_valid(next_pos):
                path.append(next_pos)
                current = next_pos
            else:
                # 尝试绕过障碍物
                perpendicular = Vector2D(-direction.y, direction.x)
                side_pos1 = current + perpendicular * step_size
                side_pos2 = current - perpendicular * step_size
                
                if self.is_position_valid(side_pos1):
                    path.append(side_pos1)
                    current = side_pos1
                elif self.is_position_valid(side_pos2):
                    path.append(side_pos2)
                    current = side_pos2
                else:
                    break  # 无法绕过
        
        path.append(goal)
        return path
    
    def add_resource(self, position: Vector2D, resource_type: str, amount: float):
        """在指定位置添加资源"""
        if self.is_position_valid(position):
            resource = Resource(
                position=position,
                type=resource_type,
                amount=amount
            )
            self.resources.append(resource)
            
            x, y = int(position.x), int(position.y)
            self.terrain_grid[x, y] = TerrainType.RESOURCE.value
            self.resource_grid[x, y] = amount
    
    def get_world_state(self) -> Dict:
        """获取世界状态摘要"""
        total_resources = sum(r.amount for r in self.resources)
        resource_types = {}
        
        for resource in self.resources:
            if resource.type not in resource_types:
                resource_types[resource.type] = 0
            resource_types[resource.type] += resource.amount
        
        # 计算平均环境条件
        avg_temp = np.mean([
            env.temperature for row in self.environmental_conditions for env in row
        ])
        avg_humidity = np.mean([
            env.humidity for row in self.environmental_conditions for env in row
        ])
        
        return {
            'size': self.size,
            'time_step': self.time_step,
            'total_resources': total_resources,
            'resource_types': resource_types,
            'num_resources': len(self.resources),
            'avg_temperature': avg_temp,
            'avg_humidity': avg_humidity,
            'day_cycle_position': (self.time_step % self.day_cycle) / self.day_cycle
        }
    
    def get_visualization_data(self) -> Dict:
        """获取可视化数据"""
        return {
            'terrain_grid': self.terrain_grid.copy(),
            'resource_grid': self.resource_grid.copy(),
            'resources': [(r.position.x, r.position.y, r.type, r.amount) 
                         for r in self.resources],
            'world_size': self.size
        }