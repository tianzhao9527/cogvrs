"""
气候系统 - 长期环境影响系统
代替复杂的天气系统，专注于气候周期和理论基础的环境影响

Author: Ben Hsu & Claude
"""

import numpy as np
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ..core.physics_engine import Vector2D
from ..utils.event_logger import (
    EventType, EventSeverity, log_climate_event, log_event, get_event_logger
)


class ClimateEpoch(Enum):
    """气候纪元"""
    TEMPERATE = "temperate"      # 温带期（正常）
    ICE_AGE = "ice_age"         # 冰河世纪
    GREENHOUSE = "greenhouse"    # 温室期
    ARID = "arid"               # 干旱期
    VOLCANIC = "volcanic"       # 火山期


class ClimateZone(Enum):
    """气候区域类型"""
    ARCTIC = "arctic"           # 北极区
    TEMPERATE = "temperate"     # 温带区
    TROPICAL = "tropical"       # 热带区
    DESERT = "desert"           # 沙漠区
    OCEANIC = "oceanic"         # 海洋区


@dataclass
class ClimateEffect:
    """气候效应"""
    temperature_modifier: float = 1.0      # 温度调节
    humidity_modifier: float = 1.0         # 湿度调节
    resource_abundance: float = 1.0        # 资源丰富度
    energy_cost_modifier: float = 1.0      # 能量消耗调节
    health_modifier: float = 1.0           # 健康影响
    reproduction_modifier: float = 1.0     # 繁殖影响
    migration_pressure: float = 0.0        # 迁移压力


class ClimateSystem:
    """
    气候系统 - 基于科学理论的长期环境影响
    
    理论基础：
    1. 米兰科维奇循环：地球轨道变化导致的气候周期
    2. 冰河世纪理论：长期气候变化对生物进化的影响
    3. 适应性辐射：环境变化推动的物种分化
    4. 生态位理论：不同气候区的生态适应
    """
    
    def __init__(self, world_size: Tuple[int, int], config: Dict = None):
        self.world_size = world_size
        self.config = config or {}
        
        # 气候纪元设置
        self.current_epoch = ClimateEpoch.TEMPERATE
        self.epoch_start_time = time.time()
        self.epoch_duration = 400  # 延长纪元持续时间到6.67分钟
        
        # 环境压力减少设置
        self.reduce_severity = self.config.get('reduce_climate_severity', False)
        self.stable_probability = self.config.get('stable_climate_probability', 0.4)
        
        # 气候周期参数
        self.orbital_cycle = {
            'eccentricity': 0.0167,  # 轨道偏心率
            'obliquity': 23.5,       # 地轴倾斜角
            'precession': 0.0        # 岁差
        }
        
        # 创建气候区域
        self.climate_zones = self._create_climate_zones()
        
        # 纪元效应配置
        self.epoch_effects = {
            ClimateEpoch.TEMPERATE: ClimateEffect(
                temperature_modifier=1.0,
                humidity_modifier=1.0,
                resource_abundance=1.0,
                energy_cost_modifier=1.0,
                health_modifier=1.0,
                reproduction_modifier=1.0,
                migration_pressure=0.0
            ),
            
            ClimateEpoch.ICE_AGE: ClimateEffect(
                temperature_modifier=0.4,      # 极低温度
                humidity_modifier=0.6,         # 低湿度
                resource_abundance=0.3,        # 资源稀缺
                energy_cost_modifier=1.8,      # 高能量消耗
                health_modifier=0.7,           # 健康挑战
                reproduction_modifier=0.4,     # 繁殖困难
                migration_pressure=0.8         # 强迁移压力
            ),
            
            ClimateEpoch.GREENHOUSE: ClimateEffect(
                temperature_modifier=1.6,      # 高温
                humidity_modifier=1.4,         # 高湿度
                resource_abundance=1.3,        # 丰富资源
                energy_cost_modifier=1.2,      # 略高能耗（散热）
                health_modifier=0.9,           # 轻微健康影响
                reproduction_modifier=1.2,     # 有利繁殖
                migration_pressure=0.2         # 轻微迁移
            ),
            
            ClimateEpoch.ARID: ClimateEffect(
                temperature_modifier=1.3,      # 高温
                humidity_modifier=0.3,         # 极低湿度
                resource_abundance=0.5,        # 资源稀缺
                energy_cost_modifier=1.4,      # 高能耗（寻水）
                health_modifier=0.8,           # 健康挑战
                reproduction_modifier=0.6,     # 繁殖困难
                migration_pressure=0.7         # 高迁移压力
            ),
            
            ClimateEpoch.VOLCANIC: ClimateEffect(
                temperature_modifier=0.7,      # 火山冬天
                humidity_modifier=0.8,         # 降湿
                resource_abundance=0.4,        # 资源破坏
                energy_cost_modifier=1.5,      # 高能耗（避险）
                health_modifier=0.6,           # 严重健康影响
                reproduction_modifier=0.3,     # 极低繁殖
                migration_pressure=0.9         # 极高迁移压力
            )
        }
        
        # 统计数据
        self.epoch_history = []
        self.climate_events = []
        
        # 如果启用了减少严酷度，调整气候效应
        if self.reduce_severity:
            self._apply_reduced_severity()
        
        print(f"🌍 气候系统初始化完成")
        print(f"   当前纪元: {self.current_epoch.value}")
        print(f"   世界大小: {world_size}")
        print(f"   气候区域数: {len(self.climate_zones)}")
        if self.reduce_severity:
            print(f"   🛡️ 已启用环境压力减少模式")
    
    def _create_climate_zones(self) -> List[Dict]:
        """创建气候区域"""
        zones = []
        
        # 基于世界纬度创建气候区域
        world_width, world_height = self.world_size
        
        # 北极区 (顶部)
        zones.append({
            'type': ClimateZone.ARCTIC,
            'bounds': (0, 0, world_width, world_height * 0.2),
            'base_temperature': -10,
            'base_humidity': 0.3
        })
        
        # 温带区 (中上部)
        zones.append({
            'type': ClimateZone.TEMPERATE,
            'bounds': (0, world_height * 0.2, world_width, world_height * 0.4),
            'base_temperature': 15,
            'base_humidity': 0.6
        })
        
        # 热带区 (中部)
        zones.append({
            'type': ClimateZone.TROPICAL,
            'bounds': (0, world_height * 0.4, world_width, world_height * 0.3),
            'base_temperature': 28,
            'base_humidity': 0.8
        })
        
        # 沙漠区 (特定区域)
        zones.append({
            'type': ClimateZone.DESERT,
            'bounds': (world_width * 0.6, world_height * 0.6, world_width * 0.4, world_height * 0.3),
            'base_temperature': 35,
            'base_humidity': 0.1
        })
        
        # 海洋区 (边缘)
        zones.append({
            'type': ClimateZone.OCEANIC,
            'bounds': (0, world_height * 0.9, world_width, world_height * 0.1),
            'base_temperature': 12,
            'base_humidity': 0.9
        })
        
        return zones
    
    def _apply_reduced_severity(self):
        """应用减少严酷度的配置"""
        # 减少恶劣气候的负面影响
        severity_reduction = 0.4  # 减少40%的负面影响
        
        for epoch, effect in self.epoch_effects.items():
            if epoch != ClimateEpoch.TEMPERATE:
                # 改善极端温度
                if effect.temperature_modifier < 1.0:
                    effect.temperature_modifier = min(1.0, effect.temperature_modifier + severity_reduction)
                elif effect.temperature_modifier > 1.0:
                    effect.temperature_modifier = max(1.0, effect.temperature_modifier - severity_reduction * 0.5)
                
                # 改善资源可获得性
                if effect.resource_abundance < 1.0:
                    effect.resource_abundance = min(1.0, effect.resource_abundance + severity_reduction)
                
                # 降低能量消耗
                if effect.energy_cost_modifier > 1.0:
                    effect.energy_cost_modifier = max(1.0, effect.energy_cost_modifier - severity_reduction)
                
                # 改善健康影响
                if effect.health_modifier < 1.0:
                    effect.health_modifier = min(1.0, effect.health_modifier + severity_reduction * 0.5)
                
                # 改善繁殖条件
                if effect.reproduction_modifier < 1.0:
                    effect.reproduction_modifier = min(1.0, effect.reproduction_modifier + severity_reduction * 0.6)
                
                # 降低迁移压力
                effect.migration_pressure = max(0.0, effect.migration_pressure - severity_reduction)
    
    def update(self, dt: float):
        """更新气候系统"""
        # 检查是否需要切换纪元
        current_time = time.time()
        if current_time - self.epoch_start_time > self.epoch_duration:
            self._advance_epoch()
    
    def _advance_epoch(self):
        """推进到下一个气候纪元"""
        # 记录当前纪元
        duration = time.time() - self.epoch_start_time
        self.epoch_history.append({
            'epoch': self.current_epoch,
            'duration': duration,
            'end_time': time.time()
        })
        
        # 基于概率选择下一个纪元
        if self.reduce_severity:
            # 启用环境压力减少时，增加稳定气候概率
            epoch_probabilities = {
                ClimateEpoch.TEMPERATE: self.stable_probability,  # 增加稳定期概率
                ClimateEpoch.ICE_AGE: (1 - self.stable_probability) * 0.25,    # 降低恶劣气候概率
                ClimateEpoch.GREENHOUSE: (1 - self.stable_probability) * 0.35,  # 温室期相对温和
                ClimateEpoch.ARID: (1 - self.stable_probability) * 0.25,       # 降低干旱期概率
                ClimateEpoch.VOLCANIC: (1 - self.stable_probability) * 0.15    # 大幅降低火山期概率
            }
        else:
            # 原始概率分布
            epoch_probabilities = {
                ClimateEpoch.TEMPERATE: 0.4,  # 40% - 稳定期最常见
                ClimateEpoch.ICE_AGE: 0.15,    # 15% - 冰河期
                ClimateEpoch.GREENHOUSE: 0.2,  # 20% - 温室期
                ClimateEpoch.ARID: 0.15,       # 15% - 干旱期
                ClimateEpoch.VOLCANIC: 0.1     # 10% - 火山期（最罕见）
            }
        
        # 避免连续相同纪元
        if len(self.epoch_history) > 0:
            last_epoch = self.epoch_history[-1]['epoch']
            epoch_probabilities[last_epoch] *= 0.3
        
        # 重新归一化概率
        total_prob = sum(epoch_probabilities.values())
        for epoch in epoch_probabilities:
            epoch_probabilities[epoch] /= total_prob
        
        # 选择新纪元
        epochs = list(epoch_probabilities.keys())
        probabilities = list(epoch_probabilities.values())
        self.current_epoch = np.random.choice(epochs, p=probabilities)
        
        self.epoch_start_time = time.time()
        
        print(f"\n🌍 气候纪元变化: {self.current_epoch.value}")
        print(f"   预计持续: {self.epoch_duration}秒")
        
        # 记录重大气候事件
        self.climate_events.append({
            'type': 'epoch_change',
            'new_epoch': self.current_epoch,
            'timestamp': time.time()
        })
        
        # 记录气候纪元变化事件
        epoch_info = {
            ClimateEpoch.TEMPERATE: "温带期 - 适宜条件",
            ClimateEpoch.ICE_AGE: "冰河世纪 - 极寒环境",
            ClimateEpoch.GREENHOUSE: "温室期 - 高温高湿",
            ClimateEpoch.ARID: "干旱期 - 高温缺水",
            ClimateEpoch.VOLCANIC: "火山期 - 极端环境"
        }
        
        effects = self.epoch_effects[self.current_epoch]
        
        log_climate_event(
            event_type=EventType.CLIMATE_EPOCH_CHANGE,
            climate_info=self.current_epoch.value,
            description=f"全球气候进入{epoch_info.get(self.current_epoch, self.current_epoch.value)}",
            data={
                'new_epoch': self.current_epoch.value,
                'epoch_duration': self.epoch_duration,
                'temperature_modifier': effects.temperature_modifier,
                'resource_abundance': effects.resource_abundance,
                'energy_cost_modifier': effects.energy_cost_modifier,
                'health_modifier': effects.health_modifier,
                'reproduction_modifier': effects.reproduction_modifier,
                'migration_pressure': effects.migration_pressure,
                'previous_epoch_count': len(self.epoch_history)
            },
            impact_score=8.0 if self.current_epoch != ClimateEpoch.TEMPERATE else 3.0
        )
    
    def get_climate_effects_for_position(self, position: Vector2D) -> ClimateEffect:
        """获取指定位置的气候效应"""
        # 获取当前纪元的基础效应
        base_effect = self.epoch_effects[self.current_epoch]
        
        # 根据位置的气候区域调整
        zone_modifier = self._get_zone_modifier(position)
        
        # 组合效应
        combined_effect = ClimateEffect(
            temperature_modifier=base_effect.temperature_modifier * zone_modifier.temperature_modifier,
            humidity_modifier=base_effect.humidity_modifier * zone_modifier.humidity_modifier,
            resource_abundance=base_effect.resource_abundance * zone_modifier.resource_abundance,
            energy_cost_modifier=base_effect.energy_cost_modifier * zone_modifier.energy_cost_modifier,
            health_modifier=base_effect.health_modifier * zone_modifier.health_modifier,
            reproduction_modifier=base_effect.reproduction_modifier * zone_modifier.reproduction_modifier,
            migration_pressure=max(base_effect.migration_pressure, zone_modifier.migration_pressure)
        )
        
        return combined_effect
    
    def _get_zone_modifier(self, position: Vector2D) -> ClimateEffect:
        """根据气候区域获取修正值"""
        for zone in self.climate_zones:
            bounds = zone['bounds']
            if (bounds[0] <= position.x <= bounds[0] + bounds[2] and
                bounds[1] <= position.y <= bounds[1] + bounds[3]):
                
                zone_type = zone['type']
                
                if zone_type == ClimateZone.ARCTIC:
                    return ClimateEffect(
                        temperature_modifier=0.6,
                        resource_abundance=0.7,
                        energy_cost_modifier=1.3,
                        migration_pressure=0.3
                    )
                elif zone_type == ClimateZone.TROPICAL:
                    return ClimateEffect(
                        temperature_modifier=1.3,
                        humidity_modifier=1.4,
                        resource_abundance=1.4,
                        reproduction_modifier=1.2
                    )
                elif zone_type == ClimateZone.DESERT:
                    return ClimateEffect(
                        temperature_modifier=1.4,
                        humidity_modifier=0.2,
                        resource_abundance=0.4,
                        energy_cost_modifier=1.4,
                        migration_pressure=0.6
                    )
                elif zone_type == ClimateZone.OCEANIC:
                    return ClimateEffect(
                        temperature_modifier=0.9,
                        humidity_modifier=1.2,
                        resource_abundance=1.1,
                        energy_cost_modifier=0.9
                    )
        
        # 默认温带效应
        return ClimateEffect()
    
    def get_status_info(self) -> Dict:
        """获取气候系统状态信息"""
        current_time = time.time()
        epoch_progress = (current_time - self.epoch_start_time) / self.epoch_duration
        
        return {
            'current_epoch': self.current_epoch.value,
            'epoch_progress': epoch_progress,
            'time_remaining': self.epoch_duration - (current_time - self.epoch_start_time),
            'climate_zones': len(self.climate_zones),
            'epoch_history_count': len(self.epoch_history),
            'climate_events_count': len(self.climate_events)
        }
    
    def get_visualization_data(self) -> Dict:
        """获取可视化数据"""
        return {
            'current_epoch': self.current_epoch,
            'climate_zones': self.climate_zones,
            'epoch_effects': self.epoch_effects[self.current_epoch],
            'world_size': self.world_size
        }
    
    def apply_climate_to_agent(self, agent, dt: float):
        """对智能体应用气候效应"""
        climate_effect = self.get_climate_effects_for_position(agent.position)
        
        # 应用能量消耗修正
        if hasattr(agent, 'energy'):
            energy_cost = 0.5 * dt * climate_effect.energy_cost_modifier
            agent.energy = max(0, agent.energy - energy_cost)
        
        # 应用健康修正
        if hasattr(agent, 'health'):
            health_change = (climate_effect.health_modifier - 1.0) * 2.0 * dt
            agent.health = max(0, min(agent.max_health, agent.health + health_change))
        
        # 影响繁殖概率（通过修改行为系统）
        if hasattr(agent, 'behavior_system') and hasattr(agent.behavior_system, 'motivations'):
            if 'reproduction' in agent.behavior_system.motivations:
                original_value = agent.behavior_system.motivations['reproduction'].value
                modified_value = original_value * climate_effect.reproduction_modifier
                agent.behavior_system.motivations['reproduction'].value = modified_value
        
        return climate_effect
    
    def get_climate_history(self) -> List[Dict]:
        """获取气候变化历史
        
        Returns:
            包含气候纪元变化历史的列表，每个条目包含:
            - epoch: 气候纪元
            - timestamp: 变化时间戳
            - duration: 持续时间（如果已结束）
        """
        # 将epoch_history转换为更适合分析的格式
        history = []
        
        for i, record in enumerate(self.epoch_history):
            entry = {
                'epoch': record['epoch'].value,
                'timestamp': record['end_time'] - record['duration'],  # 开始时间
                'duration': record['duration']
            }
            history.append(entry)
        
        # 添加当前正在进行的纪元
        if self.current_epoch:
            current_duration = time.time() - self.epoch_start_time
            current_entry = {
                'epoch': self.current_epoch.value,
                'timestamp': self.epoch_start_time,
                'duration': current_duration,
                'is_current': True
            }
            history.append(current_entry)
        
        return history