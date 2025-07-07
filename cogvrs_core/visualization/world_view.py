"""
Cogvrs - World Visualization
世界可视化：实时显示2D世界和智能体状态

Author: Ben Hsu & Claude
"""

import pygame
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class WorldRenderer:
    """
    世界渲染器
    
    Features:
    - 2D世界实时渲染
    - 智能体可视化
    - 资源显示
    - 轨迹追踪
    - 状态信息展示
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.screen_width = config.get('screen_width', 1000)
        self.screen_height = config.get('screen_height', 700)
        self.world_width = config.get('world_width', 100)
        self.world_height = config.get('world_height', 100)
        
        # 颜色配置
        self.colors = {
            'background': (20, 25, 40),
            'grid': (40, 45, 60),
            'agent': (100, 150, 255),
            'agent_high_energy': (150, 255, 150),
            'agent_low_energy': (255, 100, 100),
            'resource_food': (50, 255, 50),
            'resource_energy': (255, 255, 50),
            'resource_material': (200, 150, 100),
            'obstacle': (80, 80, 80),
            'text': (255, 255, 255),
            'trajectory': (100, 100, 150),
            'connection': (255, 255, 100, 128)  # 半透明
        }
        
        # 渲染选项
        self.show_grid = config.get('show_grid', True)
        self.show_trajectories = config.get('show_trajectories', True)
        self.show_connections = config.get('show_connections', True)
        self.show_perception_radius = config.get('show_perception_radius', False)
        self.show_tribes = config.get('show_tribes', True)  # 默认显示部落
        
        # 缩放和平移
        self.scale_x = self.screen_width / self.world_width
        self.scale_y = self.screen_height / self.world_height
        self.offset_x = 0
        self.offset_y = 0
        
        # 轨迹存储
        self.agent_trajectories = {}
        self.max_trajectory_length = 50
        
        # 初始化pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Cogvrs - Cognitive Universe")
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        logger.info(f"WorldRenderer initialized: {self.screen_width}x{self.screen_height}")
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """世界坐标转屏幕坐标"""
        screen_x = int((world_x + self.offset_x) * self.scale_x)
        screen_y = int((world_y + self.offset_y) * self.scale_y)
        return screen_x, screen_y
    
    def render_frame(self, world_state: Dict, agents: List, time_info: Dict):
        """渲染一帧"""
        # 清空屏幕
        self.screen.fill(self.colors['background'])
        
        # 绘制网格
        if self.show_grid:
            self._draw_grid()
        
        # 绘制世界元素
        self._draw_terrain(world_state)
        self._draw_resources(world_state)
        
        # 绘制部落领土和交互
        if self.show_tribes:
            self._draw_tribes(world_state)
        
        # 绘制智能体轨迹
        if self.show_trajectories:
            self._draw_trajectories()
        
        # 绘制智能体连接
        if self.show_connections:
            self._draw_agent_connections(agents)
        
        # 绘制智能体
        self._draw_agents(agents)
        
        # 绘制UI信息
        self._draw_ui_info(world_state, agents, time_info)
        
        # 更新显示
        pygame.display.flip()
    
    def _draw_tribes(self, world_state: Dict):
        """绘制部落领土和交互"""
        tribes = world_state.get('tribes', [])
        tribe_interactions = world_state.get('tribe_interactions', [])
        
        # 绘制部落间交互连线
        for interaction in tribe_interactions:
            center_a = interaction['center_a']
            center_b = interaction['center_b']
            relation_type = interaction['relation_type']
            color = interaction['color']
            
            # 转换坐标到屏幕坐标
            screen_a = self.world_to_screen(center_a[0], center_a[1])
            screen_b = self.world_to_screen(center_b[0], center_b[1])
            
            # 根据关系类型选择线条样式
            if relation_type == 'alliance':
                # 同盟：实线，较粗
                pygame.draw.line(self.screen, color, screen_a, screen_b, 3)
            elif relation_type == 'conflict':
                # 冲突：虚线效果
                self._draw_dashed_line(screen_a, screen_b, color, 2)
            else:
                # 中性：细线
                pygame.draw.line(self.screen, color, screen_a, screen_b, 1)
        
        # 绘制部落领土圆圈
        for tribe in tribes:
            center = tribe['center']
            radius = tribe['radius']
            color = tribe['color']
            population = tribe['population']
            name = tribe['name']
            
            # 转换坐标
            screen_center = self.world_to_screen(center[0], center[1])
            screen_radius = int(radius * self.scale_x)
            
            # 绘制领土边界（半透明圆圈）
            territory_color = (*color, 50)  # 半透明
            self._draw_transparent_circle(screen_center, screen_radius, territory_color, 2)
            
            # 绘制部落中心点
            pygame.draw.circle(self.screen, color, screen_center, 8)
            pygame.draw.circle(self.screen, (255, 255, 255), screen_center, 8, 2)
            
            # 绘制部落名称和信息
            if screen_radius > 30:  # 只在足够大的时候显示文字
                font = pygame.font.Font(None, 20)
                name_text = font.render(name, True, (255, 255, 255))
                pop_text = font.render(f"Pop: {population}", True, (200, 200, 200))
                
                # 计算文字位置
                text_x = screen_center[0] - name_text.get_width() // 2
                text_y = screen_center[1] - 25
                
                self.screen.blit(name_text, (text_x, text_y))
                self.screen.blit(pop_text, (text_x, text_y + 15))
    
    def _draw_dashed_line(self, start, end, color, width):
        """绘制虚线"""
        start_x, start_y = start
        end_x, end_y = end
        
        # 计算线段长度和方向
        length = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        if length == 0:
            return
        
        dx = (end_x - start_x) / length
        dy = (end_y - start_y) / length
        
        # 绘制虚线段
        dash_length = 5
        gap_length = 3
        current_pos = 0
        
        while current_pos < length:
            # 虚线段开始位置
            dash_start_x = int(start_x + dx * current_pos)
            dash_start_y = int(start_y + dy * current_pos)
            
            # 虚线段结束位置
            dash_end_pos = min(current_pos + dash_length, length)
            dash_end_x = int(start_x + dx * dash_end_pos)
            dash_end_y = int(start_y + dy * dash_end_pos)
            
            # 绘制虚线段
            pygame.draw.line(self.screen, color, 
                           (dash_start_x, dash_start_y), 
                           (dash_end_x, dash_end_y), width)
            
            current_pos += dash_length + gap_length
    
    def _draw_transparent_circle(self, center, radius, color, width):
        """绘制半透明圆圈"""
        # 创建临时surface
        temp_surface = pygame.Surface((radius * 2 + width, radius * 2 + width), pygame.SRCALPHA)
        temp_surface.set_alpha(color[3] if len(color) > 3 else 128)
        
        # 在临时surface上绘制圆圈
        circle_color = color[:3] if len(color) > 3 else color
        pygame.draw.circle(temp_surface, circle_color, 
                         (radius + width//2, radius + width//2), radius, width)
        
        # 将临时surface绘制到主屏幕
        self.screen.blit(temp_surface, 
                        (center[0] - radius - width//2, center[1] - radius - width//2))
    
    def _draw_leader_icon(self, screen_x: int, screen_y: int, radius: int):
        """绘制首领图标（皇冠）"""
        # 皇冠颜色
        crown_color = (255, 215, 0)  # 金色
        crown_outline = (255, 255, 255)  # 白色边框
        
        # 皇冠位置（在智能体上方）
        crown_x = screen_x
        crown_y = screen_y - radius - 8
        
        # 绘制皇冠底座
        crown_base_points = [
            (crown_x - 6, crown_y + 3),
            (crown_x + 6, crown_y + 3),
            (crown_x + 4, crown_y),
            (crown_x - 4, crown_y)
        ]
        pygame.draw.polygon(self.screen, crown_color, crown_base_points)
        pygame.draw.polygon(self.screen, crown_outline, crown_base_points, 1)
        
        # 绘制皇冠尖齿
        crown_teeth = [
            (crown_x - 4, crown_y),
            (crown_x - 2, crown_y - 4),
            (crown_x, crown_y - 6),
            (crown_x + 2, crown_y - 4),
            (crown_x + 4, crown_y)
        ]
        pygame.draw.polygon(self.screen, crown_color, crown_teeth)
        pygame.draw.polygon(self.screen, crown_outline, crown_teeth, 1)
        
        # 绘制皇冠中央的宝石
        pygame.draw.circle(self.screen, (255, 100, 100), (crown_x, crown_y - 3), 2)  # 红宝石
    
    def _draw_grid(self):
        """绘制网格"""
        # 垂直线
        for x in range(0, self.world_width + 1, 10):
            screen_x, _ = self.world_to_screen(x, 0)
            if 0 <= screen_x <= self.screen_width:
                pygame.draw.line(
                    self.screen, self.colors['grid'],
                    (screen_x, 0), (screen_x, self.screen_height), 1
                )
        
        # 水平线
        for y in range(0, self.world_height + 1, 10):
            _, screen_y = self.world_to_screen(0, y)
            if 0 <= screen_y <= self.screen_height:
                pygame.draw.line(
                    self.screen, self.colors['grid'],
                    (0, screen_y), (self.screen_width, screen_y), 1
                )
    
    def _draw_terrain(self, world_state: Dict):
        """绘制地形"""
        terrain_grid = world_state.get('terrain_grid')
        if terrain_grid is None:
            return
        
        for x in range(len(terrain_grid)):
            for y in range(len(terrain_grid[0])):
                if terrain_grid[x][y] == 2:  # 障碍物
                    screen_x, screen_y = self.world_to_screen(x, y)
                    rect = pygame.Rect(
                        screen_x, screen_y,
                        max(1, int(self.scale_x)), max(1, int(self.scale_y))
                    )
                    pygame.draw.rect(self.screen, self.colors['obstacle'], rect)
    
    def _draw_resources(self, world_state: Dict):
        """绘制资源"""
        resources = world_state.get('resources', [])
        
        for resource_data in resources:
            x, y, resource_type, amount = resource_data
            if amount <= 0:
                continue
            
            screen_x, screen_y = self.world_to_screen(x, y)
            
            # 选择颜色
            if resource_type == 'food':
                color = self.colors['resource_food']
            elif resource_type == 'energy':
                color = self.colors['resource_energy']
            else:
                color = self.colors['resource_material']
            
            # 大小基于资源量
            radius = max(2, min(8, int(amount / 10)))
            
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)
            
            # 绘制资源量文字
            if radius > 4:
                text = self.small_font.render(f"{int(amount)}", True, self.colors['text'])
                text_rect = text.get_rect(center=(screen_x, screen_y - radius - 8))
                self.screen.blit(text, text_rect)
    
    def _draw_trajectories(self):
        """绘制智能体轨迹"""
        for agent_id, trajectory in self.agent_trajectories.items():
            if len(trajectory) < 2:
                continue
            
            # 绘制轨迹线
            screen_points = []
            for pos in trajectory:
                screen_x, screen_y = self.world_to_screen(pos[0], pos[1])
                screen_points.append((screen_x, screen_y))
            
            if len(screen_points) >= 2:
                pygame.draw.lines(
                    self.screen, self.colors['trajectory'], 
                    False, screen_points, 1
                )
    
    def _draw_agent_connections(self, agents: List):
        """绘制智能体之间的连接"""
        # 创建半透明表面
        connection_surface = pygame.Surface((self.screen_width, self.screen_height))
        connection_surface.set_alpha(128)
        connection_surface.fill((0, 0, 0, 0))
        
        for i, agent1 in enumerate(agents):
            if not agent1.alive:
                continue
                
            pos1 = self.world_to_screen(agent1.position.x, agent1.position.y)
            
            for agent2 in agents[i+1:]:
                if not agent2.alive:
                    continue
                
                # 计算距离
                distance = agent1.position.distance_to(agent2.position)
                
                # 只显示近距离连接
                if distance < 8:
                    pos2 = self.world_to_screen(agent2.position.x, agent2.position.y)
                    
                    # 线条透明度基于距离
                    alpha = max(0, 255 - int(distance * 30))
                    color = (*self.colors['connection'][:3], alpha)
                    
                    pygame.draw.line(
                        connection_surface, color[:3], pos1, pos2, 1
                    )
        
        self.screen.blit(connection_surface, (0, 0))
    
    def _draw_agents(self, agents: List):
        """绘制智能体"""
        for agent in agents:
            if not agent.alive:
                continue
            
            screen_x, screen_y = self.world_to_screen(agent.position.x, agent.position.y)
            
            # 更新轨迹
            self._update_agent_trajectory(agent.agent_id, (agent.position.x, agent.position.y))
            
            # 选择颜色 - 优先使用部落颜色
            if hasattr(agent, 'tribe_color') and agent.tribe_color:
                base_color = agent.tribe_color
                # 根据能量水平调整亮度
                energy_ratio = agent.energy / agent.max_energy
                if energy_ratio > 0.7:
                    # 高能量：增加亮度
                    color = tuple(min(255, int(c * 1.2)) for c in base_color)
                elif energy_ratio < 0.3:
                    # 低能量：降低亮度
                    color = tuple(max(50, int(c * 0.6)) for c in base_color)
                else:
                    color = base_color
            else:
                # 无部落时使用默认颜色方案
                energy_ratio = agent.energy / agent.max_energy
                if energy_ratio > 0.7:
                    color = self.colors['agent_high_energy']
                elif energy_ratio < 0.3:
                    color = self.colors['agent_low_energy']
                else:
                    color = self.colors['agent']
            
            # 大小基于健康状态
            health_ratio = agent.health / agent.max_health
            radius = max(3, int(4 + health_ratio * 2))
            
            # 绘制感知半径
            if self.show_perception_radius:
                perception_radius = int(agent.perception_radius * self.scale_x)
                pygame.draw.circle(
                    self.screen, (50, 50, 100), 
                    (screen_x, screen_y), perception_radius, 1
                )
            
            # 绘制智能体主体
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)
            
            # 绘制首领图标
            if hasattr(agent, 'is_tribe_leader') and agent.is_tribe_leader:
                self._draw_leader_icon(screen_x, screen_y, radius)
            
            # 绘制方向指示
            if agent.velocity.magnitude() > 0.1:
                direction = agent.velocity.normalize()
                end_x = screen_x + direction.x * (radius + 5)
                end_y = screen_y + direction.y * (radius + 5)
                pygame.draw.line(
                    self.screen, color, 
                    (screen_x, screen_y), (int(end_x), int(end_y)), 2
                )
            
            # 绘制状态指示器
            self._draw_agent_status(agent, screen_x, screen_y, radius)
    
    def _draw_agent_status(self, agent, screen_x: int, screen_y: int, radius: int):
        """绘制智能体状态指示器"""
        # 能量条
        energy_ratio = agent.energy / agent.max_energy
        energy_width = 20
        energy_height = 3
        energy_x = screen_x - energy_width // 2
        energy_y = screen_y + radius + 5
        
        # 背景
        pygame.draw.rect(
            self.screen, (60, 60, 60),
            (energy_x, energy_y, energy_width, energy_height)
        )
        
        # 能量条
        energy_color = (255, 100, 100) if energy_ratio < 0.3 else (100, 255, 100)
        pygame.draw.rect(
            self.screen, energy_color,
            (energy_x, energy_y, int(energy_width * energy_ratio), energy_height)
        )
        
        # 健康条
        health_ratio = agent.health / agent.max_health
        health_y = energy_y + 5
        
        pygame.draw.rect(
            self.screen, (60, 60, 60),
            (energy_x, health_y, energy_width, energy_height)
        )
        
        health_color = (255, 255, 100) if health_ratio > 0.5 else (255, 150, 100)
        pygame.draw.rect(
            self.screen, health_color,
            (energy_x, health_y, int(energy_width * health_ratio), energy_height)
        )
        
        # 年龄指示
        if agent.age > 100:
            age_text = self.small_font.render(f"{int(agent.age)}", True, (200, 200, 200))
            age_rect = age_text.get_rect(center=(screen_x, screen_y - radius - 8))
            self.screen.blit(age_text, age_rect)
    
    def _update_agent_trajectory(self, agent_id: str, position: Tuple[float, float]):
        """更新智能体轨迹"""
        if agent_id not in self.agent_trajectories:
            self.agent_trajectories[agent_id] = []
        
        trajectory = self.agent_trajectories[agent_id]
        trajectory.append(position)
        
        # 限制轨迹长度
        if len(trajectory) > self.max_trajectory_length:
            trajectory.pop(0)
    
    def _draw_ui_info(self, world_state: Dict, agents: List, time_info: Dict):
        """绘制UI信息"""
        # 背景面板
        panel_rect = pygame.Rect(10, 10, 200, 150)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height))
        panel_surface.set_alpha(200)
        panel_surface.fill((30, 30, 50))
        self.screen.blit(panel_surface, panel_rect)
        
        # 信息文本
        y_offset = 20
        
        # 时间信息
        time_text = f"Time: {time_info.get('current_step', 0)}"
        self._draw_text(time_text, 20, y_offset)
        y_offset += 20
        
        # 智能体统计
        alive_agents = [a for a in agents if a.alive]
        agent_text = f"Agents: {len(alive_agents)}/{len(agents)}"
        self._draw_text(agent_text, 20, y_offset)
        y_offset += 20
        
        # 平均年龄
        if alive_agents:
            avg_age = np.mean([a.age for a in alive_agents])
            age_text = f"Avg Age: {avg_age:.1f}"
            self._draw_text(age_text, 20, y_offset)
            y_offset += 20
        
        # 平均能量
        if alive_agents:
            avg_energy = np.mean([a.energy for a in alive_agents])
            energy_text = f"Avg Energy: {avg_energy:.1f}"
            self._draw_text(energy_text, 20, y_offset)
            y_offset += 20
        
        # 资源统计
        resources = world_state.get('resources', [])
        total_resources = sum(r[3] for r in resources)  # r[3] is amount
        resource_text = f"Resources: {total_resources:.0f}"
        self._draw_text(resource_text, 20, y_offset)
        y_offset += 20
        
        # FPS
        fps_text = f"FPS: {time_info.get('actual_fps', 0):.1f}"
        self._draw_text(fps_text, 20, y_offset)
    
    def _draw_text(self, text: str, x: int, y: int, color: Tuple[int, int, int] = None):
        """绘制文本"""
        if color is None:
            color = self.colors['text']
        
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def handle_event(self, event):
        """处理输入事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                self.show_grid = not self.show_grid
            elif event.key == pygame.K_t:
                self.show_trajectories = not self.show_trajectories
            elif event.key == pygame.K_c:
                self.show_connections = not self.show_connections
            elif event.key == pygame.K_p:
                self.show_perception_radius = not self.show_perception_radius
            elif event.key == pygame.K_b:
                # B键切换部落显示
                self.show_tribes = not self.show_tribes
                print(f"🏘️ 部落显示: {'开启' if self.show_tribes else '关闭'}")
            elif event.key == pygame.K_r:
                # 重置轨迹
                self.agent_trajectories.clear()
    
    def cleanup(self):
        """清理资源"""
        pygame.quit()
        logger.info("WorldRenderer cleaned up")