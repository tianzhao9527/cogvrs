#!/usr/bin/env python3
"""
优化的GUI界面
移除multi-scale系统，集成地形显示和右侧信息面板

Author: Ben Hsu & Claude
"""

import pygame
import numpy as np
import time
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging

from ..core import PhysicsEngine, World2D, TimeManager
from ..core.physics_engine import Vector2D
from ..agents import SimpleAgent
from ..environment import EnvironmentManager, WeatherSystem, TerrainSystem
from ..environment.terrain_system import TerrainType
from ..civilization.technology_system import TechnologyManager
from ..consciousness.consciousness_system import ConsciousnessManager  
from ..skills.skill_system import SkillManager
from ..civilization.tribe_formation import TribeFormationSystem
from ..integration.system_integration import SystemIntegration
from ..utils.event_logger import get_event_logger
from ..utils.system_reporter import SystemReporter

logger = logging.getLogger(__name__)

class RenderMode(Enum):
    """渲染模式"""
    TERRAIN_AGENTS = "terrain_agents"     # 地形+智能体
    TERRAIN_TRIBES = "terrain_tribes"     # 地形+部落
    PURE_TERRAIN = "pure_terrain"         # 纯地形
    SYSTEM_STATUS = "system_status"       # 系统状态

class OptimizedCogvrsGUI:
    """优化的Cogvrs主界面"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.running = True
        self.paused = False
        
        # 窗口配置
        self.window_width = config.get('window_width', 1600)
        self.window_height = config.get('window_height', 1000)
        
        # 布局配置
        self.info_panel_width = 400  # 右侧信息面板宽度
        self.world_view_width = self.window_width - self.info_panel_width
        self.world_view_height = self.window_height
        
        # 初始化pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Cogvrs - 认知宇宙模拟平台")
        
        # 创建子表面
        self.world_surface = pygame.Surface((self.world_view_width, self.world_view_height))
        self.info_surface = pygame.Surface((self.info_panel_width, self.world_view_height))
        
        # 字体配置 - 支持中文
        pygame.font.init()
        try:
            # 尝试加载系统中文字体
            import platform
            if platform.system() == "Darwin":  # macOS
                # 尝试多个中文字体路径
                chinese_fonts = [
                    "/System/Library/Fonts/STHeiti Light.ttc",
                    "/System/Library/Fonts/STHeiti Medium.ttc", 
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",
                    "/System/Library/Fonts/SFNS.ttf"
                ]
                
                font_loaded = False
                for font_path in chinese_fonts:
                    try:
                        self.font_large = pygame.font.Font(font_path, 24)
                        self.font_medium = pygame.font.Font(font_path, 20)
                        self.font_small = pygame.font.Font(font_path, 16)
                        font_loaded = True
                        break
                    except:
                        continue
                
                if not font_loaded:
                    raise Exception("No Chinese font found")
                    
            elif platform.system() == "Windows":
                self.font_large = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 24)
                self.font_medium = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 20)
                self.font_small = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 16)
            else:  # Linux
                self.font_large = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
                self.font_medium = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
                self.font_small = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            # 如果无法加载系统字体，使用默认字体
            self.font_large = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 20)
            self.font_small = pygame.font.Font(None, 16)
        
        # 渲染模式
        self.current_render_mode = RenderMode.TERRAIN_AGENTS
        
        # 颜色配置
        self.colors = {
            'background': (20, 25, 35),
            'panel_bg': (30, 35, 45),
            'text': (255, 255, 255),
            'accent': (0, 150, 255),
            'success': (0, 255, 0),
            'warning': (255, 255, 0),
            'error': (255, 100, 100),
            'terrain_ocean': (25, 50, 120),
            'terrain_river': (50, 120, 180),
            'terrain_mountain': (100, 80, 70),
            'terrain_hill': (120, 100, 80),
            'terrain_forest': (34, 80, 34),
            'terrain_grassland': (85, 120, 55),
            'terrain_desert': (194, 178, 128),
            'terrain_swamp': (80, 90, 60),
            'terrain_tundra': (150, 160, 170),
            'terrain_coast': (70, 130, 160),
        }
        
        # 地形颜色映射
        self.terrain_colors = {
            TerrainType.OCEAN: self.colors['terrain_ocean'],
            TerrainType.RIVER: self.colors['terrain_river'],
            TerrainType.MOUNTAIN: self.colors['terrain_mountain'],
            TerrainType.HILL: self.colors['terrain_hill'],
            TerrainType.FOREST: self.colors['terrain_forest'],
            TerrainType.GRASSLAND: self.colors['terrain_grassland'],
            TerrainType.DESERT: self.colors['terrain_desert'],
            TerrainType.SWAMP: self.colors['terrain_swamp'],
            TerrainType.TUNDRA: self.colors['terrain_tundra'],
            TerrainType.COAST: self.colors['terrain_coast'],
        }
        
        # 初始化核心系统
        self._initialize_core_systems()
        
        # 初始化智能体
        self._initialize_agents()
        
        # 渲染状态
        self.zoom_level = 1.0
        self.camera_x = 0
        self.camera_y = 0
        self.show_terrain_effects = True
        self.show_agent_trails = True
        self.show_tribal_territories = True
        
        # 统计信息
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        
        # 报告生成器
        self.reporter = SystemReporter()
        
        logger.info("优化GUI初始化完成")
    
    def _initialize_core_systems(self):
        """初始化核心系统"""
        # 物理引擎
        physics_config = self.config.get('physics', {})
        world_size = self.config.get('world', {}).get('size', (100, 100))
        physics_config['world_size'] = world_size
        self.physics_engine = PhysicsEngine(physics_config)
        
        # 地形系统
        self.terrain_system = TerrainSystem(world_size)
        self.terrain_system.initialize()
        
        # 科技管理器
        self.technology_manager = TechnologyManager()
        
        # 意识管理器
        self.consciousness_manager = ConsciousnessManager()
        
        # 技能管理器
        self.skill_manager = SkillManager()
        
        # 部落形成系统
        self.tribe_formation_system = TribeFormationSystem()
        
        # 系统集成
        self.system_integration = SystemIntegration(self.config)
        # 手动设置已初始化的系统
        self.system_integration.terrain_system = self.terrain_system
        self.system_integration.technology_manager = self.technology_manager
        self.system_integration.consciousness_manager = self.consciousness_manager
        self.system_integration.skill_manager = self.skill_manager
        
        # 计算缩放因子
        self.world_width = world_size[0]
        self.world_height = world_size[1]
        self.scale_x = self.world_view_width / self.world_width
        self.scale_y = self.world_view_height / self.world_height
        
        logger.info("核心系统初始化完成")
    
    def _initialize_agents(self):
        """初始化智能体"""
        self.agents = []
        world_config = self.config.get('world', {})
        initial_count = world_config.get('initial_agents', 20)
        
        for i in range(initial_count):
            position = Vector2D(
                np.random.uniform(10, self.world_width - 10),
                np.random.uniform(10, self.world_height - 10)
            )
            
            agent = SimpleAgent({}, position)
            agent.energy = np.random.uniform(80, 120)
            agent.health = np.random.uniform(90, 100)
            agent.position_history = [position]
            
            self.agents.append(agent)
        
        logger.info(f"创建了 {len(self.agents)} 个智能体")
    
    def run(self):
        """运行主循环"""
        clock = pygame.time.Clock()
        target_fps = self.config.get('time', {}).get('target_fps', 60)
        
        logger.info("开始运行优化GUI...")
        
        while self.running:
            dt = clock.tick(target_fps) / 1000.0
            
            # 处理事件
            self._handle_events()
            
            # 更新模拟
            if not self.paused:
                self._update_simulation(dt)
            
            # 渲染
            self._render_frame()
            
            # 更新FPS
            self._update_fps()
            
            pygame.display.flip()
    
    def _handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keyboard(event)
    
    def _handle_keyboard(self, event):
        """处理键盘输入"""
        if event.key == pygame.K_SPACE:
            self.paused = not self.paused
            logger.info(f"模拟{'暂停' if self.paused else '继续'}")
        
        elif event.key == pygame.K_ESCAPE:
            self.running = False
        
        elif event.key == pygame.K_m:
            # 切换渲染模式 - Toggle Render Mode
            modes = list(RenderMode)
            current_index = modes.index(self.current_render_mode)
            self.current_render_mode = modes[(current_index + 1) % len(modes)]
            logger.info(f"切换渲染模式: {self.current_render_mode.value}")
        
        elif event.key == pygame.K_t:
            self.show_terrain_effects = not self.show_terrain_effects
            logger.info(f"地形效果: {'开启' if self.show_terrain_effects else '关闭'}")
        
        elif event.key == pygame.K_r:
            self.show_agent_trails = not self.show_agent_trails
            logger.info(f"智能体轨迹: {'开启' if self.show_agent_trails else '关闭'}")
        
        elif event.key == pygame.K_b:
            self.show_tribal_territories = not self.show_tribal_territories
            logger.info(f"部落领土: {'开启' if self.show_tribal_territories else '关闭'}")
        
        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
            self.zoom_level = min(3.0, self.zoom_level * 1.2)
        
        elif event.key == pygame.K_MINUS:
            self.zoom_level = max(0.5, self.zoom_level / 1.2)
        
        elif event.key == pygame.K_s:
            # 生成并保存系统报告
            self._generate_system_report()
        
        elif event.key == pygame.K_p:
            # 打印系统状态到控制台
            self._print_system_summary()
    
    def _update_simulation(self, dt: float):
        """更新模拟"""
        # 更新智能体
        for agent in self.agents:
            if agent.alive:
                # 获取世界状态
                world_state = self._get_world_state()
                
                # 智能体决策和行动
                nearby_agents = self._get_nearby_agents(agent, 30.0)
                nearby_resources = self._get_nearby_resources(agent, 20.0)
                
                # 模拟智能体行为
                self._simulate_agent_behavior(agent, world_state, dt)
                
                # 更新系统状态
                self.system_integration.update_agent_systems(agent, world_state, dt)
                
                # 更新轨迹
                if hasattr(agent, 'position_history'):
                    agent.position_history.append(agent.position)
                    if len(agent.position_history) > 50:
                        agent.position_history.pop(0)
        
        # 更新部落系统
        self.tribe_formation_system.update_social_dynamics(self.agents, dt)
        
        # 更新其他系统
        self.technology_manager.update_research(dt)
        self.skill_manager.update_all_skills(dt)
        
        # 智能体生命周期
        self._update_agent_lifecycle(dt)
    
    def _simulate_agent_behavior(self, agent, world_state: Dict, dt: float):
        """模拟智能体基本行为"""
        # 随机移动
        if hasattr(agent, 'velocity'):
            # 应用地形影响
            terrain_effects = self.terrain_system.get_terrain_effects_at_position(agent.position)
            movement_modifier = terrain_effects.get('movement_speed', 1.0)
            
            # 随机方向变化
            if np.random.random() < 0.1:
                angle = np.random.uniform(0, 2 * np.pi)
                speed = np.random.uniform(0.5, 2.0) * movement_modifier
                agent.velocity = Vector2D(np.cos(angle) * speed, np.sin(angle) * speed)
            
            # 更新位置
            agent.position.x += agent.velocity.x * dt
            agent.position.y += agent.velocity.y * dt
            
            # 边界处理
            agent.position.x = max(0, min(self.world_width, agent.position.x))
            agent.position.y = max(0, min(self.world_height, agent.position.y))
        else:
            # 初始化速度
            agent.velocity = Vector2D(0, 0)
    
    def _get_world_state(self) -> Dict[str, Any]:
        """获取世界状态"""
        return {
            'terrain_system': self.terrain_system,
            'size': (self.world_width, self.world_height),
            'agent_count': len([a for a in self.agents if a.alive]),
            'tribes': self.tribe_formation_system.get_formation_visualization_data().get('social_groups', [])
        }
    
    def _get_nearby_agents(self, agent, radius: float) -> List:
        """获取附近智能体"""
        nearby = []
        for other in self.agents:
            if other != agent and other.alive:
                distance = agent.position.distance_to(other.position)
                if distance <= radius:
                    nearby.append(other)
        return nearby
    
    def _get_nearby_resources(self, agent, radius: float) -> List:
        """获取附近资源"""
        # 简化的资源系统
        terrain_effects = self.terrain_system.get_terrain_effects_at_position(agent.position)
        resource_modifier = terrain_effects.get('resource_modifier', 1.0)
        
        resources = []
        if resource_modifier > 1.0:
            for _ in range(int(resource_modifier)):
                resource_pos = Vector2D(
                    agent.position.x + np.random.uniform(-radius, radius),
                    agent.position.y + np.random.uniform(-radius, radius)
                )
                resource = type('Resource', (), {
                    'position': resource_pos,
                    'type': 'food',
                    'amount': np.random.uniform(10, 30)
                })()
                resources.append(resource)
        
        return resources
    
    def _update_agent_lifecycle(self, dt: float):
        """更新智能体生命周期"""
        for agent in self.agents:
            if not agent.alive:
                continue
            
            # 年龄增长
            if not hasattr(agent, 'age'):
                agent.age = 0
            agent.age += dt
            
            # 能量衰减
            agent.energy -= 0.1 * dt
            
            # 健康更新
            if agent.energy <= 0:
                agent.health -= 1.0 * dt
            elif agent.energy < 30:
                agent.health -= 0.1 * dt
            else:
                agent.health = min(100, agent.health + 0.05 * dt)
            
            # 死亡检查
            if agent.health <= 0 or agent.age > 500:
                agent.alive = False
    
    def _render_frame(self):
        """渲染一帧"""
        # 清空屏幕
        self.screen.fill(self.colors['background'])
        
        # 渲染世界视图
        self._render_world_view()
        
        # 渲染信息面板
        self._render_info_panel()
        
        # 绘制分界线
        pygame.draw.line(
            self.screen, 
            self.colors['accent'], 
            (self.world_view_width, 0), 
            (self.world_view_width, self.world_view_height), 
            2
        )
        
        # 绘制状态栏
        self._render_status_bar()
    
    def _render_world_view(self):
        """渲染世界视图"""
        self.world_surface.fill(self.colors['background'])
        
        if self.current_render_mode == RenderMode.PURE_TERRAIN:
            self._render_terrain_only()
        elif self.current_render_mode == RenderMode.TERRAIN_AGENTS:
            self._render_terrain_and_agents()
        elif self.current_render_mode == RenderMode.TERRAIN_TRIBES:
            self._render_terrain_and_tribes()
        elif self.current_render_mode == RenderMode.SYSTEM_STATUS:
            self._render_system_status()
        
        # 绘制到主屏幕
        self.screen.blit(self.world_surface, (0, 0))
    
    def _render_terrain_only(self):
        """渲染纯地形"""
        cell_width = max(1, int(self.scale_x * self.zoom_level))
        cell_height = max(1, int(self.scale_y * self.zoom_level))
        
        for x in range(self.world_width):
            for y in range(self.world_height):
                # 直接从地形系统获取地形特征
                terrain_feature = self.terrain_system.get_terrain_at(x, y)
                if terrain_feature:
                    terrain_type = terrain_feature.terrain_type
                else:
                    terrain_type = TerrainType.GRASSLAND
                
                color = self.terrain_colors.get(terrain_type, (100, 100, 100))
                
                screen_x = int(x * self.scale_x * self.zoom_level)
                screen_y = int(y * self.scale_y * self.zoom_level)
                
                if (screen_x >= -cell_width and screen_x < self.world_view_width and
                    screen_y >= -cell_height and screen_y < self.world_view_height):
                    
                    rect = pygame.Rect(screen_x, screen_y, cell_width, cell_height)
                    pygame.draw.rect(self.world_surface, color, rect)
                    
                    # 添加地形效果
                    if self.show_terrain_effects:
                        self._draw_terrain_effects(x, y, screen_x, screen_y, cell_width, cell_height)
    
    def _render_terrain_and_agents(self):
        """渲染地形和智能体"""
        # 先渲染地形
        self._render_terrain_only()
        
        # 渲染智能体轨迹
        if self.show_agent_trails:
            self._draw_agent_trails()
        
        # 渲染智能体
        self._draw_agents()
    
    def _render_terrain_and_tribes(self):
        """渲染地形和部落"""
        # 先渲染地形
        self._render_terrain_only()
        
        # 渲染部落领土
        if self.show_tribal_territories:
            self._draw_tribal_territories()
        
        # 渲染智能体（按部落着色）
        self._draw_agents_by_tribe()
    
    def _render_system_status(self):
        """渲染系统状态"""
        self.world_surface.fill((20, 20, 30))
        
        # 绘制系统状态图表
        y_offset = 20
        
        # 绘制标题
        title = self.font_large.render("系统状态概览", True, self.colors['text'])
        self.world_surface.blit(title, (20, y_offset))
        y_offset += 40
        
        # 绘制各系统状态
        systems_data = [
            ("地形系统", "运行正常", self.colors['success']),
            ("智能体系统", f"{len([a for a in self.agents if a.alive])}/{len(self.agents)} 活跃", self.colors['success']),
            ("科技系统", "研发中", self.colors['warning']),
            ("意识系统", "发展中", self.colors['warning']),
            ("技能系统", "活跃", self.colors['success']),
            ("部落系统", f"{len(self.tribe_formation_system.social_groups)} 群体", self.colors['success']),
        ]
        
        for system_name, status, color in systems_data:
            text = self.font_medium.render(f"{system_name}: {status}", True, color)
            self.world_surface.blit(text, (20, y_offset))
            y_offset += 25
    
    def _draw_terrain_effects(self, world_x: int, world_y: int, screen_x: int, screen_y: int, width: int, height: int):
        """绘制地形效果"""
        # 获取地形特征
        terrain_feature = self.terrain_system.get_terrain_at(world_x, world_y)
        if not terrain_feature:
            return
        
        # 高资源区域
        resource_values = list(terrain_feature.resource_modifier.values()) if terrain_feature.resource_modifier else [1.0]
        avg_resource = np.mean(resource_values)
        if avg_resource > 1.2:
            effect_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            effect_surface.fill((255, 255, 100, 50))
            self.world_surface.blit(effect_surface, (screen_x, screen_y))
        
        # 移动困难区域
        if terrain_feature.movement_cost > 1.5:
            effect_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            effect_surface.fill((255, 100, 100, 30))
            self.world_surface.blit(effect_surface, (screen_x, screen_y))
        
        # 通信障碍区域
        if terrain_feature.communication_barrier > 0.5:
            pygame.draw.rect(self.world_surface, (255, 0, 0), 
                           pygame.Rect(screen_x, screen_y, width, height), 1)
    
    def _draw_agent_trails(self):
        """绘制智能体轨迹"""
        for agent in self.agents:
            if not hasattr(agent, 'position_history') or len(agent.position_history) < 2:
                continue
            
            points = []
            for pos in agent.position_history[-20:]:
                screen_x = int(pos.x * self.scale_x * self.zoom_level)
                screen_y = int(pos.y * self.scale_y * self.zoom_level)
                points.append((screen_x, screen_y))
            
            if len(points) >= 2:
                pygame.draw.lines(self.world_surface, (100, 100, 100), False, points, 1)
    
    def _draw_agents(self):
        """绘制智能体"""
        for agent in self.agents:
            if not agent.alive:
                continue
            
            screen_x = int(agent.position.x * self.scale_x * self.zoom_level)
            screen_y = int(agent.position.y * self.scale_y * self.zoom_level)
            
            # 基础颜色
            color = (255, 255, 255)
            
            # 根据健康状态调整颜色
            if hasattr(agent, 'health'):
                health_ratio = agent.health / 100.0
                if health_ratio < 0.3:
                    color = (255, 100, 100)  # 红色 - 低健康
                elif health_ratio < 0.7:
                    color = (255, 255, 100)  # 黄色 - 中等健康
                else:
                    color = (100, 255, 100)  # 绿色 - 高健康
            
            # 绘制智能体
            radius = max(2, int(4 * self.zoom_level))
            pygame.draw.circle(self.world_surface, color, (screen_x, screen_y), radius)
            pygame.draw.circle(self.world_surface, (255, 255, 255), (screen_x, screen_y), radius, 1)
    
    def _draw_agents_by_tribe(self):
        """按部落绘制智能体"""
        tribe_colors = [
            (255, 100, 100), (100, 255, 100), (100, 100, 255),
            (255, 255, 100), (255, 100, 255), (100, 255, 255),
            (255, 150, 100), (150, 255, 100), (100, 150, 255)
        ]
        
        for agent in self.agents:
            if not agent.alive:
                continue
            
            screen_x = int(agent.position.x * self.scale_x * self.zoom_level)
            screen_y = int(agent.position.y * self.scale_y * self.zoom_level)
            
            # 获取部落颜色
            color = (255, 255, 255)  # 默认颜色
            if hasattr(agent, 'tribe_id') and agent.tribe_id is not None:
                tribe_index = hash(agent.tribe_id) % len(tribe_colors)
                color = tribe_colors[tribe_index]
            
            radius = max(2, int(4 * self.zoom_level))
            pygame.draw.circle(self.world_surface, color, (screen_x, screen_y), radius)
            pygame.draw.circle(self.world_surface, (255, 255, 255), (screen_x, screen_y), radius, 1)
    
    def _draw_tribal_territories(self):
        """绘制部落领土"""
        tribes = self.tribe_formation_system.get_formation_visualization_data().get('social_groups', [])
        
        tribe_colors = [
            (255, 100, 100, 50), (100, 255, 100, 50), (100, 100, 255, 50),
            (255, 255, 100, 50), (255, 100, 255, 50), (100, 255, 255, 50)
        ]
        
        for i, tribe in enumerate(tribes):
            if hasattr(tribe, 'territory_center') and hasattr(tribe, 'territory_radius'):
                center_x = int(tribe.territory_center[0] * self.scale_x * self.zoom_level)
                center_y = int(tribe.territory_center[1] * self.scale_y * self.zoom_level)
                radius = int(tribe.territory_radius * self.scale_x * self.zoom_level)
                
                color = tribe_colors[i % len(tribe_colors)]
                
                # 绘制领土范围
                territory_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(territory_surface, color, (radius, radius), radius)
                self.world_surface.blit(territory_surface, (center_x - radius, center_y - radius))
                
                # 绘制边界
                pygame.draw.circle(self.world_surface, color[:3], (center_x, center_y), radius, 2)
    
    def _render_info_panel(self):
        """渲染右侧信息面板"""
        self.info_surface.fill(self.colors['panel_bg'])
        
        y_offset = 10
        
        # 标题
        title = self.font_large.render("系统状态", True, self.colors['text'])
        self.info_surface.blit(title, (10, y_offset))
        y_offset += 40
        
        # 模拟统计
        stats_text = [
            f"模拟时间: {time.time() - getattr(self, 'start_time', time.time()):.1f}s",
            f"活跃智能体: {len([a for a in self.agents if a.alive])}/{len(self.agents)}",
            f"部落数量: {len(self.tribe_formation_system.social_groups)}",
            f"FPS: {self.fps:.1f}",
            f"缩放: {self.zoom_level:.1f}x",
        ]
        
        for text in stats_text:
            rendered = self.font_small.render(text, True, self.colors['text'])
            self.info_surface.blit(rendered, (10, y_offset))
            y_offset += 20
        
        y_offset += 20
        
        # 科技发展
        tech_title = self.font_medium.render("科技发展", True, self.colors['accent'])
        self.info_surface.blit(tech_title, (10, y_offset))
        y_offset += 25
        
        tech_report = self.technology_manager.get_system_stats()
        tech_texts = [
            f"总研究点: {tech_report.get('total_research_points', 0):.0f}",
            f"已解锁科技: {tech_report.get('technologies_researched', 0)}",
            f"研发中科技: {tech_report.get('active_research_projects', 0)}",
        ]
        
        for text in tech_texts:
            rendered = self.font_small.render(text, True, self.colors['text'])
            self.info_surface.blit(rendered, (10, y_offset))
            y_offset += 18
        
        y_offset += 20
        
        # 意识发展
        consciousness_title = self.font_medium.render("意识发展", True, self.colors['accent'])
        self.info_surface.blit(consciousness_title, (10, y_offset))
        y_offset += 25
        
        consciousness_report = self.consciousness_manager.get_collective_consciousness_report()
        consciousness_texts = [
            f"智能体总数: {consciousness_report.get('total_agents', 0)}",
            f"最高等级: {consciousness_report.get('highest_level', 'N/A')}",
            f"平均意识: {consciousness_report.get('average_consciousness', 0):.2f}",
        ]
        
        for text in consciousness_texts:
            rendered = self.font_small.render(text, True, self.colors['text'])
            self.info_surface.blit(rendered, (10, y_offset))
            y_offset += 18
        
        y_offset += 20
        
        # 技能发展
        skill_title = self.font_medium.render("技能发展", True, self.colors['accent'])
        self.info_surface.blit(skill_title, (10, y_offset))
        y_offset += 25
        
        skill_report = self.skill_manager.get_skill_distribution_report()
        skill_texts = [
            f"个体数量: {skill_report.get('total_individuals', 0)}",
            f"部落数量: {skill_report.get('total_tribes', 0)}",
        ]
        
        for text in skill_texts:
            rendered = self.font_small.render(text, True, self.colors['text'])
            self.info_surface.blit(rendered, (10, y_offset))
            y_offset += 18
        
        y_offset += 20
        
        # 地形信息
        terrain_title = self.font_medium.render("地形效果", True, self.colors['accent'])
        self.info_surface.blit(terrain_title, (10, y_offset))
        y_offset += 25
        
        terrain_legend = [
            ("海洋", self.colors['terrain_ocean']),
            ("河流", self.colors['terrain_river']),
            ("山脉", self.colors['terrain_mountain']),
            ("森林", self.colors['terrain_forest']),
            ("草原", self.colors['terrain_grassland']),
            ("沙漠", self.colors['terrain_desert']),
        ]
        
        for name, color in terrain_legend:
            # 绘制颜色块
            pygame.draw.rect(self.info_surface, color, (10, y_offset, 15, 15))
            
            # 绘制名称
            text = self.font_small.render(name, True, self.colors['text'])
            self.info_surface.blit(text, (30, y_offset))
            y_offset += 20
        
        # 绘制信息面板到主屏幕
        self.screen.blit(self.info_surface, (self.world_view_width, 0))
    
    def _render_status_bar(self):
        """渲染状态栏"""
        # 底部状态栏
        status_text = f"渲染模式: {self.current_render_mode.value} | "
        status_text += f"{'暂停' if self.paused else '运行'} | "
        status_text += "M:切换模式 T:地形效果 R:轨迹 B:部落领土 S:保存报告 P:打印报告 空格:暂停"
        
        status_surface = self.font_small.render(status_text, True, self.colors['text'])
        status_bg = pygame.Rect(0, self.window_height - 25, self.window_width, 25)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), status_bg)
        self.screen.blit(status_surface, (10, self.window_height - 20))
    
    def _update_fps(self):
        """更新FPS"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def _generate_system_report(self):
        """生成并保存系统报告"""
        try:
            # 创建模拟状态对象
            simulation_state = type('SimulationState', (), {
                'current_step': getattr(self, 'current_step', 0),
                'simulation_time': time.time() - self.reporter.start_time,
                'fps': self.fps,
                'target_fps': 60,
                'paused': self.paused
            })()
            
            # 生成综合报告
            report = self.reporter.generate_comprehensive_report(
                terrain_system=self.terrain_system,
                technology_manager=self.technology_manager,
                consciousness_manager=self.consciousness_manager,
                skill_manager=self.skill_manager,
                tribe_formation_system=self.tribe_formation_system,
                agents=self.agents,
                simulation_state=simulation_state
            )
            
            # 保存报告
            filename = self.reporter.save_report_to_file(report)
            if filename:
                print(f"✅ 系统报告已保存到: {filename}")
                logger.info(f"系统报告已保存到: {filename}")
            else:
                print("❌ 报告保存失败")
                logger.error("报告保存失败")
                
        except Exception as e:
            print(f"❌ 生成报告时出错: {e}")
            logger.error(f"生成报告时出错: {e}")
    
    def _print_system_summary(self):
        """打印系统摘要到控制台"""
        try:
            # 创建模拟状态对象
            simulation_state = type('SimulationState', (), {
                'current_step': getattr(self, 'current_step', 0),
                'simulation_time': time.time() - self.reporter.start_time,
                'fps': self.fps,
                'target_fps': 60,
                'paused': self.paused
            })()
            
            # 生成综合报告
            report = self.reporter.generate_comprehensive_report(
                terrain_system=self.terrain_system,
                technology_manager=self.technology_manager,
                consciousness_manager=self.consciousness_manager,
                skill_manager=self.skill_manager,
                tribe_formation_system=self.tribe_formation_system,
                agents=self.agents,
                simulation_state=simulation_state
            )
            
            # 打印报告摘要
            self.reporter.print_summary_report(report)
            
        except Exception as e:
            print(f"❌ 打印报告时出错: {e}")
            logger.error(f"打印报告时出错: {e}")

# 主函数
def main():
    """测试优化GUI"""
    config = {
        'window_width': 1600,
        'window_height': 1000,
        'world': {'size': (100, 100), 'initial_agents': 30},
        'physics': {},
        'terrain': {},
        'time': {'target_fps': 60}
    }
    
    gui = OptimizedCogvrsGUI(config)
    gui.start_time = time.time()
    gui.run()

if __name__ == "__main__":
    main()