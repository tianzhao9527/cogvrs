"""
地形系统 - 处理地形类型和地理特征
"""

from enum import Enum
from typing import Dict, List, Tuple
from dataclasses import dataclass

from ..core.physics_engine import Vector2D


class TerrainType(Enum):
    """地形类型"""
    PLAINS = "plains"           # 平原 - 易于移动
    FOREST = "forest"           # 森林 - 资源丰富但移动困难
    MOUNTAIN = "mountain"       # 山地 - 移动困难但视野好
    WATER = "water"             # 水域 - 阻挡移动但提供资源
    SWAMP = "swamp"             # 沼泽 - 移动缓慢
    DESERT = "desert"           # 沙漠 - 资源稀少
    HILLS = "hills"             # 丘陵 - 中等难度地形


@dataclass
class TerrainFeature:
    """地形特征"""
    terrain_type: TerrainType
    center: Vector2D
    radius: float
    elevation: float            # 海拔高度
    
    def get_terrain_effects(self) -> Dict[str, float]:
        """获取地形对智能体的影响"""
        effects = {
            'movement_speed': 1.0,
            'energy_cost': 1.0,
            'perception_range': 1.0,
            'resource_availability': 1.0,
            'shelter_value': 1.0
        }
        
        if self.terrain_type == TerrainType.PLAINS:
            effects['movement_speed'] = 1.2
            effects['perception_range'] = 1.3
            effects['resource_availability'] = 1.0
            
        elif self.terrain_type == TerrainType.FOREST:
            effects['movement_speed'] = 0.8
            effects['perception_range'] = 0.7
            effects['resource_availability'] = 1.8
            effects['shelter_value'] = 1.5
            
        elif self.terrain_type == TerrainType.MOUNTAIN:
            effects['movement_speed'] = 0.6
            effects['energy_cost'] = 1.5
            effects['perception_range'] = 1.8
            effects['resource_availability'] = 0.6
            effects['shelter_value'] = 1.2
            
        elif self.terrain_type == TerrainType.WATER:
            effects['movement_speed'] = 0.3
            effects['energy_cost'] = 2.0
            effects['resource_availability'] = 1.4
            
        elif self.terrain_type == TerrainType.SWAMP:
            effects['movement_speed'] = 0.5
            effects['energy_cost'] = 1.4
            effects['perception_range'] = 0.6
            effects['resource_availability'] = 1.3
            
        elif self.terrain_type == TerrainType.DESERT:
            effects['movement_speed'] = 0.9
            effects['energy_cost'] = 1.3
            effects['perception_range'] = 1.4
            effects['resource_availability'] = 0.3
            
        elif self.terrain_type == TerrainType.HILLS:
            effects['movement_speed'] = 0.9
            effects['energy_cost'] = 1.2
            effects['perception_range'] = 1.2
            effects['resource_availability'] = 0.8
            effects['shelter_value'] = 1.1
        
        return effects


class TerrainSystem:
    """地形系统"""
    
    def __init__(self, world_size: Tuple[int, int]):
        self.world_size = world_size
        self.terrain_features: List[TerrainFeature] = []
        self._generate_terrain()
    
    def _generate_terrain(self):
        """生成地形特征"""
        # 创建多样化的地形
        terrain_configs = [
            # 中央大平原
            {
                'type': TerrainType.PLAINS,
                'center': Vector2D(self.world_size[0] * 0.5, self.world_size[1] * 0.5),
                'radius': min(self.world_size) * 0.3,
                'elevation': 0
            },
            # 北部森林
            {
                'type': TerrainType.FOREST,
                'center': Vector2D(self.world_size[0] * 0.5, self.world_size[1] * 0.2),
                'radius': min(self.world_size) * 0.2,
                'elevation': 20
            },
            # 东部山脉
            {
                'type': TerrainType.MOUNTAIN,
                'center': Vector2D(self.world_size[0] * 0.85, self.world_size[1] * 0.5),
                'radius': min(self.world_size) * 0.15,
                'elevation': 100
            },
            # 西部沙漠
            {
                'type': TerrainType.DESERT,
                'center': Vector2D(self.world_size[0] * 0.15, self.world_size[1] * 0.5),
                'radius': min(self.world_size) * 0.18,
                'elevation': 10
            },
            # 南部沼泽
            {
                'type': TerrainType.SWAMP,
                'center': Vector2D(self.world_size[0] * 0.3, self.world_size[1] * 0.8),
                'radius': min(self.world_size) * 0.12,
                'elevation': -5
            },
            # 东南丘陵
            {
                'type': TerrainType.HILLS,
                'center': Vector2D(self.world_size[0] * 0.7, self.world_size[1] * 0.7),
                'radius': min(self.world_size) * 0.1,
                'elevation': 40
            },
            # 小水域
            {
                'type': TerrainType.WATER,
                'center': Vector2D(self.world_size[0] * 0.6, self.world_size[1] * 0.3),
                'radius': min(self.world_size) * 0.08,
                'elevation': -10
            }
        ]
        
        for config in terrain_configs:
            feature = TerrainFeature(
                terrain_type=config['type'],
                center=config['center'],
                radius=config['radius'],
                elevation=config['elevation']
            )
            self.terrain_features.append(feature)
    
    def get_terrain_at_position(self, position: Vector2D) -> TerrainType:
        """获取指定位置的地形类型"""
        for feature in self.terrain_features:
            if position.distance_to(feature.center) <= feature.radius:
                return feature.terrain_type
        return TerrainType.PLAINS  # 默认地形
    
    def get_terrain_effects_at_position(self, position: Vector2D) -> Dict[str, float]:
        """获取指定位置的地形影响"""
        base_effects = {
            'movement_speed': 1.0,
            'energy_cost': 1.0,
            'perception_range': 1.0,
            'resource_availability': 1.0,
            'shelter_value': 1.0
        }
        
        for feature in self.terrain_features:
            distance = position.distance_to(feature.center)
            if distance <= feature.radius:
                influence = max(0, 1.0 - distance / feature.radius)
                terrain_effects = feature.get_terrain_effects()
                
                # 按影响强度混合地形效果
                for key in base_effects:
                    base_effects[key] = (
                        base_effects[key] * (1 - influence) + 
                        terrain_effects[key] * influence
                    )
        
        return base_effects
    
    def get_elevation_at_position(self, position: Vector2D) -> float:
        """获取指定位置的海拔高度"""
        elevation = 0
        total_influence = 0
        
        for feature in self.terrain_features:
            distance = position.distance_to(feature.center)
            if distance <= feature.radius:
                influence = max(0, 1.0 - distance / feature.radius)
                elevation += feature.elevation * influence
                total_influence += influence
        
        return elevation / max(total_influence, 1.0)
    
    def get_terrain_info(self) -> List[Dict]:
        """获取地形信息"""
        return [
            {
                'type': feature.terrain_type.value,
                'center': (feature.center.x, feature.center.y),
                'radius': feature.radius,
                'elevation': feature.elevation
            }
            for feature in self.terrain_features
        ]