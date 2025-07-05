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
            
            # 选择颜色基于能量水平
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
            elif event.key == pygame.K_r:
                # 重置轨迹
                self.agent_trajectories.clear()
    
    def cleanup(self):
        """清理资源"""
        pygame.quit()
        logger.info("WorldRenderer cleaned up")