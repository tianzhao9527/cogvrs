"""
环境管理器 - 统一管理世界环境系统
集成新的气候系统以提高性能
"""

import time
import math
import random
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from ..core.physics_engine import Vector2D
from .climate_system import ClimateSystem


class ClimateType(Enum):
    """气候类型"""
    TROPICAL = "tropical"           # 热带 - 高温高湿
    TEMPERATE = "temperate"         # 温带 - 适中温度
    ARCTIC = "arctic"               # 极地 - 寒冷干燥
    DESERT = "desert"               # 沙漠 - 高温干燥
    FOREST = "forest"               # 森林 - 湿润温和
    MOUNTAIN = "mountain"           # 山地 - 寒冷多变


@dataclass
class EnvironmentZone:
    """环境区域"""
    center: Vector2D
    radius: float
    climate: ClimateType
    temperature: float              # 温度 (-50 到 50)
    humidity: float                 # 湿度 (0 到 100)
    resource_abundance: float       # 资源丰富度 (0 到 2.0)
    danger_level: float             # 危险度 (0 到 1.0)
    
    def get_environmental_effects(self) -> Dict[str, float]:
        """获取环境对智能体的影响"""
        effects = {
            'energy_modifier': 1.0,
            'health_modifier': 1.0,
            'movement_speed': 1.0,
            'perception_range': 1.0,
            'reproduction_rate': 1.0
        }
        
        # 温度影响
        if self.temperature < -20:  # 极寒
            effects['energy_modifier'] *= 0.7
            effects['movement_speed'] *= 0.8
        elif self.temperature > 40:  # 极热
            effects['energy_modifier'] *= 0.8
            effects['health_modifier'] *= 0.9
        elif 15 <= self.temperature <= 25:  # 适宜温度
            effects['energy_modifier'] *= 1.1
            effects['reproduction_rate'] *= 1.2
        
        # 湿度影响
        if self.humidity < 20:  # 干燥
            effects['health_modifier'] *= 0.9
        elif self.humidity > 80:  # 潮湿
            effects['perception_range'] *= 0.9
        
        # 资源丰富度影响
        effects['energy_modifier'] *= (0.8 + 0.4 * self.resource_abundance)
        
        # 危险度影响
        effects['health_modifier'] *= (1.0 - 0.3 * self.danger_level)
        
        return effects


class EnvironmentManager:
    """环境管理器"""
    
    def __init__(self, world_size: Tuple[int, int]):
        self.world_size = world_size
        self.zones: List[EnvironmentZone] = []
        self.season_duration = 120.0  # 季节长度（秒）
        self.day_duration = 30.0      # 昼夜长度（秒）
        self.start_time = time.time()
        
        # 初始化新的气候系统（替代复杂天气系统）
        self.climate_system = ClimateSystem(world_size, {})  # 稍后会通过GUI配置更新
        self.use_climate_system = True  # 标志：使用气候系统而非天气系统
        
        self._generate_environment_zones()
    
    def _generate_environment_zones(self):
        """生成环境区域"""
        # 创建多样化的环境区域
        zone_configs = [
            # 中心森林区域
            {
                'center': Vector2D(self.world_size[0] * 0.5, self.world_size[1] * 0.5),
                'radius': min(self.world_size) * 0.2,
                'climate': ClimateType.FOREST,
                'temp_base': 20, 'humidity_base': 70,
                'resources': 1.5, 'danger': 0.2
            },
            # 北部寒带
            {
                'center': Vector2D(self.world_size[0] * 0.5, self.world_size[1] * 0.15),
                'radius': min(self.world_size) * 0.25,
                'climate': ClimateType.ARCTIC,
                'temp_base': -10, 'humidity_base': 40,
                'resources': 0.6, 'danger': 0.4
            },
            # 南部热带
            {
                'center': Vector2D(self.world_size[0] * 0.5, self.world_size[1] * 0.85),
                'radius': min(self.world_size) * 0.2,
                'climate': ClimateType.TROPICAL,
                'temp_base': 35, 'humidity_base': 85,
                'resources': 1.8, 'danger': 0.3
            },
            # 西部沙漠
            {
                'center': Vector2D(self.world_size[0] * 0.15, self.world_size[1] * 0.5),
                'radius': min(self.world_size) * 0.18,
                'climate': ClimateType.DESERT,
                'temp_base': 42, 'humidity_base': 15,
                'resources': 0.4, 'danger': 0.6
            },
            # 东部山地
            {
                'center': Vector2D(self.world_size[0] * 0.85, self.world_size[1] * 0.5),
                'radius': min(self.world_size) * 0.15,
                'climate': ClimateType.MOUNTAIN,
                'temp_base': 5, 'humidity_base': 50,
                'resources': 0.8, 'danger': 0.5
            },
            # 温带草原
            {
                'center': Vector2D(self.world_size[0] * 0.3, self.world_size[1] * 0.3),
                'radius': min(self.world_size) * 0.12,
                'climate': ClimateType.TEMPERATE,
                'temp_base': 18, 'humidity_base': 55,
                'resources': 1.2, 'danger': 0.1
            }
        ]
        
        for config in zone_configs:
            zone = EnvironmentZone(
                center=config['center'],
                radius=config['radius'],
                climate=config['climate'],
                temperature=config['temp_base'],
                humidity=config['humidity_base'],
                resource_abundance=config['resources'],
                danger_level=config['danger']
            )
            self.zones.append(zone)
    
    def get_current_season(self) -> str:
        """获取当前季节"""
        elapsed = time.time() - self.start_time
        season_progress = (elapsed % self.season_duration) / self.season_duration
        
        if season_progress < 0.25:
            return "Spring"
        elif season_progress < 0.5:
            return "Summer"
        elif season_progress < 0.75:
            return "Autumn"
        else:
            return "Winter"
    
    def get_time_of_day(self) -> str:
        """获取一天中的时间"""
        elapsed = time.time() - self.start_time
        day_progress = (elapsed % self.day_duration) / self.day_duration
        
        if day_progress < 0.25:
            return "Dawn"
        elif day_progress < 0.5:
            return "Day"
        elif day_progress < 0.75:
            return "Dusk"
        else:
            return "Night"
    
    def get_environmental_effects_at_position(self, position: Vector2D) -> Dict[str, float]:
        """获取指定位置的环境影响"""
        # 默认影响
        base_effects = {
            'energy_modifier': 1.0,
            'health_modifier': 1.0,
            'movement_speed': 1.0,
            'perception_range': 1.0,
            'reproduction_rate': 1.0
        }
        
        # 查找影响该位置的环境区域
        for zone in self.zones:
            distance = position.distance_to(zone.center)
            if distance <= zone.radius:
                # 计算在区域内的影响强度
                influence = max(0, 1.0 - distance / zone.radius)
                zone_effects = zone.get_environmental_effects()
                
                # 按影响强度混合效果
                for key in base_effects:
                    base_effects[key] = (
                        base_effects[key] * (1 - influence) + 
                        zone_effects[key] * influence
                    )
        
        # 季节影响
        season = self.get_current_season()
        if season == "Winter":
            base_effects['energy_modifier'] *= 0.8
            base_effects['reproduction_rate'] *= 0.5
        elif season == "Summer":
            base_effects['energy_modifier'] *= 1.1
            base_effects['reproduction_rate'] *= 1.3
        elif season == "Spring":
            base_effects['reproduction_rate'] *= 1.5
        
        # 昼夜影响
        time_of_day = self.get_time_of_day()
        if time_of_day == "Night":
            base_effects['perception_range'] *= 0.7
            base_effects['movement_speed'] *= 0.9
        elif time_of_day == "Day":
            base_effects['perception_range'] *= 1.1
        
        return base_effects
    
    def get_zone_at_position(self, position: Vector2D) -> Optional[EnvironmentZone]:
        """获取指定位置的环境区域"""
        for zone in self.zones:
            if position.distance_to(zone.center) <= zone.radius:
                return zone
        return None
    
    def get_environment_status(self) -> Dict:
        """获取环境状态信息"""
        return {
            'season': self.get_current_season(),
            'time_of_day': self.get_time_of_day(),
            'total_zones': len(self.zones),
            'zone_types': [zone.climate.value for zone in self.zones]
        }