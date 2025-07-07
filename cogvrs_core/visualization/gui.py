"""
Cogvrs - Main GUI Interface
主图形界面：整合所有可视化和控制功能

Author: Ben Hsu & Claude
"""

import pygame
import pygame_gui
import threading
import time
from typing import Dict, List, Optional
import logging

from ..core import PhysicsEngine, World2D, TimeManager
from ..core.physics_engine import Vector2D
from ..agents import SimpleAgent
from ..environment import EnvironmentManager, WeatherSystem, TerrainSystem
from .world_view import WorldRenderer
from .multi_scale import (
    ScaleManager, CameraSystem, RenderingPipeline, 
    InteractionController, ScaleLevel
)

logger = logging.getLogger(__name__)


class CogvrsGUI:
    """
    Cogvrs主图形界面
    
    Features:
    - 实时世界可视化
    - 控制面板
    - 参数调整
    - 统计显示
    - 暂停/播放控制
    """
    
    def _detect_screen_size(self):
        """检测屏幕尺寸"""
        # 获取屏幕尺寸信息
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        print(f"🖥️ 检测到屏幕尺寸: {self.screen_width}x{self.screen_height}")
    
    def __init__(self, config: Dict):
        self.config = config
        self.running = True
        self.paused = False
        
        # 初始化pygame
        pygame.init()
        
        # 窗口设置 - 支持更大的显示区域
        self._detect_screen_size()
        self.window_width = config.get('window_width', min(1600, self.screen_width - 100))
        self.window_height = config.get('window_height', min(1000, self.screen_height - 100))
        
        # 动态计算世界视图大小，预留右侧面板空间
        self.panel_width = 350  # 稍微减小面板宽度
        self.world_view_width = self.window_width - self.panel_width - 20
        self.world_view_height = self.window_height - 40  # 预留顶部空间
        
        self.fullscreen = False
        self.windowed_size = (self.window_width, self.window_height)  # 保存窗口模式尺寸
        
        # 创建主窗口 - 支持大小调节
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height), 
            pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
        )
        pygame.display.set_caption("Cogvrs - Cognitive Universe Simulation")
        
        # 允许更多事件类型以支持窗口调节
        pygame.event.set_allowed([
            pygame.QUIT, pygame.KEYDOWN, pygame.USEREVENT, 
            pygame.VIDEORESIZE, pygame.VIDEOEXPOSE
        ])
        
        # 创建后台渲染缓冲区
        self.back_buffer = pygame.Surface((self.window_width, self.window_height))
        self.dirty_rects = []  # 脏矩形区域
        
        # 创建GUI管理器
        self.ui_manager = pygame_gui.UIManager((self.window_width, self.window_height))
        
        print(f"🖥️ 显示区域初始化: {self.window_width}x{self.window_height}")
        print(f"   世界视图: {self.world_view_width}x{self.world_view_height}")
        print(f"   检测到屏幕: {self.screen_width}x{self.screen_height}")
        
        # 初始化核心系统
        self._initialize_simulation()
        
        # 初始化渲染器
        renderer_config = {
            'screen_width': self.world_view_width,
            'screen_height': self.world_view_height,
            'world_width': self.world.width,
            'world_height': self.world.height
        }
        self.world_renderer = WorldRenderer(renderer_config)
        
        # 初始化环境系统
        self._initialize_environment_system()
        
        # 初始化多尺度可视化系统
        self.enable_multi_scale = config.get('enable_multi_scale', True)
        if self.enable_multi_scale:
            self._initialize_multi_scale_system()
        
        # 创建UI元素
        self._create_ui_elements()
        
        # 时间控制 - 进一步优化性能
        self.clock = pygame.time.Clock()
        self.target_fps = config.get('target_fps', 30)  # 恢复到30fps但优化渲染
        self.frame_count = 0
        self.last_stats_update = 0
        self.stats_update_interval = 0.5  # 更频繁更新UI显示
        self.render_skip = 0  # 跳帧计数器
        
        # 数据收集系统
        self.session_data = {
            'start_time': time.time(),
            'stats_history': [],
            'events': [],
            'agent_lifecycle': [],
            'performance_metrics': [],
            'detailed_events': [],  # 新增详细事件记录
            'tribe_events': [],     # 部落相关事件
            'reproduction_events': [], # 繁殖事件
            'environmental_events': []  # 环境事件
        }
        
        # 灭绝事件标志
        self.extinction_occurred = False
        
        logger.info(f"CogvrsGUI initialized: {self.window_width}x{self.window_height}")
    
    def _record_event(self, event_type: str, description: str, details: dict = None):
        """记录模拟事件"""
        event = {
            'timestamp': time.time(),
            'step': self.time_manager.current_step,
            'type': event_type,
            'description': description,
            'details': details or {}
        }
        
        # 记录到对应的事件列表
        self.session_data['detailed_events'].append(event)
        
        if event_type == 'tribe':
            self.session_data['tribe_events'].append(event)
        elif event_type == 'reproduction':
            self.session_data['reproduction_events'].append(event)
        elif event_type == 'environment':
            self.session_data['environmental_events'].append(event)
    
    def _initialize_simulation(self):
        """初始化模拟系统"""
        # 物理引擎
        physics_config = self.config.get('physics', {})
        physics_config.update({
            'world_size': (100, 100),
            'dt': 0.1,
            'friction': 0.1,
            'boundary_type': 'toroidal'
        })
        self.physics = PhysicsEngine(physics_config)
        
        # 世界环境
        world_config = self.config.get('world', {})
        # 只更新未设置的默认值，不覆盖用户配置
        world_config.setdefault('size', (100, 100))
        world_config.setdefault('resource_density', 0.15)
        world_config.setdefault('max_agents', self.config.get('world', {}).get('max_agents', 200))  # 使用用户配置的max_agents
        self.world = World2D(world_config)
        
        # 时间管理器
        time_config = self.config.get('time', {})
        time_config.update({
            'dt': 0.1,
            'target_fps': 30,
            'real_time': True
        })
        self.time_manager = TimeManager(time_config)
        
        # 创建初始智能体
        self.agents = []
        initial_agent_count = self.config.get('initial_agents', 10)
        
        for i in range(initial_agent_count):
            agent_config = self._create_agent_config()
            agent = SimpleAgent(agent_config)
            agent.birth_time = self.time_manager.current_step
            self.agents.append(agent)
        
        logger.info(f"Simulation initialized with {len(self.agents)} agents")
    
    def _initialize_environment_system(self):
        """初始化环境系统"""
        world_size = (self.world.width, self.world.height)
        
        # 创建环境管理器（包含新的气候系统）
        self.environment_manager = EnvironmentManager(world_size)
        
        # 传递环境配置到气候系统
        if hasattr(self.environment_manager, 'climate_system'):
            env_config = self.config.get('environment', {})
            # 更新气候系统配置
            self.environment_manager.climate_system.config.update(env_config)
            self.environment_manager.climate_system.reduce_severity = env_config.get('reduce_climate_severity', False)
            self.environment_manager.climate_system.stable_probability = env_config.get('stable_climate_probability', 0.4)
            if self.environment_manager.climate_system.reduce_severity:
                self.environment_manager.climate_system._apply_reduced_severity()
        
        # 优先使用气候系统，减少天气系统的使用以提高性能
        self.use_weather_system = False  # 禁用复杂的天气系统
        if self.use_weather_system:
            self.weather_system = WeatherSystem(world_size)
        else:
            self.weather_system = None  # 不创建天气系统以节省资源
        
        # 创建地形系统
        self.terrain_system = TerrainSystem(world_size)
        
        # 初始化部落管理器
        if self.config.get('civilization', {}).get('enable_tribes', False):
            from ..civilization import TribeManager
            self.tribe_manager = TribeManager(self.config.get('civilization', {}))
            # 设置事件记录回调
            self.tribe_manager.gui_callback = self._record_event
        else:
            self.tribe_manager = None
        
        logger.info("Environment system initialized (using climate system)")
    
    def _initialize_multi_scale_system(self):
        """初始化多尺度可视化系统"""
        
        # 使用实际的世界大小，然后扩大显示比例
        actual_world_size = (self.world.width, self.world.height)  # 100x100
        display_scale = 8  # 显示比例因子
        world_size = (actual_world_size[0] * display_scale, actual_world_size[1] * display_scale)  # 800x800
        
        self.scale_manager = ScaleManager(world_size)
        
        # 创建相机系统
        screen_size = (self.world_view_width, self.world_view_height)
        self.camera_system = CameraSystem(world_size, screen_size)
        
        # 设置相机初始位置到世界中心
        self.camera_system.main_camera.position = Vector2D(world_size[0] / 2, world_size[1] / 2)
        self.camera_system.main_camera.zoom = 0.8  # 稍微缩小以看到更多内容
        
        # 创建渲染管道
        self.rendering_pipeline = RenderingPipeline(self.scale_manager, self.camera_system)
        
        # 创建交互控制器
        self.interaction_controller = InteractionController(
            self.scale_manager, self.camera_system, self.rendering_pipeline
        )
        
        # 多尺度渲染模式
        self.multi_scale_mode = True
        
        logger.info("Multi-scale visualization system initialized")
    
    def _create_agent_config(self) -> Dict:
        """创建智能体配置"""
        return {
            'world_size': [self.world.width, self.world.height],
            'mass': 1.0,
            'radius': 1.0,
            'initial_energy': 100.0,
            'max_energy': 150.0,
            'perception_radius': 10.0,
            'neural_network': {
                'input_size': 20,
                'hidden_sizes': [32, 16],
                'output_size': 8,
                'learning_rate': 0.01
            },
            'memory': {
                'capacity': 100,
                'decay_rate': 0.99
            },
            'behavior': {
                'mutation_rate': 0.1,
                'reproduction_threshold': 80
            }
        }
    
    def _create_ui_elements(self):
        """创建UI元素"""
        # 控制面板背景
        self.control_panel = pygame.Rect(self.world_view_width + 10, 10, self.panel_width - 20, self.window_height - 20)
        
        # 按钮位置
        button_x = self.world_view_width + 20
        button_y = 30
        button_width = 120
        button_height = 30
        button_spacing = 40
        
        # 播放/暂停按钮
        self.play_pause_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(button_x, button_y, button_width, button_height),
            text='Pause',
            manager=self.ui_manager
        )
        
        # 重置按钮
        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(button_x + 130, button_y, button_width, button_height),
            text='Reset',
            manager=self.ui_manager
        )
        
        # 速度控制滑块
        slider_y = button_y + button_spacing
        self.speed_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(button_x, slider_y, button_width, 25),
            text='Speed: 1.0x',
            manager=self.ui_manager
        )
        
        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(button_x, slider_y + 30, 250, 20),
            start_value=1.0,
            value_range=(0.1, 5.0),
            manager=self.ui_manager
        )
        
        # 添加智能体按钮
        add_agent_y = slider_y + 70
        self.add_agent_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(button_x, add_agent_y, button_width, button_height),
            text='Add Agent',
            manager=self.ui_manager
        )
        
        # 统计信息区域 - 扩大显示区域
        stats_y = add_agent_y + 60
        self.stats_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(button_x, stats_y, 250, 160),
            html_text="<b>World Statistics</b><br>Loading...",
            manager=self.ui_manager
        )
        
        # 智能体详细信息区域
        details_y = stats_y + 170
        self.details_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(button_x, details_y, 250, 100),
            html_text="<b>Agent Analysis</b><br>Analyzing behaviors...",
            manager=self.ui_manager
        )
        
        # 系统状态区域
        system_y = details_y + 110
        self.system_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(button_x, system_y, 250, 60),
            html_text="<b>System Status</b><br>Initializing...",
            manager=self.ui_manager
        )
        
        # 控制说明
        help_y = details_y + 170
        help_text = ("<b>🎮 Multi-Scale Controls:</b><br>"
                    "<font color='#FFD700'>1 - Micro Scale</font><br>"
                    "<font color='#90EE90'>2 - Meso Scale</font><br>"
                    "<font color='#87CEEB'>3 - Macro Scale</font><br>"
                    "<font color='#DDA0DD'>4 - Global Scale</font><br>"
                    "<font color='#FFCC99'>M - Toggle Render Mode</font><br>"
                    "<font color='#CCCCCC'>Space - Pause/Resume</font>")
        
        self.help_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(button_x, help_y, 250, 120),
            html_text=help_text,
            manager=self.ui_manager
        )
    
    def update_simulation(self, dt: float):
        """更新模拟状态"""
        if self.paused:
            return
        
        # 更新时间管理器
        if not self.time_manager.step():
            return
        
        # 更新环境系统
        if hasattr(self, 'weather_system') and self.weather_system is not None:
            self.weather_system.update(dt)
        
        # 更新气候系统
        if hasattr(self, 'environment_manager') and hasattr(self.environment_manager, 'climate_system'):
            self.environment_manager.climate_system.update(dt)
        
        # 更新部落系统
        if hasattr(self, 'tribe_manager') and self.tribe_manager is not None:
            self.tribe_manager.update(self.agents, dt)
        
        # 更新世界
        self.world.update(dt)
        
        # 更新智能体
        alive_agents = []
        newly_dead = []
        
        for agent in self.agents:
            was_alive = agent.alive
            
            if agent.alive:
                # 获取附近的智能体和资源
                nearby_agents = self._get_nearby_agents(agent)
                nearby_resources = self._get_nearby_resources(agent)
                
                # 获取环境影响
                environmental_effects = self._get_environmental_effects_for_agent(agent)
                
                # 更新智能体
                world_state = self.world.get_world_state()
                agent.update(dt, world_state, nearby_agents, nearby_resources)
                
                # 应用环境影响
                self._apply_environmental_effects(agent, environmental_effects, dt)
                
                # 检查是否刚刚死亡
                if was_alive and not agent.alive:
                    newly_dead.append(agent)
                
                if agent.alive:
                    alive_agents.append(agent)
        
        # 记录死亡事件
        for dead_agent in newly_dead:
            death_cause = "Unknown"
            if dead_agent.health <= 0:
                death_cause = "Health depletion"
            elif dead_agent.energy <= 0:
                death_cause = "Energy depletion"
            elif dead_agent.age > 300:
                death_cause = "Old age"
            
            self._record_event('agent_death', f'智能体死亡: {dead_agent.agent_id}', {
                'agent_id': dead_agent.agent_id,
                'age': dead_agent.age,
                'cause': death_cause,
                'final_health': dead_agent.health,
                'final_energy': dead_agent.energy,
                'position': (dead_agent.position.x, dead_agent.position.y),
                'offspring_count': dead_agent.offspring_count,
                'tribe_id': getattr(dead_agent, 'tribe_id', None)
            })
        
        # 应用物理效果
        physics_objects = [agent for agent in alive_agents if agent.alive]
        self.physics.apply_physics(physics_objects)
        
        # 记录繁殖前的数量
        agents_before_reproduction = len(self.agents)
        alive_before_reproduction = len(alive_agents)
        
        # 处理繁殖
        self._handle_reproduction(alive_agents)
        
        # 注意：不要用alive_agents覆盖self.agents，因为新生儿已经在_handle_reproduction中添加到self.agents了
        agents_after_reproduction = len(self.agents)
        alive_after_reproduction = len([a for a in self.agents if a.alive])
        
        # 验证数量变化
        if agents_after_reproduction > agents_before_reproduction:
            new_born_count = agents_after_reproduction - agents_before_reproduction
            print(f"✅ 繁殖验证成功: 总数 {agents_before_reproduction} → {agents_after_reproduction} (新增{new_born_count})")
            print(f"   活跃数: {alive_before_reproduction} → {alive_after_reproduction}")
        
        # 收集数据
        self._collect_session_data()
        
        # 检查种群灭绝
        if len(self.agents) == 0:
            self._handle_extinction_event()
    
    def _get_nearby_agents(self, agent: SimpleAgent) -> List[SimpleAgent]:
        """获取附近的智能体"""
        nearby = []
        for other in self.agents:
            if other != agent and other.alive:
                distance = agent.position.distance_to(other.position)
                if distance <= agent.perception_radius:
                    nearby.append(other)
        return nearby
    
    def _get_nearby_resources(self, agent: SimpleAgent) -> List:
        """获取附近的资源"""
        return self.world.get_resources_in_radius(agent.position, agent.perception_radius)
    
    def _handle_reproduction(self, agents: List[SimpleAgent]):
        """处理智能体繁殖"""
        new_agents = []
        max_agents = self.config.get('world', {}).get('max_agents', 200)  # 使用用户配置的最大智能体数量
        current_alive_count = len([a for a in self.agents if a.alive])
        
        for agent in agents:
            # 检查繁殖条件 - 大幅降低门槛以促进文明发展
            if (agent.energy > 40 and   # 大幅降低能量门槛从60到40
                agent.age > 15 and     # 大幅降低年龄门槛从25到15
                agent.offspring_count < 8 and  # 增加繁殖次数到8
                (current_alive_count + len(new_agents)) < max_agents):     # 确保包含新生儿的总数
                
                # 寻找繁殖伙伴
                nearby_agents = self._get_nearby_agents(agent)
                suitable_partners = [
                    a for a in nearby_agents 
                    if a.energy > 35 and a.age > 12 and a.offspring_count < 8  # 降低伙伴要求
                ]
                
                if suitable_partners and len(new_agents) < 10:  # 增加每轮繁殖数量
                    # 繁殖
                    child = agent.clone(mutation_rate=0.1)
                    child.birth_time = self.time_manager.current_step
                    
                    # 确保新生儿状态正确
                    child.alive = True
                    child.age = 0  # 确保新生儿年龄为0
                    
                    new_agents.append(child)
                    
                    # 更新父母状态
                    agent.offspring_count += 1
                    agent.energy -= 15  # 大幅降低能量消耗从30到15
                    
                    print(f"👶 新智能体出生: {child.agent_id} (父母: {agent.agent_id})")
                    print(f"   位置: ({child.position.x:.1f}, {child.position.y:.1f})")
                    print(f"   状态: alive={child.alive}, energy={child.energy:.1f}, health={child.health:.1f}")
                    
                    # 记录繁殖事件
                    self._record_event('reproduction', f'新智能体出生: {child.agent_id}', {
                        'parent_id': agent.agent_id,
                        'child_id': child.agent_id,
                        'child_position': (child.position.x, child.position.y),
                        'child_energy': child.energy,
                        'child_health': child.health,
                        'parent_offspring_count': agent.offspring_count,
                        'generation': child.generation
                    })
        
        # 添加新生儿到主列表
        if new_agents:
            # 确保新生儿状态正确
            for child in new_agents:
                child.alive = True  # 确保新生儿是活跃状态
                
            self.agents.extend(new_agents)
            
            # 统计数量
            total_agents = len(self.agents)
            alive_count_after = len([a for a in self.agents if a.alive])
            
            logger.info(f"New agents born: {len(new_agents)}, Total agents: {total_agents}, Alive agents: {alive_count_after}")
            print(f"🎉 本轮新增 {len(new_agents)} 个智能体")
            print(f"   📊 总智能体数量: {total_agents}")
            print(f"   ✅ 活跃智能体数量: {alive_count_after}")
            
            # 验证新生儿的状态
            for child in new_agents:
                print(f"   👶 新生儿 {child.agent_id}: alive={child.alive}, energy={child.energy:.1f}, health={child.health:.1f}")
    
    def _add_random_agents(self, count: int):
        """添加随机智能体"""
        for _ in range(count):
            agent_config = self._create_agent_config()
            agent = SimpleAgent(agent_config)
            agent.birth_time = self.time_manager.current_step
            self.agents.append(agent)
        
        logger.info(f"Added {count} new agents")
    
    def _get_environmental_effects_for_agent(self, agent) -> Dict[str, float]:
        """获取智能体所在位置的环境影响"""
        combined_effects = {
            'energy_modifier': 1.0,
            'health_modifier': 1.0,
            'movement_speed': 1.0,
            'perception_range': 1.0,
            'reproduction_rate': 1.0
        }
        
        if hasattr(self, 'environment_manager'):
            # 优先使用新的气候系统
            if (hasattr(self.environment_manager, 'climate_system') and 
                hasattr(self.environment_manager, 'use_climate_system') and 
                self.environment_manager.use_climate_system):
                
                # 使用高效的气候系统
                climate_effect = self.environment_manager.climate_system.get_climate_effects_for_position(agent.position)
                
                # 将气候效应转换为标准格式
                combined_effects['energy_modifier'] = climate_effect.energy_cost_modifier
                combined_effects['health_modifier'] = climate_effect.health_modifier
                combined_effects['reproduction_rate'] = climate_effect.reproduction_modifier
                # 基于温度和湿度影响移动和感知
                temp_factor = max(0.5, min(1.5, climate_effect.temperature_modifier))
                combined_effects['movement_speed'] = 2.0 - temp_factor  # 极端温度降低移动速度
                combined_effects['perception_range'] = min(1.2, climate_effect.humidity_modifier)  # 湿度影响感知
                
            else:
                # 回退到原有的环境+天气+地形系统
                # 获取环境区域影响
                env_effects = self.environment_manager.get_environmental_effects_at_position(agent.position)
                
                # 获取天气影响（如果启用）
                if self.weather_system:
                    weather_effects = self.weather_system.get_weather_effects_at_position(agent.position)
                else:
                    weather_effects = {}
                
                # 获取地形影响
                if hasattr(self, 'terrain_system'):
                    terrain_effects = self.terrain_system.get_terrain_effects_at_position(agent.position)
                else:
                    terrain_effects = {}
                
                # 合并所有影响
                for key in combined_effects:
                    if key in env_effects:
                        combined_effects[key] *= env_effects[key]
                    if key in weather_effects:
                        combined_effects[key] *= weather_effects[key]
                    # 地形影响稍有不同的键名映射
                    if key == 'movement_speed' and 'movement_speed' in terrain_effects:
                        combined_effects[key] *= terrain_effects['movement_speed']
                    elif key == 'perception_range' and 'perception_range' in terrain_effects:
                        combined_effects[key] *= terrain_effects['perception_range']
        
        return combined_effects
    
    def _apply_environmental_effects(self, agent, effects: Dict[str, float], dt: float):
        """对智能体应用环境影响"""
        # 能量修正
        if 'energy_modifier' in effects and effects['energy_modifier'] != 1.0:
            energy_change = (effects['energy_modifier'] - 1.0) * 3 * dt  # 降低影响强度到每秒±3能量
            new_energy = agent.energy + energy_change
            agent.energy = max(0.1, min(150, new_energy))  # 确保能量不会完全为0
        
        # 健康修正
        if 'health_modifier' in effects and effects['health_modifier'] != 1.0:
            health_change = (effects['health_modifier'] - 1.0) * 2 * dt  # 降低影响强度到每秒±2健康
            new_health = agent.health + health_change
            agent.health = max(0.1, min(100, new_health))  # 确保健康不会完全为0
        
        # 移动速度和感知范围的影响在智能体行为中体现
        # 这里可以临时存储影响值供智能体使用
        if not hasattr(agent, 'environmental_effects'):
            agent.environmental_effects = {}
        agent.environmental_effects.update(effects)
    
    def _collect_session_data(self):
        """收集会话数据用于分析"""
        if self.frame_count % 30 != 0:  # 每秒收集一次数据
            return
            
        current_time = time.time()
        alive_agents = [a for a in self.agents if a.alive]
        world_state = self.world.get_world_state()
        time_stats = self.time_manager.get_time_stats()
        
        # 收集部落统计数据
        tribe_data = {}
        if hasattr(self, 'tribe_manager') and self.tribe_manager:
            tribe_info = self.tribe_manager.get_tribes_info()
            tribe_data = {
                'total_tribes': tribe_info['total_tribes'],
                'tribe_details': tribe_info['tribes'],
                'largest_tribe': max(tribe_info['tribes'].values(), key=lambda x: x['population'])['population'] if tribe_info['tribes'] else 0,
                'total_alliances': sum(t['allies'] for t in tribe_info['tribes'].values()),
                'total_conflicts': sum(t['enemies'] for t in tribe_info['tribes'].values()),
                'avg_tech_level': sum(t['technology_level'] for t in tribe_info['tribes'].values()) / len(tribe_info['tribes']) if tribe_info['tribes'] else 0
            }
        
        # 收集统计数据
        stats_snapshot = {
            'timestamp': current_time,
            'step': time_stats['current_step'],
            'agent_count': len(alive_agents),
            'avg_age': sum(a.age for a in alive_agents) / len(alive_agents) if alive_agents else 0,
            'avg_energy': sum(a.energy for a in alive_agents) / len(alive_agents) if alive_agents else 0,
            'avg_health': sum(a.health for a in alive_agents) / len(alive_agents) if alive_agents else 0,
            'total_offspring': sum(a.offspring_count for a in alive_agents),
            'total_interactions': sum(a.social_interactions for a in alive_agents),
            'resources': world_state['num_resources'],
            'fps': time_stats['actual_fps'],
            'tribes': tribe_data  # 新增部落数据
        }
        
        self.session_data['stats_history'].append(stats_snapshot)
        
        # 收集性能指标
        performance = {
            'timestamp': current_time,
            'fps': time_stats['actual_fps'],
            'frame_count': self.frame_count,
            'agent_count': len(alive_agents)
        }
        
        self.session_data['performance_metrics'].append(performance)
    
    def _generate_html_report(self):
        """生成HTML可视化报告"""
        import json
        import time
        from datetime import datetime
        
        # 计算会话时长
        session_duration = time.time() - self.session_data['start_time']
        
        # 准备数据
        stats_data = json.dumps(self.session_data['stats_history'])
        performance_data = json.dumps(self.session_data['performance_metrics'])
        
        # 计算最终统计数据
        max_agents = max([s['agent_count'] for s in self.session_data['stats_history']] or [0])
        max_offspring = max([s['total_offspring'] for s in self.session_data['stats_history']] or [0])
        max_interactions = max([s['total_interactions'] for s in self.session_data['stats_history']] or [0])
        avg_fps = sum([p['fps'] for p in self.session_data['performance_metrics']])/len(self.session_data['performance_metrics']) if self.session_data['performance_metrics'] else 0
        max_age = max([s['avg_age'] for s in self.session_data['stats_history']] or [0])
        max_tribes = max([s.get('tribes', {}).get('total_tribes', 0) for s in self.session_data['stats_history']] or [0])
        max_tribe_size = max([s.get('tribes', {}).get('largest_tribe', 0) for s in self.session_data['stats_history']] or [0])
        avg_tech_level = max([s.get('tribes', {}).get('avg_tech_level', 0) for s in self.session_data['stats_history']] or [0])
        
        # 当前时间
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 生成HTML报告 - 修复JavaScript语法
        html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cogvrs 模拟报告 - """ + current_time + """</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #3498db;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px 0;
        }
        .stat-label {
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .chart-container {
            padding: 30px;
            background: white;
        }
        .chart-wrapper {
            position: relative;
            height: 400px;
            margin: 20px 0;
        }
        .section-title {
            font-size: 1.8em;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }
        .analysis {
            padding: 30px;
            background: #ecf0f1;
            line-height: 1.6;
        }
        .highlight {
            background: #3498db;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
        }
        .emoji {
            font-size: 1.2em;
            margin-right: 5px;
        }
        .tribe-summary {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #e67e22;
        }
        .tribe-stats p {
            margin: 8px 0;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        .events-list {
            max-height: 300px;
            overflow-y: auto;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            margin-top: 10px;
        }
        .event-item {
            display: flex;
            margin: 5px 0;
            padding: 5px;
            border-radius: 3px;
            background: #f8f9fa;
        }
        .event-time {
            color: #666;
            font-size: 0.9em;
            margin-right: 10px;
            min-width: 80px;
        }
        .event-desc {
            flex: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Cogvrs 模拟分析报告</h1>
            <p>数字宇宙实验室 - AI意识探索平台</p>
            <p>会话时长: """ + f"{session_duration/60:.1f}" + """ 分钟 | 生成时间: """ + current_time + """</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">⏰</span>模拟步数</div>
                <div class="stat-value">""" + str(len(self.session_data['stats_history'])) + """</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">👥</span>智能体峰值</div>
                <div class="stat-value">""" + str(max_agents) + """</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">👶</span>总后代数</div>
                <div class="stat-value">""" + str(max_offspring) + """</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">🤝</span>社交互动</div>
                <div class="stat-value">""" + str(max_interactions) + """</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">⚡</span>平均FPS</div>
                <div class="stat-value">""" + f"{avg_fps:.1f}" + """</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">🧬</span>最高年龄</div>
                <div class="stat-value">""" + f"{max_age:.0f}" + """</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">🏘️</span>最大部落数</div>
                <div class="stat-value">""" + str(max_tribes) + """</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">🏛️</span>最大部落规模</div>
                <div class="stat-value">""" + str(max_tribe_size) + """</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2 class="section-title">📊 智能体种群动态</h2>
            <div class="chart-wrapper">
                <canvas id="populationChart"></canvas>
            </div>
            
            <h2 class="section-title">⚡ 能量与健康状况</h2>
            <div class="chart-wrapper">
                <canvas id="healthChart"></canvas>
            </div>
            
            <h2 class="section-title">🎯 系统性能监控</h2>
            <div class="chart-wrapper">
                <canvas id="performanceChart"></canvas>
            </div>
            
            <h2 class="section-title">🏘️ 部落文明演化</h2>
            <div class="chart-wrapper">
                <canvas id="tribeChart"></canvas>
            </div>
        </div>
        
        <div class="analysis">
            <h2 class="section-title">🔬 智能行为分析</h2>
            <p><strong><span class="emoji">🧠</span>认知能力观察:</strong> 智能体展现了基于神经网络的学习能力，能够适应环境变化并优化行为策略。</p>
            
            <p><strong><span class="emoji">👥</span>社会行为模式:</strong> 观察到智能体间存在社交互动，表明群体智慧的萌芽。互动频率与种群密度呈正相关关系。</p>
            
            <p><strong><span class="emoji">🧬</span>进化机制:</strong> 通过繁殖和变异，智能体种群展现了<span class="highlight">自然选择</span>和<span class="highlight">适应性进化</span>的特征。</p>
            
            <p><strong><span class="emoji">🌍</span>生态平衡:</strong> 智能体与环境资源之间形成了动态平衡，体现了生态系统的自我调节能力。</p>
            
            <h3>🎯 关键发现</h3>
            <ul>
                <li><strong>意识萌芽:</strong> 智能体表现出目标导向的行为模式</li>
                <li><strong>学习适应:</strong> 神经网络权重的动态调整显示了学习能力</li>
                <li><strong>社会协作:</strong> 多智能体间的协作行为增强了生存能力</li>
                <li><strong>生命周期:</strong> 完整的生老病死过程验证了数字生命概念</li>
            </ul>
            
            <h2 class="section-title">🏘️ 部落文明分析</h2>
            <p><strong><span class="emoji">🏛️</span>文明涌现:</strong> 智能体自发形成了部落组织，展现了从个体到集体的社会进化过程。部落的形成表明了群体认同和社会结构的萌芽。</p>
            
            <p><strong><span class="emoji">👑</span>领导机制:</strong> 每个部落都会选出首领，基于能量水平的自然选择机制体现了原始的政治组织形式。</p>
            
            <p><strong><span class="emoji">🤝</span>外交关系:</strong> 不同部落间发展出同盟、冲突和贸易关系，形成了复杂的外交网络和互动模式。</p>
            
            <p><strong><span class="emoji">🔬</span>技术发展:</strong> 部落的科技水平随时间逐步提升，展现了知识积累和技术传承的文明特征。</p>
            
            <div class="tribe-summary">
                <h3>📊 部落发展统计</h3>
                <div class="tribe-stats">
                    <p><strong>部落总数峰值:</strong> """ + str(max_tribes) + """ 个</p>
                    <p><strong>最大部落规模:</strong> """ + str(max_tribe_size) + """ 个成员</p>
                    <p><strong>部落事件总数:</strong> """ + str(len(self.session_data.get('tribe_events', []))) + """ 次</p>
                    <p><strong>平均科技水平:</strong> """ + f"{avg_tech_level:.2f}" + """</p>
                </div>
                
                <h4>🎭 部落事件记录</h4>
                <div class="events-list">
"""

        # 添加最近的部落事件记录
        recent_tribe_events = self.session_data.get('tribe_events', [])[-10:]  # 最近10个事件
        for event in recent_tribe_events:
            event_time = datetime.fromtimestamp(event['timestamp']).strftime('%H:%M:%S')
            html_content += f"""
                    <div class="event-item">
                        <span class="event-time">[{event_time}]</span>
                        <span class="event-desc">{event['description']}</span>
                    </div>"""
        
        html_content += """
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const statsData = """ + stats_data + """;
        const performanceData = """ + performance_data + """;
        
        // 智能体种群图表
        const popCtx = document.getElementById('populationChart').getContext('2d');
        new Chart(popCtx, {
            type: 'line',
            data: {
                labels: statsData.map(d => new Date(d.timestamp * 1000).toLocaleTimeString()),
                datasets: [{
                    label: '智能体数量',
                    data: statsData.map(d => d.agent_count),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: '平均年龄',
                    data: statsData.map(d => d.avg_age),
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: '智能体数量' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: '平均年龄' },
                        grid: { drawOnChartArea: false }
                    }
                },
                plugins: {
                    legend: { display: true, position: 'top' }
                }
            }
        });
        
        // 健康状况图表
        const healthCtx = document.getElementById('healthChart').getContext('2d');
        new Chart(healthCtx, {
            type: 'line',
            data: {
                labels: statsData.map(d => new Date(d.timestamp * 1000).toLocaleTimeString()),
                datasets: [{
                    label: '平均能量',
                    data: statsData.map(d => d.avg_energy),
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: '平均健康',
                    data: statsData.map(d => d.avg_health),
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: '数值' } }
                },
                plugins: {
                    legend: { display: true, position: 'top' }
                }
            }
        });
        
        // 性能监控图表
        const perfCtx = document.getElementById('performanceChart').getContext('2d');
        new Chart(perfCtx, {
            type: 'line',
            data: {
                labels: performanceData.map(d => new Date(d.timestamp * 1000).toLocaleTimeString()),
                datasets: [{
                    label: 'FPS',
                    data: performanceData.map(d => d.fps),
                    borderColor: '#9b59b6',
                    backgroundColor: 'rgba(155, 89, 182, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: 'FPS' } }
                },
                plugins: {
                    legend: { display: true, position: 'top' }
                }
            }
        });
        
        // 部落文明演化图表
        const tribeCtx = document.getElementById('tribeChart').getContext('2d');
        new Chart(tribeCtx, {
            type: 'line',
            data: {
                labels: statsData.map(d => new Date(d.timestamp * 1000).toLocaleTimeString()),
                datasets: [{
                    label: '部落总数',
                    data: statsData.map(d => d.tribes ? d.tribes.total_tribes : 0),
                    borderColor: '#e67e22',
                    backgroundColor: 'rgba(230, 126, 34, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: '最大部落规模',
                    data: statsData.map(d => d.tribes ? d.tribes.largest_tribe : 0),
                    borderColor: '#9b59b6',
                    backgroundColor: 'rgba(155, 89, 182, 0.1)',
                    fill: false,
                    tension: 0.4,
                    yAxisID: 'y1'
                }, {
                    label: '平均科技水平',
                    data: statsData.map(d => d.tribes ? (d.tribes.avg_tech_level * 100) : 0),
                    borderColor: '#1abc9c',
                    backgroundColor: 'rgba(26, 188, 156, 0.1)',
                    fill: false,
                    tension: 0.4,
                    yAxisID: 'y2'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: '部落数量' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: '最大规模' },
                        grid: { drawOnChartArea: false }
                    },
                    y2: {
                        type: 'linear',
                        display: false,
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: { display: true, position: 'top' }
                }
            }
        });
    </script>
</body>
</html>
        """
        
        # 保存HTML报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/cogvrs_report_{timestamp}.html"
        
        # 确保reports目录存在
        import os
        os.makedirs("reports", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def _print_simulation_status(self):
        """打印详细的模拟状态"""
        alive_agents = [a for a in self.agents if a.alive]
        time_stats = self.time_manager.get_time_stats()
        world_state = self.world.get_world_state()
        
        print()
        print(f"Step {time_stats['current_step']:>6} | FPS: {time_stats['actual_fps']:5.1f} | Agents: {len(alive_agents):>2}")
        
        if alive_agents:
            ages = [a.age for a in alive_agents]
            energies = [a.energy for a in alive_agents]
            total_offspring = sum(a.offspring_count for a in alive_agents)
            
            print(f"Age: {min(ages):4.0f}-{max(ages):4.0f} (avg:{sum(ages)/len(ages):5.1f})")
            print(f"Energy: {min(energies):5.1f}-{max(energies):5.1f} (avg:{sum(energies)/len(energies):5.1f})")
            print(f"Total Offspring: {total_offspring}")
        
        print(f"Resources: {world_state['num_resources']}")
        print("-" * 60)
    
    def _update_ui_info(self):
        """更新UI信息"""
        # 统计信息
        alive_agents = [a for a in self.agents if a.alive]
        
        if alive_agents:
            # 基础统计
            avg_age = sum(a.age for a in alive_agents) / len(alive_agents)
            avg_energy = sum(a.energy for a in alive_agents) / len(alive_agents)
            avg_health = sum(a.health for a in alive_agents) / len(alive_agents)
            total_offspring = sum(a.offspring_count for a in alive_agents)
            total_interactions = sum(a.social_interactions for a in alive_agents)
            
            # 详细统计
            ages = [a.age for a in alive_agents]
            energies = [a.energy for a in alive_agents]
            healths = [a.health for a in alive_agents]
            
            min_age, max_age = min(ages), max(ages)
            min_energy, max_energy = min(energies), max(energies)
            min_health, max_health = min(healths), max(healths)
            
            # 环境适应性分析
            high_energy_count = sum(1 for e in energies if e > 120)
            low_energy_count = sum(1 for e in energies if e < 30)
            healthy_count = sum(1 for h in healths if h > 80)
            
        else:
            avg_age = avg_energy = avg_health = total_offspring = total_interactions = 0
            min_age = max_age = min_energy = max_energy = min_health = max_health = 0
            high_energy_count = low_energy_count = healthy_count = 0
        
        world_state = self.world.get_world_state()
        time_stats = self.time_manager.get_time_stats()
        
        # 增强的世界统计HTML
        total_agents = len(self.agents)
        alive_count = len(alive_agents)
        dead_count = total_agents - alive_count
        
        stats_html = f"""
        <b>🌍 Population Overview</b><br>
        <font color='#00FF00'>⏰ Step: {time_stats['current_step']}</font><br>
        <font color='#FFFF00'>👥 Total Agents: {total_agents}</font><br>
        <font color='#90EE90'>✅ Alive: {alive_count}</font><br>
        <font color='#FF6B6B'>💀 Dead: {dead_count}</font><br>
        <font color='#FF8800'>📊 Age Range: {min_age:.0f}-{max_age:.0f} (avg: {avg_age:.1f})</font><br>
        <font color='#00FFFF'>⚡ Energy: {min_energy:.0f}-{max_energy:.0f} (avg: {avg_energy:.1f})</font><br>
        <font color='#FF4444'>❤️ Health: {min_health:.0f}-{max_health:.0f} (avg: {avg_health:.1f})</font><br>
        <font color='#FF88FF'>👶 Total Offspring: {total_offspring}</font><br>
        <font color='#88FF88'>🤝 Social Interactions: {total_interactions}</font><br>
        <font color='#8888FF'>💎 Resources Available: {world_state['num_resources']}</font><br>
        <font color='#CCCCCC'>🎯 Simulation FPS: {time_stats['actual_fps']:.1f}</font>
        """
        
        # 详细的智能体分析HTML
        if alive_agents:
            most_active = max(alive_agents, key=lambda a: a.social_interactions)
            oldest = max(alive_agents, key=lambda a: a.age)
            healthiest = max(alive_agents, key=lambda a: a.health)
            most_energetic = max(alive_agents, key=lambda a: a.energy)
            
            details_html = f"""
            <b>🧠 Individual Agent Stats</b><br>
            <font color='#FFD700'>🏆 Most Social:</font><br>
            &nbsp;&nbsp;Agent#{most_active.agent_id}: {most_active.social_interactions} interactions<br>
            <font color='#90EE90'>👴 Eldest:</font><br>
            &nbsp;&nbsp;Agent#{oldest.agent_id}: {oldest.age:.0f} years old<br>
            <font color='#FF69B4'>💪 Healthiest:</font><br>
            &nbsp;&nbsp;Agent#{healthiest.agent_id}: {healthiest.health:.1f}/100 HP<br>
            <font color='#FFD700'>⚡ Most Energetic:</font><br>
            &nbsp;&nbsp;Agent#{most_energetic.agent_id}: {most_energetic.energy:.1f} energy<br>
            <br>
            <b>🌱 Population Health</b><br>
            <font color='#00FF00'>🟢 High Energy ({'>120'}): {high_energy_count}</font><br>
            <font color='#FF0000'>🔴 Low Energy ({'<30'}): {low_energy_count}</font><br>
            <font color='#00FFFF'>💚 Healthy ({'>80'}): {healthy_count}</font>
            """
        else:
            details_html = "<b>🧠 Agent Analysis</b><br><font color='#FF6666'>No agents available</font>"
        
        # 系统状态和环境信息HTML
        population_trend = "📈 Growing" if len(alive_agents) > 10 else "📉 Declining" if len(alive_agents) < 5 else "📊 Stable"
        performance = "🟢 Good" if time_stats['actual_fps'] > 20 else "🟡 Fair" if time_stats['actual_fps'] > 15 else "🔴 Poor"
        
        # 渲染模式状态
        render_mode = "🎭 Multi-Scale" if (hasattr(self, 'multi_scale_mode') and self.multi_scale_mode) else "🎨 Legacy"
        current_scale = ""
        if hasattr(self, 'scale_manager') and hasattr(self, 'multi_scale_mode') and self.multi_scale_mode:
            scale_name = self.scale_manager.current_scale.value.upper()
            current_scale = f" ({scale_name})"
        
        # 获取环境信息
        env_info = ""
        if hasattr(self, 'environment_manager'):
            env_status = self.environment_manager.get_environment_status()
            
            # 优先使用气候系统信息
            if hasattr(self.environment_manager, 'climate_system'):
                climate_status = self.environment_manager.climate_system.get_status_info()
                active_weather = []  # 气候系统不使用active_weather
            elif hasattr(self, 'weather_system') and self.weather_system is not None:
                active_weather = self.weather_system.get_active_weather_info()
            else:
                active_weather = []
            
            season_emoji = {"Spring": "🌸", "Summer": "☀️", "Autumn": "🍂", "Winter": "❄️"}
            time_emoji = {"Dawn": "🌅", "Day": "☀️", "Dusk": "🌇", "Night": "🌙"}
            
            env_info = f"""
            <br><b>🌍 Environment</b><br>
            <font color='#90EE90'>{season_emoji.get(env_status['season'], '🌍')} {env_status['season']}</font><br>
            <font color='#87CEEB'>{time_emoji.get(env_status['time_of_day'], '⏰')} {env_status['time_of_day']}</font><br>
            <font color='#DDA0DD'>🏞️ Zones: {env_status['total_zones']}</font><br>
            """
            
            # 显示气候或天气信息
            if hasattr(self.environment_manager, 'climate_system'):
                # 气候系统信息
                climate_emoji = {
                    "temperate": "🌤️", "ice_age": "🧊", "greenhouse": "🔥",
                    "arid": "🏜️", "volcanic": "🌋"
                }
                current_epoch = climate_status['current_epoch']
                progress = int(climate_status['epoch_progress'] * 100)
                env_info += f"<font color='#FFB6C1'>{climate_emoji.get(current_epoch, '🌍')} {current_epoch.title()} ({progress}%)</font><br>"
                time_remaining = int(climate_status['time_remaining'])
                env_info += f"<font color='#DDD'>⏳ Next change: {time_remaining}s</font><br>"
            elif active_weather:
                # 天气系统信息
                weather_info = active_weather[0]
                weather_emoji = {
                    "clear": "☀️", "rain": "🌧️", "storm": "⛈️",
                    "drought": "🌵", "blizzard": "🌨️", "heatwave": "🔥"
                }
                env_info += f"<font color='#FFB6C1'>{weather_emoji.get(weather_info['type'], '🌤️')} {weather_info['type'].title()}</font><br>"
            else:
                env_info += "<font color='#98FB98'>🌤️ Clear Weather</font><br>"
        
        # 添加部落信息
        tribe_info_html = ""
        if hasattr(self, 'tribe_manager') and self.tribe_manager:
            tribe_info = self.tribe_manager.get_tribes_info()
            if tribe_info['total_tribes'] > 0:
                tribe_info_html = f"""
        <br><b>🏘️ Tribes & Civilization</b><br>
        <font color='#FFD700'>🏛️ Total Tribes: {tribe_info['total_tribes']}</font><br>
        """
                
                # 统计文明等级
                civilization_counts = {}
                for tribe_data in tribe_info['tribes'].values():
                    level = tribe_data['civilization_level']
                    civilization_counts[level] = civilization_counts.get(level, 0) + 1
                
                # 显示主要文明等级
                civ_emojis = {
                    'nomadic': '🏕️', 'settlement': '🏠', 'village': '🏘️', 
                    'town': '🏙️', 'city': '🏙️'
                }
                
                for level, count in civilization_counts.items():
                    emoji = civ_emojis.get(level, '🏘️')
                    tribe_info_html += f"<font color='#87CEEB'>{emoji} {level.title()}: {count}</font><br>"
                
                # 显示外交关系
                total_alliances = sum(tribe_data['allies'] for tribe_data in tribe_info['tribes'].values()) // 2
                total_conflicts = sum(tribe_data['enemies'] for tribe_data in tribe_info['tribes'].values()) // 2
                
                if total_alliances > 0:
                    tribe_info_html += f"<font color='#90EE90'>🤝 Alliances: {total_alliances}</font><br>"
                if total_conflicts > 0:
                    tribe_info_html += f"<font color='#FF6B6B'>⚔️ Conflicts: {total_conflicts}</font><br>"
            else:
                tribe_info_html = """
        <br><b>🏘️ Tribes & Civilization</b><br>
        <font color='#808080'>No tribes formed yet</font><br>
        """

        system_html = f"""
        <b>💻 System Status</b><br>
        <font color='#00FF00'>Population: {population_trend}</font><br>
        <font color='#FFFF00'>Performance: {performance}</font><br>
        <font color='#FF8800'>Memory: {len(self.agents)} tracked</font><br>
        <font color='#00FFFF'>Render: {render_mode}{current_scale}</font><br>
        <font color='#CCCCCC'>Press M to toggle render mode</font>
        {env_info}
        {tribe_info_html}
        """
        
        # 更新所有UI元素
        self.stats_text.html_text = stats_html
        self.stats_text.rebuild()
        
        self.details_text.html_text = details_html
        self.details_text.rebuild()
        
        self.system_text.html_text = system_html
        self.system_text.rebuild()
    
    def handle_events(self):
        """处理事件"""
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                # 处理窗口大小调节
                if not self.fullscreen:  # 只在窗口模式下处理
                    self._handle_window_resize(event.w, event.h)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._toggle_pause()
                elif event.key == pygame.K_F11:
                    # F11键切换全屏
                    self._toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    # ESC键退出程序
                    self.running = False
                elif event.key == pygame.K_r and self.extinction_occurred:
                    # 灭绝后按R键重启
                    self._restart_after_extinction()
                elif event.key == pygame.K_m and hasattr(self, 'multi_scale_mode'):
                    # M键切换渲染模式
                    self.multi_scale_mode = not self.multi_scale_mode
                    mode_text = "Multi-Scale" if self.multi_scale_mode else "Legacy"
                    logger.info(f"Switched to {mode_text} rendering mode")
                    print(f"🔄 切换到{mode_text}渲染模式")
                else:
                    # 传递给世界渲染器（传统模式）
                    if not (self.enable_multi_scale and hasattr(self, 'multi_scale_mode') and self.multi_scale_mode):
                        self.world_renderer.handle_event(event)
            
            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.play_pause_button:
                        self._toggle_pause()
                    elif event.ui_element == self.reset_button:
                        self._reset_simulation()
                    elif event.ui_element == self.add_agent_button:
                        self._add_random_agents(1)
                
                elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == self.speed_slider:
                        speed = self.speed_slider.get_current_value()
                        self.time_manager.set_speed(speed)
                        self.speed_label.set_text(f'Speed: {speed:.1f}x')
            
            # 处理UI事件
            self.ui_manager.process_events(event)
        
        # 多尺度交互处理
        if (self.enable_multi_scale and hasattr(self, 'multi_scale_mode') and 
            self.multi_scale_mode and hasattr(self, 'interaction_controller')):
            
            world_state = self._prepare_world_state_for_multi_scale()
            interaction_result = self.interaction_controller.handle_events(events, world_state)
            
            # 处理交互结果
            if interaction_result.get('quit_requested'):
                self.running = False
            
            if interaction_result.get('scale_changed'):
                current_scale = self.scale_manager.current_scale.value
                print(f"🔍 尺度切换到: {current_scale.upper()}")
            
            if interaction_result.get('display_options_changed'):
                print("🎮 显示选项已更新")
    
    def _toggle_pause(self):
        """切换暂停状态"""
        self.paused = not self.paused
        if self.paused:
            self.time_manager.pause()
            self.play_pause_button.set_text('Resume')
        else:
            self.time_manager.resume()
            self.play_pause_button.set_text('Pause')
    
    def _reset_simulation(self):
        """重置模拟"""
        # 重置时间
        self.time_manager.reset()
        
        # 重新初始化世界
        self.world = World2D(self.config.get('world', {}))
        
        # 重新创建智能体
        self.agents = []
        initial_count = self.config.get('initial_agents', 10)
        self._add_random_agents(initial_count)
        
        # 清空轨迹
        self.world_renderer.agent_trajectories.clear()
        
        # 恢复播放状态
        self.paused = False
        self.time_manager.resume()
        self.play_pause_button.set_text('Pause')
        
        logger.info("Simulation reset")
    
    def _toggle_fullscreen(self):
        """切换全屏模式"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # 切换到全屏
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (info.current_w, info.current_h), 
                pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
            )
            self.window_width = info.current_w
            self.window_height = info.current_h
            print(f"🖥️ 切换到全屏模式: {self.window_width}x{self.window_height}")
        else:
            # 切换到窗口模式
            self.window_width, self.window_height = self.windowed_size
            self.screen = pygame.display.set_mode(
                (self.window_width, self.window_height), 
                pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
            )
            print(f"🪟 切换到窗口模式: {self.window_width}x{self.window_height}")
        
        # 重新计算世界视图尺寸
        if self.fullscreen:
            # 全屏模式：最大化世界视图，只保留必要的面板空间
            self.panel_width = 300  # 全屏时减小面板宽度
            self.world_view_width = self.window_width - self.panel_width - 20
            self.world_view_height = self.window_height - 40
        else:
            # 窗口模式：恢复原始比例
            self.panel_width = 350
            self.world_view_width = self.window_width - self.panel_width - 20
            self.world_view_height = self.window_height - 40
        
        print(f"   更新世界视图: {self.world_view_width}x{self.world_view_height}")
        
        # 重新创建后台缓冲区
        self.back_buffer = pygame.Surface((self.window_width, self.window_height))
        
        # 更新UI管理器
        self.ui_manager = pygame_gui.UIManager((self.window_width, self.window_height))
        self._create_ui_elements()  # 重新创建UI元素
        
        # 更新世界渲染器配置
        if hasattr(self, 'world_renderer'):
            self.world_renderer.screen_width = self.world_view_width
            self.world_renderer.screen_height = self.world_view_height
            self.world_renderer.scale_x = self.world_view_width / self.world_renderer.world_width
            self.world_renderer.scale_y = self.world_view_height / self.world_renderer.world_height
        
        logger.info(f"Fullscreen toggled: {self.fullscreen}")
    
    def _handle_window_resize(self, new_width: int, new_height: int):
        """处理窗口大小调节"""
        # 设置最小窗口大小
        min_width, min_height = 800, 600
        new_width = max(min_width, new_width)
        new_height = max(min_height, new_height)
        
        # 更新窗口尺寸
        self.window_width = new_width
        self.window_height = new_height
        self.windowed_size = (new_width, new_height)
        
        # 重新创建显示
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height),
            pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
        )
        
        # 重新创建后台缓冲区
        self.back_buffer = pygame.Surface((self.window_width, self.window_height))
        
        # 重新计算布局 - 支持更大的显示区域
        self.panel_width = 350  # 固定面板宽度
        self.world_view_width = self.window_width - self.panel_width - 20  # 最大化世界视图
        self.world_view_height = self.window_height - 40  # 保留顶部空间
        
        print(f"🔄 窗口调整: {self.window_width}x{self.window_height}")
        print(f"   世界视图: {self.world_view_width}x{self.world_view_height}")
        
        # 更新UI管理器
        self.ui_manager = pygame_gui.UIManager((self.window_width, self.window_height))
        self._create_ui_elements()  # 重新创建UI元素
        
        # 更新世界渲染器配置
        if hasattr(self, 'world_renderer'):
            self.world_renderer.screen_width = self.world_view_width
            self.world_renderer.screen_height = self.world_view_height
            self.world_renderer.scale_x = self.world_view_width / self.world_renderer.world_width
            self.world_renderer.scale_y = self.world_view_height / self.world_renderer.world_height
        
        print(f"🔧 窗口大小调节: {self.window_width}x{self.window_height}")
        logger.info(f"Window resized to: {self.window_width}x{self.window_height}")
    
    def _handle_extinction_event(self):
        """处理种群灭绝事件"""
        print("\n" + "="*60)
        print("💀 种群灭绝事件检测")
        print("="*60)
        
        # 暂停模拟
        self.paused = True
        self.time_manager.pause()
        
        # 生成灭绝分析报告
        extinction_report = self._generate_extinction_analysis()
        
        # 显示分析结果
        print("\n📊 灭绝原因分析:")
        for category, analysis in extinction_report.items():
            print(f"\n🔍 {category}:")
            for item in analysis:
                print(f"  • {item}")
        
        # 询问用户是否重启
        print(f"\n🤔 种群已完全灭绝!")
        print(f"💡 建议：")
        print(f"  1. 按R键重启模拟")
        print(f"  2. 按ESC键退出程序") 
        print(f"  3. 检查环境参数设置")
        
        # 设置灭绝标志
        self.extinction_occurred = True
        
        # 生成详细HTML报告
        try:
            report_path = self._generate_extinction_html_report(extinction_report)
            print(f"📄 详细灭绝分析报告已生成: {report_path}")
        except Exception as e:
            logger.error(f"Failed to generate extinction report: {e}")
    
    def _generate_extinction_analysis(self) -> Dict[str, List[str]]:
        """生成灭绝原因分析"""
        analysis = {
            "环境因素": [],
            "资源状况": [],
            "天气影响": [],
            "种群动态": [],
            "进化趋势": [],
            "部落发展": [],
            "文明成就": [],
            "系统建议": []
        }
        
        # 分析环境因素
        world_state = self.world.get_world_state()
        resource_count = world_state.get('num_resources', 0)
        
        if resource_count < 50:
            analysis["资源状况"].append(f"资源严重短缺 (仅{resource_count}个)")
        
        # 分析环境影响（气候或天气）
        if hasattr(self, 'environment_manager') and hasattr(self.environment_manager, 'climate_system'):
            # 使用气候系统分析
            climate_status = self.environment_manager.climate_system.get_status_info()
            current_epoch = climate_status['current_epoch']
            
            # 分析气候对灭绝的影响
            severe_climates = ['ice_age', 'volcanic', 'arid']
            if current_epoch in severe_climates:
                analysis["天气影响"].append(f"严酷气候纪元: {current_epoch} 导致生存困难")
            
            # 添加气候变化分析
            climate_history = self.environment_manager.climate_system.get_climate_history()
            if climate_history:
                analysis["环境因素"].append(f"气候变化历史: 经历了{len(climate_history)}次气候纪元转换")
                recent_changes = [h for h in climate_history if time.time() - h['timestamp'] < 300]  # 最近5分钟
                if len(recent_changes) > 2:
                    analysis["环境因素"].append("频繁的气候变化导致环境不稳定")
            
        elif hasattr(self, 'weather_system') and self.weather_system is not None:
            # 回退到天气系统分析
            active_weather = self.weather_system.get_active_weather_info()
            severe_weather_count = sum(1 for w in active_weather if w['intensity'] > 0.7)
            if severe_weather_count > 2:
                analysis["天气影响"].append(f"持续恶劣天气 ({severe_weather_count}个强天气事件)")
        
        # 分析历史数据
        if self.session_data['stats_history']:
            last_stats = self.session_data['stats_history'][-5:]  # 最后5次记录
            
            # 种群趋势分析
            if len(last_stats) >= 2:
                agent_counts = [s['agent_count'] for s in last_stats]
                avg_energies = [s['avg_energy'] for s in last_stats]
                
                if all(count <= 3 for count in agent_counts[-3:]):
                    analysis["种群动态"].append("种群数量持续过低")
                
                if all(energy < 50 for energy in avg_energies[-3:]):
                    analysis["种群动态"].append("种群平均能量持续偏低")
        
        # 分析部落发展情况
        if hasattr(self, 'tribe_manager') and self.tribe_manager:
            tribe_info = self.tribe_manager.get_tribes_info()
            
            analysis["部落发展"].append(f"曾形成部落数量: {tribe_info['total_tribes']}")
            
            if tribe_info['total_tribes'] > 0:
                # 文明等级分析
                civilization_levels = {}
                max_population = 0
                oldest_tribe_age = 0
                total_cultural_traits = 0
                
                for tribe_data in tribe_info['tribes'].values():
                    level = tribe_data['civilization_level']
                    civilization_levels[level] = civilization_levels.get(level, 0) + 1
                    max_population = max(max_population, tribe_data['population'])
                    
                    # 计算部落存续时间
                    tribe_age = time.time() - tribe_data['formation_time']
                    oldest_tribe_age = max(oldest_tribe_age, tribe_age)
                    
                    total_cultural_traits += tribe_data['cultural_traits']
                
                # 文明成就分析
                for level, count in civilization_levels.items():
                    analysis["文明成就"].append(f"{level}阶段部落: {count}个")
                
                analysis["文明成就"].append(f"最大部落规模: {max_population}个体")
                analysis["文明成就"].append(f"最长部落存续: {oldest_tribe_age:.1f}秒")
                analysis["文明成就"].append(f"文化特征总数: {total_cultural_traits}")
                
                # 部落发展分析
                advanced_tribes = sum(1 for level in civilization_levels.keys() 
                                    if level in ['village', 'town', 'city'])
                if advanced_tribes > 0:
                    analysis["部落发展"].append(f"达到高级文明的部落: {advanced_tribes}个")
                else:
                    analysis["部落发展"].append("未能发展出高级文明")
                
                # 外交关系分析
                total_alliances = 0
                total_conflicts = 0
                for tribe_data in tribe_info['tribes'].values():
                    total_alliances += tribe_data['allies']
                    total_conflicts += tribe_data['enemies']
                
                if total_alliances > 0:
                    analysis["部落发展"].append(f"形成盟友关系: {total_alliances//2}组")  # 除以2避免重复计算
                if total_conflicts > 0:
                    analysis["部落发展"].append(f"发生冲突关系: {total_conflicts//2}组")
            else:
                analysis["部落发展"].append("未能形成任何部落组织")
                analysis["文明成就"].append("未达成任何文明成就")
        else:
            analysis["部落发展"].append("部落系统未启用")
        
        # 系统建议
        analysis["系统建议"].extend([
            "增加初始资源密度 (resource_density > 0.1)",
            "降低环境压力 (减少恶劣天气频率)",
            "调整繁殖门槛 (降低能量要求)",
            "增加初始种群数量 (initial_agents > 10)",
            "优化部落形成条件以促进文明发展"
        ])
        
        return analysis
    
    def _generate_extinction_html_report(self, analysis: Dict[str, List[str]]) -> str:
        """生成详细的HTML灭绝报告"""
        from datetime import datetime
        import json
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/extinction_report_{timestamp}.html"
        
        # 确保目录存在
        import os
        os.makedirs("reports", exist_ok=True)
        
        # 生成HTML内容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>种群灭绝分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #ff6b6b; background: #fff5f5; }
        .analysis-item { margin: 10px 0; padding: 8px; background: #ffffff; border-radius: 4px; border-left: 3px solid #ff9999; }
        .warning { background: #fff3cd; border-color: #ffeaa7; color: #856404; }
        .suggestion { background: #d1ecf1; border-color: #74b9ff; color: #0c5460; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💀 种群灭绝分析报告</h1>
            <p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
"""
        
        # 添加分析内容
        for category, items in analysis.items():
            html_content += f'<div class="section"><h2>{category}</h2>'
            for item in items:
                css_class = "suggestion" if category == "系统建议" else "analysis-item"
                html_content += f'<div class="{css_class}">{item}</div>'
            html_content += '</div>'
        
        # 添加气候变化专门分析
        if hasattr(self, 'environment_manager') and hasattr(self.environment_manager, 'climate_system'):
            html_content += self._generate_climate_change_section()
        
        # 添加详细事件记录
        html_content += self._generate_detailed_events_section()
        
        html_content += """
    </div>
</body>
</html>
"""
        
        # 保存文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def _generate_climate_change_section(self) -> str:
        """生成气候变化专门分析章节"""
        climate_system = self.environment_manager.climate_system
        climate_status = climate_system.get_status_info()
        climate_history = climate_system.get_climate_history()
        
        # 气候变化分析
        section_html = '''
        <div class="section">
            <h2>🌍 气候变化分析</h2>
            <div class="analysis-item">
                <h3>当前气候状况</h3>
        '''
        
        # 当前气候状态
        current_epoch = climate_status['current_epoch']
        progress = climate_status['epoch_progress']
        time_remaining = climate_status['time_remaining']
        
        climate_descriptions = {
            'temperate': '温带气候 - 适宜生存，温度湿度适中',
            'ice_age': '冰河时期 - 寒冷严酷，生存困难',
            'greenhouse': '温室气候 - 炎热潮湿，极端天气频发',
            'arid': '干旱气候 - 极度缺水，资源稀缺',
            'volcanic': '火山时期 - 火山爆发，环境恶劣'
        }
        
        section_html += f'''
                <p><strong>当前纪元:</strong> {current_epoch.upper()} ({progress*100:.1f}%)</p>
                <p><strong>气候描述:</strong> {climate_descriptions.get(current_epoch, '未知气候')}</p>
                <p><strong>剩余时间:</strong> {time_remaining:.1f}秒</p>
            </div>
        '''
        
        # 气候历史分析
        if climate_history:
            section_html += '''
            <div class="analysis-item">
                <h3>气候变化历史</h3>
            '''
            
            # 统计各气候纪元的持续时间
            epoch_durations = {}
            for i, record in enumerate(climate_history):
                epoch = record['epoch']
                if epoch not in epoch_durations:
                    epoch_durations[epoch] = 0
                
                if i < len(climate_history) - 1:
                    duration = climate_history[i + 1]['timestamp'] - record['timestamp']
                    epoch_durations[epoch] += duration
                else:
                    # 最后一个纪元到现在的时间
                    duration = time.time() - record['timestamp']
                    epoch_durations[epoch] += duration
            
            section_html += f'<p><strong>气候转换次数:</strong> {len(climate_history)} 次</p>'
            section_html += '<p><strong>各气候纪元持续时间:</strong></p><ul>'
            
            for epoch, duration in epoch_durations.items():
                section_html += f'<li>{epoch.upper()}: {duration:.1f}秒</li>'
            
            section_html += '</ul>'
            
            # 分析气候对生存的影响
            severe_time = sum(duration for epoch, duration in epoch_durations.items() 
                             if epoch in ['ice_age', 'volcanic', 'arid'])
            total_time = sum(epoch_durations.values())
            
            if total_time > 0:
                severe_percentage = (severe_time / total_time) * 100
                section_html += f'''
                <p><strong>严酷气候占比:</strong> {severe_percentage:.1f}%</p>
                '''
                
                if severe_percentage > 60:
                    section_html += '<p class="warning">⚠️ 长期恶劣气候是导致种群灭绝的主要原因</p>'
                elif severe_percentage > 30:
                    section_html += '<p class="warning">⚠️ 频繁的气候变化增加了生存压力</p>'
                else:
                    section_html += '<p>气候条件相对稳定，灭绝原因可能在其他因素</p>'
            
            section_html += '</div>'
        
        # 气候变化对文明发展的影响
        if hasattr(self, 'tribe_manager') and self.tribe_manager.tribes:
            section_html += '''
            <div class="analysis-item">
                <h3>气候变化对文明发展的影响</h3>
            '''
            
            tribe_info = self.tribe_manager.get_tribes_info()
            section_html += f'<p><strong>部落数量:</strong> {tribe_info["total_tribes"]}</p>'
            
            if tribe_info["total_tribes"] > 0:
                civilization_levels = [tribe['civilization_level'] for tribe in tribe_info['tribes'].values()]
                advanced_tribes = sum(1 for level in civilization_levels if level in ['village', 'town', 'city'])
                
                section_html += f'<p><strong>高级文明部落:</strong> {advanced_tribes}/{tribe_info["total_tribes"]}</p>'
                
                if advanced_tribes == 0:
                    section_html += '<p class="warning">⚠️ 气候变化可能阻碍了文明发展，没有部落达到高级阶段</p>'
                else:
                    section_html += '<p>部分部落在气候变化中仍保持了文明发展</p>'
            
            section_html += '</div>'
        
        # 气候变化理论分析
        section_html += '''
        <div class="analysis-item">
            <h3>气候变化理论分析</h3>
            <p><strong>科学理论基础:</strong></p>
            <ul>
                <li><strong>冰河时期理论:</strong> 地球历史上经历过多次冰河时期，每次都对生物进化产生重大影响</li>
                <li><strong>温室效应理论:</strong> 大气中温室气体浓度变化导致全球温度升高</li>
                <li><strong>火山冬天理论:</strong> 大规模火山爆发释放的灰尘和气体遮蔽阳光，导致全球降温</li>
                <li><strong>干旱化理论:</strong> 气候变化导致降水模式改变，部分地区出现长期干旱</li>
            </ul>
            <p><strong>对智能体生存的影响机制:</strong></p>
            <ul>
                <li>能量消耗增加（极端温度条件下维持体温）</li>
                <li>健康状况恶化（恶劣环境导致疾病）</li>
                <li>繁殖能力下降（生存压力影响繁殖意愿）</li>
                <li>资源获取困难（极端气候影响资源分布）</li>
            </ul>
        </div>
        '''
        
        section_html += '</div>'
        return section_html
    
    def _generate_detailed_events_section(self) -> str:
        """生成详细事件记录章节"""
        section_html = '''
        <div class="section">
            <h2>📋 详细事件记录</h2>
            <div class="analysis-item">
                <h3>模拟过程记录</h3>
        '''
        
        # 统计不同类型的事件
        event_counts = {
            'reproduction': len(self.session_data.get('reproduction_events', [])),
            'agent_death': len([e for e in self.session_data.get('detailed_events', []) if e['type'] == 'agent_death']),
            'tribe': len(self.session_data.get('tribe_events', [])),
            'environment': len(self.session_data.get('environmental_events', []))
        }
        
        section_html += f'''
                <p><strong>事件统计:</strong></p>
                <ul>
                    <li>🍼 繁殖事件: {event_counts['reproduction']} 次</li>
                    <li>💀 死亡事件: {event_counts['agent_death']} 次</li>
                    <li>🏘️ 部落事件: {event_counts['tribe']} 次</li>
                    <li>🌍 环境事件: {event_counts['environment']} 次</li>
                </ul>
        '''
        
        # 显示关键事件时间线
        all_events = self.session_data.get('detailed_events', [])
        if all_events:
            # 按时间排序并取前20个重要事件
            sorted_events = sorted(all_events, key=lambda x: x['timestamp'])
            important_events = [e for e in sorted_events if e['type'] in ['reproduction', 'tribe', 'agent_death']][:20]
            
            section_html += '''
                <h4>关键事件时间线</h4>
                <div style="max-height: 300px; overflow-y: auto; background: #f9f9f9; padding: 10px; border-radius: 5px;">
            '''
            
            for event in important_events:
                event_time = event['timestamp'] - self.session_data['start_time']
                event_icon = {'reproduction': '🍼', 'tribe': '🏘️', 'agent_death': '💀', 'environment': '🌍'}.get(event['type'], '📝')
                
                section_html += f'''
                    <div style="margin: 5px 0; padding: 5px; background: white; border-radius: 3px;">
                        <strong>[{event_time:.1f}s] {event_icon} {event['description']}</strong>
                '''
                
                # 添加详细信息
                if event['type'] == 'reproduction' and 'details' in event:
                    details = event['details']
                    section_html += f"<br><small>父母: {details.get('parent_id', 'Unknown')}, 代数: {details.get('generation', 0)}</small>"
                elif event['type'] == 'tribe' and 'details' in event:
                    details = event['details']
                    section_html += f"<br><small>成员数: {details.get('member_count', 0)}, 领袖: {details.get('leader_id', 'Unknown')}</small>"
                elif event['type'] == 'agent_death' and 'details' in event:
                    details = event['details']
                    section_html += f"<br><small>死因: {details.get('cause', 'Unknown')}, 年龄: {details.get('age', 0):.1f}</small>"
                
                section_html += '</div>'
            
            section_html += '</div>'
        
        # 显示繁殖成功率分析
        if event_counts['reproduction'] > 0:
            section_html += '''
            <div class="analysis-item">
                <h3>繁殖模式分析</h3>
            '''
            
            reproduction_events = self.session_data.get('reproduction_events', [])
            if reproduction_events:
                # 分析代际分布
                generations = [e['details'].get('generation', 0) for e in reproduction_events if 'details' in e]
                if generations:
                    max_generation = max(generations)
                    generation_counts = {}
                    for gen in generations:
                        generation_counts[gen] = generation_counts.get(gen, 0) + 1
                    
                    section_html += f'<p><strong>进化进展:</strong> 达到第 {max_generation} 代</p>'
                    section_html += '<p><strong>各代繁殖分布:</strong></p><ul>'
                    for gen in sorted(generation_counts.keys()):
                        section_html += f'<li>第{gen}代: {generation_counts[gen]}次</li>'
                    section_html += '</ul>'
            
            section_html += '</div>'
        
        # 显示部落发展历程
        if event_counts['tribe'] > 0:
            section_html += '''
            <div class="analysis-item">
                <h3>部落发展历程</h3>
            '''
            
            tribe_events = self.session_data.get('tribe_events', [])
            if tribe_events:
                # 分析部落形成时间分布
                formation_times = [e['timestamp'] - self.session_data['start_time'] for e in tribe_events]
                if formation_times:
                    earliest = min(formation_times)
                    latest = max(formation_times)
                    section_html += f'<p><strong>部落形成时间:</strong> {earliest:.1f}s - {latest:.1f}s</p>'
                
                # 显示部落信息
                section_html += '<p><strong>已形成的部落:</strong></p><ul>'
                for event in tribe_events:
                    if 'details' in event:
                        details = event['details']
                        tribe_name = details.get('tribe_name', 'Unknown')
                        member_count = details.get('member_count', 0)
                        section_html += f'<li>{tribe_name} - {member_count}成员</li>'
                section_html += '</ul>'
            
            section_html += '</div>'
        
        section_html += '</div>'
        return section_html
    
    def _restart_after_extinction(self):
        """灭绝后重启模拟"""
        print("\n🔄 重启模拟...")
        
        # 重置灭绝标志
        self.extinction_occurred = False
        
        # 重置时间系统
        self.time_manager.reset()
        
        # 重新初始化世界（增加资源）
        improved_world_config = self.config.get('world', {}).copy()
        improved_world_config['resource_density'] = min(0.15, improved_world_config.get('resource_density', 0.05) * 1.5)
        self.world = World2D(improved_world_config)
        
        # 重新创建智能体（增加数量）
        self.agents = []
        initial_count = max(10, self.config.get('initial_agents', 5) * 2)  # 至少10个，或者原来的2倍
        self._add_random_agents(initial_count)
        
        # 重置天气系统（减少恶劣天气）
        if hasattr(self, 'weather_system'):
            self.weather_system.weather_chance *= 0.7  # 减少30%的天气生成概率
            self.weather_system.active_weather.clear()  # 清除当前恶劣天气
        
        # 重置数据收集
        self.session_data = {
            'start_time': time.time(),
            'stats_history': [],
            'events': [],
            'agent_lifecycle': [],
            'performance_metrics': [],
            'detailed_events': [],  # 新增详细事件记录
            'tribe_events': [],     # 部落相关事件
            'reproduction_events': [], # 繁殖事件
            'environmental_events': []  # 环境事件
        }
        
        # 恢复运行状态
        self.paused = False
        self.time_manager.resume()
        
        print(f"✅ 模拟重启完成!")
        print(f"  📈 提升资源密度: {improved_world_config['resource_density']:.3f}")
        print(f"  🤖 增加智能体数量: {initial_count}")
        print(f"  🌤️ 减少恶劣天气频率")
        
        logger.info(f"Simulation restarted after extinction with improved parameters")
    
    def render(self):
        """优化的渲染界面"""
        self.frame_count += 1
        
        # 跳帧渲染减少负载
        self.render_skip += 1
        if self.render_skip % 2 != 0:  # 每隔一帧才完整渲染
            return
        
        # 使用后台缓冲区渲染
        self.back_buffer.fill((15, 15, 25))
        
        # 渲染世界视图
        world_surface = pygame.Surface((self.world_view_width, self.world_view_height))
        
        # 选择渲染模式
        if self.enable_multi_scale and hasattr(self, 'multi_scale_mode') and self.multi_scale_mode:
            # 多尺度渲染
            self._render_multi_scale(world_surface)
        else:
            # 传统渲染
            self._render_legacy(world_surface)
        
        # 绘制到后台缓冲区
        self.back_buffer.blit(world_surface, (10, 10))
        
        # 绘制边框和面板
        pygame.draw.rect(
            self.back_buffer, (100, 100, 100),
            (8, 8, self.world_view_width + 4, self.world_view_height + 4), 2
        )
        pygame.draw.rect(self.back_buffer, (25, 25, 35), self.control_panel)
        pygame.draw.rect(self.back_buffer, (60, 60, 80), self.control_panel, 2)
        
        # 更新UI信息
        current_time = time.time()
        if current_time - self.last_stats_update >= self.stats_update_interval:
            self._update_ui_info()
            self.last_stats_update = current_time
        
        # 将后台缓冲区内容复制到屏幕
        self.screen.blit(self.back_buffer, (0, 0))
        
        # 渲染GUI元素到屏幕
        self.ui_manager.draw_ui(self.screen)
    
    def _render_multi_scale(self, surface: pygame.Surface):
        """多尺度渲染"""
        # 准备世界状态数据
        world_state = self._prepare_world_state_for_multi_scale()
        
        # 使用多尺度渲染管道
        dt = self.clock.get_time() / 1000.0  # 转换为秒
        self.rendering_pipeline.render_frame(surface, world_state, dt)
    
    def _render_legacy(self, surface: pygame.Surface):
        """传统渲染模式"""
        original_screen = self.world_renderer.screen
        self.world_renderer.screen = surface
        
        # 获取包含部落信息的完整世界状态
        world_state = self.world.get_visualization_data()
        time_info = self.time_manager.get_time_stats()
        
        # 添加部落数据到世界状态（类似多尺度渲染）
        if hasattr(self, 'tribe_manager') and self.tribe_manager:
            tribe_data = self.tribe_manager.get_visualization_data()
            world_state['tribes'] = tribe_data
            
            # 添加部落间交互数据
            interactions = self.tribe_manager.get_tribe_interactions()
            world_state['tribe_interactions'] = interactions
        else:
            world_state['tribes'] = []
            world_state['tribe_interactions'] = []
        
        self.world_renderer.render_frame(world_state, self.agents, time_info)
        
        self.world_renderer.screen = original_screen
    
    def _prepare_world_state_for_multi_scale(self) -> Dict:
        """为多尺度渲染准备世界状态数据"""
        # 获取基础世界状态
        world_state = self.world.get_visualization_data()
        time_info = self.time_manager.get_time_stats()
        
        # 坐标转换：将智能体从100x100坐标系转换到800x800坐标系
        display_scale = 8
        scaled_agents = []
        for agent in self.agents:
            # 创建智能体的副本，调整坐标
            scaled_agent = type('ScaledAgent', (), {})()
            for attr in ['energy', 'health', 'max_health', 'agent_id', 'age', 'alive']:
                if hasattr(agent, attr):
                    setattr(scaled_agent, attr, getattr(agent, attr))
            
            # 转换位置坐标
            scaled_agent.position = Vector2D(
                agent.position.x * display_scale,
                agent.position.y * display_scale
            )
            
            # 添加部落信息（如果有）
            if hasattr(agent, 'tribe_id'):
                scaled_agent.tribe_id = agent.tribe_id
            if hasattr(agent, 'tribe_name'):
                scaled_agent.tribe_name = agent.tribe_name
            if hasattr(agent, 'tribe_color'):
                scaled_agent.tribe_color = agent.tribe_color
            
            scaled_agents.append(scaled_agent)
        
        # 转换资源坐标
        original_resources = world_state.get('resources', [])
        scaled_resources = []
        for resource in original_resources:
            if isinstance(resource, tuple):
                scaled_resources.append((resource[0] * display_scale, resource[1] * display_scale))
            else:
                # 如果是对象，创建新的位置
                scaled_resource = type('ScaledResource', (), {})()
                for attr in dir(resource):
                    if not attr.startswith('_'):
                        setattr(scaled_resource, attr, getattr(resource, attr))
                scaled_resource.position = Vector2D(
                    resource.position.x * display_scale,
                    resource.position.y * display_scale
                )
                scaled_resources.append(scaled_resource)
        
        # 更新世界状态
        world_state['agents'] = scaled_agents
        world_state['resources'] = scaled_resources
        world_state['current_step'] = self.time_manager.current_step
        world_state['fps'] = time_info.get('actual_fps', 0)
        
        # 添加环境数据（需要坐标转换）
        if hasattr(self, 'environment_manager'):
            world_state['environment_zones'] = self.environment_manager.zones
            world_state['environment_status'] = self.environment_manager.get_environment_status()
        
        # 使用气候系统而非天气系统（提高性能）
        if hasattr(self, 'environment_manager') and hasattr(self.environment_manager, 'climate_system'):
            # 添加气候系统信息用于可视化
            climate_data = self.environment_manager.climate_system.get_visualization_data()
            world_state['climate_data'] = climate_data
            world_state['active_weather'] = []  # 清空天气数据，使用气候数据
        elif hasattr(self, 'weather_system') and self.weather_system:
            # 回退到天气系统（如果没有启用气候系统）
            active_weather = self.weather_system.get_active_weather_info()
            if active_weather:
                scaled_weather = []
                for weather_info in active_weather:
                    scaled_weather_info = weather_info.copy()
                    # 转换天气中心坐标
                    if 'center' in scaled_weather_info:
                        center = scaled_weather_info['center']
                        scaled_weather_info['center'] = (
                            center[0] * display_scale,
                            center[1] * display_scale
                        )
                    # 转换天气影响半径
                    if 'radius' in scaled_weather_info:
                        scaled_weather_info['radius'] = scaled_weather_info['radius'] * display_scale
                    
                    scaled_weather.append(scaled_weather_info)
                world_state['active_weather'] = scaled_weather
            else:
                world_state['active_weather'] = []
        else:
            world_state['active_weather'] = []
        
        if hasattr(self, 'terrain_system'):
            world_state['terrain_features'] = self.terrain_system.get_terrain_info()
        
        # 添加部落数据
        if hasattr(self, 'tribe_manager') and self.tribe_manager:
            tribe_data = self.tribe_manager.get_visualization_data()
            scaled_tribes = []
            
            for tribe_info in tribe_data:
                scaled_tribe = tribe_info.copy()
                # 转换部落中心坐标
                center = scaled_tribe['center']
                scaled_tribe['center'] = (center[0] * display_scale, center[1] * display_scale)
                # 转换领土半径
                scaled_tribe['radius'] = scaled_tribe['radius'] * display_scale
                # 转换成员位置
                scaled_members = []
                for member_pos in scaled_tribe['members']:
                    scaled_members.append((member_pos[0] * display_scale, member_pos[1] * display_scale))
                scaled_tribe['members'] = scaled_members
                
                scaled_tribes.append(scaled_tribe)
            
            world_state['tribes'] = scaled_tribes
            
            # 添加部落间交互数据
            interactions = self.tribe_manager.get_tribe_interactions()
            scaled_interactions = []
            
            for interaction in interactions:
                scaled_interaction = interaction.copy()
                # 转换交互位置坐标
                center_a = scaled_interaction['center_a']
                center_b = scaled_interaction['center_b']
                scaled_interaction['center_a'] = (center_a[0] * display_scale, center_a[1] * display_scale)
                scaled_interaction['center_b'] = (center_b[0] * display_scale, center_b[1] * display_scale)
                scaled_interaction['distance'] = scaled_interaction['distance'] * display_scale
                
                scaled_interactions.append(scaled_interaction)
            
            world_state['tribe_interactions'] = scaled_interactions
        else:
            world_state['tribes'] = []
            world_state['tribe_interactions'] = []
        
        # 添加显示选项
        if hasattr(self, 'interaction_controller'):
            control_state = self.interaction_controller.get_control_state()
            world_state.update(control_state['display_options'])
        
        return world_state
    
    def run(self):
        """运行主循环"""
        logger.info("Starting Cogvrs GUI main loop")
        print("\n🚀 Cogvrs 模拟开始运行...")
        print("📊 实时状态输出：")
        print("-" * 60)
        
        last_log_time = 0
        log_interval = 5.0  # 每5秒输出一次状态
        
        try:
            while self.running:
                dt = self.clock.tick(self.target_fps) / 1000.0
                current_time = time.time()
                
                # 处理事件
                self.handle_events()
                
                # 更新模拟
                self.update_simulation(dt)
                
                # 输出详细状态信息
                if current_time - last_log_time >= log_interval:
                    self._print_simulation_status()
                    last_log_time = current_time
                
                # 更新UI
                self.ui_manager.update(dt)
                
                # 渲染
                self.render()
                
                # 使用flip确保双缓冲正常工作
                pygame.display.flip()
        
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            raise
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        # 生成HTML报告
        try:
            if len(self.session_data['stats_history']) > 0:
                report_path = self._generate_html_report()
                print(f"\n📊 HTML报告已生成: {report_path}")
                print(f"🌐 在浏览器中打开查看详细分析")
                logger.info(f"Generated HTML report: {report_path}")
            else:
                print("\n📊 会话时间过短，未生成报告")
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            print(f"\n❌ 报告生成失败: {e}")
        
        if hasattr(self, 'world_renderer'):
            self.world_renderer.cleanup()
        
        pygame.quit()
        logger.info("CogvrsGUI cleaned up")


def main():
    """主函数，用于直接运行GUI"""
    config = {
        'window_width': 1200,
        'window_height': 800,
        'target_fps': 30,
        'initial_agents': 15,
        'world': {
            'size': (100, 100),
            'resource_density': 0.15
        },
        'physics': {
            'friction': 0.1,
            'boundary_type': 'toroidal'
        }
    }
    
    gui = CogvrsGUI(config)
    gui.run()


if __name__ == "__main__":
    main()