#!/usr/bin/env python3
"""
地形系统
生成和管理复杂的地形要素，包括河流、海洋、山脉、平原等
对智能体和部落产生不同的影响

Author: Ben Hsu & Claude
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass
import logging

from ..core.physics_engine import Vector2D

logger = logging.getLogger(__name__)

class TerrainType(Enum):
    """地形类型枚举"""
    OCEAN = "ocean"          # 海洋
    RIVER = "river"          # 河流
    MOUNTAIN = "mountain"    # 山脉
    HILL = "hill"           # 丘陵
    FOREST = "forest"       # 森林
    GRASSLAND = "grassland" # 草原
    DESERT = "desert"       # 沙漠
    SWAMP = "swamp"         # 沼泽
    TUNDRA = "tundra"       # 苔原
    COAST = "coast"         # 海岸

@dataclass
class TerrainFeature:
    """地形要素数据结构"""
    terrain_type: TerrainType
    position: Tuple[int, int]
    size: int
    elevation: float
    moisture: float
    temperature: float
    fertility: float
    # 对智能体的影响
    movement_cost: float    # 移动成本
    visibility_modifier: float  # 可见性修正
    resource_modifier: Dict[str, float]  # 资源修正
    # 对部落的影响
    communication_barrier: float  # 通讯阻碍
    tech_bonus: Dict[str, float]  # 科技加成
    trade_modifier: float  # 贸易修正

class TerrainGenerator:
    """地形生成器"""
    
    def __init__(self, world_size: Tuple[int, int]):
        self.world_size = world_size
        self.width, self.height = world_size
        self.terrain_map = np.zeros((self.height, self.width), dtype=int)
        self.features: List[TerrainFeature] = []
        self.feature_map: Dict[Tuple[int, int], TerrainFeature] = {}
        
        # 地形生成参数
        self.noise_scale = 0.1
        self.octaves = 4
        self.persistence = 0.5
        self.lacunarity = 2.0
        
        logger.info(f"地形生成器初始化: 世界大小 {world_size}")
    
    def generate_terrain(self) -> Dict[Tuple[int, int], TerrainFeature]:
        """生成完整的地形系统"""
        logger.info("开始生成地形...")
        
        # 1. 生成高度图
        elevation_map = self._generate_elevation_map()
        
        # 2. 生成水分图
        moisture_map = self._generate_moisture_map()
        
        # 3. 生成温度图
        temperature_map = self._generate_temperature_map()
        
        # 4. 根据环境参数确定地形类型
        self._classify_terrain(elevation_map, moisture_map, temperature_map)
        
        # 5. 生成河流系统
        self._generate_rivers(elevation_map)
        
        # 6. 生成海洋和海岸
        self._generate_water_bodies(elevation_map)
        
        # 7. 完善地形特征
        self._finalize_terrain_features()
        
        logger.info(f"地形生成完成: {len(self.features)} 个地形要素")
        return self.feature_map
    
    def _generate_elevation_map(self) -> np.ndarray:
        """生成高度图"""
        elevation = np.zeros((self.height, self.width))
        
        for y in range(self.height):
            for x in range(self.width):
                # 使用多层噪声生成高度
                value = 0
                amplitude = 1
                frequency = self.noise_scale
                
                for _ in range(self.octaves):
                    value += amplitude * self._noise(x * frequency, y * frequency)
                    amplitude *= self.persistence
                    frequency *= self.lacunarity
                
                elevation[y, x] = value
        
        # 标准化到0-1范围
        elevation = (elevation - elevation.min()) / (elevation.max() - elevation.min())
        return elevation
    
    def _generate_moisture_map(self) -> np.ndarray:
        """生成水分图"""
        moisture = np.zeros((self.height, self.width))
        
        for y in range(self.height):
            for x in range(self.width):
                # 基于距离海洋的远近和噪声
                distance_to_edge = min(x, y, self.width - x - 1, self.height - y - 1)
                base_moisture = 1.0 - (distance_to_edge / (min(self.width, self.height) / 2))
                
                # 添加噪声
                noise_value = self._noise(x * 0.05, y * 0.05)
                moisture[y, x] = np.clip(base_moisture + noise_value * 0.3, 0, 1)
        
        return moisture
    
    def _generate_temperature_map(self) -> np.ndarray:
        """生成温度图"""
        temperature = np.zeros((self.height, self.width))
        
        for y in range(self.height):
            for x in range(self.width):
                # 基于纬度的温度梯度
                latitude_factor = 1.0 - (abs(y - self.height / 2) / (self.height / 2))
                
                # 添加噪声
                noise_value = self._noise(x * 0.03, y * 0.03)
                temperature[y, x] = np.clip(latitude_factor + noise_value * 0.2, 0, 1)
        
        return temperature
    
    def _classify_terrain(self, elevation: np.ndarray, moisture: np.ndarray, temperature: np.ndarray):
        """根据环境参数分类地形"""
        for y in range(self.height):
            for x in range(self.width):
                e = elevation[y, x]
                m = moisture[y, x]
                t = temperature[y, x]
                
                terrain_type = self._determine_terrain_type(e, m, t)
                
                if terrain_type != TerrainType.OCEAN:  # 海洋后面单独处理
                    feature = self._create_terrain_feature(terrain_type, (x, y), e, m, t)
                    self.features.append(feature)
                    self.feature_map[(x, y)] = feature
    
    def _determine_terrain_type(self, elevation: float, moisture: float, temperature: float) -> TerrainType:
        """确定地形类型"""
        # 海洋判定
        if elevation < 0.2:
            return TerrainType.OCEAN
        
        # 山脉判定
        if elevation > 0.8:
            return TerrainType.MOUNTAIN if temperature > 0.3 else TerrainType.TUNDRA
        
        # 丘陵判定
        if elevation > 0.6:
            return TerrainType.HILL
        
        # 基于温度和湿度的分类
        if temperature < 0.3:
            return TerrainType.TUNDRA
        elif temperature > 0.7:
            if moisture < 0.3:
                return TerrainType.DESERT
            elif moisture > 0.7:
                return TerrainType.SWAMP
            else:
                return TerrainType.GRASSLAND
        else:  # 温带
            if moisture < 0.4:
                return TerrainType.GRASSLAND
            elif moisture > 0.6:
                return TerrainType.FOREST
            else:
                return TerrainType.GRASSLAND
    
    def _create_terrain_feature(self, terrain_type: TerrainType, position: Tuple[int, int], 
                               elevation: float, moisture: float, temperature: float) -> TerrainFeature:
        """创建地形要素"""
        # 根据地形类型设置属性
        terrain_config = self._get_terrain_config(terrain_type)
        
        fertility = self._calculate_fertility(terrain_type, elevation, moisture, temperature)
        
        return TerrainFeature(
            terrain_type=terrain_type,
            position=position,
            size=1,
            elevation=elevation,
            moisture=moisture,
            temperature=temperature,
            fertility=fertility,
            movement_cost=terrain_config['movement_cost'],
            visibility_modifier=terrain_config['visibility_modifier'],
            resource_modifier=terrain_config['resource_modifier'],
            communication_barrier=terrain_config['communication_barrier'],
            tech_bonus=terrain_config['tech_bonus'],
            trade_modifier=terrain_config['trade_modifier']
        )
    
    def _get_terrain_config(self, terrain_type: TerrainType) -> Dict:
        """获取地形配置"""
        configs = {
            TerrainType.OCEAN: {
                'movement_cost': 2.0,
                'visibility_modifier': 1.2,
                'resource_modifier': {'food': 0.8, 'material': 0.2, 'energy': 0.5},
                'communication_barrier': 0.9,
                'tech_bonus': {'navigation': 2.0, 'fishing': 1.5},
                'trade_modifier': 0.3
            },
            TerrainType.RIVER: {
                'movement_cost': 0.8,
                'visibility_modifier': 1.0,
                'resource_modifier': {'food': 1.5, 'material': 0.8, 'energy': 1.2},
                'communication_barrier': 0.3,
                'tech_bonus': {'agriculture': 1.5, 'transportation': 1.3},
                'trade_modifier': 1.5
            },
            TerrainType.MOUNTAIN: {
                'movement_cost': 3.0,
                'visibility_modifier': 1.5,
                'resource_modifier': {'food': 0.3, 'material': 2.0, 'energy': 0.8},
                'communication_barrier': 0.8,
                'tech_bonus': {'mining': 2.0, 'metalworking': 1.5},
                'trade_modifier': 0.5
            },
            TerrainType.HILL: {
                'movement_cost': 1.5,
                'visibility_modifier': 1.3,
                'resource_modifier': {'food': 0.7, 'material': 1.3, 'energy': 1.0},
                'communication_barrier': 0.4,
                'tech_bonus': {'defense': 1.3, 'herding': 1.2},
                'trade_modifier': 0.8
            },
            TerrainType.FOREST: {
                'movement_cost': 1.3,
                'visibility_modifier': 0.7,
                'resource_modifier': {'food': 1.2, 'material': 1.8, 'energy': 0.9},
                'communication_barrier': 0.5,
                'tech_bonus': {'woodworking': 2.0, 'hunting': 1.5},
                'trade_modifier': 0.9
            },
            TerrainType.GRASSLAND: {
                'movement_cost': 1.0,
                'visibility_modifier': 1.0,
                'resource_modifier': {'food': 1.3, 'material': 0.8, 'energy': 1.1},
                'communication_barrier': 0.2,
                'tech_bonus': {'agriculture': 1.3, 'animal_husbandry': 1.5},
                'trade_modifier': 1.2
            },
            TerrainType.DESERT: {
                'movement_cost': 1.8,
                'visibility_modifier': 1.4,
                'resource_modifier': {'food': 0.2, 'material': 0.5, 'energy': 1.5},
                'communication_barrier': 0.6,
                'tech_bonus': {'astronomy': 1.5, 'endurance': 1.3},
                'trade_modifier': 0.6
            },
            TerrainType.SWAMP: {
                'movement_cost': 2.5,
                'visibility_modifier': 0.6,
                'resource_modifier': {'food': 0.9, 'material': 0.6, 'energy': 0.7},
                'communication_barrier': 0.7,
                'tech_bonus': {'medicine': 1.5, 'alchemy': 1.3},
                'trade_modifier': 0.4
            },
            TerrainType.TUNDRA: {
                'movement_cost': 1.6,
                'visibility_modifier': 1.2,
                'resource_modifier': {'food': 0.4, 'material': 0.7, 'energy': 0.8},
                'communication_barrier': 0.5,
                'tech_bonus': {'survival': 1.8, 'cold_adaptation': 2.0},
                'trade_modifier': 0.7
            },
            TerrainType.COAST: {
                'movement_cost': 1.1,
                'visibility_modifier': 1.1,
                'resource_modifier': {'food': 1.4, 'material': 0.9, 'energy': 1.0},
                'communication_barrier': 0.3,
                'tech_bonus': {'navigation': 1.5, 'trade': 1.4},
                'trade_modifier': 1.4
            }
        }
        
        return configs.get(terrain_type, configs[TerrainType.GRASSLAND])
    
    def _calculate_fertility(self, terrain_type: TerrainType, elevation: float, 
                           moisture: float, temperature: float) -> float:
        """计算地形肥沃度"""
        base_fertility = {
            TerrainType.OCEAN: 0.3,
            TerrainType.RIVER: 0.9,
            TerrainType.MOUNTAIN: 0.2,
            TerrainType.HILL: 0.5,
            TerrainType.FOREST: 0.7,
            TerrainType.GRASSLAND: 0.8,
            TerrainType.DESERT: 0.1,
            TerrainType.SWAMP: 0.4,
            TerrainType.TUNDRA: 0.3,
            TerrainType.COAST: 0.6
        }.get(terrain_type, 0.5)
        
        # 根据环境参数调整肥沃度
        moisture_factor = moisture
        temperature_factor = 1.0 - abs(temperature - 0.5) * 2  # 温带最适宜
        
        return np.clip(base_fertility * moisture_factor * temperature_factor, 0, 1)
    
    def _generate_rivers(self, elevation: np.ndarray):
        """生成河流系统"""
        # 找到山脉作为河流源头
        mountains = np.where(elevation > 0.7)
        
        for i in range(len(mountains[0])):
            y, x = mountains[0][i], mountains[1][i]
            
            # 有概率生成河流
            if random.random() < 0.3:
                self._trace_river(x, y, elevation)
    
    def _trace_river(self, start_x: int, start_y: int, elevation: np.ndarray):
        """追踪河流路径"""
        x, y = start_x, start_y
        path = []
        
        # 向低处流淌
        while True:
            path.append((x, y))
            
            # 寻找最低的相邻点
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny, elevation[ny, nx]))
            
            if not neighbors:
                break
            
            # 选择最低点
            next_x, next_y, next_elevation = min(neighbors, key=lambda p: p[2])
            
            # 如果没有更低的点或到达海洋，结束
            if next_elevation >= elevation[y, x] or next_elevation < 0.2:
                break
            
            x, y = next_x, next_y
            
            # 河流长度限制
            if len(path) > 50:
                break
        
        # 创建河流地形
        for rx, ry in path:
            if (rx, ry) not in self.feature_map:
                feature = self._create_terrain_feature(
                    TerrainType.RIVER, (rx, ry),
                    elevation[ry, rx], 1.0, 0.5
                )
                self.features.append(feature)
                self.feature_map[(rx, ry)] = feature
    
    def _generate_water_bodies(self, elevation: np.ndarray):
        """生成水体和海岸"""
        for y in range(self.height):
            for x in range(self.width):
                if elevation[y, x] < 0.2:
                    # 海洋
                    feature = self._create_terrain_feature(
                        TerrainType.OCEAN, (x, y),
                        elevation[y, x], 1.0, 0.5
                    )
                    self.features.append(feature)
                    self.feature_map[(x, y)] = feature
                elif elevation[y, x] < 0.3:
                    # 检查是否临近海洋，如果是则为海岸
                    is_coast = False
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if elevation[ny, nx] < 0.2:
                                is_coast = True
                                break
                    
                    if is_coast and (x, y) not in self.feature_map:
                        feature = self._create_terrain_feature(
                            TerrainType.COAST, (x, y),
                            elevation[y, x], 0.8, 0.6
                        )
                        self.features.append(feature)
                        self.feature_map[(x, y)] = feature
    
    def _finalize_terrain_features(self):
        """完善地形特征"""
        # 计算地形要素的连通性和大小
        for feature in self.features:
            feature.size = self._calculate_feature_size(feature)
    
    def _calculate_feature_size(self, feature: TerrainFeature) -> int:
        """计算地形要素大小"""
        # 简化版本，返回连通的同类地形数量
        visited = set()
        queue = [feature.position]
        size = 0
        
        while queue and size < 100:  # 限制搜索范围
            x, y = queue.pop(0)
            if (x, y) in visited:
                continue
            
            visited.add((x, y))
            size += 1
            
            # 检查相邻同类地形
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in self.feature_map:
                    neighbor = self.feature_map[(nx, ny)]
                    if (neighbor.terrain_type == feature.terrain_type and 
                        (nx, ny) not in visited):
                        queue.append((nx, ny))
        
        return size
    
    def _noise(self, x: float, y: float) -> float:
        """简单的噪声函数"""
        # 使用简单的伪随机噪声
        return (np.sin(x * 12.9898 + y * 78.233) * 43758.5453) % 1.0 - 0.5
    
    def get_terrain_at(self, x: int, y: int) -> Optional[TerrainFeature]:
        """获取指定位置的地形"""
        return self.feature_map.get((x, y))
    
    def get_terrain_effects(self, x: int, y: int) -> Dict:
        """获取地形对智能体的影响"""
        feature = self.get_terrain_at(x, y)
        if feature:
            return {
                'movement_cost': feature.movement_cost,
                'visibility_modifier': feature.visibility_modifier,
                'resource_modifier': feature.resource_modifier,
                'fertility': feature.fertility
            }
        else:
            # 默认平原地形
            return {
                'movement_cost': 1.0,
                'visibility_modifier': 1.0,
                'resource_modifier': {'food': 1.0, 'material': 1.0, 'energy': 1.0},
                'fertility': 0.5
            }
    
    def get_tribe_effects(self, positions: List[Tuple[int, int]]) -> Dict:
        """获取地形对部落的影响"""
        if not positions:
            return {}
        
        # 统计部落领土内的地形分布
        terrain_count = {}
        total_communication_barrier = 0
        tech_bonuses = {}
        trade_modifiers = []
        
        for x, y in positions:
            feature = self.get_terrain_at(x, y)
            if feature:
                terrain_type = feature.terrain_type
                terrain_count[terrain_type] = terrain_count.get(terrain_type, 0) + 1
                total_communication_barrier += feature.communication_barrier
                
                # 累计科技加成
                for tech, bonus in feature.tech_bonus.items():
                    tech_bonuses[tech] = max(tech_bonuses.get(tech, 0), bonus)
                
                trade_modifiers.append(feature.trade_modifier)
        
        return {
            'terrain_distribution': terrain_count,
            'communication_barrier': total_communication_barrier / len(positions),
            'tech_bonuses': tech_bonuses,
            'trade_modifier': np.mean(trade_modifiers) if trade_modifiers else 1.0
        }

class TerrainSystem:
    """地形系统管理器"""
    
    def __init__(self, world_size: Tuple[int, int]):
        self.world_size = world_size
        self.generator = TerrainGenerator(world_size)
        self.terrain_map: Dict[Tuple[int, int], TerrainFeature] = {}
        self.initialized = False
        
        logger.info(f"地形系统初始化: {world_size}")
    
    def initialize(self) -> bool:
        """初始化地形系统"""
        try:
            self.terrain_map = self.generator.generate_terrain()
            self.initialized = True
            logger.info("地形系统初始化成功")
            return True
        except Exception as e:
            logger.error(f"地形系统初始化失败: {e}")
            return False
    
    def get_terrain_at(self, x: int, y: int) -> Optional[TerrainFeature]:
        """获取指定位置的地形"""
        if not self.initialized:
            return None
        return self.terrain_map.get((x, y))
    
    def get_terrain_at_position(self, position: Vector2D) -> TerrainType:
        """获取指定位置的地形类型（兼容旧接口）"""
        x, y = int(position.x), int(position.y)
        terrain = self.get_terrain_at(x, y)
        if terrain:
            return terrain.terrain_type
        return TerrainType.GRASSLAND
    
    def get_terrain_effects_at_position(self, position: Vector2D) -> Dict[str, float]:
        """获取指定位置的地形影响（兼容旧接口）"""
        x, y = int(position.x), int(position.y)
        terrain = self.get_terrain_at(x, y)
        if terrain:
            return {
                'movement_speed': 1.0 / terrain.movement_cost,
                'energy_cost': terrain.movement_cost,
                'perception_range': terrain.visibility_modifier,
                'resource_availability': np.mean(list(terrain.resource_modifier.values())),
                'shelter_value': terrain.fertility
            }
        else:
            return {
                'movement_speed': 1.0,
                'energy_cost': 1.0,
                'perception_range': 1.0,
                'resource_availability': 1.0,
                'shelter_value': 1.0
            }
    
    def get_movement_cost(self, x: int, y: int) -> float:
        """获取移动成本"""
        terrain = self.get_terrain_at(x, y)
        return terrain.movement_cost if terrain else 1.0
    
    def get_visibility_modifier(self, x: int, y: int) -> float:
        """获取可见性修正"""
        terrain = self.get_terrain_at(x, y)
        return terrain.visibility_modifier if terrain else 1.0
    
    def get_resource_modifier(self, x: int, y: int) -> Dict[str, float]:
        """获取资源修正"""
        terrain = self.get_terrain_at(x, y)
        return terrain.resource_modifier if terrain else {'food': 1.0, 'material': 1.0, 'energy': 1.0}
    
    def get_communication_barrier(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """获取两点间的通讯阻碍"""
        # 计算路径上的地形阻碍
        x1, y1 = pos1
        x2, y2 = pos2
        
        # 简化版本：使用两点间的直线路径
        points = self._get_line_points(x1, y1, x2, y2)
        
        total_barrier = 0
        for x, y in points:
            terrain = self.get_terrain_at(x, y)
            if terrain:
                total_barrier += terrain.communication_barrier
        
        return total_barrier / len(points) if points else 0
    
    def _get_line_points(self, x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """获取两点间的直线路径点"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            if 0 <= x < self.world_size[0] and 0 <= y < self.world_size[1]:
                points.append((x, y))
            
            if x == x2 and y == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return points
    
    def get_terrain_info(self) -> List[Dict]:
        """获取地形信息（兼容旧接口）"""
        if not self.initialized:
            return []
        
        info = []
        for feature in self.terrain_map.values():
            info.append({
                'type': feature.terrain_type.value,
                'center': feature.position,
                'radius': feature.size,
                'elevation': feature.elevation
            })
        
        return info
    
    def get_terrain_stats(self) -> Dict:
        """获取地形统计信息"""
        if not self.initialized:
            return {}
        
        terrain_count = {}
        for feature in self.terrain_map.values():
            terrain_type = feature.terrain_type
            terrain_count[terrain_type] = terrain_count.get(terrain_type, 0) + 1
        
        return {
            'total_tiles': len(self.terrain_map),
            'terrain_distribution': terrain_count,
            'water_percentage': (terrain_count.get(TerrainType.OCEAN, 0) + 
                               terrain_count.get(TerrainType.RIVER, 0)) / len(self.terrain_map),
            'mountain_percentage': terrain_count.get(TerrainType.MOUNTAIN, 0) / len(self.terrain_map)
        }