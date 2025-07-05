"""
Cogvrs - Physics Engine
基础物理引擎：管理2D世界的物理法则和规律

Author: Ben Hsu & Claude
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Vector2D:
    """2D向量类"""
    x: float
    y: float
    
    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def magnitude(self) -> float:
        """向量长度"""
        return np.sqrt(self.x**2 + self.y**2)
    
    def normalize(self) -> 'Vector2D':
        """单位向量"""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)
    
    def distance_to(self, other: 'Vector2D') -> float:
        """到另一个向量的距离"""
        return (self - other).magnitude()


@dataclass
class PhysicsObject:
    """物理对象"""
    position: Vector2D
    velocity: Vector2D
    mass: float = 1.0
    radius: float = 1.0
    energy: float = 100.0
    
    def update_position(self, dt: float):
        """更新位置"""
        self.position = self.position + self.velocity * dt


class PhysicsEngine:
    """
    物理引擎：管理2D世界的基础物理法则
    
    Features:
    - 2D空间中的运动和碰撞
    - 能量守恒
    - 熵增过程
    - 边界处理
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.world_size = config.get('world_size', (100, 100))
        self.dt = config.get('dt', 0.1)
        self.friction = config.get('friction', 0.1)
        self.boundary_type = config.get('boundary_type', 'toroidal')
        self.max_speed = config.get('max_speed', 2.0)
        
        # 物理常数
        self.energy_conservation = config.get('energy_conservation', True)
        self.entropy_increase = config.get('entropy_increase', True)
        
        # 世界状态
        self.total_energy = 0.0
        self.total_entropy = 0.0
        self.time_step = 0
        
        logger.info(f"Physics engine initialized: {self.world_size}")
    
    def apply_physics(self, objects: List[PhysicsObject]) -> None:
        """
        应用物理法则到所有对象
        
        Args:
            objects: 物理对象列表
        """
        # 更新位置
        for obj in objects:
            self._update_object_motion(obj)
        
        # 处理碰撞
        self._handle_collisions(objects)
        
        # 应用边界条件
        for obj in objects:
            self._apply_boundaries(obj)
        
        # 能量和熵计算
        if self.energy_conservation:
            self._calculate_total_energy(objects)
        
        if self.entropy_increase:
            self._update_entropy(objects)
        
        self.time_step += 1
    
    def _update_object_motion(self, obj: PhysicsObject) -> None:
        """更新对象运动"""
        # 应用摩擦力
        friction_force = obj.velocity * (-self.friction)
        obj.velocity = obj.velocity + friction_force * self.dt
        
        # 限制最大速度
        speed = obj.velocity.magnitude()
        if speed > self.max_speed:
            obj.velocity = obj.velocity.normalize() * self.max_speed
        
        # 更新位置
        obj.update_position(self.dt)
        
        # 能量消耗
        obj.energy -= 0.1 * self.dt  # 基础能量消耗
    
    def _handle_collisions(self, objects: List[PhysicsObject]) -> None:
        """处理对象间碰撞"""
        for i, obj1 in enumerate(objects):
            for obj2 in objects[i+1:]:
                distance = obj1.position.distance_to(obj2.position)
                
                if distance < (obj1.radius + obj2.radius):
                    self._resolve_collision(obj1, obj2)
    
    def _resolve_collision(self, obj1: PhysicsObject, obj2: PhysicsObject) -> None:
        """解决碰撞"""
        # 计算碰撞方向
        collision_vector = obj2.position - obj1.position
        distance = collision_vector.magnitude()
        
        if distance == 0:
            return
        
        # 分离重叠的对象
        overlap = (obj1.radius + obj2.radius) - distance
        separation = collision_vector.normalize() * (overlap / 2)
        
        obj1.position = obj1.position - separation
        obj2.position = obj2.position + separation
        
        # 弹性碰撞动量交换
        normal = collision_vector.normalize()
        relative_velocity = obj1.velocity - obj2.velocity
        
        # 计算冲量
        impulse_magnitude = 2 * np.dot([relative_velocity.x, relative_velocity.y], 
                                      [normal.x, normal.y]) / (obj1.mass + obj2.mass)
        
        impulse = normal * impulse_magnitude
        
        obj1.velocity = obj1.velocity - impulse * obj2.mass
        obj2.velocity = obj2.velocity + impulse * obj1.mass
    
    def _apply_boundaries(self, obj: PhysicsObject) -> None:
        """应用边界条件"""
        width, height = self.world_size
        
        if self.boundary_type == 'toroidal':
            # 环形边界（穿越边界出现在对面）
            obj.position.x = obj.position.x % width
            obj.position.y = obj.position.y % height
            
        elif self.boundary_type == 'reflective':
            # 反射边界
            if obj.position.x < 0 or obj.position.x > width:
                obj.velocity.x *= -1
                obj.position.x = max(0, min(width, obj.position.x))
            
            if obj.position.y < 0 or obj.position.y > height:
                obj.velocity.y *= -1
                obj.position.y = max(0, min(height, obj.position.y))
                
        elif self.boundary_type == 'absorbing':
            # 吸收边界（对象消失）
            if (obj.position.x < 0 or obj.position.x > width or 
                obj.position.y < 0 or obj.position.y > height):
                obj.energy = 0  # 标记为死亡
    
    def _calculate_total_energy(self, objects: List[PhysicsObject]) -> None:
        """计算系统总能量"""
        kinetic_energy = sum(
            0.5 * obj.mass * obj.velocity.magnitude()**2 
            for obj in objects
        )
        
        potential_energy = sum(obj.energy for obj in objects)
        
        self.total_energy = kinetic_energy + potential_energy
    
    def _update_entropy(self, objects: List[PhysicsObject]) -> None:
        """更新系统熵（简化模型）"""
        # 位置熵：对象分布的均匀程度
        positions = [(obj.position.x, obj.position.y) for obj in objects]
        position_entropy = self._calculate_spatial_entropy(positions)
        
        # 速度熵：速度分布的混乱程度
        velocities = [obj.velocity.magnitude() for obj in objects]
        velocity_entropy = self._calculate_distribution_entropy(velocities)
        
        self.total_entropy = position_entropy + velocity_entropy
    
    def _calculate_spatial_entropy(self, positions: List[Tuple[float, float]]) -> float:
        """计算空间分布熵"""
        if not positions:
            return 0.0
        
        # 将世界划分为网格，计算每个网格的对象密度
        grid_size = 10
        width, height = self.world_size
        grid = np.zeros((grid_size, grid_size))
        
        for x, y in positions:
            grid_x = int(x / width * grid_size) % grid_size
            grid_y = int(y / height * grid_size) % grid_size
            grid[grid_x, grid_y] += 1
        
        # 计算概率分布和熵
        total = len(positions)
        probabilities = grid.flatten() / total
        probabilities = probabilities[probabilities > 0]  # 移除零概率
        
        return -np.sum(probabilities * np.log2(probabilities))
    
    def _calculate_distribution_entropy(self, values: List[float]) -> float:
        """计算数值分布熵"""
        if not values:
            return 0.0
        
        # 简化：使用标准差作为熵的度量
        return float(np.std(values))
    
    def get_world_state(self) -> Dict:
        """获取世界物理状态"""
        return {
            'total_energy': self.total_energy,
            'total_entropy': self.total_entropy,
            'time_step': self.time_step,
            'world_size': self.world_size,
            'physics_config': self.config
        }
    
    def add_random_force(self, obj: PhysicsObject, strength: float = 1.0) -> None:
        """添加随机力（模拟环境不确定性）"""
        random_angle = np.random.uniform(0, 2 * np.pi)
        force = Vector2D(
            np.cos(random_angle) * strength,
            np.sin(random_angle) * strength
        )
        
        obj.velocity = obj.velocity + force * (self.dt / obj.mass)