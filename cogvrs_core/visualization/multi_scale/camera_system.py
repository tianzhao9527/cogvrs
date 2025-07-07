"""
Camera System - 相机系统
处理世界坐标转换、视口计算和相机控制

Author: Ben Hsu & Claude
"""

import math
from typing import Tuple, Optional, List
import pygame
import logging

from ...core.physics_engine import Vector2D

logger = logging.getLogger(__name__)


class Camera:
    """相机类 - 处理视角和坐标转换"""
    
    def __init__(self, world_size: Tuple[int, int], screen_size: Tuple[int, int]):
        self.world_size = world_size
        self.screen_size = screen_size
        
        # 相机位置（世界坐标）
        self.position = Vector2D(world_size[0] / 2, world_size[1] / 2)
        self.target_position = Vector2D(world_size[0] / 2, world_size[1] / 2)
        
        # 缩放设置
        self.zoom = 1.0
        self.target_zoom = 1.0
        
        # 移动设置
        self.movement_speed = 5.0
        self.zoom_speed = 2.0
        self.smooth_factor = 8.0
        
        # 边界限制
        self.enable_bounds = True
        self.boundary_padding = 50  # 边界缓冲区
        
        # 跟随模式
        self.follow_target = None
        self.follow_smooth_factor = 12.0
        
        logger.debug(f"Camera initialized: world={world_size}, screen={screen_size}")
    
    def world_to_screen(self, world_pos: Vector2D) -> Vector2D:
        """世界坐标转屏幕坐标"""
        # 计算相对于相机的位置
        relative_pos = world_pos - self.position
        
        # 应用缩放
        scaled_pos = relative_pos * self.zoom
        
        # 转换到屏幕中心
        screen_x = scaled_pos.x + self.screen_size[0] / 2
        screen_y = scaled_pos.y + self.screen_size[1] / 2
        
        return Vector2D(screen_x, screen_y)
    
    def screen_to_world(self, screen_pos: Vector2D) -> Vector2D:
        """屏幕坐标转世界坐标"""
        # 转换到相机坐标系
        camera_x = screen_pos.x - self.screen_size[0] / 2
        camera_y = screen_pos.y - self.screen_size[1] / 2
        
        # 逆向缩放
        world_relative = Vector2D(camera_x / self.zoom, camera_y / self.zoom)
        
        # 加上相机位置
        return self.position + world_relative
    
    def get_visible_area(self) -> pygame.Rect:
        """获取可见区域（世界坐标）"""
        # 计算可见区域的半宽半高
        half_width = (self.screen_size[0] / 2) / self.zoom
        half_height = (self.screen_size[1] / 2) / self.zoom
        
        # 计算边界
        left = self.position.x - half_width
        top = self.position.y - half_height
        width = half_width * 2
        height = half_height * 2
        
        return pygame.Rect(left, top, width, height)
    
    def is_visible(self, world_pos: Vector2D, radius: float = 0) -> bool:
        """检查世界坐标点是否在可见区域内"""
        visible_area = self.get_visible_area()
        
        # 扩展检查区域（考虑对象半径）
        expanded_area = pygame.Rect(
            visible_area.left - radius,
            visible_area.top - radius,
            visible_area.width + radius * 2,
            visible_area.height + radius * 2
        )
        
        return expanded_area.collidepoint(world_pos.x, world_pos.y)
    
    def move_to(self, world_pos: Vector2D, smooth: bool = True):
        """移动相机到指定位置"""
        if smooth:
            self.target_position = world_pos
        else:
            self.position = world_pos
            self.target_position = world_pos
    
    def move_by(self, offset: Vector2D, smooth: bool = True):
        """相对移动相机"""
        new_pos = (self.target_position if smooth else self.position) + offset
        self.move_to(new_pos, smooth)
    
    def set_zoom(self, zoom_level: float, smooth: bool = True):
        """设置缩放级别"""
        zoom_level = max(0.01, min(10.0, zoom_level))  # 限制缩放范围
        
        if smooth:
            self.target_zoom = zoom_level
        else:
            self.zoom = zoom_level
            self.target_zoom = zoom_level
    
    def zoom_by(self, zoom_delta: float, smooth: bool = True):
        """相对缩放"""
        new_zoom = (self.target_zoom if smooth else self.zoom) * zoom_delta
        self.set_zoom(new_zoom, smooth)
    
    def set_follow_target(self, target):
        """设置跟随目标"""
        self.follow_target = target
    
    def clear_follow_target(self):
        """清除跟随目标"""
        self.follow_target = None
    
    def update(self, dt: float):
        """更新相机状态"""
        
        # 跟随目标
        if self.follow_target and hasattr(self.follow_target, 'position'):
            target_pos = Vector2D(self.follow_target.position.x, self.follow_target.position.y)
            self.target_position = target_pos
        
        # 平滑移动到目标位置
        if (self.position - self.target_position).magnitude() > 0.1:
            movement = (self.target_position - self.position) * self.smooth_factor * dt
            self.position = self.position + movement
        
        # 平滑缩放到目标级别
        if abs(self.zoom - self.target_zoom) > 0.001:
            zoom_change = (self.target_zoom - self.zoom) * self.zoom_speed * dt
            self.zoom += zoom_change
        
        # 边界限制
        if self.enable_bounds:
            self._apply_boundary_limits()
    
    def _apply_boundary_limits(self):
        """应用边界限制"""
        visible_area = self.get_visible_area()
        
        # 计算边界
        min_x = visible_area.width / 2 - self.boundary_padding
        max_x = self.world_size[0] - visible_area.width / 2 + self.boundary_padding
        min_y = visible_area.height / 2 - self.boundary_padding
        max_y = self.world_size[1] - visible_area.height / 2 + self.boundary_padding
        
        # 限制位置
        self.position.x = max(min_x, min(max_x, self.position.x))
        self.position.y = max(min_y, min(max_y, self.position.y))
        
        # 同时限制目标位置
        self.target_position.x = max(min_x, min(max_x, self.target_position.x))
        self.target_position.y = max(min_y, min(max_y, self.target_position.y))
    
    def get_distance_to_camera(self, world_pos: Vector2D) -> float:
        """计算世界坐标点到相机的距离"""
        return self.position.distance_to(world_pos)
    
    def focus_on_area(self, center: Vector2D, radius: float, margin: float = 1.2):
        """聚焦到指定区域"""
        # 移动到中心
        self.move_to(center)
        
        # 计算合适的缩放级别
        required_zoom_x = self.screen_size[0] / (radius * 2 * margin)
        required_zoom_y = self.screen_size[1] / (radius * 2 * margin)
        optimal_zoom = min(required_zoom_x, required_zoom_y)
        
        self.set_zoom(optimal_zoom)


class CameraSystem:
    """相机系统 - 管理多个相机和视角切换"""
    
    def __init__(self, world_size: Tuple[int, int], screen_size: Tuple[int, int]):
        self.world_size = world_size
        self.screen_size = screen_size
        
        # 主相机
        self.main_camera = Camera(world_size, screen_size)
        
        # 相机预设位置
        self.camera_presets = {
            'center': Vector2D(world_size[0] / 2, world_size[1] / 2),
            'top_left': Vector2D(world_size[0] / 4, world_size[1] / 4),
            'top_right': Vector2D(world_size[0] * 3/4, world_size[1] / 4),
            'bottom_left': Vector2D(world_size[0] / 4, world_size[1] * 3/4),
            'bottom_right': Vector2D(world_size[0] * 3/4, world_size[1] * 3/4)
        }
        
        # 智能焦点系统
        self.auto_focus_enabled = False
        self.focus_history = []
        self.max_focus_history = 10
        
        logger.info(f"CameraSystem initialized with world size: {world_size}")
    
    def get_main_camera(self) -> Camera:
        """获取主相机"""
        return self.main_camera
    
    def update(self, dt: float):
        """更新相机系统"""
        self.main_camera.update(dt)
        
        # 智能焦点更新
        if self.auto_focus_enabled:
            self._update_auto_focus()
    
    def handle_keyboard_input(self, keys_pressed, scale_manager) -> bool:
        """处理键盘输入"""
        camera_moved = False
        movement_speed = scale_manager.get_camera_speed()
        
        # WASD 移动
        movement = Vector2D(0, 0)
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            movement.y -= movement_speed
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            movement.y += movement_speed
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            movement.x -= movement_speed
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            movement.x += movement_speed
        
        if movement.magnitude() > 0:
            self.main_camera.move_by(movement)
            camera_moved = True
        
        return camera_moved
    
    def handle_mouse_input(self, event: pygame.event.Event, scale_manager) -> bool:
        """处理鼠标输入"""
        handled = False
        
        if event.type == pygame.MOUSEWHEEL:
            # 滚轮缩放
            zoom_factor = 1.1 if event.y > 0 else 0.9
            
            # 获取鼠标位置作为缩放中心
            mouse_pos = pygame.mouse.get_pos()
            world_mouse_pos = self.main_camera.screen_to_world(Vector2D(mouse_pos[0], mouse_pos[1]))
            
            # 缩放
            old_zoom = self.main_camera.zoom
            new_zoom = old_zoom * zoom_factor
            
            # 通过scale_manager设置缩放（可能触发尺度切换）
            scale_manager.set_zoom(new_zoom)
            
            # 调整相机位置，使鼠标位置保持不变
            actual_new_zoom = scale_manager.current_zoom
            if abs(actual_new_zoom - old_zoom) > 0.001:
                zoom_ratio = actual_new_zoom / old_zoom
                camera_to_mouse = world_mouse_pos - self.main_camera.position
                camera_offset = camera_to_mouse * (1 - 1/zoom_ratio)
                self.main_camera.move_by(camera_offset, smooth=False)
            
            handled = True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:  # 中键
                # 中键点击居中
                mouse_pos = pygame.mouse.get_pos()
                world_pos = self.main_camera.screen_to_world(Vector2D(mouse_pos[0], mouse_pos[1]))
                self.main_camera.move_to(world_pos)
                handled = True
        
        return handled
    
    def focus_on_agents(self, agents: List, margin: float = 1.5):
        """聚焦到一组智能体"""
        if not agents:
            return
        
        # 计算包围盒
        min_x = min(agent.position.x for agent in agents)
        max_x = max(agent.position.x for agent in agents)
        min_y = min(agent.position.y for agent in agents)
        max_y = max(agent.position.y for agent in agents)
        
        # 计算中心和半径
        center = Vector2D((min_x + max_x) / 2, (min_y + max_y) / 2)
        radius = max((max_x - min_x) / 2, (max_y - min_y) / 2)
        
        # 确保最小半径
        radius = max(radius, 50)
        
        self.main_camera.focus_on_area(center, radius, margin)
        
        # 记录焦点历史
        self.focus_history.append({
            'timestamp': pygame.time.get_ticks(),
            'center': center,
            'radius': radius,
            'target_type': 'agents',
            'target_count': len(agents)
        })
        
        if len(self.focus_history) > self.max_focus_history:
            self.focus_history.pop(0)
    
    def focus_on_interesting_event(self, world_state: dict) -> bool:
        """自动聚焦到有趣的事件"""
        
        # 优先级1: 新生或死亡事件
        if 'recent_births' in world_state and world_state['recent_births']:
            birth_event = world_state['recent_births'][0]
            if hasattr(birth_event, 'position'):
                self.main_camera.move_to(Vector2D(birth_event.position.x, birth_event.position.y))
                return True
        
        # 优先级2: 冲突或异常行为
        agents = world_state.get('agents', [])
        if agents:
            # 寻找能量最低的智能体（可能处于危险中）
            critical_agents = [agent for agent in agents if hasattr(agent, 'energy') and agent.energy < 20]
            if critical_agents:
                self.focus_on_agents(critical_agents[:3])
                return True
            
            # 寻找社交最活跃的区域
            if all(hasattr(agent, 'social_interactions') for agent in agents):
                social_agents = sorted(agents, key=lambda a: a.social_interactions, reverse=True)[:5]
                if social_agents[0].social_interactions > 10:
                    self.focus_on_agents(social_agents)
                    return True
        
        return False
    
    def go_to_preset(self, preset_name: str):
        """移动到预设位置"""
        if preset_name in self.camera_presets:
            self.main_camera.move_to(self.camera_presets[preset_name])
            logger.debug(f"Camera moved to preset: {preset_name}")
    
    def enable_auto_focus(self, enabled: bool = True):
        """启用/禁用自动焦点"""
        self.auto_focus_enabled = enabled
        logger.info(f"Auto focus {'enabled' if enabled else 'disabled'}")
    
    def _update_auto_focus(self):
        """更新自动焦点系统"""
        # 这里可以实现更复杂的自动焦点逻辑
        # 比如检测世界状态变化，自动跟随有趣的事件
        pass
    
    def get_camera_info(self) -> dict:
        """获取相机信息"""
        camera = self.main_camera
        visible_area = camera.get_visible_area()
        
        return {
            'position': {'x': camera.position.x, 'y': camera.position.y},
            'target_position': {'x': camera.target_position.x, 'y': camera.target_position.y},
            'zoom': camera.zoom,
            'target_zoom': camera.target_zoom,
            'visible_area': {
                'left': visible_area.left,
                'top': visible_area.top,
                'width': visible_area.width,
                'height': visible_area.height
            },
            'follow_target': camera.follow_target is not None,
            'auto_focus_enabled': self.auto_focus_enabled
        }