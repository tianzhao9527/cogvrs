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
from ..agents import SimpleAgent
from .world_view import WorldRenderer

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
    
    def __init__(self, config: Dict):
        self.config = config
        self.running = True
        self.paused = False
        
        # 初始化pygame
        pygame.init()
        
        # 窗口设置
        self.window_width = config.get('window_width', 1200)
        self.window_height = config.get('window_height', 800)
        self.world_view_width = 800
        self.world_view_height = 600
        self.panel_width = 400
        
        # 创建主窗口
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Cogvrs - Cognitive Universe Simulation")
        
        # 创建GUI管理器
        self.ui_manager = pygame_gui.UIManager((self.window_width, self.window_height))
        
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
        
        # 创建UI元素
        self._create_ui_elements()
        
        # 时间控制
        self.clock = pygame.time.Clock()
        self.target_fps = config.get('target_fps', 30)
        
        logger.info(f"CogvrsGUI initialized: {self.window_width}x{self.window_height}")
    
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
        world_config.update({
            'size': (100, 100),
            'resource_density': 0.15,
            'max_agents': 50
        })
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
        
        # 统计信息区域
        stats_y = add_agent_y + 60
        self.stats_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(button_x, stats_y, 250, 200),
            html_text="<b>Statistics</b><br>Loading...",
            manager=self.ui_manager
        )
        
        # 详细信息区域
        details_y = stats_y + 220
        self.details_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(button_x, details_y, 250, 150),
            html_text="<b>Selected Agent</b><br>Click an agent to view details",
            manager=self.ui_manager
        )
        
        # 控制说明
        help_y = details_y + 170
        help_text = ("<b>Controls:</b><br>"
                    "G - Toggle Grid<br>"
                    "T - Toggle Trajectories<br>"
                    "C - Toggle Connections<br>"
                    "P - Toggle Perception<br>"
                    "R - Reset Trajectories<br>"
                    "Space - Pause/Resume")
        
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
        
        # 更新世界
        self.world.update(dt)
        
        # 更新智能体
        alive_agents = []
        for agent in self.agents:
            if agent.alive:
                # 获取附近的智能体和资源
                nearby_agents = self._get_nearby_agents(agent)
                nearby_resources = self._get_nearby_resources(agent)
                
                # 更新智能体
                world_state = self.world.get_world_state()
                agent.update(dt, world_state, nearby_agents, nearby_resources)
                
                alive_agents.append(agent)
        
        # 应用物理效果
        physics_objects = [agent for agent in alive_agents if agent.alive]
        self.physics.apply_physics(physics_objects)
        
        # 处理繁殖
        self._handle_reproduction(alive_agents)
        
        # 更新智能体列表
        self.agents = alive_agents
        
        # 如果所有智能体都死了，自动添加新的
        if len(self.agents) == 0:
            self._add_random_agents(5)
    
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
        
        for agent in agents:
            # 检查繁殖条件
            if (agent.energy > 80 and 
                agent.age > 50 and 
                agent.offspring_count < 3 and
                len(agents) < 50):  # 限制总数量
                
                # 寻找繁殖伙伴
                nearby_agents = self._get_nearby_agents(agent)
                suitable_partners = [
                    a for a in nearby_agents 
                    if a.energy > 70 and a.age > 40 and a.offspring_count < 3
                ]
                
                if suitable_partners and len(new_agents) < 5:  # 限制每轮繁殖数量
                    # 繁殖
                    child = agent.clone(mutation_rate=0.1)
                    child.birth_time = self.time_manager.current_step
                    new_agents.append(child)
                    
                    # 更新父母状态
                    agent.offspring_count += 1
                    agent.energy -= 30
        
        # 添加新生儿
        self.agents.extend(new_agents)
        if new_agents:
            logger.info(f"New agents born: {len(new_agents)}")
    
    def _add_random_agents(self, count: int):
        """添加随机智能体"""
        for _ in range(count):
            agent_config = self._create_agent_config()
            agent = SimpleAgent(agent_config)
            agent.birth_time = self.time_manager.current_step
            self.agents.append(agent)
        
        logger.info(f"Added {count} new agents")
    
    def _update_ui_info(self):
        """更新UI信息"""
        # 统计信息
        alive_agents = [a for a in self.agents if a.alive]
        
        if alive_agents:
            avg_age = sum(a.age for a in alive_agents) / len(alive_agents)
            avg_energy = sum(a.energy for a in alive_agents) / len(alive_agents)
            avg_health = sum(a.health for a in alive_agents) / len(alive_agents)
            total_offspring = sum(a.offspring_count for a in alive_agents)
            total_interactions = sum(a.social_interactions for a in alive_agents)
        else:
            avg_age = avg_energy = avg_health = total_offspring = total_interactions = 0
        
        world_state = self.world.get_world_state()
        time_stats = self.time_manager.get_time_stats()
        
        stats_html = f"""
        <b>World Statistics</b><br>
        Time Step: {time_stats['current_step']}<br>
        Agents: {len(alive_agents)}<br>
        Avg Age: {avg_age:.1f}<br>
        Avg Energy: {avg_energy:.1f}<br>
        Avg Health: {avg_health:.1f}<br>
        Total Offspring: {total_offspring}<br>
        Social Interactions: {total_interactions}<br>
        Resources: {world_state['num_resources']}<br>
        Total Resources: {world_state['total_resources']:.0f}<br>
        FPS: {time_stats['actual_fps']:.1f}
        """
        
        self.stats_text.html_text = stats_html
        self.stats_text.rebuild()
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._toggle_pause()
                else:
                    # 传递给世界渲染器
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
    
    def render(self):
        """渲染界面"""
        # 清空屏幕
        self.screen.fill((15, 15, 25))
        
        # 渲染世界视图到子表面
        world_surface = pygame.Surface((self.world_view_width, self.world_view_height))
        
        # 临时替换渲染器的屏幕
        original_screen = self.world_renderer.screen
        self.world_renderer.screen = world_surface
        
        # 渲染世界
        world_state = self.world.get_visualization_data()
        time_info = self.time_manager.get_time_stats()
        self.world_renderer.render_frame(world_state, self.agents, time_info)
        
        # 恢复原始屏幕
        self.world_renderer.screen = original_screen
        
        # 将世界视图绘制到主屏幕
        self.screen.blit(world_surface, (10, 10))
        
        # 绘制世界视图边框
        pygame.draw.rect(
            self.screen, (100, 100, 100),
            (8, 8, self.world_view_width + 4, self.world_view_height + 4), 2
        )
        
        # 绘制控制面板背景
        pygame.draw.rect(self.screen, (25, 25, 35), self.control_panel)
        pygame.draw.rect(self.screen, (60, 60, 80), self.control_panel, 2)
        
        # 更新UI信息
        self._update_ui_info()
        
        # 渲染GUI元素
        self.ui_manager.draw_ui(self.screen)
    
    def run(self):
        """运行主循环"""
        logger.info("Starting Cogvrs GUI main loop")
        
        try:
            while self.running:
                dt = self.clock.tick(self.target_fps) / 1000.0
                
                # 处理事件
                self.handle_events()
                
                # 更新模拟
                self.update_simulation(dt)
                
                # 更新UI
                self.ui_manager.update(dt)
                
                # 渲染
                self.render()
                
                # 更新显示
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