"""
Scale Renderers - 各尺度专用渲染器
为每个尺度层次提供专门的渲染逻辑

Author: Ben Hsu & Claude
"""

import math
import time
from typing import Dict, List, Tuple, Optional
import pygame
import logging

from ...core.physics_engine import Vector2D
from .camera_system import Camera
from .lod_renderer import LODRenderer, LODLevel
from .scale_manager import ScaleLevel

logger = logging.getLogger(__name__)


class BaseScaleRenderer:
    """基础尺度渲染器"""
    
    def __init__(self, scale_level: ScaleLevel):
        self.scale_level = scale_level
        self.lod_renderer = LODRenderer()
        self.render_cache = {}
        
    def render(self, screen: pygame.Surface, world_state: Dict, camera: Camera):
        """渲染当前尺度"""
        raise NotImplementedError("Subclasses must implement render method")
    
    def _should_render_object(self, obj, camera: Camera) -> bool:
        """检查对象是否应该被渲染"""
        if not hasattr(obj, 'position'):
            return False
        
        return camera.is_visible(obj.position, getattr(obj, 'radius', 10))


class MicroRenderer(BaseScaleRenderer):
    """微观渲染器 - 专注于个体智能体的详细行为"""
    
    def __init__(self):
        super().__init__(ScaleLevel.MICRO)
        self.show_perception_radius = False
        self.show_trajectories = False
        self.show_social_connections = False
        self.trajectory_cache = {}
        
    def render(self, screen: pygame.Surface, world_state: Dict, camera: Camera):
        """渲染微观层次"""
        
        agents = world_state.get('agents', [])
        resources = world_state.get('resources', [])
        
        # 1. 渲染背景网格（可选）
        if world_state.get('show_grid', False):
            self._render_grid(screen, camera)
        
        # 2. 渲染资源
        self._render_resources(screen, resources, camera)
        
        # 3. 渲染智能体轨迹
        if self.show_trajectories:
            self._render_agent_trajectories(screen, agents, camera)
        
        # 4. 渲染社交连接
        if self.show_social_connections:
            self._render_social_connections(screen, agents, camera)
        
        # 5. 渲染感知半径
        if self.show_perception_radius:
            self._render_perception_radii(screen, agents, camera)
        
        # 6. 渲染智能体
        self._render_agents(screen, agents, camera)
        
        # 7. 渲染天气效果
        self._render_weather_effects(screen, world_state, camera)
        
        # 8. 渲染调试信息
        if world_state.get('debug_mode', False):
            self._render_debug_info(screen, world_state, camera)
    
    def _render_grid(self, screen: pygame.Surface, camera: Camera):
        """渲染背景网格"""
        
        grid_size = 50  # 网格大小
        visible_area = camera.get_visible_area()
        
        # 计算网格线的起始和结束位置
        start_x = int(visible_area.left // grid_size) * grid_size
        start_y = int(visible_area.top // grid_size) * grid_size
        end_x = int(visible_area.right) + grid_size
        end_y = int(visible_area.bottom) + grid_size
        
        grid_color = (40, 40, 40)
        
        # 绘制垂直线
        for x in range(start_x, end_x, grid_size):
            start_screen = camera.world_to_screen(Vector2D(x, visible_area.top))
            end_screen = camera.world_to_screen(Vector2D(x, visible_area.bottom))
            
            if 0 <= start_screen.x <= screen.get_width():
                pygame.draw.line(screen, grid_color, 
                               (start_screen.x, 0), 
                               (end_screen.x, screen.get_height()))
        
        # 绘制水平线
        for y in range(start_y, end_y, grid_size):
            start_screen = camera.world_to_screen(Vector2D(visible_area.left, y))
            end_screen = camera.world_to_screen(Vector2D(visible_area.right, y))
            
            if 0 <= start_screen.y <= screen.get_height():
                pygame.draw.line(screen, grid_color,
                               (0, start_screen.y),
                               (screen.get_width(), end_screen.y))
    
    def _render_resources(self, screen: pygame.Surface, resources: List, camera: Camera):
        """渲染资源"""
        
        for resource in resources:
            if not self._should_render_object(resource, camera):
                continue
            
            screen_pos = camera.world_to_screen(resource.position)
            
            # 资源大小基于价值
            resource_value = getattr(resource, 'value', 10)
            radius = max(3, min(8, int(resource_value / 10)))
            
            # 资源颜色基于类型
            resource_type = getattr(resource, 'type', 'food')
            if resource_type == 'food':
                color = (0, 255, 0)  # 绿色食物
            elif resource_type == 'water':
                color = (0, 100, 255)  # 蓝色水源
            else:
                color = (255, 165, 0)  # 橙色其他资源
            
            # 绘制资源
            pygame.draw.circle(screen, color, (int(screen_pos.x), int(screen_pos.y)), radius)
            
            # 如果缩放足够大，显示资源值
            if camera.zoom > 1.5:
                font = pygame.font.Font(None, 16)
                value_text = font.render(str(int(resource_value)), True, (255, 255, 255))
                text_pos = (int(screen_pos.x) + radius + 2, int(screen_pos.y) - 8)
                screen.blit(value_text, text_pos)
    
    def _render_agent_trajectories(self, screen: pygame.Surface, agents: List, camera: Camera):
        """渲染智能体轨迹"""
        
        for agent in agents:
            if not hasattr(agent, 'agent_id'):
                continue
            
            agent_id = agent.agent_id
            
            # 获取或创建轨迹记录
            if agent_id not in self.trajectory_cache:
                self.trajectory_cache[agent_id] = []
            
            trajectory = self.trajectory_cache[agent_id]
            
            # 添加当前位置
            current_time = time.time()
            trajectory.append((agent.position.x, agent.position.y, current_time))
            
            # 清理旧的轨迹点（保留30秒）
            cutoff_time = current_time - 30.0
            trajectory[:] = [(x, y, t) for x, y, t in trajectory if t > cutoff_time]
            
            # 绘制轨迹
            if len(trajectory) > 1:
                screen_points = []
                for x, y, t in trajectory:
                    world_pos = Vector2D(x, y)
                    if camera.is_visible(world_pos):
                        screen_pos = camera.world_to_screen(world_pos)
                        screen_points.append((int(screen_pos.x), int(screen_pos.y)))
                
                if len(screen_points) > 1:
                    # 颜色随时间衰减
                    for i in range(1, len(screen_points)):
                        alpha = int(255 * (i / len(screen_points)))
                        color = (255, 255, 255, alpha)
                        
                        # 创建带透明度的surface
                        line_surf = pygame.Surface((abs(screen_points[i][0] - screen_points[i-1][0]) + 2,
                                                   abs(screen_points[i][1] - screen_points[i-1][1]) + 2), 
                                                  pygame.SRCALPHA)
                        pygame.draw.line(line_surf, color, (0, 0), 
                                       (screen_points[i][0] - screen_points[i-1][0],
                                        screen_points[i][1] - screen_points[i-1][1]))
                        screen.blit(line_surf, (min(screen_points[i][0], screen_points[i-1][0]),
                                               min(screen_points[i][1], screen_points[i-1][1])))
    
    def _render_social_connections(self, screen: pygame.Surface, agents: List, camera: Camera):
        """渲染社交连接"""
        
        connection_distance = 60  # 社交连接的最大距离
        
        for i, agent1 in enumerate(agents):
            if not self._should_render_object(agent1, camera):
                continue
            
            for agent2 in agents[i+1:]:
                if not self._should_render_object(agent2, camera):
                    continue
                
                distance = agent1.position.distance_to(agent2.position)
                
                if distance <= connection_distance:
                    # 计算连接强度
                    strength = 1.0 - (distance / connection_distance)
                    
                    # 基于社交历史调整强度
                    if (hasattr(agent1, 'social_interactions') and 
                        hasattr(agent2, 'social_interactions')):
                        social_factor = min(agent1.social_interactions, agent2.social_interactions) / 50.0
                        strength *= (0.5 + social_factor * 0.5)
                    
                    if strength > 0.3:  # 只显示较强的连接
                        screen_pos1 = camera.world_to_screen(agent1.position)
                        screen_pos2 = camera.world_to_screen(agent2.position)
                        
                        # 连接线颜色和透明度
                        alpha = int(strength * 150)
                        line_color = (100, 200, 255, alpha)
                        
                        # 绘制连接线
                        line_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                        pygame.draw.line(line_surf, line_color,
                                       (int(screen_pos1.x), int(screen_pos1.y)),
                                       (int(screen_pos2.x), int(screen_pos2.y)), 2)
                        screen.blit(line_surf, (0, 0))
    
    def _render_perception_radii(self, screen: pygame.Surface, agents: List, camera: Camera):
        """渲染感知半径"""
        
        for agent in agents:
            if not self._should_render_object(agent, camera):
                continue
            
            # 获取感知半径
            perception_radius = getattr(agent, 'perception_radius', 30)
            
            screen_pos = camera.world_to_screen(agent.position)
            screen_radius = int(perception_radius * camera.zoom)
            
            if screen_radius > 5:  # 只在半径足够大时绘制
                # 绘制感知圆圈
                perception_color = (255, 255, 255, 50)
                circle_surf = pygame.Surface((screen_radius * 2, screen_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(circle_surf, perception_color, (screen_radius, screen_radius), screen_radius, 1)
                
                screen.blit(circle_surf, (int(screen_pos.x) - screen_radius, int(screen_pos.y) - screen_radius))
    
    def _render_agents(self, screen: pygame.Surface, agents: List, camera: Camera):
        """渲染智能体"""
        
        for agent in agents:
            if not self._should_render_object(agent, camera):
                continue
            
            screen_pos = camera.world_to_screen(agent.position)
            screen_pos_tuple = (int(screen_pos.x), int(screen_pos.y))
            
            # 简化的智能体渲染
            self._render_simple_agent(screen, agent, screen_pos_tuple)
    
    def _render_simple_agent(self, screen: pygame.Surface, agent, screen_pos: tuple):
        """简化的智能体渲染"""
        try:
            # 基础圆形
            radius = 8
            agent_color = self._get_agent_color(agent)
            pygame.draw.circle(screen, agent_color, screen_pos, radius)
            
            # 边框
            pygame.draw.circle(screen, (255, 255, 255), screen_pos, radius, 1)
            
            # 健康条
            if hasattr(agent, 'health') and hasattr(agent, 'max_health'):
                health_ratio = agent.health / getattr(agent, 'max_health', 100)
                bar_width = 20
                bar_height = 3
                bar_x = screen_pos[0] - bar_width // 2
                bar_y = screen_pos[1] - radius - 8
                
                # 背景
                pygame.draw.rect(screen, (100, 100, 100), 
                               (bar_x, bar_y, bar_width, bar_height))
                # 健康条
                health_color = (255, 0, 0) if health_ratio < 0.3 else (255, 255, 0) if health_ratio < 0.7 else (0, 255, 0)
                pygame.draw.rect(screen, health_color, 
                               (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        except Exception as e:
            # 如果渲染失败，绘制一个简单的点
            pygame.draw.circle(screen, (255, 0, 0), screen_pos, 3)
    
    def _get_agent_color(self, agent):
        """获取智能体颜色"""
        try:
            if hasattr(agent, 'energy'):
                # 使用更宽泛的能量范围，适应实际情况
                energy = max(0, agent.energy)  # 确保不为负
                max_energy = getattr(agent, 'max_energy', 150.0)
                energy_ratio = energy / max_energy
                
                # 更明显的颜色区分
                if energy_ratio > 0.8:
                    return (0, 255, 0)      # 高能量 - 亮绿色
                elif energy_ratio > 0.6:
                    return (154, 205, 50)   # 中高能量 - 黄绿色
                elif energy_ratio > 0.4:
                    return (255, 255, 0)    # 中等能量 - 黄色
                elif energy_ratio > 0.2:
                    return (255, 165, 0)    # 低能量 - 橙色
                elif energy_ratio > 0.05:
                    return (255, 69, 0)     # 很低能量 - 橙红色
                else:
                    return (255, 0, 0)      # 极低能量 - 红色
            else:
                return (100, 150, 255)      # 默认蓝色（无能量信息）
        except Exception as e:
            # 如果出错，返回显眼的紫色以便调试
            return (255, 0, 255)            # 紫色（错误指示）
    
    def _render_weather_effects(self, screen: pygame.Surface, world_state: Dict, camera: Camera):
        """渲染天气效果"""
        active_weather = world_state.get('active_weather', [])
        
        for weather_info in active_weather:
            try:
                weather_type = weather_info['type']
                intensity = weather_info['intensity']
                center = weather_info['center']
                radius = weather_info['radius']
                
                # 转换到屏幕坐标
                weather_center = Vector2D(center[0], center[1])
                screen_center = camera.world_to_screen(weather_center)
                screen_radius = int(radius * camera.zoom)
                
                # 检查是否在可见区域内
                if (screen_center.x + screen_radius < 0 or screen_center.x - screen_radius > screen.get_width() or
                    screen_center.y + screen_radius < 0 or screen_center.y - screen_radius > screen.get_height()):
                    continue
                
                # 根据天气类型绘制效果
                if weather_type == 'rain':
                    self._render_rain_effect(screen, screen_center, screen_radius, intensity)
                elif weather_type == 'storm':
                    self._render_storm_effect(screen, screen_center, screen_radius, intensity)
                elif weather_type == 'drought':
                    self._render_drought_effect(screen, screen_center, screen_radius, intensity)
                elif weather_type == 'blizzard':
                    self._render_blizzard_effect(screen, screen_center, screen_radius, intensity)
                elif weather_type == 'heatwave':
                    self._render_heatwave_effect(screen, screen_center, screen_radius, intensity)
                    
            except Exception as e:
                continue  # 跳过有问题的天气事件
    
    def _render_rain_effect(self, screen: pygame.Surface, center: Vector2D, radius: int, intensity: float):
        """渲染雨效果"""
        import random
        
        # 绘制雨滴 - 使用屏幕坐标
        drops_count = int(20 * intensity)
        for _ in range(drops_count):
            drop_x = int(center.x + random.randint(-radius, radius))
            drop_y = int(center.y + random.randint(-radius, radius))
            
            if (drop_x - center.x)**2 + (drop_y - center.y)**2 <= radius**2:
                # 在圆形区域内绘制雨滴
                drop_length = random.randint(3, 8)
                alpha = min(255, int(150 * intensity))  # 增加可见度
                color = (173, 216, 230, alpha)  # 浅蓝色
                
                # 创建透明surface
                drop_surf = pygame.Surface((2, drop_length), pygame.SRCALPHA)
                pygame.draw.rect(drop_surf, color, (0, 0, 2, drop_length))
                screen.blit(drop_surf, (drop_x, drop_y))
        
        # 绘制雨云覆盖
        if radius > 10:
            cloud_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            cloud_alpha = min(255, int(50 * intensity))  # 增加可见度
            pygame.draw.circle(cloud_surf, (128, 128, 128, cloud_alpha), (radius, radius), radius)
            screen.blit(cloud_surf, (int(center.x) - radius, int(center.y) - radius))
    
    def _render_storm_effect(self, screen: pygame.Surface, center: Vector2D, radius: int, intensity: float):
        """渲染暴风雨效果"""
        import random
        
        # 绘制闪电效果
        if random.random() < 0.2 * intensity:  # 20% 概率闪电 - 增加概率
            lightning_color = (255, 255, 0, 255)  # 完全不透明的闪电
            lightning_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            
            # 简单的闪电线条
            start_x = radius + random.randint(-radius//2, radius//2)
            for i in range(5):
                end_x = start_x + random.randint(-20, 20)
                end_y = (i + 1) * radius // 3
                pygame.draw.line(lightning_surf, lightning_color, 
                               (start_x, i * radius // 3), (end_x, end_y), 4)  # 增加线条宽度
                start_x = end_x
            
            screen.blit(lightning_surf, (int(center.x) - radius, int(center.y) - radius))
        
        # 深色云层
        storm_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        storm_alpha = min(255, int(80 * intensity))  # 增加可见度
        pygame.draw.circle(storm_surf, (64, 64, 64, storm_alpha), (radius, radius), radius)
        screen.blit(storm_surf, (int(center.x) - radius, int(center.y) - radius))
    
    def _render_drought_effect(self, screen: pygame.Surface, center: Vector2D, radius: int, intensity: float):
        """渲染干旱效果"""
        # 绘制干燥的土地效果
        drought_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        drought_alpha = min(255, int(60 * intensity))  # 增加可见度
        pygame.draw.circle(drought_surf, (139, 69, 19, drought_alpha), (radius, radius), radius)
        screen.blit(drought_surf, (int(center.x) - radius, int(center.y) - radius))
        
        # 绘制裂缝效果
        import random
        for _ in range(int(8 * intensity)):  # 增加裂缝数量
            crack_x = int(center.x + random.randint(-radius//2, radius//2))
            crack_y = int(center.y + random.randint(-radius//2, radius//2))
            crack_length = random.randint(10, 30)
            pygame.draw.line(screen, (101, 67, 33), 
                           (crack_x, crack_y), (crack_x + crack_length, crack_y), 2)
    
    def _render_blizzard_effect(self, screen: pygame.Surface, center: Vector2D, radius: int, intensity: float):
        """渲染暴雪效果"""
        import random
        
        # 绘制雪花
        snow_count = int(40 * intensity)  # 增加雪花数量
        for _ in range(snow_count):
            snow_x = int(center.x + random.randint(-radius, radius))
            snow_y = int(center.y + random.randint(-radius, radius))
            
            if (snow_x - center.x)**2 + (snow_y - center.y)**2 <= radius**2:
                snow_size = random.randint(2, 4)  # 增大雪花
                pygame.draw.circle(screen, (255, 255, 255), (snow_x, snow_y), snow_size)
        
        # 白色覆盖层
        blizzard_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        blizzard_alpha = min(255, int(70 * intensity))  # 增加可见度
        pygame.draw.circle(blizzard_surf, (255, 255, 255, blizzard_alpha), (radius, radius), radius)
        screen.blit(blizzard_surf, (int(center.x) - radius, int(center.y) - radius))
    
    def _render_heatwave_effect(self, screen: pygame.Surface, center: Vector2D, radius: int, intensity: float):
        """渲染热浪效果"""
        # 绘制热浪扭曲效果（简化版）
        heatwave_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        heatwave_alpha = min(255, int(50 * intensity))  # 增加可见度
        
        # 绘制热浪圆圈
        for i in range(3):
            circle_radius = radius - i * 15
            if circle_radius > 0:
                alpha = heatwave_alpha // (i + 1)
                pygame.draw.circle(heatwave_surf, (255, 69, 0, alpha), 
                                 (radius, radius), circle_radius, 3)  # 增加线条宽度
        
        screen.blit(heatwave_surf, (int(center.x) - radius, int(center.y) - radius))
    
    def _render_debug_info(self, screen: pygame.Surface, world_state: Dict, camera: Camera):
        """渲染调试信息"""
        
        debug_font = pygame.font.Font(None, 20)
        y_offset = 10
        
        debug_info = [
            f"Camera: ({camera.position.x:.1f}, {camera.position.y:.1f})",
            f"Zoom: {camera.zoom:.2f}",
            f"Agents: {len(world_state.get('agents', []))}",
            f"Resources: {len(world_state.get('resources', []))}",
            f"FPS: {world_state.get('fps', 0):.1f}"
        ]
        
        for info in debug_info:
            text_surf = debug_font.render(info, True, (255, 255, 255))
            screen.blit(text_surf, (10, y_offset))
            y_offset += 25


class MesoRenderer(BaseScaleRenderer):
    """中观渲染器 - 专注于群体交互和区域行为"""
    
    def __init__(self):
        super().__init__(ScaleLevel.MESO)
        self.group_detection_radius = 100
        
    def render(self, screen: pygame.Surface, world_state: Dict, camera: Camera):
        """渲染中观层次"""
        
        agents = world_state.get('agents', [])
        resources = world_state.get('resources', [])
        
        try:
            # 简化的中观渲染
            self._render_simple_resources(screen, resources, camera)
            self._render_simple_agent_clusters(screen, agents, camera)
        except Exception as e:
            # 如果出错，使用基础渲染
            self._render_fallback(screen, agents, resources, camera)
    
    def _render_simple_resources(self, screen: pygame.Surface, resources: List, camera: Camera):
        """简化资源渲染"""
        for resource in resources:
            try:
                if isinstance(resource, tuple):
                    pos = Vector2D(resource[0], resource[1])
                    value = 10
                else:
                    pos = resource.position
                    value = getattr(resource, 'value', 10)
                
                if camera.is_visible(pos):
                    screen_pos = camera.world_to_screen(pos)
                    pygame.draw.circle(screen, (0, 255, 0), 
                                     (int(screen_pos.x), int(screen_pos.y)), 3)
            except:
                continue
    
    def _render_simple_agent_clusters(self, screen: pygame.Surface, agents: List, camera: Camera):
        """简化智能体集群渲染"""
        for agent in agents:
            try:
                if camera.is_visible(agent.position):
                    screen_pos = camera.world_to_screen(agent.position)
                    pygame.draw.circle(screen, (100, 150, 255), 
                                     (int(screen_pos.x), int(screen_pos.y)), 6)
            except:
                continue
    
    def _render_fallback(self, screen: pygame.Surface, agents: List, resources: List, camera: Camera):
        """备用渲染方法"""
        pygame.draw.rect(screen, (50, 50, 50), (10, 10, 200, 30))
        font = pygame.font.Font(None, 24)
        text = font.render("MESO Scale", True, (255, 255, 255))
        screen.blit(text, (15, 15))
    
    def _detect_agent_groups(self, agents: List) -> List[List]:
        """检测智能体群组"""
        
        if not agents:
            return []
        
        groups = []
        unprocessed = list(agents)
        
        while unprocessed:
            # 开始新群组
            seed_agent = unprocessed[0]
            current_group = [seed_agent]
            unprocessed.remove(seed_agent)
            
            # 查找附近的智能体
            to_check = [seed_agent]
            
            while to_check:
                current_agent = to_check.pop()
                
                for other_agent in list(unprocessed):
                    distance = current_agent.position.distance_to(other_agent.position)
                    
                    if distance <= self.group_detection_radius:
                        current_group.append(other_agent)
                        unprocessed.remove(other_agent)
                        to_check.append(other_agent)
            
            # 只保留有意义的群组（2个或更多成员）
            if len(current_group) >= 2:
                groups.append(current_group)
        
        return groups
    
    def _render_agent_groups(self, screen: pygame.Surface, groups: List[List], camera: Camera):
        """渲染智能体群组"""
        
        group_colors = [
            (255, 100, 100, 80),  # 红色
            (100, 255, 100, 80),  # 绿色
            (100, 100, 255, 80),  # 蓝色
            (255, 255, 100, 80),  # 黄色
            (255, 100, 255, 80),  # 品红
            (100, 255, 255, 80),  # 青色
        ]
        
        for i, group in enumerate(groups):
            if len(group) < 2:
                continue
            
            # 计算群组边界
            positions = [agent.position for agent in group]
            min_x = min(pos.x for pos in positions) - 20
            max_x = max(pos.x for pos in positions) + 20
            min_y = min(pos.y for pos in positions) - 20
            max_y = max(pos.y for pos in positions) + 20
            
            # 转换到屏幕坐标
            top_left = camera.world_to_screen(Vector2D(min_x, min_y))
            bottom_right = camera.world_to_screen(Vector2D(max_x, max_y))
            
            width = int(bottom_right.x - top_left.x)
            height = int(bottom_right.y - top_left.y)
            
            if width > 0 and height > 0:
                # 绘制群组背景
                group_color = group_colors[i % len(group_colors)]
                group_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                pygame.draw.rect(group_surf, group_color, (0, 0, width, height))
                screen.blit(group_surf, (int(top_left.x), int(top_left.y)))
                
                # 绘制群组边框
                pygame.draw.rect(screen, group_color[:3], 
                               (int(top_left.x), int(top_left.y), width, height), 2)
            
            # 渲染群组中的智能体（简化版）
            for agent in group:
                screen_pos = camera.world_to_screen(agent.position)
                screen_pos_tuple = (int(screen_pos.x), int(screen_pos.y))
                
                # 使用中等LOD
                lod_level = LODLevel.MEDIUM_DETAIL
                self.lod_renderer.render_agent_with_lod(screen, agent, camera, lod_level, screen_pos_tuple)
            
            # 显示群组信息
            center_x = sum(pos.x for pos in positions) / len(positions)
            center_y = sum(pos.y for pos in positions) / len(positions)
            center_screen = camera.world_to_screen(Vector2D(center_x, center_y))
            
            font = pygame.font.Font(None, 24)
            group_text = font.render(f"Group {i+1} ({len(group)})", True, (255, 255, 255))
            text_rect = group_text.get_rect(center=(int(center_screen.x), int(center_screen.y)))
            screen.blit(group_text, text_rect)
    
    def _render_resource_density_heatmap(self, screen: pygame.Surface, resources: List, camera: Camera):
        """渲染资源密度热图"""
        
        if not resources:
            return
        
        visible_area = camera.get_visible_area()
        grid_size = 40  # 热图网格大小
        
        # 计算网格
        grid_width = int(visible_area.width // grid_size) + 2
        grid_height = int(visible_area.height // grid_size) + 2
        
        density_grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
        
        # 计算每个网格的资源密度
        for resource in resources:
            # 处理资源位置 - 可能是tuple或对象
            if isinstance(resource, tuple):
                pos = Vector2D(resource[0], resource[1])
            else:
                pos = resource.position
            
            if not camera.is_visible(pos):
                continue
            
            grid_x = int((pos.x - visible_area.left) // grid_size)
            grid_y = int((pos.y - visible_area.top) // grid_size)
            
            if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:
                resource_value = getattr(resource, 'value', 10)
                density_grid[grid_y][grid_x] += resource_value
        
        # 绘制热图
        max_density = max(max(row) for row in density_grid) if any(any(row) for row in density_grid) else 1
        
        for y in range(grid_height):
            for x in range(grid_width):
                density = density_grid[y][x]
                if density > 0:
                    # 计算热图颜色
                    intensity = min(density / max_density, 1.0)
                    alpha = int(intensity * 100)
                    
                    # 从蓝色到红色的渐变
                    if intensity < 0.5:
                        color = (0, int(255 * intensity * 2), 255, alpha)
                    else:
                        color = (int(255 * (intensity - 0.5) * 2), 255, int(255 * (1 - intensity)), alpha)
                    
                    # 计算屏幕位置
                    world_x = visible_area.left + x * grid_size
                    world_y = visible_area.top + y * grid_size
                    screen_pos = camera.world_to_screen(Vector2D(world_x, world_y))
                    screen_size = int(grid_size * camera.zoom)
                    
                    # 绘制热图方块
                    heat_surf = pygame.Surface((screen_size, screen_size), pygame.SRCALPHA)
                    pygame.draw.rect(heat_surf, color, (0, 0, screen_size, screen_size))
                    screen.blit(heat_surf, (int(screen_pos.x), int(screen_pos.y)))
    
    def _render_resource_flows(self, screen: pygame.Surface, agents: List, resources: List, camera: Camera):
        """渲染资源流向"""
        
        flow_distance = 80  # 资源流向的检测距离
        
        for agent in agents:
            if not self._should_render_object(agent, camera):
                continue
            
            # 寻找附近的资源
            nearby_resources = [r for r in resources 
                              if agent.position.distance_to(r.position) <= flow_distance]
            
            if nearby_resources:
                # 找到最近的资源
                closest_resource = min(nearby_resources, 
                                     key=lambda r: agent.position.distance_to(r.position))
                
                # 绘制流向箭头
                agent_screen = camera.world_to_screen(agent.position)
                resource_screen = camera.world_to_screen(closest_resource.position)
                
                # 计算箭头
                direction = (resource_screen - agent_screen).normalize()
                arrow_start = agent_screen + direction * 15
                arrow_end = resource_screen - direction * 10
                
                # 绘制流向线
                pygame.draw.line(screen, (255, 200, 0, 120),
                               (int(arrow_start.x), int(arrow_start.y)),
                               (int(arrow_end.x), int(arrow_end.y)), 2)
    
    def _render_territorial_boundaries(self, screen: pygame.Surface, groups: List[List], camera: Camera):
        """渲染区域边界"""
        
        for group in groups:
            if len(group) < 3:  # 至少需要3个智能体才能形成有意义的边界
                continue
            
            # 计算边界点
            positions = [agent.position for agent in group]
            
            # 简化的凸包算法（用于演示）
            boundary_points = self._compute_simple_boundary(positions)
            
            if len(boundary_points) >= 3:
                # 转换到屏幕坐标
                screen_points = [camera.world_to_screen(point) for point in boundary_points]
                screen_points = [(int(p.x), int(p.y)) for p in screen_points]
                
                # 绘制边界线
                if len(screen_points) >= 3:
                    pygame.draw.polygon(screen, (255, 255, 255), screen_points, 2)
    
    def _compute_simple_boundary(self, positions: List[Vector2D]) -> List[Vector2D]:
        """计算简单边界（简化的凸包）"""
        
        if len(positions) < 3:
            return positions
        
        # 找到最左下角的点作为起点
        start_point = min(positions, key=lambda p: (p.y, p.x))
        
        # 简化版凸包：按角度排序
        center_x = sum(p.x for p in positions) / len(positions)
        center_y = sum(p.y for p in positions) / len(positions)
        center = Vector2D(center_x, center_y)
        
        def angle_from_center(point):
            return math.atan2(point.y - center.y, point.x - center.x)
        
        sorted_points = sorted(positions, key=angle_from_center)
        
        # 扩展边界（添加一些缓冲区）
        expanded_points = []
        for point in sorted_points:
            direction = (point - center).normalize()
            expanded_point = point + direction * 30  # 30像素缓冲区
            expanded_points.append(expanded_point)
        
        return expanded_points


class MacroRenderer(BaseScaleRenderer):
    """宏观渲染器 - 专注于部落和文明级别的交互"""
    
    def __init__(self):
        super().__init__(ScaleLevel.MACRO)
        
    def render(self, screen: pygame.Surface, world_state: Dict, camera: Camera):
        """渲染宏观层次"""
        
        agents = world_state.get('agents', [])
        
        try:
            # 简化的宏观渲染
            self._render_simple_macro_view(screen, agents, camera)
        except Exception as e:
            # 备用渲染
            self._render_macro_fallback(screen)
    
    def _render_simple_macro_view(self, screen: pygame.Surface, agents: List, camera: Camera):
        """简化的宏观视图"""
        # 绘制世界背景
        pygame.draw.rect(screen, (30, 30, 50), (0, 0, screen.get_width(), screen.get_height()))
        
        # 绘制智能体为小点
        for agent in agents:
            try:
                if camera.is_visible(agent.position):
                    screen_pos = camera.world_to_screen(agent.position)
                    pygame.draw.circle(screen, (255, 255, 0), 
                                     (int(screen_pos.x), int(screen_pos.y)), 2)
            except:
                continue
    
    def _render_macro_fallback(self, screen: pygame.Surface):
        """宏观渲染备用方案"""
        pygame.draw.rect(screen, (50, 50, 50), (10, 10, 200, 30))
        font = pygame.font.Font(None, 24)
        text = font.render("MACRO Scale", True, (255, 255, 255))
        screen.blit(text, (15, 15))
    
    def _create_virtual_tribes(self, agents: List) -> List:
        """创建虚拟部落用于演示"""
        
        if not agents:
            return []
        
        # 简单的聚类算法创建虚拟部落
        tribes = []
        tribe_distance = 150  # 部落形成距离
        processed_agents = set()
        
        for agent in agents:
            if agent in processed_agents:
                continue
            
            # 创建新部落
            tribe_members = [agent]
            processed_agents.add(agent)
            
            # 寻找附近的智能体
            for other_agent in agents:
                if other_agent in processed_agents:
                    continue
                
                distance = agent.position.distance_to(other_agent.position)
                if distance <= tribe_distance:
                    tribe_members.append(other_agent)
                    processed_agents.add(other_agent)
            
            # 只有足够大的群体才被认为是部落
            if len(tribe_members) >= 5:
                # 创建虚拟部落对象
                virtual_tribe = type('VirtualTribe', (), {
                    'members': tribe_members,
                    'name': f"Tribe {len(tribes) + 1}",
                    'territory_center': self._calculate_center(tribe_members),
                    'territory_radius': self._calculate_radius(tribe_members),
                    'population': len(tribe_members),
                    'total_energy': sum(getattr(m, 'energy', 50) for m in tribe_members),
                    'avg_health': sum(getattr(m, 'health', 100) for m in tribe_members) / len(tribe_members)
                })()
                
                tribes.append(virtual_tribe)
        
        return tribes
    
    def _calculate_center(self, members: List) -> Vector2D:
        """计算成员中心点"""
        if not members:
            return Vector2D(0, 0)
        
        total_x = sum(m.position.x for m in members)
        total_y = sum(m.position.y for m in members)
        return Vector2D(total_x / len(members), total_y / len(members))
    
    def _calculate_radius(self, members: List) -> float:
        """计算群体半径"""
        if not members:
            return 50
        
        center = self._calculate_center(members)
        max_distance = max(center.distance_to(m.position) for m in members)
        return max_distance + 30  # 添加缓冲区
    
    def _render_geographical_background(self, screen: pygame.Surface, camera: Camera):
        """渲染地理背景"""
        
        # 简单的地形渲染
        visible_area = camera.get_visible_area()
        terrain_size = 100
        
        # 生成简单的地形噪声
        for x in range(int(visible_area.left), int(visible_area.right), terrain_size):
            for y in range(int(visible_area.top), int(visible_area.bottom), terrain_size):
                
                # 简单的噪声函数
                noise_value = (math.sin(x * 0.01) * math.cos(y * 0.01) + 1) / 2
                
                # 地形颜色
                if noise_value < 0.3:
                    terrain_color = (0, 50, 100)  # 水
                elif noise_value < 0.6:
                    terrain_color = (34, 80, 34)  # 草地
                else:
                    terrain_color = (139, 90, 43)  # 山地
                
                # 转换到屏幕坐标
                screen_pos = camera.world_to_screen(Vector2D(x, y))
                screen_size = int(terrain_size * camera.zoom)
                
                if screen_size > 2:
                    pygame.draw.rect(screen, terrain_color,
                                   (int(screen_pos.x), int(screen_pos.y), screen_size, screen_size))
    
    def _render_tribes(self, screen: pygame.Surface, tribes: List, camera: Camera):
        """渲染部落"""
        
        tribe_colors = [
            (255, 100, 100),  # 红色
            (100, 255, 100),  # 绿色
            (100, 100, 255),  # 蓝色
            (255, 255, 100),  # 黄色
            (255, 100, 255),  # 品红
            (100, 255, 255),  # 青色
        ]
        
        for i, tribe in enumerate(tribes):
            if not hasattr(tribe, 'territory_center'):
                continue
            
            tribe_color = tribe_colors[i % len(tribe_colors)]
            
            # 渲染部落领土
            center_screen = camera.world_to_screen(tribe.territory_center)
            territory_radius = getattr(tribe, 'territory_radius', 100)
            screen_radius = int(territory_radius * camera.zoom)
            
            if screen_radius > 5:
                # 部落领土圆圈
                pygame.draw.circle(screen, (*tribe_color, 50), 
                                 (int(center_screen.x), int(center_screen.y)), screen_radius, 3)
            
            # 渲染部落中心
            pygame.draw.circle(screen, tribe_color,
                             (int(center_screen.x), int(center_screen.y)), 8)
            pygame.draw.circle(screen, (255, 255, 255),
                             (int(center_screen.x), int(center_screen.y)), 8, 2)
            
            # 部落信息
            if camera.zoom > 0.1:
                font = pygame.font.Font(None, 24)
                tribe_name = getattr(tribe, 'name', f"Tribe {i+1}")
                population = getattr(tribe, 'population', len(getattr(tribe, 'members', [])))
                
                info_text = f"{tribe_name} ({population})"
                text_surface = font.render(info_text, True, (255, 255, 255))
                text_pos = (int(center_screen.x) + 12, int(center_screen.y) - 12)
                screen.blit(text_surface, text_pos)
            
            # 渲染部落成员（聚类表示）
            if hasattr(tribe, 'members') and camera.zoom > 0.2:
                member_clusters = self.lod_renderer.cluster_nearby_agents(tribe.members, camera, 80)
                for cluster in member_clusters:
                    self.lod_renderer.render_agent_cluster(screen, cluster, camera)
    
    def _render_trade_routes(self, screen: pygame.Surface, tribes: List, camera: Camera):
        """渲染贸易路线"""
        
        if len(tribes) < 2:
            return
        
        trade_distance = 300  # 贸易距离阈值
        
        for i, tribe1 in enumerate(tribes):
            for tribe2 in tribes[i+1:]:
                if not (hasattr(tribe1, 'territory_center') and hasattr(tribe2, 'territory_center')):
                    continue
                
                distance = tribe1.territory_center.distance_to(tribe2.territory_center)
                
                if distance <= trade_distance:
                    # 计算贸易强度
                    trade_strength = 1.0 - (distance / trade_distance)
                    
                    if trade_strength > 0.5:  # 只显示较强的贸易关系
                        pos1 = camera.world_to_screen(tribe1.territory_center)
                        pos2 = camera.world_to_screen(tribe2.territory_center)
                        
                        # 贸易路线颜色
                        alpha = int(trade_strength * 150)
                        trade_color = (255, 215, 0, alpha)  # 金色
                        
                        # 绘制贸易路线
                        line_width = max(2, int(trade_strength * 4))
                        trade_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                        pygame.draw.line(trade_surf, trade_color,
                                       (int(pos1.x), int(pos1.y)),
                                       (int(pos2.x), int(pos2.y)), line_width)
                        screen.blit(trade_surf, (0, 0))
    
    def _render_civilizations(self, screen: pygame.Surface, civilizations: List, camera: Camera):
        """渲染文明"""
        
        for civilization in civilizations:
            if not hasattr(civilization, 'capital'):
                continue
            
            # 渲染文明首都
            capital_screen = camera.world_to_screen(civilization.capital.territory_center)
            
            # 文明标志（星形）
            star_points = []
            star_radius = 15
            for i in range(10):
                angle = i * math.pi / 5
                radius = star_radius if i % 2 == 0 else star_radius / 2
                x = int(capital_screen.x + radius * math.cos(angle))
                y = int(capital_screen.y + radius * math.sin(angle))
                star_points.append((x, y))
            
            pygame.draw.polygon(screen, (255, 215, 0), star_points)  # 金色星形
            pygame.draw.polygon(screen, (255, 255, 255), star_points, 2)
            
            # 文明信息
            if camera.zoom > 0.05:
                font = pygame.font.Font(None, 32)
                civ_name = getattr(civilization, 'name', 'Unknown Civilization')
                population = getattr(civilization, 'population', 0)
                
                info_text = f"{civ_name} (Pop: {population})"
                text_surface = font.render(info_text, True, (255, 255, 255))
                text_pos = (int(capital_screen.x) + 20, int(capital_screen.y) - 20)
                screen.blit(text_surface, text_pos)
    
    def _render_major_events(self, screen: pygame.Surface, world_state: Dict, camera: Camera):
        """渲染重大事件"""
        
        major_events = world_state.get('major_events', [])
        
        for event in major_events:
            if not hasattr(event, 'position'):
                continue
            
            event_screen = camera.world_to_screen(event.position)
            
            # 事件类型决定图标
            event_type = getattr(event, 'type', 'unknown')
            
            if event_type == 'conflict':
                # 冲突事件 - 红色爆炸图标
                pygame.draw.circle(screen, (255, 0, 0), 
                                 (int(event_screen.x), int(event_screen.y)), 12)
                pygame.draw.circle(screen, (255, 255, 0),
                                 (int(event_screen.x), int(event_screen.y)), 8)
            elif event_type == 'alliance':
                # 联盟事件 - 绿色握手图标
                pygame.draw.circle(screen, (0, 255, 0),
                                 (int(event_screen.x), int(event_screen.y)), 10)
            elif event_type == 'discovery':
                # 发现事件 - 蓝色星形
                pygame.draw.circle(screen, (0, 100, 255),
                                 (int(event_screen.x), int(event_screen.y)), 10)


class GlobalRenderer(BaseScaleRenderer):
    """全球渲染器 - 专注于世界级别的趋势和模式"""
    
    def __init__(self):
        super().__init__(ScaleLevel.GLOBAL)
        
    def render(self, screen: pygame.Surface, world_state: Dict, camera: Camera):
        """渲染全球层次"""
        
        agents = world_state.get('agents', [])
        
        try:
            # 简化的全球渲染
            self._render_simple_global_view(screen, agents, camera)
        except Exception as e:
            # 备用渲染
            self._render_global_fallback(screen)
    
    def _render_simple_global_view(self, screen: pygame.Surface, agents: List, camera: Camera):
        """简化的全球视图"""
        # 绘制世界背景
        screen.fill((25, 25, 112))  # 深蓝色海洋
        
        # 绘制基础陆地背景
        land_rect = pygame.Rect(50, 50, screen.get_width()-100, screen.get_height()-100)
        pygame.draw.rect(screen, (34, 139, 34), land_rect)  # 森林绿
        
        # 绘制环境特征
        self._render_environment_features(screen, camera)
        
        # 绘制智能体密度热图
        self._render_population_density(screen, agents, camera)
        
        # 绘制统计信息
        self._render_global_statistics(screen, agents)
    
    def _render_environment_features(self, screen: pygame.Surface, camera: Camera):
        """渲染环境特征（简化版）"""
        # 绘制固定的环境区域以确保可见
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # 森林区域 (绿色)
        forest_rect = pygame.Rect(screen_width * 0.3, screen_height * 0.2, 
                                screen_width * 0.4, screen_height * 0.3)
        pygame.draw.rect(screen, (34, 139, 34), forest_rect)
        pygame.draw.rect(screen, (0, 100, 0), forest_rect, 3)
        
        # 沙漠区域 (黄色)
        desert_rect = pygame.Rect(screen_width * 0.1, screen_height * 0.6,
                                screen_width * 0.3, screen_height * 0.25)
        pygame.draw.rect(screen, (255, 218, 185), desert_rect)
        pygame.draw.rect(screen, (255, 165, 0), desert_rect, 3)
        
        # 山地区域 (灰色)
        mountain_rect = pygame.Rect(screen_width * 0.7, screen_height * 0.3,
                                  screen_width * 0.25, screen_height * 0.4)
        pygame.draw.rect(screen, (139, 137, 137), mountain_rect)
        pygame.draw.rect(screen, (105, 105, 105), mountain_rect, 3)
        
        # 水域 (蓝色)
        water_rect = pygame.Rect(screen_width * 0.5, screen_height * 0.7,
                               screen_width * 0.15, screen_height * 0.15)
        pygame.draw.rect(screen, (64, 224, 208), water_rect)
        pygame.draw.rect(screen, (0, 191, 255), water_rect, 2)
        
        # 添加标签
        font = pygame.font.Font(None, 16)
        labels = [
            ("Forest", forest_rect.centerx, forest_rect.centery, (255, 255, 255)),
            ("Desert", desert_rect.centerx, desert_rect.centery, (139, 69, 19)),
            ("Mountain", mountain_rect.centerx, mountain_rect.centery, (255, 255, 255)),
            ("Lake", water_rect.centerx, water_rect.centery, (255, 255, 255))
        ]
        
        for label, x, y, color in labels:
            text_surface = font.render(label, True, color)
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
    
    def _render_terrain_zones(self, screen: pygame.Surface, camera: Camera):
        """渲染地形区域"""
        terrain_colors = {
            'plains': (144, 238, 144),    # 浅绿色
            'forest': (34, 139, 34),      # 深绿色
            'mountain': (139, 137, 137),  # 灰色
            'desert': (255, 218, 185),    # 沙色
            'water': (64, 224, 208),      # 青色
            'swamp': (107, 142, 35),      # 橄榄绿
            'hills': (205, 133, 63)       # 秘鲁色
        }
        
        # 简化的地形绘制
        zones = [
            {'type': 'forest', 'rect': (100, 50, 200, 100)},
            {'type': 'desert', 'rect': (50, 200, 150, 120)},
            {'type': 'mountain', 'rect': (400, 100, 100, 150)},
            {'type': 'water', 'rect': (250, 250, 80, 60)}
        ]
        
        for zone in zones:
            color = terrain_colors.get(zone['type'], (100, 139, 100))
            pygame.draw.rect(screen, color, zone['rect'])
    
    def _render_climate_zones(self, screen: pygame.Surface, camera: Camera):
        """渲染气候区域边界"""
        # 绘制气候区域的边界线
        zone_boundaries = [
            {'center': (200, 150), 'radius': 80, 'color': (0, 255, 0)},    # 森林
            {'center': (120, 260), 'radius': 60, 'color': (255, 165, 0)},  # 沙漠
            {'center': (450, 175), 'radius': 50, 'color': (128, 128, 128)} # 山地
        ]
        
        for zone in zone_boundaries:
            pygame.draw.circle(screen, zone['color'], zone['center'], zone['radius'], 2)
    
    def _render_population_density(self, screen: pygame.Surface, agents: List, camera: Camera):
        """渲染种群密度"""
        if not agents:
            return
        
        # 创建密度网格（基于世界坐标）
        world_grid_size = 100  # 世界坐标中的网格大小
        density_grid = {}
        
        for agent in agents:
            try:
                # 使用世界坐标计算网格位置
                world_pos = agent.position
                grid_x = int(world_pos.x // world_grid_size)
                grid_y = int(world_pos.y // world_grid_size)
                key = (grid_x, grid_y)
                density_grid[key] = density_grid.get(key, 0) + 1
            except:
                continue
        
        # 绘制密度热图
        max_density = max(density_grid.values()) if density_grid else 1
        for (grid_x, grid_y), count in density_grid.items():
            if count > 0:
                # 计算网格在世界坐标中的位置
                world_rect_center = Vector2D(
                    (grid_x + 0.5) * world_grid_size,
                    (grid_y + 0.5) * world_grid_size
                )
                
                # 转换到屏幕坐标
                screen_center = camera.world_to_screen(world_rect_center)
                screen_size = int(world_grid_size * camera.zoom)
                
                # 确保在屏幕范围内
                if (0 <= screen_center.x <= screen.get_width() and 
                    0 <= screen_center.y <= screen.get_height() and 
                    screen_size > 2):
                    
                    intensity = min(count / max_density, 1.0)
                    alpha = int(150 * intensity)
                    color = (255, int(255 * (1 - intensity)), 0, alpha)
                    
                    # 绘制热点
                    heat_surf = pygame.Surface((screen_size, screen_size), pygame.SRCALPHA)
                    pygame.draw.rect(heat_surf, color, (0, 0, screen_size, screen_size))
                    screen.blit(heat_surf, (int(screen_center.x - screen_size//2), 
                                          int(screen_center.y - screen_size//2)))
                    
                    # 在密度高的地方显示智能体数量
                    if count > 1 and screen_size > 20:
                        font = pygame.font.Font(None, max(12, min(24, screen_size//3)))
                        text = font.render(str(count), True, (255, 255, 255))
                        text_rect = text.get_rect(center=(int(screen_center.x), int(screen_center.y)))
                        screen.blit(text, text_rect)
    
    def _render_global_statistics(self, screen: pygame.Surface, agents: List):
        """渲染全球统计信息"""
        if not agents:
            return
            
        total_agents = len(agents)
        avg_energy = sum(getattr(agent, 'energy', 0) for agent in agents) / total_agents
        avg_health = sum(getattr(agent, 'health', 0) for agent in agents) / total_agents
        
        font = pygame.font.Font(None, 20)
        stats = [
            f"🌍 Global Population: {total_agents}",
            f"⚡ Average Energy: {avg_energy:.1f}",
            f"❤️ Average Health: {avg_health:.1f}",
            f"🌿 Ecosystem Health: {'Good' if avg_health > 70 else 'Poor'}"
        ]
        
        for i, stat in enumerate(stats):
            text_surface = font.render(stat, True, (255, 255, 255))
            screen.blit(text_surface, (20, 20 + i * 25))
    
    def _render_global_fallback(self, screen: pygame.Surface):
        """全球渲染备用方案"""
        pygame.draw.rect(screen, (50, 50, 50), (10, 10, 200, 30))
        font = pygame.font.Font(None, 24)
        text = font.render("GLOBAL Scale", True, (255, 255, 255))
        screen.blit(text, (15, 15))
    
    def _render_world_map(self, screen: pygame.Surface, camera: Camera):
        """渲染世界地图"""
        
        # 渲染大陆轮廓
        visible_area = camera.get_visible_area()
        
        # 简化的大陆形状
        continent_color = (100, 139, 100)
        ocean_color = (25, 25, 112)
        
        # 填充海洋背景
        screen.fill(ocean_color)
        
        # 绘制简化的大陆
        continent_points = [
            (0.2, 0.3), (0.8, 0.2), (0.9, 0.7), (0.1, 0.8)
        ]
        
        # 转换到屏幕坐标
        screen_points = []
        for x_ratio, y_ratio in continent_points:
            world_x = visible_area.left + x_ratio * visible_area.width
            world_y = visible_area.top + y_ratio * visible_area.height
            screen_pos = camera.world_to_screen(Vector2D(world_x, world_y))
            screen_points.append((int(screen_pos.x), int(screen_pos.y)))
        
        if len(screen_points) >= 3:
            pygame.draw.polygon(screen, continent_color, screen_points)
    
    def _render_civilization_distribution(self, screen: pygame.Surface, world_state: Dict, camera: Camera):
        """渲染文明分布"""
        
        civilizations = world_state.get('civilizations', [])
        tribes = world_state.get('tribes', [])
        
        # 如果没有文明数据，基于智能体密度创建虚拟文明区域
        if not civilizations and not tribes:
            agents = world_state.get('agents', [])
            self._render_population_density(screen, agents, camera)
    
    def _render_population_density(self, screen: pygame.Surface, agents: List, camera: Camera):
        """渲染人口密度"""
        
        if not agents:
            return
        
        visible_area = camera.get_visible_area()
        grid_size = 200  # 大网格用于全球视角
        
        # 计算网格
        grid_width = int(visible_area.width // grid_size) + 2
        grid_height = int(visible_area.height // grid_size) + 2
        
        density_grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
        
        # 计算人口密度
        for agent in agents:
            if not camera.is_visible(agent.position):
                continue
            
            grid_x = int((agent.position.x - visible_area.left) // grid_size)
            grid_y = int((agent.position.y - visible_area.top) // grid_size)
            
            if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:
                density_grid[grid_y][grid_x] += 1
        
        # 渲染密度热图
        max_density = max(max(row) for row in density_grid) if any(any(row) for row in density_grid) else 1
        
        for y in range(grid_height):
            for x in range(grid_width):
                density = density_grid[y][x]
                if density > 0:
                    intensity = min(density / max_density, 1.0)
                    
                    # 人口密度颜色（从绿到红）
                    if intensity < 0.5:
                        color = (int(255 * intensity * 2), 255, 0, int(intensity * 150))
                    else:
                        color = (255, int(255 * (1 - intensity)), 0, int(intensity * 150))
                    
                    # 绘制密度方块
                    world_x = visible_area.left + x * grid_size
                    world_y = visible_area.top + y * grid_size
                    screen_pos = camera.world_to_screen(Vector2D(world_x, world_y))
                    screen_size = int(grid_size * camera.zoom)
                    
                    if screen_size > 1:
                        density_surf = pygame.Surface((screen_size, screen_size), pygame.SRCALPHA)
                        pygame.draw.rect(density_surf, color, (0, 0, screen_size, screen_size))
                        screen.blit(density_surf, (int(screen_pos.x), int(screen_pos.y)))
    
    def _render_global_trends(self, screen: pygame.Surface, world_state: Dict, camera: Camera):
        """渲染全球趋势"""
        
        # 在屏幕角落显示全球统计信息
        font = pygame.font.Font(None, 24)
        y_offset = 20
        
        stats = [
            f"Total Population: {len(world_state.get('agents', []))}",
            f"Tribes: {len(world_state.get('tribes', []))}",
            f"Civilizations: {len(world_state.get('civilizations', []))}",
            f"Global Step: {world_state.get('current_step', 0)}"
        ]
        
        for stat in stats:
            text_surf = font.render(stat, True, (255, 255, 255))
            # 在右上角显示
            text_rect = text_surf.get_rect(topright=(screen.get_width() - 20, y_offset))
            
            # 添加半透明背景
            bg_surf = pygame.Surface((text_rect.width + 10, text_rect.height + 4), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (0, 0, 0, 128), (0, 0, text_rect.width + 10, text_rect.height + 4))
            screen.blit(bg_surf, (text_rect.left - 5, text_rect.top - 2))
            
            screen.blit(text_surf, text_rect)
            y_offset += 30
    
    def _render_climate_zones(self, screen: pygame.Surface, camera: Camera):
        """渲染气候区域"""
        
        visible_area = camera.get_visible_area()
        
        # 简化的气候带（基于纬度）
        zone_height = visible_area.height / 5
        
        climate_zones = [
            ((100, 150, 255), "Arctic"),      # 北极 - 浅蓝
            ((50, 200, 50), "Temperate"),     # 温带 - 绿色
            ((255, 200, 50), "Tropical"),     # 热带 - 黄色
            ((50, 200, 50), "Temperate"),     # 温带 - 绿色
            ((200, 200, 255), "Antarctic")    # 南极 - 浅紫
        ]
        
        for i, (color, name) in enumerate(climate_zones):
            zone_top = visible_area.top + i * zone_height
            zone_bottom = zone_top + zone_height
            
            # 转换到屏幕坐标
            screen_top = camera.world_to_screen(Vector2D(visible_area.left, zone_top))
            screen_bottom = camera.world_to_screen(Vector2D(visible_area.right, zone_bottom))
            
            zone_rect = pygame.Rect(0, int(screen_top.y), 
                                  screen.get_width(), int(screen_bottom.y - screen_top.y))
            
            # 绘制半透明气候带
            zone_surf = pygame.Surface((zone_rect.width, zone_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(zone_surf, (*color, 30), (0, 0, zone_rect.width, zone_rect.height))
            screen.blit(zone_surf, zone_rect.topleft)
            
            # 气候带标签
            if camera.zoom < 0.05:  # 只在极小缩放时显示
                font = pygame.font.Font(None, 36)
                label = font.render(name, True, (255, 255, 255))
                label_pos = (20, zone_rect.centery - label.get_height() // 2)
                screen.blit(label, label_pos)