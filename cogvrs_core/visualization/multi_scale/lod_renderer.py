"""
LOD Renderer - 细节层次渲染器
根据距离和缩放级别智能调整渲染细节

Author: Ben Hsu & Claude
"""

import math
from typing import Dict, List, Tuple, Optional
import pygame
import numpy as np
import logging

from ...core.physics_engine import Vector2D
from .camera_system import Camera
from .scale_manager import ScaleLevel

logger = logging.getLogger(__name__)


class LODLevel:
    """LOD级别定义"""
    FULL_DETAIL = "full_detail"     # 完整细节
    HIGH_DETAIL = "high_detail"     # 高细节
    MEDIUM_DETAIL = "medium_detail" # 中等细节
    LOW_DETAIL = "low_detail"       # 低细节
    ICON_ONLY = "icon_only"         # 仅图标
    CLUSTER = "cluster"             # 聚类表示


class LODRenderer:
    """细节层次渲染器"""
    
    def __init__(self):
        # LOD阈值配置
        self.lod_thresholds = {
            'full_detail': 3.0,      # 完整细节显示阈值
            'high_detail': 1.5,      # 高细节显示阈值
            'medium_detail': 0.8,    # 中等细节显示阈值
            'low_detail': 0.3,       # 低细节显示阈值
            'icon_only': 0.1,        # 仅图标显示阈值
            'cluster_distance': 50   # 聚类距离阈值
        }
        
        # 缓存系统
        self.render_cache = {}
        self.cache_expiry_time = 1000  # 1秒缓存过期
        
        # 性能监控
        self.performance_stats = {
            'total_objects': 0,
            'culled_objects': 0,
            'cached_renders': 0,
            'lod_distribution': {level: 0 for level in ['full', 'high', 'medium', 'low', 'icon', 'cluster']}
        }
        
        logger.debug("LODRenderer initialized")
    
    def determine_agent_lod(self, agent, camera: Camera, scale_level: ScaleLevel) -> str:
        """确定智能体的LOD级别"""
        
        # 计算到相机的距离
        distance = camera.get_distance_to_camera(agent.position)
        
        # 计算有效缩放级别
        effective_zoom = camera.zoom * (200 / max(distance, 1))
        
        # 根据尺度级别调整阈值
        scale_multiplier = {
            ScaleLevel.MICRO: 1.0,
            ScaleLevel.MESO: 0.7,
            ScaleLevel.MACRO: 0.4,
            ScaleLevel.GLOBAL: 0.1
        }.get(scale_level, 1.0)
        
        adjusted_zoom = effective_zoom * scale_multiplier
        
        # 确定LOD级别
        if adjusted_zoom >= self.lod_thresholds['full_detail']:
            return LODLevel.FULL_DETAIL
        elif adjusted_zoom >= self.lod_thresholds['high_detail']:
            return LODLevel.HIGH_DETAIL
        elif adjusted_zoom >= self.lod_thresholds['medium_detail']:
            return LODLevel.MEDIUM_DETAIL
        elif adjusted_zoom >= self.lod_thresholds['low_detail']:
            return LODLevel.LOW_DETAIL
        elif adjusted_zoom >= self.lod_thresholds['icon_only']:
            return LODLevel.ICON_ONLY
        else:
            return LODLevel.CLUSTER
    
    def render_agent_with_lod(self, screen: pygame.Surface, agent, camera: Camera, 
                             lod_level: str, screen_pos: Tuple[int, int]):
        """根据LOD级别渲染智能体"""
        
        # 检查缓存
        cache_key = f"agent_{agent.agent_id}_{lod_level}_{agent.energy:.0f}_{agent.health:.0f}"
        current_time = pygame.time.get_ticks()
        
        if cache_key in self.render_cache:
            cache_entry = self.render_cache[cache_key]
            if current_time - cache_entry['timestamp'] < self.cache_expiry_time:
                # 使用缓存的渲染结果
                self._apply_cached_render(screen, cache_entry['surface'], screen_pos)
                self.performance_stats['cached_renders'] += 1
                return
        
        # 根据LOD级别渲染
        if lod_level == LODLevel.FULL_DETAIL:
            self._render_full_detail_agent(screen, agent, screen_pos)
        elif lod_level == LODLevel.HIGH_DETAIL:
            self._render_high_detail_agent(screen, agent, screen_pos)
        elif lod_level == LODLevel.MEDIUM_DETAIL:
            self._render_medium_detail_agent(screen, agent, screen_pos)
        elif lod_level == LODLevel.LOW_DETAIL:
            self._render_low_detail_agent(screen, agent, screen_pos)
        elif lod_level == LODLevel.ICON_ONLY:
            self._render_icon_agent(screen, agent, screen_pos)
        
        # 更新性能统计
        lod_key = lod_level.split('_')[0]
        if lod_key in self.performance_stats['lod_distribution']:
            self.performance_stats['lod_distribution'][lod_key] += 1
    
    def _render_full_detail_agent(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """渲染完整细节智能体"""
        
        # 1. 智能体主体（带轮廓）
        agent_color = self._get_agent_color(agent)
        
        # 主体圆圈
        pygame.draw.circle(screen, agent_color, screen_pos, 10)
        pygame.draw.circle(screen, (255, 255, 255), screen_pos, 10, 2)  # 白色轮廓
        
        # 2. 详细状态条
        self._render_detailed_status_bars(screen, agent, screen_pos)
        
        # 3. 方向指示器
        self._render_direction_indicator(screen, agent, screen_pos)
        
        # 4. 状态图标
        self._render_status_icons(screen, agent, screen_pos)
        
        # 5. ID标签
        self._render_agent_label(screen, agent, screen_pos)
        
        # 6. 如果有特殊状态，添加特效
        self._render_special_effects(screen, agent, screen_pos)
    
    def _render_high_detail_agent(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """渲染高细节智能体"""
        
        # 智能体主体
        agent_color = self._get_agent_color(agent)
        pygame.draw.circle(screen, agent_color, screen_pos, 8)
        pygame.draw.circle(screen, (200, 200, 200), screen_pos, 8, 1)
        
        # 简化状态条
        self._render_simple_status_bars(screen, agent, screen_pos)
        
        # 方向指示器
        self._render_direction_indicator(screen, agent, screen_pos, scale=0.8)
        
        # 主要状态图标
        self._render_primary_status_icon(screen, agent, screen_pos)
    
    def _render_medium_detail_agent(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """渲染中等细节智能体"""
        
        # 智能体主体
        agent_color = self._get_agent_color(agent)
        pygame.draw.circle(screen, agent_color, screen_pos, 6)
        
        # 仅健康状态条
        self._render_health_bar_only(screen, agent, screen_pos)
        
        # 简化方向指示器
        if hasattr(agent, 'velocity') and agent.velocity.magnitude() > 0.5:
            self._render_direction_indicator(screen, agent, screen_pos, scale=0.6)
    
    def _render_low_detail_agent(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """渲染低细节智能体"""
        
        # 简单的彩色圆点
        agent_color = self._get_agent_color(agent)
        pygame.draw.circle(screen, agent_color, screen_pos, 4)
        
        # 危险状态指示器
        if hasattr(agent, 'health') and agent.health < 30:
            pygame.draw.circle(screen, (255, 0, 0), screen_pos, 6, 2)
    
    def _render_icon_agent(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """渲染图标模式智能体"""
        
        # 最简单的小点
        agent_color = self._get_agent_color(agent)
        pygame.draw.circle(screen, agent_color, screen_pos, 2)
    
    def _get_agent_color(self, agent) -> Tuple[int, int, int]:
        """获取智能体颜色"""
        if not hasattr(agent, 'energy') or not hasattr(agent, 'max_energy'):
            return (128, 128, 128)  # 默认灰色
        
        energy_ratio = agent.energy / agent.max_energy
        
        if energy_ratio > 0.7:
            return (0, 255, 0)      # 绿色 - 健康
        elif energy_ratio > 0.4:
            return (255, 255, 0)    # 黄色 - 一般
        else:
            return (255, 0, 0)      # 红色 - 危险
    
    def _render_detailed_status_bars(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """渲染详细状态条"""
        
        bar_width = 20
        bar_height = 3
        x_offset = -bar_width // 2
        
        # 健康条
        if hasattr(agent, 'health'):
            health_ratio = agent.health / 100.0
            health_y = screen_pos[1] - 18
            
            # 背景
            pygame.draw.rect(screen, (100, 100, 100), 
                           (screen_pos[0] + x_offset, health_y, bar_width, bar_height))
            # 健康值
            health_color = (255, 0, 0) if health_ratio < 0.3 else (255, 255, 0) if health_ratio < 0.7 else (0, 255, 0)
            pygame.draw.rect(screen, health_color,
                           (screen_pos[0] + x_offset, health_y, int(bar_width * health_ratio), bar_height))
        
        # 能量条
        if hasattr(agent, 'energy') and hasattr(agent, 'max_energy'):
            energy_ratio = agent.energy / agent.max_energy
            energy_y = screen_pos[1] - 14
            
            # 背景
            pygame.draw.rect(screen, (50, 50, 50),
                           (screen_pos[0] + x_offset, energy_y, bar_width, bar_height))
            # 能量值
            pygame.draw.rect(screen, (0, 100, 255),
                           (screen_pos[0] + x_offset, energy_y, int(bar_width * energy_ratio), bar_height))
    
    def _render_simple_status_bars(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """渲染简化状态条"""
        
        bar_width = 16
        bar_height = 2
        x_offset = -bar_width // 2
        
        # 仅显示能量条
        if hasattr(agent, 'energy') and hasattr(agent, 'max_energy'):
            energy_ratio = agent.energy / agent.max_energy
            energy_y = screen_pos[1] - 12
            
            pygame.draw.rect(screen, (40, 40, 40),
                           (screen_pos[0] + x_offset, energy_y, bar_width, bar_height))
            
            energy_color = self._get_agent_color(agent)
            pygame.draw.rect(screen, energy_color,
                           (screen_pos[0] + x_offset, energy_y, int(bar_width * energy_ratio), bar_height))
    
    def _render_health_bar_only(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """仅渲染健康条"""
        
        if not hasattr(agent, 'health'):
            return
        
        bar_width = 12
        bar_height = 1
        health_ratio = agent.health / 100.0
        health_y = screen_pos[1] - 8
        x_offset = -bar_width // 2
        
        if health_ratio < 0.8:  # 仅在健康不满时显示
            health_color = (255, 0, 0) if health_ratio < 0.3 else (255, 255, 0)
            pygame.draw.rect(screen, health_color,
                           (screen_pos[0] + x_offset, health_y, int(bar_width * health_ratio), bar_height))
    
    def _render_direction_indicator(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int], scale: float = 1.0):
        """渲染方向指示器"""
        
        if not hasattr(agent, 'velocity'):
            return
        
        velocity_magnitude = agent.velocity.magnitude()
        if velocity_magnitude < 0.1:
            return
        
        # 计算方向
        direction = agent.velocity.normalize()
        arrow_length = 15 * scale
        
        end_pos = (
            screen_pos[0] + direction.x * arrow_length,
            screen_pos[1] + direction.y * arrow_length
        )
        
        # 绘制箭头
        line_width = max(1, int(2 * scale))
        pygame.draw.line(screen, (255, 255, 255), screen_pos, end_pos, line_width)
        
        # 箭头头部
        if scale >= 0.7:
            head_size = 4 * scale
            head_angle = math.pi / 6
            
            # 计算箭头头部的两个点
            head1_x = end_pos[0] - head_size * math.cos(math.atan2(direction.y, direction.x) - head_angle)
            head1_y = end_pos[1] - head_size * math.sin(math.atan2(direction.y, direction.x) - head_angle)
            
            head2_x = end_pos[0] - head_size * math.cos(math.atan2(direction.y, direction.x) + head_angle)
            head2_y = end_pos[1] - head_size * math.sin(math.atan2(direction.y, direction.x) + head_angle)
            
            pygame.draw.line(screen, (255, 255, 255), end_pos, (head1_x, head1_y), line_width)
            pygame.draw.line(screen, (255, 255, 255), end_pos, (head2_x, head2_y), line_width)
    
    def _render_status_icons(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """渲染状态图标"""
        
        if not hasattr(agent, 'behavior_system'):
            return
        
        # 获取主导动机
        motivations = agent.behavior_system.motivations
        strongest_motivation = max(motivations.items(), key=lambda x: x[1].value)
        
        # 动机颜色映射
        motivation_colors = {
            'hunger': (255, 165, 0),     # 橙色
            'social': (255, 192, 203),   # 粉色
            'curiosity': (128, 0, 128),  # 紫色
            'reproduction': (255, 20, 147), # 深粉
            'safety': (0, 255, 0),       # 绿色
            'energy': (255, 255, 0)      # 黄色
        }
        
        if strongest_motivation[1].value > 0.6:  # 仅在动机较强时显示
            color = motivation_colors.get(strongest_motivation[0], (255, 255, 255))
            icon_pos = (screen_pos[0] + 12, screen_pos[1] - 8)
            pygame.draw.circle(screen, color, icon_pos, 3)
    
    def _render_primary_status_icon(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """渲染主要状态图标"""
        
        # 仅显示最重要的状态
        if hasattr(agent, 'health') and agent.health < 20:
            # 危险状态
            pygame.draw.circle(screen, (255, 0, 0), (screen_pos[0] + 10, screen_pos[1] - 6), 2)
        elif hasattr(agent, 'energy') and hasattr(agent, 'max_energy') and agent.energy > agent.max_energy * 0.9:
            # 充满能量状态
            pygame.draw.circle(screen, (0, 255, 0), (screen_pos[0] + 10, screen_pos[1] - 6), 2)
    
    def _render_agent_label(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """渲染智能体标签"""
        
        font = pygame.font.Font(None, 16)
        agent_id = f"A{agent.agent_id[-3:]}" if hasattr(agent, 'agent_id') else "A???"
        text_surface = font.render(agent_id, True, (255, 255, 255))
        
        label_pos = (screen_pos[0] + 12, screen_pos[1] - 25)
        screen.blit(text_surface, label_pos)
    
    def _render_special_effects(self, screen: pygame.Surface, agent, screen_pos: Tuple[int, int]):
        """渲染特殊效果"""
        
        current_time = pygame.time.get_ticks()
        
        # 新生智能体发光效果
        if hasattr(agent, 'age') and agent.age < 10:
            glow_alpha = int(128 * (1 - agent.age / 10))
            glow_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 255, glow_alpha), (15, 15), 15)
            screen.blit(glow_surface, (screen_pos[0] - 15, screen_pos[1] - 15))
        
        # 死亡动画效果
        if hasattr(agent, 'health') and agent.health <= 0:
            fade_alpha = max(0, 255 - (current_time % 1000) // 4)
            fade_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(fade_surface, (255, 0, 0, fade_alpha), (10, 10), 10)
            screen.blit(fade_surface, (screen_pos[0] - 10, screen_pos[1] - 10))
    
    def _apply_cached_render(self, screen: pygame.Surface, cached_surface: pygame.Surface, screen_pos: Tuple[int, int]):
        """应用缓存的渲染结果"""
        screen.blit(cached_surface, (screen_pos[0] - cached_surface.get_width() // 2, 
                                    screen_pos[1] - cached_surface.get_height() // 2))
    
    def cluster_nearby_agents(self, agents: List, camera: Camera, cluster_distance: float = 50) -> List:
        """聚类附近的智能体"""
        
        if not agents:
            return []
        
        clusters = []
        processed_agents = set()
        
        for agent in agents:
            if agent in processed_agents:
                continue
            
            # 创建新聚类
            cluster = [agent]
            processed_agents.add(agent)
            
            # 寻找附近的智能体
            for other_agent in agents:
                if other_agent in processed_agents:
                    continue
                
                distance = agent.position.distance_to(other_agent.position)
                if distance <= cluster_distance:
                    cluster.append(other_agent)
                    processed_agents.add(other_agent)
            
            clusters.append(cluster)
        
        return clusters
    
    def render_agent_cluster(self, screen: pygame.Surface, cluster: List, camera: Camera):
        """渲染智能体聚类"""
        
        if not cluster:
            return
        
        # 计算聚类中心
        center_x = sum(agent.position.x for agent in cluster) / len(cluster)
        center_y = sum(agent.position.y for agent in cluster) / len(cluster)
        center_pos = Vector2D(center_x, center_y)
        
        screen_pos = camera.world_to_screen(center_pos)
        screen_pos_tuple = (int(screen_pos.x), int(screen_pos.y))
        
        # 计算聚类大小
        cluster_radius = max(8, min(30, len(cluster) * 2))
        
        # 计算平均健康状态
        avg_energy = sum(getattr(agent, 'energy', 50) for agent in cluster) / len(cluster)
        avg_max_energy = sum(getattr(agent, 'max_energy', 100) for agent in cluster) / len(cluster)
        energy_ratio = avg_energy / avg_max_energy
        
        # 选择聚类颜色
        if energy_ratio > 0.7:
            cluster_color = (0, 255, 0)
        elif energy_ratio > 0.4:
            cluster_color = (255, 255, 0)
        else:
            cluster_color = (255, 0, 0)
        
        # 绘制聚类圆圈
        pygame.draw.circle(screen, cluster_color, screen_pos_tuple, cluster_radius)
        pygame.draw.circle(screen, (255, 255, 255), screen_pos_tuple, cluster_radius, 2)
        
        # 显示聚类数量
        font = pygame.font.Font(None, 24)
        count_text = font.render(str(len(cluster)), True, (255, 255, 255))
        text_rect = count_text.get_rect(center=screen_pos_tuple)
        screen.blit(count_text, text_rect)
    
    def get_performance_stats(self) -> Dict:
        """获取性能统计信息"""
        total_rendered = sum(self.performance_stats['lod_distribution'].values())
        
        return {
            'total_objects': self.performance_stats['total_objects'],
            'objects_rendered': total_rendered,
            'objects_culled': self.performance_stats['culled_objects'],
            'cached_renders': self.performance_stats['cached_renders'],
            'lod_distribution': self.performance_stats['lod_distribution'].copy(),
            'cull_ratio': self.performance_stats['culled_objects'] / max(self.performance_stats['total_objects'], 1)
        }
    
    def reset_performance_stats(self):
        """重置性能统计"""
        self.performance_stats = {
            'total_objects': 0,
            'culled_objects': 0,
            'cached_renders': 0,
            'lod_distribution': {level: 0 for level in ['full', 'high', 'medium', 'low', 'icon', 'cluster']}
        }