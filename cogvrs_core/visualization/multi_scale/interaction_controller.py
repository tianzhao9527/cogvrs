"""
Interaction Controller - 多尺度交互控制器
处理用户输入和尺度切换逻辑

Author: Ben Hsu & Claude
"""

import pygame
from typing import Dict, List, Optional, Tuple
import logging

from ...core.physics_engine import Vector2D
from .scale_manager import ScaleManager, ScaleLevel
from .camera_system import CameraSystem
from .rendering_pipeline import RenderingPipeline

logger = logging.getLogger(__name__)


class InteractionController:
    """多尺度交互控制器"""
    
    def __init__(self, scale_manager: ScaleManager, camera_system: CameraSystem, 
                 rendering_pipeline: RenderingPipeline):
        self.scale_manager = scale_manager
        self.camera_system = camera_system
        self.rendering_pipeline = rendering_pipeline
        
        # 键盘状态
        self.keys_pressed = set()
        self.key_repeat_delay = 200  # 按键重复延迟（毫秒）
        self.last_key_times = {}
        
        # 鼠标状态
        self.mouse_pos = (0, 0)
        self.mouse_buttons = [False] * 10  # 支持最多10个鼠标按钮
        self.mouse_drag_start = None
        self.is_dragging = False
        
        # 控制模式
        self.control_modes = {
            'camera': True,      # 相机控制
            'scale_switching': True,  # 尺度切换
            'object_selection': True,  # 对象选择
            'debug': False       # 调试模式
        }
        
        # 选择状态
        self.selected_objects = []
        self.hover_object = None
        
        # 快捷键映射
        self.keybindings = {
            # 尺度切换
            pygame.K_1: ('switch_scale', ScaleLevel.MICRO),
            pygame.K_2: ('switch_scale', ScaleLevel.MESO),
            pygame.K_3: ('switch_scale', ScaleLevel.MACRO),
            pygame.K_4: ('switch_scale', ScaleLevel.GLOBAL),
            
            # 相机控制
            pygame.K_f: ('camera', 'auto_focus'),
            pygame.K_c: ('camera', 'center'),
            pygame.K_r: ('camera', 'reset'),
            
            # 显示选项
            pygame.K_g: ('toggle', 'grid'),
            pygame.K_t: ('toggle', 'trajectories'),
            pygame.K_p: ('toggle', 'perception_radius'),
            pygame.K_l: ('toggle', 'social_connections'),
            
            # 调试
            pygame.K_F1: ('debug', 'toggle_debug_mode'),
            pygame.K_F2: ('debug', 'print_stats'),
            pygame.K_F3: ('debug', 'reset_stats'),
        }
        
        # 状态标志
        self.display_options = {
            'grid': False,
            'trajectories': False,
            'perception_radius': False,
            'social_connections': False
        }
        
        logger.info("InteractionController initialized")
    
    def handle_events(self, events: List[pygame.event.Event], world_state: Dict) -> Dict:
        """处理事件列表"""
        
        interaction_result = {
            'scale_changed': False,
            'camera_moved': False,
            'selection_changed': False,
            'display_options_changed': False,
            'quit_requested': False
        }
        
        for event in events:
            if event.type == pygame.QUIT:
                interaction_result['quit_requested'] = True
            
            elif event.type == pygame.KEYDOWN:
                result = self._handle_keydown(event, world_state)
                self._merge_results(interaction_result, result)
            
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = self._handle_mouse_button_down(event, world_state)
                self._merge_results(interaction_result, result)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                result = self._handle_mouse_button_up(event, world_state)
                self._merge_results(interaction_result, result)
            
            elif event.type == pygame.MOUSEMOTION:
                result = self._handle_mouse_motion(event, world_state)
                self._merge_results(interaction_result, result)
            
            elif event.type == pygame.MOUSEWHEEL:
                result = self._handle_mouse_wheel(event, world_state)
                self._merge_results(interaction_result, result)
        
        # 处理持续按键
        continuous_result = self._handle_continuous_input(world_state)
        self._merge_results(interaction_result, continuous_result)
        
        return interaction_result
    
    def _handle_keydown(self, event: pygame.event.Event, world_state: Dict) -> Dict:
        """处理按键按下"""
        
        result = {
            'scale_changed': False,
            'camera_moved': False,
            'selection_changed': False,
            'display_options_changed': False
        }
        
        self.keys_pressed.add(event.key)
        self.last_key_times[event.key] = pygame.time.get_ticks()
        
        # 检查快捷键
        if event.key in self.keybindings:
            action_type, action_data = self.keybindings[event.key]
            
            if action_type == 'switch_scale':
                if self.control_modes['scale_switching']:
                    success = self.scale_manager.set_scale(action_data, animate=True)
                    if success:
                        result['scale_changed'] = True
                        logger.info(f"Scale switched to {action_data.value} via keyboard")
            
            elif action_type == 'camera':
                if self.control_modes['camera']:
                    success = self._handle_camera_action(action_data, world_state)
                    if success:
                        result['camera_moved'] = True
            
            elif action_type == 'toggle':
                success = self._handle_display_toggle(action_data)
                if success:
                    result['display_options_changed'] = True
            
            elif action_type == 'debug':
                self._handle_debug_action(action_data, world_state)
        
        return result
    
    def _handle_keyup(self, event: pygame.event.Event):
        """处理按键释放"""
        self.keys_pressed.discard(event.key)
    
    def _handle_mouse_button_down(self, event: pygame.event.Event, world_state: Dict) -> Dict:
        """处理鼠标按下"""
        
        result = {
            'scale_changed': False,
            'camera_moved': False,
            'selection_changed': False,
            'display_options_changed': False
        }
        
        # 安全地设置鼠标按钮状态
        if 1 <= event.button <= len(self.mouse_buttons):
            self.mouse_buttons[event.button - 1] = True
        self.mouse_pos = event.pos
        
        if event.button == 1:  # 左键
            if self.control_modes['object_selection']:
                # 对象选择
                selected_obj = self._find_object_at_position(event.pos, world_state)
                if selected_obj:
                    if selected_obj not in self.selected_objects:
                        if not (pygame.key.get_pressed()[pygame.K_LCTRL] or 
                               pygame.key.get_pressed()[pygame.K_RCTRL]):
                            self.selected_objects.clear()
                        self.selected_objects.append(selected_obj)
                        result['selection_changed'] = True
                        logger.debug(f"Object selected: {type(selected_obj).__name__}")
                else:
                    if not (pygame.key.get_pressed()[pygame.K_LCTRL] or 
                           pygame.key.get_pressed()[pygame.K_RCTRL]):
                        if self.selected_objects:
                            self.selected_objects.clear()
                            result['selection_changed'] = True
            
            # 开始拖拽
            self.mouse_drag_start = event.pos
        
        elif event.button == 2:  # 中键 - 居中相机
            if self.control_modes['camera']:
                screen_pos = Vector2D(event.pos[0], event.pos[1])
                world_pos = self.camera_system.main_camera.screen_to_world(screen_pos)
                self.camera_system.main_camera.move_to(world_pos)
                result['camera_moved'] = True
        
        elif event.button == 3:  # 右键 - 上下文菜单
            self._show_context_menu(event.pos, world_state)
        
        return result
    
    def _handle_mouse_button_up(self, event: pygame.event.Event, world_state: Dict) -> Dict:
        """处理鼠标释放"""
        
        result = {
            'scale_changed': False,
            'camera_moved': False,
            'selection_changed': False,
            'display_options_changed': False
        }
        
        # 安全地设置鼠标按钮状态
        if 1 <= event.button <= len(self.mouse_buttons):
            self.mouse_buttons[event.button - 1] = False
        
        if event.button == 1:  # 左键释放
            if self.is_dragging:
                self.is_dragging = False
                # 处理拖拽结束
                if self.mouse_drag_start:
                    drag_distance = ((event.pos[0] - self.mouse_drag_start[0])**2 + 
                                   (event.pos[1] - self.mouse_drag_start[1])**2)**0.5
                    
                    if drag_distance > 5:  # 最小拖拽距离
                        # 区域选择
                        selected_objects = self._find_objects_in_rect(
                            self.mouse_drag_start, event.pos, world_state
                        )
                        if selected_objects:
                            self.selected_objects = selected_objects
                            result['selection_changed'] = True
            
            self.mouse_drag_start = None
        
        return result
    
    def _handle_mouse_motion(self, event: pygame.event.Event, world_state: Dict) -> Dict:
        """处理鼠标移动"""
        
        result = {
            'scale_changed': False,
            'camera_moved': False,
            'selection_changed': False,
            'display_options_changed': False
        }
        
        self.mouse_pos = event.pos
        
        # 更新悬停对象
        new_hover = self._find_object_at_position(event.pos, world_state)
        if new_hover != self.hover_object:
            self.hover_object = new_hover
        
        # 处理拖拽移动相机
        if self.mouse_buttons[0] and self.mouse_drag_start:  # 左键拖拽
            drag_distance = ((event.pos[0] - self.mouse_drag_start[0])**2 + 
                           (event.pos[1] - self.mouse_drag_start[1])**2)**0.5
            
            if drag_distance > 10 and not self.is_dragging:
                self.is_dragging = True
            
            if self.is_dragging and self.control_modes['camera']:
                # 拖拽移动相机
                camera = self.camera_system.main_camera
                
                dx = event.pos[0] - self.mouse_pos[0] if hasattr(self, '_last_mouse_pos') else 0
                dy = event.pos[1] - self.mouse_pos[1] if hasattr(self, '_last_mouse_pos') else 0
                
                # 转换到世界坐标偏移
                world_offset = Vector2D(-dx / camera.zoom, -dy / camera.zoom)
                camera.move_by(world_offset, smooth=False)
                result['camera_moved'] = True
        
        self._last_mouse_pos = event.pos
        return result
    
    def _handle_mouse_wheel(self, event: pygame.event.Event, world_state: Dict) -> Dict:
        """处理鼠标滚轮"""
        
        result = {
            'scale_changed': False,
            'camera_moved': False,
            'selection_changed': False,
            'display_options_changed': False
        }
        
        if self.control_modes['scale_switching']:
            # 缩放系数
            zoom_factor = 1.2 if event.y > 0 else 1/1.2
            
            # 获取鼠标世界坐标（缩放中心）
            camera = self.camera_system.main_camera
            mouse_screen_pos = Vector2D(event.x, event.y)
            mouse_world_pos = camera.screen_to_world(mouse_screen_pos)
            
            # 计算新缩放级别
            current_zoom = self.scale_manager.current_zoom
            new_zoom = current_zoom * zoom_factor
            
            # 应用缩放（可能触发尺度切换）
            old_scale = self.scale_manager.current_scale
            self.scale_manager.set_zoom(new_zoom)
            
            # 调整相机位置，使鼠标位置保持不变
            actual_zoom_factor = self.scale_manager.current_zoom / current_zoom
            if abs(actual_zoom_factor - 1.0) > 0.001:
                camera_to_mouse = mouse_world_pos - camera.position
                offset = camera_to_mouse * (1 - 1/actual_zoom_factor)
                camera.move_by(offset, smooth=False)
                result['camera_moved'] = True
            
            # 检查是否发生了尺度切换
            if self.scale_manager.current_scale != old_scale:
                result['scale_changed'] = True
                logger.info(f"Scale auto-switched from {old_scale.value} to {self.scale_manager.current_scale.value}")
        
        return result
    
    def _handle_continuous_input(self, world_state: Dict) -> Dict:
        """处理持续输入（如按住的按键）"""
        
        result = {
            'scale_changed': False,
            'camera_moved': False,
            'selection_changed': False,
            'display_options_changed': False
        }
        
        if not self.control_modes['camera']:
            return result
        
        # WASD 相机移动
        camera_moved = self.camera_system.handle_keyboard_input(
            pygame.key.get_pressed(), self.scale_manager
        )
        
        if camera_moved:
            result['camera_moved'] = True
        
        return result
    
    def _handle_camera_action(self, action: str, world_state: Dict) -> bool:
        """处理相机动作"""
        
        camera_system = self.camera_system
        
        if action == 'auto_focus':
            # 自动聚焦到有趣的事件
            return camera_system.focus_on_interesting_event(world_state)
        
        elif action == 'center':
            # 移动到世界中心
            world_size = self.scale_manager.world_size
            center = Vector2D(world_size[0] / 2, world_size[1] / 2)
            camera_system.main_camera.move_to(center)
            return True
        
        elif action == 'reset':
            # 重置相机
            camera_system.main_camera.set_zoom(1.0)
            camera_system.main_camera.clear_follow_target()
            world_size = self.scale_manager.world_size
            center = Vector2D(world_size[0] / 2, world_size[1] / 2)
            camera_system.main_camera.move_to(center)
            return True
        
        return False
    
    def _handle_display_toggle(self, option: str) -> bool:
        """处理显示选项切换"""
        
        if option in self.display_options:
            self.display_options[option] = not self.display_options[option]
            
            # 应用到相应的渲染器
            if option == 'trajectories':
                self.rendering_pipeline.toggle_renderer_feature(
                    ScaleLevel.MICRO, 'trajectories', self.display_options[option]
                )
            elif option == 'perception_radius':
                self.rendering_pipeline.toggle_renderer_feature(
                    ScaleLevel.MICRO, 'perception_radius', self.display_options[option]
                )
            elif option == 'social_connections':
                self.rendering_pipeline.toggle_renderer_feature(
                    ScaleLevel.MICRO, 'social_connections', self.display_options[option]
                )
            
            logger.info(f"Display option '{option}' toggled to {self.display_options[option]}")
            return True
        
        return False
    
    def _handle_debug_action(self, action: str, world_state: Dict):
        """处理调试动作"""
        
        if action == 'toggle_debug_mode':
            self.control_modes['debug'] = not self.control_modes['debug']
            logger.info(f"Debug mode: {self.control_modes['debug']}")
        
        elif action == 'print_stats':
            stats = self.rendering_pipeline.get_render_stats()
            logger.info(f"Rendering stats: {stats}")
            
            camera_info = self.camera_system.get_camera_info()
            logger.info(f"Camera info: {camera_info}")
            
            scale_info = self.scale_manager.get_scale_info()
            logger.info(f"Scale info: {scale_info}")
        
        elif action == 'reset_stats':
            self.rendering_pipeline.reset_stats()
            logger.info("Statistics reset")
    
    def _find_object_at_position(self, screen_pos: Tuple[int, int], world_state: Dict):
        """查找屏幕位置上的对象"""
        
        camera = self.camera_system.main_camera
        screen_vector = Vector2D(screen_pos[0], screen_pos[1])
        world_pos = camera.screen_to_world(screen_vector)
        
        # 检查智能体
        agents = world_state.get('agents', [])
        for agent in agents:
            if hasattr(agent, 'position'):
                distance = world_pos.distance_to(agent.position)
                if distance <= 15:  # 选择半径
                    return agent
        
        # 检查资源
        resources = world_state.get('resources', [])
        for resource in resources:
            if hasattr(resource, 'position'):
                distance = world_pos.distance_to(resource.position)
                if distance <= 10:  # 选择半径
                    return resource
        
        return None
    
    def _find_objects_in_rect(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                             world_state: Dict) -> List:
        """查找矩形区域内的对象"""
        
        camera = self.camera_system.main_camera
        
        # 转换到世界坐标
        start_vector = Vector2D(start_pos[0], start_pos[1])
        end_vector = Vector2D(end_pos[0], end_pos[1])
        world_start = camera.screen_to_world(start_vector)
        world_end = camera.screen_to_world(end_vector)
        
        # 创建边界矩形
        min_x = min(world_start.x, world_end.x)
        max_x = max(world_start.x, world_end.x)
        min_y = min(world_start.y, world_end.y)
        max_y = max(world_start.y, world_end.y)
        
        selected_objects = []
        
        # 检查智能体
        agents = world_state.get('agents', [])
        for agent in agents:
            if hasattr(agent, 'position'):
                pos = agent.position
                if min_x <= pos.x <= max_x and min_y <= pos.y <= max_y:
                    selected_objects.append(agent)
        
        return selected_objects
    
    def _show_context_menu(self, screen_pos: Tuple[int, int], world_state: Dict):
        """显示上下文菜单"""
        
        # 简单的上下文菜单实现
        obj = self._find_object_at_position(screen_pos, world_state)
        
        if obj:
            if hasattr(obj, 'agent_id'):
                logger.info(f"Agent context menu for {obj.agent_id}")
                # 这里可以实现更复杂的上下文菜单
            else:
                logger.info(f"Object context menu for {type(obj).__name__}")
    
    def _merge_results(self, target: Dict, source: Dict):
        """合并结果字典"""
        for key, value in source.items():
            if key in target:
                target[key] = target[key] or value
            else:
                target[key] = value
    
    def get_control_state(self) -> Dict:
        """获取控制状态"""
        
        return {
            'control_modes': self.control_modes.copy(),
            'display_options': self.display_options.copy(),
            'selected_objects_count': len(self.selected_objects),
            'hover_object': self.hover_object is not None,
            'keys_pressed': list(self.keys_pressed),
            'mouse_buttons': self.mouse_buttons.copy(),
            'is_dragging': self.is_dragging
        }
    
    def set_control_mode(self, mode: str, enabled: bool):
        """设置控制模式"""
        if mode in self.control_modes:
            self.control_modes[mode] = enabled
            logger.info(f"Control mode '{mode}' set to {enabled}")
    
    def clear_selection(self):
        """清除选择"""
        self.selected_objects.clear()
        self.hover_object = None
    
    def get_selected_objects(self) -> List:
        """获取选中的对象"""
        return self.selected_objects.copy()