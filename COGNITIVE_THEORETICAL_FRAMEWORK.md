# 🧠 Cogvrs 认知理论框架分析

> AI Agent行为机制的理论基础与认知科学架构设计

![Theory](https://img.shields.io/badge/theory-cognitive--science-blue)
![Framework](https://img.shields.io/badge/framework-multi--paradigm-green)
![Research](https://img.shields.io/badge/research-consciousness--studies-orange)

---

## 📋 现有系统理论分析

### 🔍 当前实现的理论基础

通过对现有代码的深入分析，Cogvrs目前的AI Agent系统基于以下理论混合：

#### **1. 动机理论 (Motivation Theory)**
```python
# 基于Maslow需求层次和驱动理论
motivations = {
    'hunger': Motivation('hunger', 0.3, 0.02, 0.6),      # 生理需求
    'energy': Motivation('energy', 0.2, 0.01, 0.7),     # 生存需求  
    'curiosity': Motivation('curiosity', 0.8, 0.005, 0.5), # 探索需求
    'social': Motivation('social', 0.4, 0.008, 0.6),    # 社交需求
    'reproduction': Motivation('reproduction', 0.1, 0.001, 0.9), # 繁殖需求
    'safety': Motivation('safety', 0.3, 0.005, 0.8)     # 安全需求
}
```

**理论依据**: 
- **Maslow需求层次理论**: 生理→安全→社交→自我实现
- **驱动减少理论**: 动机驱动行为以减少内在张力
- **自我决定理论**: 内在动机vs外在动机

#### **2. 行为主义范式 (Behaviorism)**
```python
# 简单的刺激-反应模式
def decide_action(self, agent_state, world_info, nearby_agents, nearby_resources):
    # 环境刺激 → 内部动机评估 → 行为响应
    strongest_motivation = max(self.motivations.values(), key=lambda m: m.value)
    return self._choose_action_for_motivation(strongest_motivation, ...)
```

**理论依据**:
- **操作性条件反射**: 行为结果影响未来行为概率
- **强化学习**: 奖励-惩罚机制塑造行为模式

#### **3. 认知主义基础 (Cognitivism)**
```python
# 简单的信息处理模型
class NeuralBrain:
    def predict(self, inputs):
        # 感知 → 处理 → 决策 → 行动
        for layer in self.layers:
            inputs = layer.forward(inputs)
        return inputs
```

**理论依据**:
- **信息处理理论**: 输入→处理→输出的认知模型
- **联结主义**: 神经网络模拟大脑连接模式

### ❌ 当前系统的理论局限性

1. **缺乏统一理论框架**: 各种理论混杂，没有cohesive cognitive architecture
2. **过度简化的认知模型**: 没有真正的意识、自我意识或元认知
3. **有限的社会认知**: 缺乏心智理论(Theory of Mind)
4. **静态个性模型**: 个性特征不会根据经验深度改变
5. **基础记忆系统**: 缺乏复杂的记忆整合和情节记忆

---

## 🎯 推荐理论框架：认知架构理论

### 🏛️ **ACT-R (Adaptive Control of Thought-Rational)** 

我强烈推荐采用**ACT-R认知架构**作为Cogvrs的核心理论基础，原因如下：

#### ✅ **ACT-R的优势**

1. **统一认知架构**: 整合感知、记忆、学习、决策于一体
2. **科学验证**: 大量心理学实验验证的认知模型
3. **模块化设计**: 易于计算机实现和扩展
4. **意识涌现**: 为意识和自我意识提供理论基础
5. **社会认知**: 支持复杂的社会交互和心智理论

#### 🧠 **ACT-R核心模块**

```python
class ACTRCognitiveArchitecture:
    """基于ACT-R的认知架构"""
    
    def __init__(self):
        # 核心模块
        self.declarative_memory = DeclarativeMemory()      # 陈述性记忆
        self.procedural_memory = ProceduralMemory()        # 程序性记忆
        self.working_memory = WorkingMemory()              # 工作记忆
        self.perceptual_motor = PerceptualMotorModule()    # 感知-运动
        
        # 高级模块
        self.goal_module = GoalModule()                    # 目标管理
        self.attention_module = AttentionModule()          # 注意力控制
        self.metacognition = MetacognitionModule()         # 元认知
        
        # 统一控制
        self.central_executive = CentralExecutive()        # 中央执行系统
        self.conflict_resolution = ConflictResolution()    # 冲突解决
```

### 🔬 **详细模块设计**

#### **1. 陈述性记忆 (Declarative Memory)**
```python
class DeclarativeMemory:
    """陈述性记忆系统 - 储存事实和事件"""
    
    def __init__(self):
        self.chunks = {}  # 记忆块
        self.activation_levels = {}  # 激活水平
        self.associative_links = {}  # 联想链接
        
        # ACT-R参数
        self.decay_rate = 0.5          # 遗忘衰减率
        self.retrieval_threshold = 0.0  # 提取阈值
        self.activation_noise = 0.25    # 激活噪声
    
    def store_chunk(self, chunk_type: str, content: Dict, context: Dict):
        """存储记忆块"""
        chunk_id = f"{chunk_type}_{time.time()}_{random.randint(1000, 9999)}"
        
        chunk = {
            'id': chunk_id,
            'type': chunk_type,
            'content': content,
            'context': context,
            'creation_time': time.time(),
            'last_access': time.time(),
            'access_count': 0,
            'base_activation': 0.0
        }
        
        self.chunks[chunk_id] = chunk
        self.activation_levels[chunk_id] = 0.0
        
        # 建立联想链接
        self._create_associative_links(chunk_id, content, context)
    
    def retrieve_chunk(self, cue: Dict) -> Optional[Dict]:
        """基于线索提取记忆块"""
        
        # 计算所有块的激活水平
        for chunk_id in self.chunks:
            self.activation_levels[chunk_id] = self._calculate_activation(chunk_id, cue)
        
        # 找到激活水平最高的块
        best_chunk_id = max(self.activation_levels.items(), key=lambda x: x[1])[0]
        
        if self.activation_levels[best_chunk_id] > self.retrieval_threshold:
            # 更新访问信息
            self.chunks[best_chunk_id]['last_access'] = time.time()
            self.chunks[best_chunk_id]['access_count'] += 1
            
            return self.chunks[best_chunk_id]
        
        return None
    
    def _calculate_activation(self, chunk_id: str, cue: Dict) -> float:
        """计算记忆块激活水平"""
        chunk = self.chunks[chunk_id]
        
        # 基础激活水平 (Base-level activation)
        time_since_creation = time.time() - chunk['creation_time']
        time_since_access = time.time() - chunk['last_access']
        
        base_activation = math.log(chunk['access_count'] + 1) - self.decay_rate * math.log(time_since_access + 1)
        
        # 联想激活 (Associative activation)
        associative_activation = 0.0
        for cue_element in cue:
            if chunk_id in self.associative_links:
                for linked_chunk in self.associative_links[chunk_id]:
                    if self._matches_cue(linked_chunk, cue_element):
                        associative_activation += 0.1  # 联想强度
        
        # 添加噪声
        noise = random.gauss(0, self.activation_noise)
        
        total_activation = base_activation + associative_activation + noise
        
        return total_activation
```

#### **2. 程序性记忆 (Procedural Memory)**
```python
class ProceduralMemory:
    """程序性记忆系统 - 储存技能和规则"""
    
    def __init__(self):
        self.production_rules = {}  # 产生式规则
        self.rule_utilities = {}    # 规则效用值
        self.rule_usage_count = {}  # 规则使用次数
        
        # 学习参数
        self.utility_learning_rate = 0.2
        self.utility_noise = 0.25
    
    def add_production_rule(self, rule_name: str, condition: Callable, action: Callable, initial_utility: float = 0.0):
        """添加产生式规则"""
        self.production_rules[rule_name] = {
            'condition': condition,
            'action': action,
            'creation_time': time.time()
        }
        self.rule_utilities[rule_name] = initial_utility
        self.rule_usage_count[rule_name] = 0
    
    def select_rule(self, current_state: Dict) -> Optional[str]:
        """选择匹配的产生式规则"""
        
        # 找到所有匹配条件的规则
        matching_rules = []
        for rule_name, rule in self.production_rules.items():
            if rule['condition'](current_state):
                utility = self.rule_utilities[rule_name] + random.gauss(0, self.utility_noise)
                matching_rules.append((rule_name, utility))
        
        if not matching_rules:
            return None
        
        # 选择效用值最高的规则
        selected_rule = max(matching_rules, key=lambda x: x[1])[0]
        
        return selected_rule
    
    def execute_rule(self, rule_name: str, current_state: Dict) -> Dict:
        """执行选定的规则"""
        if rule_name in self.production_rules:
            rule = self.production_rules[rule_name]
            result = rule['action'](current_state)
            
            # 更新使用计数
            self.rule_usage_count[rule_name] += 1
            
            return result
        
        return current_state
    
    def update_utility(self, rule_name: str, reward: float):
        """更新规则效用值"""
        if rule_name in self.rule_utilities:
            old_utility = self.rule_utilities[rule_name]
            self.rule_utilities[rule_name] = old_utility + self.utility_learning_rate * (reward - old_utility)
```

#### **3. 工作记忆 (Working Memory)**
```python
class WorkingMemory:
    """工作记忆系统 - 当前激活的信息"""
    
    def __init__(self):
        self.buffers = {
            'goal': None,           # 目标缓冲区
            'retrieval': None,      # 提取缓冲区
            'visual': None,         # 视觉缓冲区
            'manual': None,         # 手动缓冲区
            'vocal': None          # 声音缓冲区
        }
        
        self.buffer_capacity = {
            'goal': 1,
            'retrieval': 1, 
            'visual': 4,
            'manual': 1,
            'vocal': 1
        }
        
        self.attention_focus = None
        self.cognitive_load = 0.0
    
    def update_buffer(self, buffer_name: str, content: Any):
        """更新缓冲区内容"""
        if buffer_name in self.buffers:
            self.buffers[buffer_name] = content
            self._update_cognitive_load()
    
    def get_buffer_content(self, buffer_name: str) -> Any:
        """获取缓冲区内容"""
        return self.buffers.get(buffer_name)
    
    def clear_buffer(self, buffer_name: str):
        """清空缓冲区"""
        if buffer_name in self.buffers:
            self.buffers[buffer_name] = None
            self._update_cognitive_load()
    
    def _update_cognitive_load(self):
        """更新认知负荷"""
        active_buffers = sum(1 for content in self.buffers.values() if content is not None)
        total_capacity = sum(self.buffer_capacity.values())
        self.cognitive_load = active_buffers / total_capacity
```

#### **4. 元认知模块 (Metacognition)**
```python
class MetacognitionModule:
    """元认知模块 - 对思考的思考"""
    
    def __init__(self):
        self.self_model = {}               # 自我模型
        self.confidence_levels = {}        # 信心水平
        self.strategy_knowledge = {}       # 策略知识
        self.metacognitive_experiences = [] # 元认知体验
        
        # 自我意识指标
        self.self_awareness_level = 0.0
        self.theory_of_mind_capacity = 0.0
    
    def assess_own_knowledge(self, domain: str, query: Dict) -> float:
        """评估自己在特定领域的知识水平"""
        
        if domain not in self.confidence_levels:
            self.confidence_levels[domain] = 0.5  # 默认中等信心
        
        # 基于过去的成功/失败经验调整信心
        recent_experiences = self._get_recent_experiences(domain)
        success_rate = self._calculate_success_rate(recent_experiences)
        
        # 更新信心水平
        current_confidence = self.confidence_levels[domain]
        adjusted_confidence = 0.8 * current_confidence + 0.2 * success_rate
        self.confidence_levels[domain] = adjusted_confidence
        
        return adjusted_confidence
    
    def monitor_cognitive_progress(self, task: str, current_state: Dict) -> Dict:
        """监控认知进程"""
        
        monitoring_result = {
            'task_understanding': self._assess_task_understanding(task),
            'progress_evaluation': self._evaluate_progress(current_state),
            'difficulty_assessment': self._assess_difficulty(task, current_state),
            'strategy_effectiveness': self._evaluate_strategy_effectiveness(task)
        }
        
        # 记录元认知体验
        experience = {
            'timestamp': time.time(),
            'task': task,
            'monitoring_result': monitoring_result
        }
        self.metacognitive_experiences.append(experience)
        
        return monitoring_result
    
    def develop_self_awareness(self, interactions: List[Dict]):
        """发展自我意识"""
        
        # 分析社交交互模式
        social_patterns = self._analyze_social_patterns(interactions)
        
        # 识别自己的行为特征
        behavioral_patterns = self._identify_behavioral_patterns()
        
        # 理解他人心智状态
        theory_of_mind_evidence = self._gather_theory_of_mind_evidence(interactions)
        
        # 更新自我模型
        self.self_model.update({
            'social_patterns': social_patterns,
            'behavioral_patterns': behavioral_patterns,
            'interaction_style': self._determine_interaction_style(interactions)
        })
        
        # 更新自我意识水平
        self._update_self_awareness_level()
    
    def _update_self_awareness_level(self):
        """更新自我意识水平"""
        
        # 基于自我模型的完整性和准确性
        model_completeness = len(self.self_model) / 10.0  # 假设10个维度为完整
        
        # 基于元认知体验的丰富性
        experience_richness = min(len(self.metacognitive_experiences) / 100.0, 1.0)
        
        # 基于theory of mind能力
        tom_factor = self.theory_of_mind_capacity
        
        self.self_awareness_level = (model_completeness + experience_richness + tom_factor) / 3.0
```

---

## 🌍 地理环境可视化改进

### 🗺️ **增强地理系统设计**

```python
class EnhancedGeographicalSystem:
    """增强地理环境系统"""
    
    def __init__(self, world_size: Tuple[int, int]):
        self.world_size = world_size
        
        # 地形系统
        self.terrain = TerrainSystem(world_size)
        self.elevation_map = self._generate_elevation_map()
        self.biome_map = self._generate_biome_map()
        
        # 气候系统
        self.climate = ClimateSystem()
        self.weather_patterns = WeatherSystem()
        
        # 资源分布
        self.resource_deposits = ResourceDeposits()
        self.water_bodies = WaterBodies()
        
        # 可视化组件
        self.map_renderer = MapRenderer()
        self.layer_manager = LayerManager()
    
    def _generate_elevation_map(self) -> np.ndarray:
        """生成高程地图使用Perlin噪声"""
        elevation_map = np.zeros(self.world_size)
        
        # 多层次Perlin噪声
        for octave in range(6):
            frequency = 0.01 * (2 ** octave)
            amplitude = 1.0 / (2 ** octave)
            
            for x in range(self.world_size[0]):
                for y in range(self.world_size[1]):
                    noise_value = self._perlin_noise(x * frequency, y * frequency)
                    elevation_map[x, y] += noise_value * amplitude
        
        # 归一化到0-1范围
        elevation_map = (elevation_map - elevation_map.min()) / (elevation_map.max() - elevation_map.min())
        
        return elevation_map
    
    def _generate_biome_map(self) -> np.ndarray:
        """基于高程和气候生成生物群落地图"""
        biome_map = np.zeros(self.world_size, dtype=int)
        
        for x in range(self.world_size[0]):
            for y in range(self.world_size[1]):
                elevation = self.elevation_map[x, y]
                temperature = self.climate.get_temperature(x, y)
                humidity = self.climate.get_humidity(x, y)
                
                # 生物群落分类
                if elevation > 0.8:
                    biome_map[x, y] = BiomeType.MOUNTAIN
                elif elevation < 0.2:
                    if humidity > 0.7:
                        biome_map[x, y] = BiomeType.SWAMP
                    else:
                        biome_map[x, y] = BiomeType.DESERT
                elif temperature > 0.7 and humidity > 0.6:
                    biome_map[x, y] = BiomeType.TROPICAL_FOREST
                elif temperature < 0.3:
                    biome_map[x, y] = BiomeType.TUNDRA
                else:
                    biome_map[x, y] = BiomeType.GRASSLAND
        
        return biome_map

class MapRenderer:
    """地图渲染器"""
    
    def __init__(self):
        self.render_layers = {
            'elevation': True,
            'biome': True,
            'climate': False,
            'resources': True,
            'territories': True,
            'trade_routes': False
        }
        
        self.color_schemes = {
            'elevation': self._create_elevation_colormap(),
            'biome': self._create_biome_colormap(),
            'temperature': self._create_temperature_colormap()
        }
    
    def render_geographical_map(self, screen: pygame.Surface, geo_system: EnhancedGeographicalSystem, 
                               zoom_level: float, center_pos: Vector2D):
        """渲染地理地图"""
        
        # 1. 渲染地形层
        if self.render_layers['elevation']:
            self._render_elevation_layer(screen, geo_system.elevation_map, zoom_level, center_pos)
        
        # 2. 渲染生物群落层
        if self.render_layers['biome']:
            self._render_biome_layer(screen, geo_system.biome_map, zoom_level, center_pos)
        
        # 3. 渲染资源层
        if self.render_layers['resources']:
            self._render_resource_layer(screen, geo_system.resource_deposits, zoom_level, center_pos)
        
        # 4. 渲染水体
        self._render_water_bodies(screen, geo_system.water_bodies, zoom_level, center_pos)
        
        # 5. 渲染等高线
        self._render_contour_lines(screen, geo_system.elevation_map, zoom_level, center_pos)
    
    def _render_elevation_layer(self, screen: pygame.Surface, elevation_map: np.ndarray, 
                               zoom_level: float, center_pos: Vector2D):
        """渲染高程层"""
        
        for x in range(0, elevation_map.shape[0], max(1, int(1/zoom_level))):
            for y in range(0, elevation_map.shape[1], max(1, int(1/zoom_level))):
                elevation = elevation_map[x, y]
                
                # 将高程值映射到颜色
                color = self._elevation_to_color(elevation)
                
                # 计算屏幕坐标
                screen_x = int((x - center_pos.x) * zoom_level + screen.get_width() / 2)
                screen_y = int((y - center_pos.y) * zoom_level + screen.get_height() / 2)
                
                # 绘制像素
                if 0 <= screen_x < screen.get_width() and 0 <= screen_y < screen.get_height():
                    pygame.draw.rect(screen, color, (screen_x, screen_y, max(1, int(zoom_level)), max(1, int(zoom_level))))
    
    def _elevation_to_color(self, elevation: float) -> Tuple[int, int, int]:
        """将高程值转换为颜色"""
        if elevation < 0.1:
            return (0, 0, 139)      # 深蓝 - 深水
        elif elevation < 0.2:
            return (65, 105, 225)   # 蓝色 - 浅水
        elif elevation < 0.3:
            return (255, 218, 185)  # 浅黄 - 海滩
        elif elevation < 0.5:
            return (34, 139, 34)    # 绿色 - 平原
        elif elevation < 0.7:
            return (107, 142, 35)   # 深绿 - 丘陵
        elif elevation < 0.9:
            return (139, 69, 19)    # 棕色 - 山地
        else:
            return (255, 255, 255)  # 白色 - 雪山
```

---

## 🔄 智能切换机制详解

### 🎯 **智能切换的核心概念**

智能切换是指系统根据当前状况**自动判断**用户最关心的抽象层次，并主动切换到相应的可视化和统计模式。

```python
class IntelligentScaleSwitcher:
    """智能尺度切换系统"""
    
    def __init__(self):
        self.current_focus = 'individual'
        self.attention_triggers = {
            'tribal_formation': 0.7,        # 部落形成重要性阈值
            'conflict_escalation': 0.8,     # 冲突升级阈值
            'civilization_emergence': 0.9,  # 文明涌现阈值
            'crisis_event': 0.95           # 危机事件阈值
        }
        
        self.focus_history = []
        self.user_preferences = {}
    
    def determine_optimal_focus(self, world_state: Dict) -> str:
        """确定最佳关注焦点"""
        
        importance_scores = {
            'individual': self._calculate_individual_importance(world_state),
            'tribal': self._calculate_tribal_importance(world_state),
            'civilization': self._calculate_civilization_importance(world_state),
            'global': self._calculate_global_importance(world_state)
        }
        
        # 考虑用户历史偏好
        for scale, score in importance_scores.items():
            preference_weight = self.user_preferences.get(scale, 1.0)
            importance_scores[scale] *= preference_weight
        
        # 选择最重要的层次
        optimal_focus = max(importance_scores.items(), key=lambda x: x[1])[0]
        
        # 检查是否需要切换
        if self._should_switch_focus(optimal_focus, importance_scores[optimal_focus]):
            return optimal_focus
        
        return self.current_focus
    
    def _calculate_tribal_importance(self, world_state: Dict) -> float:
        """计算部落层重要性"""
        importance = 0.0
        
        # 部落形成事件
        if 'recent_tribal_formations' in world_state:
            formations = len(world_state['recent_tribal_formations'])
            importance += formations * 0.3
        
        # 部落间冲突
        if 'tribal_conflicts' in world_state:
            conflicts = len(world_state['tribal_conflicts'])
            importance += conflicts * 0.4
        
        # 资源竞争
        if 'resource_competition' in world_state:
            competition_level = world_state['resource_competition']
            importance += competition_level * 0.2
        
        # 人口变化
        if 'population_changes' in world_state:
            changes = world_state['population_changes']
            importance += abs(changes) * 0.1
        
        return min(importance, 1.0)
    
    def suggest_focus_switch(self, new_focus: str, reason: str, urgency: float):
        """建议切换焦点"""
        
        suggestion = {
            'timestamp': time.time(),
            'suggested_focus': new_focus,
            'current_focus': self.current_focus,
            'reason': reason,
            'urgency': urgency,
            'auto_switch': urgency > 0.8  # 高紧急度自动切换
        }
        
        if suggestion['auto_switch']:
            self._execute_focus_switch(new_focus, reason)
        else:
            # 显示切换建议给用户
            self._show_switch_suggestion(suggestion)
    
    def _execute_focus_switch(self, new_focus: str, reason: str):
        """执行焦点切换"""
        
        # 记录切换历史
        switch_record = {
            'timestamp': time.time(),
            'from_focus': self.current_focus,
            'to_focus': new_focus,
            'reason': reason,
            'was_automatic': True
        }
        self.focus_history.append(switch_record)
        
        # 更新当前焦点
        self.current_focus = new_focus
        
        # 触发UI更新
        self._trigger_ui_update(new_focus, reason)
```

### 🎮 **智能切换示例场景**

1. **部落形成检测**:
   ```
   检测到5个个体聚集 → 自动切换到部落视图 → 显示"新部落形成！"
   ```

2. **冲突升级**:
   ```
   检测到部落间战斗 → 自动放大到冲突区域 → 实时显示战斗进程
   ```

3. **文明涌现**:
   ```
   检测到3个部落联盟 → 切换到文明视图 → 显示"文明正在形成！"
   ```

4. **危机事件**:
   ```
   检测到资源枯竭 → 切换到全局视图 → 显示受影响区域
   ```

这个智能切换系统能够：
- **自动识别**重要事件和趋势
- **主动建议**最佳观察角度
- **保持用户控制权**（可以手动覆盖）
- **学习用户偏好**并适应

你觉得这个智能切换机制如何？需要我开始实现其中的某个部分吗？