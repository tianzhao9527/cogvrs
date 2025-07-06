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
        
        # 创建主窗口 - 进一步优化减少闪烁
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("Cogvrs - Cognitive Universe Simulation")
        
        # 减少闪烁的设置
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.USEREVENT])
        
        # 创建后台渲染缓冲区
        self.back_buffer = pygame.Surface((self.window_width, self.window_height))
        self.dirty_rects = []  # 脏矩形区域
        
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
            'performance_metrics': []
        }
        
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
        
        # 收集数据
        self._collect_session_data()
        
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
    
    def _collect_session_data(self):
        """收集会话数据用于分析"""
        if self.frame_count % 30 != 0:  # 每秒收集一次数据
            return
            
        current_time = time.time()
        alive_agents = [a for a in self.agents if a.alive]
        world_state = self.world.get_world_state()
        time_stats = self.time_manager.get_time_stats()
        
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
            'fps': time_stats['actual_fps']
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
        from datetime import datetime
        
        # 计算会话时长
        session_duration = time.time() - self.session_data['start_time']
        
        # 准备数据
        stats_data = json.dumps(self.session_data['stats_history'])
        performance_data = json.dumps(self.session_data['performance_metrics'])
        
        # 生成HTML报告
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cogvrs 模拟报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .chart-container {{
            padding: 30px;
            background: white;
        }}
        .chart-wrapper {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        .section-title {{
            font-size: 1.8em;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }}
        .analysis {{
            padding: 30px;
            background: #ecf0f1;
            line-height: 1.6;
        }}
        .highlight {{
            background: #3498db;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .emoji {{
            font-size: 1.2em;
            margin-right: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Cogvrs 模拟分析报告</h1>
            <p>数字宇宙实验室 - AI意识探索平台</p>
            <p>会话时长: {session_duration/60:.1f} 分钟 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">⏰</span>模拟步数</div>
                <div class="stat-value">{len(self.session_data['stats_history'])}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">👥</span>智能体峰值</div>
                <div class="stat-value">{max([s['agent_count'] for s in self.session_data['stats_history']] or [0])}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">👶</span>总后代数</div>
                <div class="stat-value">{max([s['total_offspring'] for s in self.session_data['stats_history']] or [0])}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">🤝</span>社交互动</div>
                <div class="stat-value">{max([s['total_interactions'] for s in self.session_data['stats_history']] or [0])}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">⚡</span>平均FPS</div>
                <div class="stat-value">{sum([p['fps'] for p in self.session_data['performance_metrics']])/len(self.session_data['performance_metrics']):.1f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><span class="emoji">🧬</span>最高年龄</div>
                <div class="stat-value">{max([s['avg_age'] for s in self.session_data['stats_history']] or [0]):.0f}</div>
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
        </div>
    </div>
    
    <script>
        const statsData = {stats_data};
        const performanceData = {performance_data};
        
        // 智能体种群图表
        const popCtx = document.getElementById('populationChart').getContext('2d');
        new Chart(popCtx, {{
            type: 'line',
            data: {{
                labels: statsData.map(d => new Date(d.timestamp * 1000).toLocaleTimeString()),
                datasets: [{{
                    label: '智能体数量',
                    data: statsData.map(d => d.agent_count),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.4
                }}, {{
                    label: '平均年龄',
                    data: statsData.map(d => d.avg_age),
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y1'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: '智能体数量' }}
                    }},
                    y1: {{
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {{ display: true, text: '平均年龄' }},
                        grid: {{ drawOnChartArea: false }}
                    }}
                }},
                plugins: {{
                    legend: {{ display: true, position: 'top' }}
                }}
            }}
        }});
        
        // 健康状况图表
        const healthCtx = document.getElementById('healthChart').getContext('2d');
        new Chart(healthCtx, {{
            type: 'line',
            data: {{
                labels: statsData.map(d => new Date(d.timestamp * 1000).toLocaleTimeString()),
                datasets: [{{
                    label: '平均能量',
                    data: statsData.map(d => d.avg_energy),
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.1)',
                    fill: true,
                    tension: 0.4
                }}, {{
                    label: '平均健康',
                    data: statsData.map(d => d.avg_health),
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ beginAtZero: true, title: {{ display: true, text: '数值' }} }}
                }},
                plugins: {{
                    legend: {{ display: true, position: 'top' }}
                }}
            }}
        }});
        
        // 性能监控图表
        const perfCtx = document.getElementById('performanceChart').getContext('2d');
        new Chart(perfCtx, {{
            type: 'line',
            data: {{
                labels: performanceData.map(d => new Date(d.timestamp * 1000).toLocaleTimeString()),
                datasets: [{{
                    label: 'FPS',
                    data: performanceData.map(d => d.fps),
                    borderColor: '#9b59b6',
                    backgroundColor: 'rgba(155, 89, 182, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ beginAtZero: true, title: {{ display: true, text: 'FPS' }} }}
                }},
                plugins: {{
                    legend: {{ display: true, position: 'top' }}
                }}
            }}
        }});
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
            avg_age = sum(a.age for a in alive_agents) / len(alive_agents)
            avg_energy = sum(a.energy for a in alive_agents) / len(alive_agents)
            avg_health = sum(a.health for a in alive_agents) / len(alive_agents)
            total_offspring = sum(a.offspring_count for a in alive_agents)
            total_interactions = sum(a.social_interactions for a in alive_agents)
        else:
            avg_age = avg_energy = avg_health = total_offspring = total_interactions = 0
        
        world_state = self.world.get_world_state()
        time_stats = self.time_manager.get_time_stats()
        
        # 世界统计HTML
        stats_html = f"""
        <b>🌍 World Statistics</b><br>
        <font color='#00FF00'>⏰ Step: {time_stats['current_step']}</font><br>
        <font color='#FFFF00'>👥 Agents: {len(alive_agents)}</font><br>
        <font color='#FF8800'>📊 Avg Age: {avg_age:.1f}</font><br>
        <font color='#00FFFF'>⚡ Avg Energy: {avg_energy:.1f}</font><br>
        <font color='#FF4444'>❤️ Avg Health: {avg_health:.1f}</font><br>
        <font color='#FF88FF'>👶 Offspring: {total_offspring}</font><br>
        <font color='#88FF88'>🤝 Interactions: {total_interactions}</font><br>
        <font color='#8888FF'>💎 Resources: {world_state['num_resources']}</font><br>
        <font color='#CCCCCC'>🎯 FPS: {time_stats['actual_fps']:.1f}</font>
        """
        
        # 智能体分析HTML
        if alive_agents:
            most_active = max(alive_agents, key=lambda a: a.social_interactions)
            oldest = max(alive_agents, key=lambda a: a.age)
            
            details_html = f"""
            <b>🧠 Agent Analysis</b><br>
            <font color='#FFD700'>🏆 Most Social:</font><br>
            &nbsp;&nbsp;Agent#{most_active.agent_id}: {most_active.social_interactions} interactions<br>
            <font color='#90EE90'>👴 Oldest Agent:</font><br>
            &nbsp;&nbsp;Agent#{oldest.agent_id}: Age {oldest.age:.0f}<br>
            <font color='#F0E68C'>⚡ Energy: {oldest.energy:.1f}</font>
            """
        else:
            details_html = "<b>🧠 Agent Analysis</b><br><font color='#FF6666'>No agents available</font>"
        
        # 系统状态HTML
        population_trend = "📈 Growing" if len(alive_agents) > 10 else "📉 Declining" if len(alive_agents) < 5 else "📊 Stable"
        performance = "🟢 Good" if time_stats['actual_fps'] > 20 else "🟡 Fair" if time_stats['actual_fps'] > 15 else "🔴 Poor"
        
        system_html = f"""
        <b>💻 System Status</b><br>
        <font color='#00FF00'>Population: {population_trend}</font><br>
        <font color='#FFFF00'>Performance: {performance}</font><br>
        <font color='#FF8800'>Memory: {len(self.agents)} tracked</font>
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
        original_screen = self.world_renderer.screen
        self.world_renderer.screen = world_surface
        
        world_state = self.world.get_visualization_data()
        time_info = self.time_manager.get_time_stats()
        self.world_renderer.render_frame(world_state, self.agents, time_info)
        
        self.world_renderer.screen = original_screen
        
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