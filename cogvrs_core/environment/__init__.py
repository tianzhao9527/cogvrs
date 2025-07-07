"""
环境系统 - 处理气候、地形、季节等环境因素
"""

from .environment_manager import EnvironmentManager, EnvironmentZone, ClimateType
from .weather_system import WeatherSystem, WeatherEvent
from .terrain_system import TerrainSystem, TerrainType

__all__ = [
    'EnvironmentManager',
    'EnvironmentZone',
    'ClimateType',
    'WeatherSystem',
    'WeatherEvent',
    'TerrainSystem',
    'TerrainType'
]