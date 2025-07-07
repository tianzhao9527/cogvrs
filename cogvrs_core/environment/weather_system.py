"""
天气系统 - 处理动态天气事件
"""

import random
import time
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..core.physics_engine import Vector2D


class WeatherEvent(Enum):
    """天气事件类型"""
    CLEAR = "clear"
    RAIN = "rain"
    STORM = "storm"
    DROUGHT = "drought"
    BLIZZARD = "blizzard"
    HEATWAVE = "heatwave"


@dataclass
class WeatherData:
    """天气数据"""
    event_type: WeatherEvent
    intensity: float        # 强度 0-1
    duration: float         # 持续时间（秒）
    affected_area: Vector2D # 影响中心
    radius: float           # 影响半径
    start_time: float       # 开始时间
    
    def is_active(self) -> bool:
        """检查天气事件是否仍然活跃"""
        return time.time() - self.start_time < self.duration
    
    def get_effects(self) -> Dict[str, float]:
        """获取天气效应"""
        effects = {
            'energy_modifier': 1.0,
            'health_modifier': 1.0,
            'movement_speed': 1.0,
            'perception_range': 1.0,
            'reproduction_rate': 1.0
        }
        
        if self.event_type == WeatherEvent.RAIN:
            effects['movement_speed'] *= (1.0 - 0.2 * self.intensity)
            effects['perception_range'] *= (1.0 - 0.3 * self.intensity)
            effects['energy_modifier'] *= (1.0 + 0.1 * self.intensity)  # 雨水补充
            
        elif self.event_type == WeatherEvent.STORM:
            effects['movement_speed'] *= (1.0 - 0.5 * self.intensity)
            effects['perception_range'] *= (1.0 - 0.6 * self.intensity)
            effects['health_modifier'] *= (1.0 - 0.2 * self.intensity)
            effects['energy_modifier'] *= (1.0 - 0.3 * self.intensity)
            
        elif self.event_type == WeatherEvent.DROUGHT:
            effects['energy_modifier'] *= (1.0 - 0.3 * self.intensity)
            effects['health_modifier'] *= (1.0 - 0.2 * self.intensity)
            effects['reproduction_rate'] *= (1.0 - 0.4 * self.intensity)
            
        elif self.event_type == WeatherEvent.BLIZZARD:
            effects['movement_speed'] *= (1.0 - 0.6 * self.intensity)
            effects['perception_range'] *= (1.0 - 0.7 * self.intensity)
            effects['energy_modifier'] *= (1.0 - 0.4 * self.intensity)
            
        elif self.event_type == WeatherEvent.HEATWAVE:
            effects['energy_modifier'] *= (1.0 - 0.25 * self.intensity)
            effects['movement_speed'] *= (1.0 - 0.15 * self.intensity)
            effects['health_modifier'] *= (1.0 - 0.1 * self.intensity)
        
        return effects


class WeatherSystem:
    """天气系统"""
    
    def __init__(self, world_size):
        self.world_size = world_size
        self.active_weather: List[WeatherData] = []
        self.last_update = time.time()
        self.weather_chance = 0.1   # 每次更新产生天气的概率 (增加到10%)
        
    def update(self, dt: float):
        """更新天气系统"""
        current_time = time.time()
        
        # 移除过期的天气事件
        self.active_weather = [w for w in self.active_weather if w.is_active()]
        
        # 随机生成新天气事件
        if random.random() < self.weather_chance:
            self._generate_weather_event()
        
        self.last_update = current_time
    
    def _generate_weather_event(self):
        """生成随机天气事件"""
        weather_types = list(WeatherEvent)
        weather_type = random.choice(weather_types)
        
        # 随机位置和参数
        center = Vector2D(
            random.uniform(0, self.world_size[0]),
            random.uniform(0, self.world_size[1])
        )
        
        radius = random.uniform(50, 200)
        intensity = random.uniform(0.3, 1.0)
        duration = random.uniform(30, 120)  # 30-120秒
        
        weather = WeatherData(
            event_type=weather_type,
            intensity=intensity,
            duration=duration,
            affected_area=center,
            radius=radius,
            start_time=time.time()
        )
        
        self.active_weather.append(weather)
    
    def get_weather_effects_at_position(self, position: Vector2D) -> Dict[str, float]:
        """获取指定位置的天气影响"""
        combined_effects = {
            'energy_modifier': 1.0,
            'health_modifier': 1.0,
            'movement_speed': 1.0,
            'perception_range': 1.0,
            'reproduction_rate': 1.0
        }
        
        for weather in self.active_weather:
            distance = position.distance_to(weather.affected_area)
            if distance <= weather.radius:
                # 计算影响强度
                influence = max(0, 1.0 - distance / weather.radius)
                weather_effects = weather.get_effects()
                
                # 累积天气效应
                for key in combined_effects:
                    # 使用乘法累积负面效应，加法累积正面效应
                    effect_change = weather_effects[key] - 1.0
                    combined_effects[key] *= (1.0 + effect_change * influence)
        
        return combined_effects
    
    def get_active_weather_info(self) -> List[Dict]:
        """获取当前活跃天气信息"""
        result = []
        for weather in self.active_weather:
            # 处理affected_area可能是tuple或Vector2D的情况
            if hasattr(weather.affected_area, 'x'):
                center = (weather.affected_area.x, weather.affected_area.y)
            else:
                center = weather.affected_area  # 已经是tuple
            
            result.append({
                'type': weather.event_type.value,
                'intensity': weather.intensity,
                'center': center,
                'radius': weather.radius,
                'remaining_time': weather.duration - (time.time() - weather.start_time)
            })
        return result