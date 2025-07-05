"""
Cogvrs Core Module
核心模块：物理引擎、世界环境、时间管理

Author: Ben Hsu & Claude
"""

from .physics_engine import PhysicsEngine, PhysicsObject, Vector2D
from .world import World2D, Resource, EnvironmentalCondition, TerrainType
from .time_manager import TimeManager, ScheduledEvent, format_simulation_time, calculate_eta

__all__ = [
    'PhysicsEngine',
    'PhysicsObject', 
    'Vector2D',
    'World2D',
    'Resource',
    'EnvironmentalCondition',
    'TerrainType',
    'TimeManager',
    'ScheduledEvent',
    'format_simulation_time',
    'calculate_eta'
]