"""
Scale Manager - 尺度管理器
管理四个尺度层次的状态和切换逻辑

Author: Ben Hsu & Claude
"""

import time
import math
from typing import Dict, Tuple, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ScaleLevel(Enum):
    """尺度层次枚举"""
    MICRO = "micro"      # 微观 - 个体细节
    MESO = "meso"        # 中观 - 群体交互
    MACRO = "macro"      # 宏观 - 部落/文明
    GLOBAL = "global"    # 全球 - 世界概览


class ScaleManager:
    """尺度管理器 - 控制多尺度可视化系统的核心逻辑"""
    
    def __init__(self, world_size: Tuple[int, int] = (1600, 1200)):
        self.world_size = world_size
        
        # 尺度配置
        self.scale_configs = {
            ScaleLevel.MICRO: {
                'zoom_range': (1.0, 5.0),
                'focus_radius': 50,
                'detail_level': 'maximum',
                'update_frequency': 30,
                'render_elements': ['agents', 'detailed_behavior', 'energy_bars', 'status_icons'],
                'camera_speed': 5.0
            },
            
            ScaleLevel.MESO: {
                'zoom_range': (0.6, 1.2),  # 提高最小缩放以便看到更多细节
                'focus_radius': 200,
                'detail_level': 'high',
                'update_frequency': 20,
                'render_elements': ['agent_groups', 'social_links', 'resource_flows', 'territories'],
                'camera_speed': 15.0
            },
            
            ScaleLevel.MACRO: {
                'zoom_range': (0.2, 0.8),  # 提高最小缩放以显示更多内容
                'focus_radius': 1000,
                'detail_level': 'medium',
                'update_frequency': 10,
                'render_elements': ['tribes', 'trade_routes', 'boundaries', 'major_events'],
                'camera_speed': 50.0
            },
            
            ScaleLevel.GLOBAL: {
                'zoom_range': (0.1, 0.3),  # 显著提高最小缩放以确保内容可见
                'focus_radius': float('inf'),
                'detail_level': 'low',
                'update_frequency': 5,
                'render_elements': ['civilizations', 'climate_zones', 'resource_distribution', 'global_trends'],
                'camera_speed': 100.0
            }
        }
        
        # 当前状态
        self.current_scale = ScaleLevel.MICRO
        self.current_zoom = 1.0
        self.target_zoom = 1.0
        
        # 过渡动画
        self.transition_active = False
        self.transition_start_time = 0
        self.transition_duration = 0.5  # 0.5秒过渡时间
        self.transition_from_scale = None
        self.transition_to_scale = None
        
        # 性能监控
        self.last_update_time = {}
        self.frame_skip_counters = {}
        
        for scale in ScaleLevel:
            self.last_update_time[scale] = 0
            self.frame_skip_counters[scale] = 0
        
        logger.info(f"ScaleManager initialized with world size: {world_size}")
    
    def get_current_config(self) -> Dict:
        """获取当前尺度配置"""
        return self.scale_configs[self.current_scale].copy()
    
    def set_scale(self, new_scale: ScaleLevel, animate: bool = True) -> bool:
        """设置新的尺度层次"""
        if new_scale == self.current_scale:
            return False
        
        old_scale = self.current_scale
        
        if animate and not self.transition_active:
            # 启动过渡动画
            self.transition_active = True
            self.transition_start_time = time.time()
            self.transition_from_scale = old_scale
            self.transition_to_scale = new_scale
            
            # 计算目标缩放级别
            new_config = self.scale_configs[new_scale]
            self.target_zoom = new_config['zoom_range'][0]  # 使用最小缩放作为默认
        else:
            # 立即切换
            self.current_scale = new_scale
            new_config = self.scale_configs[new_scale]
            self.current_zoom = new_config['zoom_range'][0]
            self.target_zoom = self.current_zoom
        
        logger.info(f"Scale change: {old_scale.value} → {new_scale.value} (animate: {animate})")
        return True
    
    def set_zoom(self, zoom_level: float) -> bool:
        """设置缩放级别，可能触发尺度切换"""
        zoom_level = max(0.005, min(10.0, zoom_level))  # 限制缩放范围
        
        # 检查是否需要切换尺度
        new_scale = self._determine_scale_from_zoom(zoom_level)
        
        if new_scale != self.current_scale:
            self.set_scale(new_scale, animate=True)
        else:
            self.current_zoom = zoom_level
            self.target_zoom = zoom_level
        
        return True
    
    def _determine_scale_from_zoom(self, zoom_level: float) -> ScaleLevel:
        """根据缩放级别确定最合适的尺度"""
        
        # 从最小尺度开始检查
        for scale in [ScaleLevel.GLOBAL, ScaleLevel.MACRO, ScaleLevel.MESO, ScaleLevel.MICRO]:
            zoom_range = self.scale_configs[scale]['zoom_range']
            if zoom_range[0] <= zoom_level <= zoom_range[1]:
                return scale
        
        # 如果超出所有范围，选择最接近的
        if zoom_level < 0.01:
            return ScaleLevel.GLOBAL
        else:
            return ScaleLevel.MICRO
    
    def update(self, dt: float):
        """更新尺度管理器状态"""
        
        # 更新过渡动画
        if self.transition_active:
            self._update_transition(dt)
        
        # 更新缩放平滑插值
        if abs(self.current_zoom - self.target_zoom) > 0.001:
            zoom_speed = 8.0 * dt  # 缩放速度
            if self.current_zoom < self.target_zoom:
                self.current_zoom = min(self.target_zoom, self.current_zoom + zoom_speed)
            else:
                self.current_zoom = max(self.target_zoom, self.current_zoom - zoom_speed)
    
    def _update_transition(self, dt: float):
        """更新尺度切换过渡动画"""
        
        current_time = time.time()
        elapsed = current_time - self.transition_start_time
        progress = min(1.0, elapsed / self.transition_duration)
        
        if progress >= 1.0:
            # 过渡完成
            self.transition_active = False
            self.current_scale = self.transition_to_scale
            self.current_zoom = self.target_zoom
            
            logger.debug(f"Transition completed: {self.transition_from_scale.value} → {self.transition_to_scale.value}")
        else:
            # 过渡进行中 - 使用缓动函数
            eased_progress = self._ease_in_out_cubic(progress)
            
            # 插值缩放级别
            from_config = self.scale_configs[self.transition_from_scale]
            to_config = self.scale_configs[self.transition_to_scale]
            
            from_zoom = from_config['zoom_range'][0]
            to_zoom = to_config['zoom_range'][0]
            
            self.current_zoom = from_zoom + (to_zoom - from_zoom) * eased_progress
    
    def _ease_in_out_cubic(self, t: float) -> float:
        """三次缓动函数"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    def should_render_at_frequency(self, scale: ScaleLevel) -> bool:
        """检查是否应该在此帧渲染指定尺度"""
        
        current_time = time.time()
        target_frequency = self.scale_configs[scale]['update_frequency']
        target_interval = 1.0 / target_frequency
        
        if current_time - self.last_update_time[scale] >= target_interval:
            self.last_update_time[scale] = current_time
            self.frame_skip_counters[scale] = 0
            return True
        else:
            self.frame_skip_counters[scale] += 1
            return False
    
    def get_camera_speed(self) -> float:
        """获取当前尺度的相机移动速度"""
        return self.scale_configs[self.current_scale]['camera_speed']
    
    def get_focus_radius(self) -> float:
        """获取当前尺度的焦点半径"""
        return self.scale_configs[self.current_scale]['focus_radius']
    
    def get_render_elements(self) -> list:
        """获取当前尺度应该渲染的元素列表"""
        return self.scale_configs[self.current_scale]['render_elements'].copy()
    
    def is_in_transition(self) -> bool:
        """检查是否正在进行尺度切换"""
        return self.transition_active
    
    def get_transition_progress(self) -> float:
        """获取过渡动画进度 (0.0-1.0)"""
        if not self.transition_active:
            return 1.0
        
        current_time = time.time()
        elapsed = current_time - self.transition_start_time
        return min(1.0, elapsed / self.transition_duration)
    
    def get_effective_zoom_for_distance(self, distance_to_camera: float) -> float:
        """根据距离相机的距离计算有效缩放级别"""
        base_zoom = self.current_zoom
        distance_factor = max(0.1, 100.0 / max(distance_to_camera, 1.0))
        return base_zoom * distance_factor
    
    def get_scale_info(self) -> Dict:
        """获取当前尺度的详细信息"""
        config = self.get_current_config()
        
        return {
            'current_scale': self.current_scale.value,
            'current_zoom': self.current_zoom,
            'target_zoom': self.target_zoom,
            'zoom_range': config['zoom_range'],
            'is_transitioning': self.transition_active,
            'transition_progress': self.get_transition_progress(),
            'camera_speed': config['camera_speed'],
            'focus_radius': config['focus_radius'],
            'render_elements': config['render_elements'],
            'update_frequency': config['update_frequency']
        }