"""
Rendering Pipeline - 多尺度渲染管道
统一管理所有尺度的渲染流程

Author: Ben Hsu & Claude
"""

import time
import math
from typing import Dict, Optional
import pygame
import logging

from .scale_manager import ScaleManager, ScaleLevel
from .camera_system import CameraSystem
from .lod_renderer import LODRenderer
from .scale_renderers import MicroRenderer, MesoRenderer, MacroRenderer, GlobalRenderer

logger = logging.getLogger(__name__)


class RenderingPipeline:
    """多尺度渲染管道"""
    
    def __init__(self, scale_manager: ScaleManager, camera_system: CameraSystem):
        self.scale_manager = scale_manager
        self.camera_system = camera_system
        
        # 创建各尺度渲染器
        self.renderers = {
            ScaleLevel.MICRO: MicroRenderer(),
            ScaleLevel.MESO: MesoRenderer(),
            ScaleLevel.MACRO: MacroRenderer(),
            ScaleLevel.GLOBAL: GlobalRenderer()
        }
        
        # 通用LOD渲染器
        self.lod_renderer = LODRenderer()
        
        # 渲染状态
        self.last_render_time = time.time()
        self.frame_count = 0
        self.render_stats = {
            'total_frames': 0,
            'avg_frame_time': 0.0,
            'last_frame_time': 0.0,
            'scale_render_counts': {scale: 0 for scale in ScaleLevel}
        }
        
        # 性能监控
        self.performance_monitor = PerformanceMonitor()
        
        logger.info("RenderingPipeline initialized with all scale renderers")
    
    def render_frame(self, screen: pygame.Surface, world_state: Dict, dt: float):
        """渲染一帧"""
        
        frame_start_time = time.time()
        
        # 清空屏幕
        screen.fill((15, 15, 25))  # 深蓝色背景
        
        # 更新系统
        self.scale_manager.update(dt)
        self.camera_system.update(dt)
        
        # 获取当前尺度和相机
        current_scale = self.scale_manager.current_scale
        camera = self.camera_system.get_main_camera()
        
        # 同步相机缩放与尺度管理器
        camera.set_zoom(self.scale_manager.current_zoom, smooth=False)
        
        # 检查是否应该在此尺度下渲染
        if self.scale_manager.should_render_at_frequency(current_scale):
            # 渲染当前尺度
            renderer = self.renderers[current_scale]
            renderer.render(screen, world_state, camera)
            
            # 更新渲染统计
            self.render_stats['scale_render_counts'][current_scale] += 1
        
        # 渲染过渡效果
        if self.scale_manager.is_in_transition():
            self._render_transition_overlay(screen, world_state, camera)
        
        # 渲染UI覆盖层
        self._render_ui_overlay(screen, world_state, camera)
        
        # 更新性能统计
        self._update_performance_stats(frame_start_time)
        
        self.frame_count += 1
    
    def _render_transition_overlay(self, screen: pygame.Surface, world_state: Dict, camera):
        """渲染尺度切换过渡效果"""
        
        progress = self.scale_manager.get_transition_progress()
        
        # 创建过渡效果 - 简单的淡入淡出
        overlay_alpha = int(50 * (1 - abs(progress - 0.5) * 2))  # 在中间时最透明
        
        if overlay_alpha > 0:
            overlay_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay_surface.fill((255, 255, 255, overlay_alpha))
            screen.blit(overlay_surface, (0, 0))
        
        # 过渡进度指示器
        if progress < 1.0:
            self._render_transition_indicator(screen, progress)
    
    def _render_transition_indicator(self, screen: pygame.Surface, progress: float):
        """渲染过渡进度指示器"""
        
        # 在屏幕中心绘制进度圆圈
        center_x, center_y = screen.get_width() // 2, screen.get_height() // 2
        radius = 30
        
        # 背景圆圈
        pygame.draw.circle(screen, (100, 100, 100), (center_x, center_y), radius, 3)
        
        # 进度弧
        if progress > 0:
            arc_angle = progress * 2 * 3.14159  # 转换为弧度
            
            # 简化的弧形绘制 - 使用多条线段
            segments = int(arc_angle * 20)  # 每弧度20段
            for i in range(segments):
                angle = (i / 20.0) - 3.14159 / 2  # 从顶部开始
                x1 = center_x + (radius - 3) * math.cos(angle)
                y1 = center_y + (radius - 3) * math.sin(angle)
                x2 = center_x + (radius + 3) * math.cos(angle)
                y2 = center_y + (radius + 3) * math.sin(angle)
                
                pygame.draw.line(screen, (0, 255, 0), (x1, y1), (x2, y2), 2)
        
        # 显示切换信息
        font = pygame.font.Font(None, 24)
        from_scale = self.scale_manager.transition_from_scale
        to_scale = self.scale_manager.transition_to_scale
        
        if from_scale and to_scale:
            transition_text = f"{from_scale.value.upper()} → {to_scale.value.upper()}"
            text_surface = font.render(transition_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(center_x, center_y + 50))
            screen.blit(text_surface, text_rect)
    
    def _render_ui_overlay(self, screen: pygame.Surface, world_state: Dict, camera):
        """渲染UI覆盖层"""
        
        # 1. 尺度指示器
        self._render_scale_indicator(screen)
        
        # 2. 相机信息（调试模式）
        if world_state.get('debug_mode', False):
            self._render_camera_debug_info(screen, camera)
        
        # 3. 性能信息
        self._render_performance_info(screen)
        
        # 4. 控制提示
        self._render_control_hints(screen)
    
    def _render_scale_indicator(self, screen: pygame.Surface):
        """渲染尺度指示器"""
        
        # 尺度指示器位置（右上角）
        indicator_x = screen.get_width() - 200
        indicator_y = 20
        
        # 背景
        bg_rect = pygame.Rect(indicator_x - 10, indicator_y - 10, 180, 100)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 150), (0, 0, bg_rect.width, bg_rect.height))
        screen.blit(bg_surface, bg_rect.topleft)
        
        # 当前尺度信息
        font_large = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)
        
        current_scale = self.scale_manager.current_scale
        current_zoom = self.scale_manager.current_zoom
        
        # 尺度名称
        scale_text = font_large.render(f"Scale: {current_scale.value.upper()}", True, (255, 255, 255))
        screen.blit(scale_text, (indicator_x, indicator_y))
        
        # 缩放级别
        zoom_text = font_small.render(f"Zoom: {current_zoom:.2f}x", True, (200, 200, 200))
        screen.blit(zoom_text, (indicator_x, indicator_y + 25))
        
        # 尺度范围
        config = self.scale_manager.get_current_config()
        zoom_range = config['zoom_range']
        range_text = font_small.render(f"Range: {zoom_range[0]:.2f} - {zoom_range[1]:.2f}", True, (150, 150, 150))
        screen.blit(range_text, (indicator_x, indicator_y + 45))
        
        # 过渡状态
        if self.scale_manager.is_in_transition():
            progress = self.scale_manager.get_transition_progress()
            transition_text = font_small.render(f"Transitioning... {progress*100:.0f}%", True, (255, 255, 0))
            screen.blit(transition_text, (indicator_x, indicator_y + 65))
    
    def _render_camera_debug_info(self, screen: pygame.Surface, camera):
        """渲染相机调试信息"""
        
        debug_x = 10
        debug_y = screen.get_height() - 120
        
        font = pygame.font.Font(None, 18)
        
        debug_info = [
            f"Camera Pos: ({camera.position.x:.1f}, {camera.position.y:.1f})",
            f"Target Pos: ({camera.target_position.x:.1f}, {camera.target_position.y:.1f})",
            f"Camera Zoom: {camera.zoom:.3f}",
            f"Target Zoom: {camera.target_zoom:.3f}",
            f"Follow Target: {camera.follow_target is not None}"
        ]
        
        for i, info in enumerate(debug_info):
            text_surface = font.render(info, True, (255, 255, 255))
            screen.blit(text_surface, (debug_x, debug_y + i * 20))
    
    def _render_performance_info(self, screen: pygame.Surface):
        """渲染性能信息"""
        
        perf_x = 10
        perf_y = 10
        
        font = pygame.font.Font(None, 18)
        
        # FPS
        current_fps = 1.0 / max(self.render_stats['last_frame_time'], 0.001)
        fps_color = (0, 255, 0) if current_fps >= 25 else (255, 255, 0) if current_fps >= 15 else (255, 0, 0)
        
        fps_text = font.render(f"FPS: {current_fps:.1f}", True, fps_color)
        screen.blit(fps_text, (perf_x, perf_y))
        
        # 总帧数
        frame_text = font.render(f"Frames: {self.render_stats['total_frames']}", True, (200, 200, 200))
        screen.blit(frame_text, (perf_x, perf_y + 20))
        
        # LOD统计
        lod_stats = self.lod_renderer.get_performance_stats()
        if lod_stats['total_objects'] > 0:
            cull_ratio = lod_stats['cull_ratio']
            cull_text = font.render(f"Culled: {cull_ratio:.1%}", True, (150, 150, 150))
            screen.blit(cull_text, (perf_x, perf_y + 40))
    
    def _render_control_hints(self, screen: pygame.Surface):
        """渲染控制提示"""
        
        hints_x = 10
        hints_y = screen.get_height() - 200
        
        font = pygame.font.Font(None, 16)
        
        hints = [
            "Controls:",
            "1,2,3,4 - Switch scales",
            "WASD - Move camera", 
            "Mouse wheel - Zoom",
            "F - Auto focus",
            "G - Toggle grid",
            "T - Toggle trajectories"
        ]
        
        # 半透明背景
        bg_height = len(hints) * 18 + 10
        bg_surface = pygame.Surface((200, bg_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 100), (0, 0, 200, bg_height))
        screen.blit(bg_surface, (hints_x - 5, hints_y - 5))
        
        for i, hint in enumerate(hints):
            color = (255, 255, 255) if i == 0 else (180, 180, 180)
            text_surface = font.render(hint, True, color)
            screen.blit(text_surface, (hints_x, hints_y + i * 18))
    
    def _update_performance_stats(self, frame_start_time: float):
        """更新性能统计"""
        
        frame_time = time.time() - frame_start_time
        
        self.render_stats['total_frames'] += 1
        self.render_stats['last_frame_time'] = frame_time
        
        # 计算平均帧时间（滑动窗口）
        alpha = 0.1  # 平滑因子
        self.render_stats['avg_frame_time'] = (
            alpha * frame_time + 
            (1 - alpha) * self.render_stats['avg_frame_time']
        )
    
    def toggle_renderer_feature(self, renderer_scale: ScaleLevel, feature: str, enabled: bool):
        """切换渲染器特性"""
        
        if renderer_scale not in self.renderers:
            return False
        
        renderer = self.renderers[renderer_scale]
        
        # 微观渲染器特性
        if renderer_scale == ScaleLevel.MICRO and isinstance(renderer, MicroRenderer):
            if feature == 'perception_radius':
                renderer.show_perception_radius = enabled
            elif feature == 'trajectories':
                renderer.show_trajectories = enabled
            elif feature == 'social_connections':
                renderer.show_social_connections = enabled
            else:
                return False
        
        logger.info(f"Toggled {feature} for {renderer_scale.value} renderer: {enabled}")
        return True
    
    def get_render_stats(self) -> Dict:
        """获取渲染统计信息"""
        
        current_fps = 1.0 / max(self.render_stats['last_frame_time'], 0.001)
        avg_fps = 1.0 / max(self.render_stats['avg_frame_time'], 0.001)
        
        return {
            'current_fps': current_fps,
            'average_fps': avg_fps,
            'total_frames': self.render_stats['total_frames'],
            'last_frame_time': self.render_stats['last_frame_time'],
            'scale_render_counts': self.render_stats['scale_render_counts'].copy(),
            'lod_stats': self.lod_renderer.get_performance_stats(),
            'performance_monitor': self.performance_monitor.get_stats()
        }
    
    def reset_stats(self):
        """重置统计信息"""
        
        self.render_stats = {
            'total_frames': 0,
            'avg_frame_time': 0.0,
            'last_frame_time': 0.0,
            'scale_render_counts': {scale: 0 for scale in ScaleLevel}
        }
        
        self.lod_renderer.reset_performance_stats()
        self.performance_monitor.reset()
        
        logger.info("Rendering pipeline statistics reset")


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.frame_times = []
        self.max_frame_times = 100  # 保留最近100帧的时间
        
        self.performance_alerts = []
        self.alert_thresholds = {
            'low_fps': 15.0,
            'high_frame_time': 0.1,  # 100ms
            'frame_time_variance': 0.05  # 50ms
        }
    
    def record_frame_time(self, frame_time: float):
        """记录帧时间"""
        
        self.frame_times.append(frame_time)
        
        if len(self.frame_times) > self.max_frame_times:
            self.frame_times.pop(0)
        
        # 检查性能警告
        self._check_performance_alerts(frame_time)
    
    def _check_performance_alerts(self, frame_time: float):
        """检查性能警告"""
        
        current_time = time.time()
        
        # 检查低FPS
        current_fps = 1.0 / max(frame_time, 0.001)
        if current_fps < self.alert_thresholds['low_fps']:
            self.performance_alerts.append({
                'type': 'low_fps',
                'timestamp': current_time,
                'value': current_fps,
                'message': f"Low FPS detected: {current_fps:.1f}"
            })
        
        # 检查高帧时间
        if frame_time > self.alert_thresholds['high_frame_time']:
            self.performance_alerts.append({
                'type': 'high_frame_time',
                'timestamp': current_time,
                'value': frame_time,
                'message': f"High frame time: {frame_time*1000:.1f}ms"
            })
        
        # 限制警告历史长度
        cutoff_time = current_time - 30.0  # 保留30秒内的警告
        self.performance_alerts = [
            alert for alert in self.performance_alerts 
            if alert['timestamp'] > cutoff_time
        ]
    
    def get_stats(self) -> Dict:
        """获取性能统计"""
        
        if not self.frame_times:
            return {
                'avg_frame_time': 0.0,
                'min_frame_time': 0.0,
                'max_frame_time': 0.0,
                'frame_time_std': 0.0,
                'avg_fps': 0.0,
                'recent_alerts': []
            }
        
        import statistics
        
        avg_frame_time = statistics.mean(self.frame_times)
        min_frame_time = min(self.frame_times)
        max_frame_time = max(self.frame_times)
        frame_time_std = statistics.stdev(self.frame_times) if len(self.frame_times) > 1 else 0.0
        avg_fps = 1.0 / max(avg_frame_time, 0.001)
        
        # 最近的警告（最多5个）
        recent_alerts = self.performance_alerts[-5:] if self.performance_alerts else []
        
        return {
            'avg_frame_time': avg_frame_time,
            'min_frame_time': min_frame_time,
            'max_frame_time': max_frame_time,
            'frame_time_std': frame_time_std,
            'avg_fps': avg_fps,
            'recent_alerts': recent_alerts
        }
    
    def reset(self):
        """重置监控器"""
        self.frame_times.clear()
        self.performance_alerts.clear()