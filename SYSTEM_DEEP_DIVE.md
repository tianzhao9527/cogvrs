# 🧠 Cogvrs 系统深度解析 - 算法机制与原理

## 📊 核心指标详解与算法机制

### 1. 🧬 智能体生命系统

#### 🔢 **Agents (智能体数量)**
```python
# 统计逻辑
alive_agents = [agent for agent in self.agents if agent.alive]
agent_count = len(alive_agents)
```

**含义**: 当前存活的AI智能体总数
**机制**: 
- 每个智能体有`alive`布尔属性
- 死亡条件：`energy <= 0` 或 `health <= 0` 或 `age > max_lifespan`
- 动态变化：出生(繁殖)增加，死亡减少

**背后算法**:
```python
# 生命状态判断 (simple_agent.py)
def update_vital_signs(self, dt):
    # 能量消耗
    self.energy -= self.base_metabolism * dt
    
    # 健康衰减（年龄相关）
    aging_factor = min(self.age / 200.0, 1.0)
    self.health -= aging_factor * 0.1 * dt
    
    # 死亡判定
    if self.energy <= 0 or self.health <= 0:
        self.alive = False
```

---

### 2. ⚡ **Avg Energy (平均能量)**
```python
# 计算逻辑
energies = [agent.energy for agent in alive_agents]
avg_energy = sum(energies) / len(energies) if energies else 0
```

**含义**: 所有存活智能体的平均生命能量
**范围**: 0 - 150 (最大能量限制)
**机制**:

#### 🔋 能量系统算法
```python
class EnergySystem:
    def __init__(self):
        self.initial_energy = 100.0
        self.max_energy = 150.0
        self.base_metabolism = 0.5  # 基础代谢率
        
    def update_energy(self, agent, dt):
        # 1. 基础代谢消耗
        metabolic_cost = self.base_metabolism * dt
        
        # 2. 活动消耗（基于移动速度）
        movement_cost = agent.velocity.magnitude() * 0.1 * dt
        
        # 3. 神经网络思考消耗
        neural_cost = agent.brain.get_computation_cost() * dt
        
        # 4. 社交互动消耗
        social_cost = agent.social_interactions * 0.01 * dt
        
        # 总消耗
        total_cost = metabolic_cost + movement_cost + neural_cost + social_cost
        agent.energy -= total_cost
        
    def gain_energy(self, agent, food_value):
        # 觅食获得能量
        energy_gain = food_value * agent.get_digestion_efficiency()
        agent.energy = min(agent.energy + energy_gain, self.max_energy)
```

**状态判定**:
- **🔴 危险 (0-30)**: 面临死亡，行为变为急迫觅食
- **🟡 一般 (30-70)**: 需要补充能量，平衡觅食和其他活动
- **🟢 健康 (70-100)**: 正常活动，可以进行社交和探索
- **🔵 优秀 (100-150)**: 能量充沛，可以繁殖和帮助他人

---

### 3. 📊 **Avg Age (平均年龄)**
```python
# 计算逻辑  
ages = [agent.age for agent in alive_agents]
avg_age = sum(ages) / len(ages) if ages else 0
```

**含义**: 智能体的生存时间，以模拟步数计算
**机制**:

#### 🕰️ 年龄系统算法
```python
def update_age(self, dt):
    # 年龄增长
    self.age += dt
    
    # 年龄对各项能力的影响
    def get_age_factor(self):
        if self.age < 20:      # 幼年期
            return 0.8  # 80%能力
        elif self.age < 100:   # 成年期  
            return 1.0  # 100%能力
        elif self.age < 200:   # 中年期
            return 0.9  # 90%能力
        else:                  # 老年期
            return 0.7  # 70%能力
    
    # 年龄影响学习能力
    def get_learning_rate(self):
        base_rate = 0.01
        if self.age < 50:
            return base_rate * 1.5  # 年轻时学习快
        else:
            return base_rate * (1.0 - (self.age - 50) / 300)
```

**生命阶段**:
- **0-20步**: 🍼 幼年期 - 学习能力强，无繁殖能力
- **20-100步**: 💪 成年期 - 各项能力巅峰，最佳繁殖期
- **100-200步**: 🧓 中年期 - 经验丰富，繁殖能力下降
- **200+步**: 👴 老年期 - 衰老加速，死亡概率增加

---

### 4. ❤️ **Avg Health (平均健康)**
```python
# 计算逻辑
healths = [agent.health for agent in alive_agents] 
avg_health = sum(healths) / len(healths) if healths else 0
```

**含义**: 智能体身体健康状况，影响所有活动效率
**范围**: 0 - 100

#### 🏥 健康系统算法
```python
class HealthSystem:
    def update_health(self, agent, dt):
        # 1. 年龄相关衰减
        aging_decay = self.calculate_aging_decay(agent.age) * dt
        
        # 2. 能量水平影响
        energy_factor = self.calculate_energy_health_factor(agent.energy)
        
        # 3. 压力影响（社交压力、资源竞争）
        stress_factor = self.calculate_stress_factor(agent)
        
        # 4. 运动影响（适度运动有益健康）
        exercise_factor = self.calculate_exercise_factor(agent.velocity)
        
        # 健康变化
        health_change = (-aging_decay + energy_factor - stress_factor + exercise_factor) * dt
        agent.health = max(0, min(100, agent.health + health_change))
    
    def calculate_aging_decay(self, age):
        # 年龄衰减函数：指数增长
        return 0.1 * (1 + (age / 100) ** 2)
    
    def calculate_energy_health_factor(self, energy):
        # 能量对健康的影响
        if energy > 80:
            return 0.2   # 能量充足，健康改善
        elif energy < 30:
            return -0.5  # 能量不足，健康恶化
        else:
            return 0     # 中等能量，健康稳定
    
    def calculate_stress_factor(self, agent):
        # 压力计算
        competition_stress = len(agent.nearby_agents) * 0.01
        resource_stress = max(0, 0.1 - agent.local_resource_density)
        return competition_stress + resource_stress
```

**健康状态判定**:
- **90-100**: 🟢 优秀 - 所有活动效率100%
- **70-89**: 🟡 良好 - 活动效率90%
- **50-69**: 🟠 一般 - 活动效率75%
- **30-49**: 🔴 不佳 - 活动效率50%
- **0-29**: ⚫ 危重 - 活动效率25%，面临死亡

---

### 5. 👶 **Offspring (后代总数)**
```python
# 计算逻辑
total_offspring = sum(agent.offspring_count for agent in alive_agents)
```

**含义**: 当前所有智能体产生的后代累计数量
**机制**:

#### 🧬 繁殖系统算法
```python
class ReproductionSystem:
    def check_reproduction_conditions(self, agent1, agent2):
        # 繁殖条件检查
        conditions = [
            agent1.energy > 80,           # 能量充足
            agent2.energy > 80,
            agent1.age > 50,              # 性成熟
            agent2.age > 50,
            agent1.health > 70,           # 健康良好
            agent2.health > 70,
            agent1.offspring_count < 3,   # 繁殖次数限制
            agent2.offspring_count < 3,
            self.calculate_distance(agent1, agent2) < 5,  # 距离足够近
            self.population_size < self.max_population     # 种群未过载
        ]
        return all(conditions)
    
    def reproduce(self, parent1, parent2):
        # 创建子代
        child_config = self.create_child_config(parent1, parent2)
        child = SimpleAgent(child_config)
        
        # 遗传算法 - 神经网络权重混合
        child.brain = self.crossover_neural_networks(
            parent1.brain, parent2.brain
        )
        
        # 突变
        child.brain.mutate(mutation_rate=0.1)
        
        # 更新父母状态
        parent1.offspring_count += 1
        parent2.offspring_count += 1
        parent1.energy -= 30  # 繁殖消耗
        parent2.energy -= 30
        
        return child
    
    def crossover_neural_networks(self, brain1, brain2):
        # 神经网络交叉算法
        new_brain = NeuralBrain(brain1.config)
        
        for layer_idx in range(len(brain1.layers)):
            # 随机选择每层权重来源
            if random.random() < 0.5:
                new_brain.layers[layer_idx].weights = brain1.layers[layer_idx].weights.copy()
            else:
                new_brain.layers[layer_idx].weights = brain2.layers[layer_idx].weights.copy()
                
            # 权重平均混合
            alpha = random.random()
            new_brain.layers[layer_idx].weights = (
                alpha * brain1.layers[layer_idx].weights + 
                (1-alpha) * brain2.layers[layer_idx].weights
            )
        
        return new_brain
```

**繁殖成功率影响因素**:
- **父母能量**: 必须>80
- **父母年龄**: 必须>50步（性成熟）
- **健康状况**: 必须>70
- **种群密度**: 过度拥挤会抑制繁殖
- **基因兼容性**: 遗传距离影响成功率

---

### 6. 🤝 **Interactions (社交互动)**
```python
# 计算逻辑
total_interactions = sum(agent.social_interactions for agent in alive_agents)
```

**含义**: 智能体间累计交流互动次数
**机制**:

#### 👥 社交系统算法
```python
class SocialSystem:
    def detect_interactions(self, agent, nearby_agents):
        interactions = 0
        
        for other_agent in nearby_agents:
            if self.should_interact(agent, other_agent):
                interaction_type = self.determine_interaction_type(agent, other_agent)
                self.execute_interaction(agent, other_agent, interaction_type)
                interactions += 1
        
        agent.social_interactions += interactions
        return interactions
    
    def should_interact(self, agent1, agent2):
        # 社交意愿计算
        distance = agent1.position.distance_to(agent2.position)
        if distance > agent1.perception_radius:
            return False
            
        # 社交动机强度
        social_motivation = agent1.behavior.get_motivation_strength('social')
        energy_threshold = 40  # 能量不足时减少社交
        
        # 相似性吸引（基于神经网络权重相似度）
        similarity = self.calculate_neural_similarity(agent1.brain, agent2.brain)
        
        # 社交概率
        interaction_probability = (
            social_motivation * 
            (agent1.energy / 100) * 
            (1 + similarity) * 
            random.random()
        )
        
        return interaction_probability > 0.3
    
    def determine_interaction_type(self, agent1, agent2):
        # 根据状态和性格确定互动类型
        if agent1.energy < 30 or agent2.energy < 30:
            return "competition"  # 资源竞争
        elif agent1.health > 80 and agent2.health > 80:
            return "cooperation"  # 合作互助
        else:
            return "information_exchange"  # 信息交换
    
    def execute_interaction(self, agent1, agent2, interaction_type):
        if interaction_type == "cooperation":
            # 合作：分享资源信息，小幅提升双方健康
            self.share_resource_information(agent1, agent2)
            agent1.health = min(100, agent1.health + 1)
            agent2.health = min(100, agent2.health + 1)
            
        elif interaction_type == "competition":
            # 竞争：能量消耗，但可能获得资源访问权
            agent1.energy -= 2
            agent2.energy -= 2
            
        elif interaction_type == "information_exchange":
            # 信息交换：学习对方的成功策略
            self.neural_knowledge_transfer(agent1, agent2)
    
    def neural_knowledge_transfer(self, agent1, agent2):
        # 神经网络知识转移
        transfer_rate = 0.01
        
        # 选择性学习：只学习对方更成功的策略
        if agent2.age > agent1.age:  # 经验更丰富
            for layer in agent1.brain.layers:
                layer.weights += transfer_rate * (
                    agent2.brain.layers[layer.index].weights - layer.weights
                )
```

**社交行为模式**:
- **🤝 合作**: 能量充足时，分享信息，互助提升
- **⚔️ 竞争**: 资源稀缺时，争夺访问权
- **📚 学习**: 年轻智能体向年长者学习经验
- **💕 求偶**: 满足繁殖条件时的配对行为

---

### 7. 💎 **Resources (资源数量)**
```python
# 计算逻辑
world_state = self.world.get_world_state()
resource_count = world_state['num_resources']
```

**含义**: 环境中可用资源点的数量
**机制**:

#### 🌍 资源系统算法
```python
class ResourceSystem:
    def __init__(self, world_size, density=0.15):
        self.world_size = world_size
        self.density = density
        self.resources = []
        self.regeneration_rate = 0.1
        
    def generate_resources(self):
        # 资源生成
        total_resources = int(self.world_size[0] * self.world_size[1] * self.density)
        
        for _ in range(total_resources):
            resource = Resource(
                position=Vector2D(
                    random.uniform(0, self.world_size[0]),
                    random.uniform(0, self.world_size[1])
                ),
                value=random.uniform(10, 50),
                type=random.choice(['food', 'energy', 'material'])
            )
            self.resources.append(resource)
    
    def update_resources(self, dt):
        # 资源再生
        for resource in self.resources:
            if resource.is_depleted():
                # 再生概率
                if random.random() < self.regeneration_rate * dt:
                    resource.regenerate()
        
        # 新资源自然生成
        if len(self.resources) < self.get_max_resources():
            if random.random() < 0.01 * dt:  # 1%概率每秒
                self.spawn_new_resource()
    
    def consume_resource(self, agent, resource):
        # 资源消耗机制
        if resource.is_available():
            consumption_efficiency = agent.get_consumption_efficiency()
            consumed_value = resource.value * consumption_efficiency
            
            # 根据资源类型给予不同效果
            if resource.type == 'food':
                agent.energy += consumed_value * 0.8
                agent.health += consumed_value * 0.2
            elif resource.type == 'energy':
                agent.energy += consumed_value
            elif resource.type == 'material':
                agent.health += consumed_value * 0.5
                # 材料可用于改善住所（未来扩展）
            
            resource.consume(consumed_value)
            return consumed_value
        
        return 0
```

**资源类型与效果**:
- **🍎 食物**: 主要恢复能量，少量恢复健康
- **⚡ 能量**: 直接补充生命能量
- **🔧 材料**: 主要改善健康，可用于建设

**资源分布影响**:
- **高密度区域**: 竞争激烈，社交活跃
- **低密度区域**: 觅食困难，迁移行为
- **资源枯竭**: 触发集体迁移和激烈竞争

---

### 8. 🎯 **FPS (帧率)**
```python
# 计算逻辑
time_stats = self.time_manager.get_time_stats()
current_fps = time_stats['actual_fps']
```

**含义**: 系统渲染性能指标，影响观察体验
**机制**:

#### ⚡ 性能监控算法
```python
class PerformanceMonitor:
    def __init__(self):
        self.frame_times = []
        self.target_fps = 30
        
    def update_fps(self, frame_time):
        self.frame_times.append(frame_time)
        if len(self.frame_times) > 60:  # 保持最近60帧
            self.frame_times.pop(0)
        
        # 计算平均FPS
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        self.current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
    def get_performance_status(self):
        if self.current_fps > 25:
            return "excellent"
        elif self.current_fps > 20:
            return "good"  
        elif self.current_fps > 15:
            return "fair"
        else:
            return "poor"
```

---

## 🎨 颜色编码系统

### 🧠 智能体颜色含义

#### 基于健康状态的颜色映射
```python
def get_agent_color(agent):
    # 健康度颜色映射
    health_ratio = agent.health / 100.0
    energy_ratio = agent.energy / agent.max_energy
    
    # 综合健康指数
    vitality = (health_ratio + energy_ratio) / 2.0
    
    if vitality > 0.8:
        return (0, 255, 0)      # 🟢 绿色 - 优秀状态
    elif vitality > 0.6:
        return (128, 255, 0)    # 🟡 黄绿 - 良好状态  
    elif vitality > 0.4:
        return (255, 255, 0)    # 🟡 黄色 - 一般状态
    elif vitality > 0.2:
        return (255, 128, 0)    # 🟠 橙色 - 不佳状态
    else:
        return (255, 0, 0)      # 🔴 红色 - 危险状态
```

#### 特殊状态颜色
```python
def get_special_state_color(agent):
    # 繁殖状态
    if agent.is_ready_for_reproduction():
        return (255, 0, 255)    # 💜 紫色 - 求偶期
    
    # 学习状态  
    if agent.is_learning():
        return (0, 255, 255)    # 🔵 青色 - 学习中
    
    # 社交活跃状态
    if agent.recent_interactions > 5:
        return (0, 0, 255)      # 🔵 蓝色 - 社交活跃
    
    # 觅食状态
    if agent.current_goal == "foraging":
        return (255, 255, 255)  # ⚪ 白色 - 觅食中
```

### 🌍 环境元素颜色

#### 资源颜色编码
```python
def get_resource_color(resource):
    if resource.type == 'food':
        # 食物：绿色系，明度表示价值
        value_ratio = resource.value / resource.max_value
        green_intensity = int(128 + 127 * value_ratio)
        return (0, green_intensity, 0)
        
    elif resource.type == 'energy':
        # 能量：蓝色系
        return (0, 100, 255)
        
    elif resource.type == 'material':
        # 材料：棕色系
        return (139, 69, 19)
```

#### 轨迹颜色
```python
def get_trajectory_color(agent):
    # 基于智能体年龄的轨迹颜色
    age_ratio = min(agent.age / 200.0, 1.0)
    
    # 年轻→老年：蓝色→红色渐变
    red = int(255 * age_ratio)
    blue = int(255 * (1 - age_ratio))
    
    return (red, 100, blue)
```

---

## 🧮 核心算法架构

### 1. 🧠 神经网络决策系统
```python
class NeuralBrain:
    """多层感知机神经网络"""
    
    def __init__(self, config):
        self.input_size = config['input_size']      # 20个输入神经元
        self.hidden_sizes = config['hidden_sizes']  # [32, 16] 隐藏层
        self.output_size = config['output_size']    # 8个输出神经元
        
        # 权重初始化：Xavier初始化
        self.layers = self._initialize_layers()
    
    def forward(self, inputs):
        """前向传播"""
        activation = np.array(inputs)
        
        for layer in self.layers:
            # 线性变换
            z = np.dot(activation, layer.weights) + layer.bias
            # 激活函数（Tanh）
            activation = np.tanh(z)
            
        return activation
    
    def backward(self, inputs, targets, learning_rate):
        """反向传播学习"""
        # 计算梯度
        gradients = self._compute_gradients(inputs, targets)
        
        # 更新权重
        for i, layer in enumerate(self.layers):
            layer.weights -= learning_rate * gradients[i]['weights']
            layer.bias -= learning_rate * gradients[i]['bias']
```

#### 🎯 决策输入编码 (20维输入向量)
```python
def encode_world_state(agent, world_state, nearby_agents, nearby_resources):
    inputs = np.zeros(20)
    
    # 自身状态 (6维)
    inputs[0] = agent.energy / agent.max_energy           # 能量水平
    inputs[1] = agent.health / 100.0                      # 健康状况  
    inputs[2] = agent.age / 200.0                         # 年龄比例
    inputs[3] = len(nearby_agents) / 10.0                 # 社交密度
    inputs[4] = len(nearby_resources) / 5.0               # 资源密度
    inputs[5] = agent.social_interactions / 100.0         # 社交经验
    
    # 最近资源信息 (6维)
    if nearby_resources:
        closest_resource = min(nearby_resources, key=lambda r: agent.position.distance_to(r.position))
        inputs[6] = closest_resource.position.x / world_state['width']
        inputs[7] = closest_resource.position.y / world_state['height']  
        inputs[8] = closest_resource.value / 50.0
        inputs[9] = agent.position.distance_to(closest_resource.position) / 20.0
        inputs[10] = 1.0 if closest_resource.type == 'food' else 0.0
        inputs[11] = 1.0 if closest_resource.type == 'energy' else 0.0
    
    # 最近智能体信息 (6维)
    if nearby_agents:
        closest_agent = min(nearby_agents, key=lambda a: agent.position.distance_to(a.position))
        inputs[12] = closest_agent.position.x / world_state['width']
        inputs[13] = closest_agent.position.y / world_state['height']
        inputs[14] = closest_agent.energy / closest_agent.max_energy
        inputs[15] = agent.position.distance_to(closest_agent.position) / 20.0
        inputs[16] = 1.0 if closest_agent.energy > agent.energy else 0.0
        inputs[17] = closest_agent.age / 200.0
    
    # 环境信息 (2维)
    inputs[18] = world_state['time_of_day']               # 昼夜周期
    inputs[19] = world_state['resource_regeneration_rate'] # 资源再生率
    
    return inputs
```

#### 🎯 决策输出解码 (8维输出向量)
```python
def decode_neural_output(outputs):
    """将神经网络输出转换为具体行动"""
    
    # 移动决策 (2维)
    move_x = np.tanh(outputs[0]) * 2.0  # X方向移动 [-2, 2]
    move_y = np.tanh(outputs[1]) * 2.0  # Y方向移动 [-2, 2]
    
    # 行为决策 (6维，使用softmax归一化)
    behavior_probs = softmax(outputs[2:8])
    behaviors = ['explore', 'forage', 'social', 'rest', 'reproduce', 'avoid']
    
    primary_behavior = behaviors[np.argmax(behavior_probs)]
    
    return {
        'movement': Vector2D(move_x, move_y),
        'behavior': primary_behavior,
        'behavior_confidence': np.max(behavior_probs)
    }
```

### 2. 🧠 记忆系统架构
```python
class MemorySystem:
    """三层记忆架构"""
    
    def __init__(self, config):
        # 工作记忆：短期，容量小，快速访问
        self.working_memory = WorkingMemory(capacity=7)
        
        # 长期记忆：永久存储，容量大，检索慢
        self.long_term_memory = LongTermMemory(capacity=1000)
        
        # 空间记忆：位置和路径信息
        self.spatial_memory = SpatialMemory(world_size=config['world_size'])
    
    def store_experience(self, experience):
        """经验存储算法"""
        # 1. 立即存入工作记忆
        self.working_memory.add(experience)
        
        # 2. 重要性评估
        importance = self._calculate_importance(experience)
        
        # 3. 超过阈值则转入长期记忆
        if importance > 0.7:
            self.long_term_memory.consolidate(experience)
        
        # 4. 空间信息单独存储
        if 'location' in experience:
            self.spatial_memory.update_location_value(
                experience['location'], 
                experience['outcome']
            )
    
    def _calculate_importance(self, experience):
        """重要性计算算法"""
        importance = 0.0
        
        # 生存相关经验更重要
        if experience['type'] == 'food_found':
            importance += 0.8
        elif experience['type'] == 'danger_avoided':
            importance += 0.9
        elif experience['type'] == 'reproduction_success':
            importance += 0.95
        elif experience['type'] == 'social_cooperation':
            importance += 0.6
        
        # 新颖性加分
        if not self._is_similar_experience_exists(experience):
            importance += 0.3
        
        # 情感强度加分
        importance += abs(experience.get('emotional_value', 0)) * 0.2
        
        return min(importance, 1.0)
```

### 3. 🎭 行为系统架构
```python
class BehaviorSystem:
    """动机驱动的行为选择系统"""
    
    def __init__(self, config):
        # 六大基础动机
        self.motivations = {
            'survival': Motivation('survival', priority=1.0),      # 生存
            'energy': Motivation('energy', priority=0.9),         # 能量获取
            'social': Motivation('social', priority=0.7),         # 社交
            'exploration': Motivation('exploration', priority=0.6), # 探索
            'reproduction': Motivation('reproduction', priority=0.8), # 繁殖
            'safety': Motivation('safety', priority=0.8)          # 安全
        }
    
    def select_behavior(self, agent_state, world_state):
        """基于动机强度的行为选择"""
        
        # 1. 更新各动机强度
        self._update_motivation_strengths(agent_state, world_state)
        
        # 2. 计算各行为的效用值
        behavior_utilities = {}
        
        for behavior_name in self.available_behaviors:
            utility = self._calculate_behavior_utility(
                behavior_name, agent_state, world_state
            )
            behavior_utilities[behavior_name] = utility
        
        # 3. 选择最高效用的行为
        best_behavior = max(behavior_utilities, key=behavior_utilities.get)
        
        # 4. 添加随机性（探索vs利用）
        if random.random() < 0.1:  # 10%探索概率
            best_behavior = random.choice(list(behavior_utilities.keys()))
        
        return best_behavior
    
    def _update_motivation_strengths(self, agent_state, world_state):
        """动机强度更新算法"""
        
        # 生存动机：能量越低越强
        energy_ratio = agent_state['energy'] / agent_state['max_energy']
        self.motivations['survival'].strength = 1.0 - energy_ratio
        
        # 能量动机：与生存动机相关但更早激活
        self.motivations['energy'].strength = max(0.2, 1.0 - energy_ratio * 1.2)
        
        # 社交动机：基于孤独感和社交历史
        loneliness = 1.0 - (agent_state['recent_interactions'] / 10.0)
        self.motivations['social'].strength = loneliness * 0.8
        
        # 探索动机：基于好奇心和环境熟悉度
        familiarity = agent_state['location_familiarity']
        self.motivations['exploration'].strength = 1.0 - familiarity
        
        # 繁殖动机：年龄、能量、健康的函数
        reproductive_readiness = (
            min(agent_state['age'] / 50.0, 1.0) *      # 年龄成熟度
            (agent_state['energy'] / 100.0) *          # 能量充足度
            (agent_state['health'] / 100.0) *          # 健康状况
            (1.0 - agent_state['offspring_count'] / 3.0) # 繁殖饱和度
        )
        self.motivations['reproduction'].strength = reproductive_readiness
        
        # 安全动机：基于威胁感知
        threat_level = agent_state.get('perceived_threats', 0)
        self.motivations['safety'].strength = threat_level
```

---

## 🔬 学习与进化机制

### 1. 🧬 遗传算法
```python
class GeneticAlgorithm:
    """神经网络进化算法"""
    
    def crossover(self, parent1_brain, parent2_brain):
        """交叉繁殖算法"""
        child_brain = NeuralBrain(parent1_brain.config)
        
        for layer_idx in range(len(parent1_brain.layers)):
            p1_weights = parent1_brain.layers[layer_idx].weights
            p2_weights = parent2_brain.layers[layer_idx].weights
            
            # 均匀交叉
            crossover_mask = np.random.random(p1_weights.shape) < 0.5
            child_weights = np.where(crossover_mask, p1_weights, p2_weights)
            
            # 算术交叉（混合）
            alpha = np.random.random()
            child_weights = alpha * p1_weights + (1 - alpha) * p2_weights
            
            child_brain.layers[layer_idx].weights = child_weights
        
        return child_brain
    
    def mutate(self, brain, mutation_rate=0.1):
        """突变算法"""
        for layer in brain.layers:
            # 权重突变
            mutation_mask = np.random.random(layer.weights.shape) < mutation_rate
            mutation_values = np.random.normal(0, 0.1, layer.weights.shape)
            layer.weights += mutation_mask * mutation_values
            
            # 结构突变（概率极低）
            if np.random.random() < 0.001:
                self._structural_mutation(layer)
    
    def _structural_mutation(self, layer):
        """结构突变：改变网络拓扑"""
        # 添加/删除连接
        if np.random.random() < 0.5:
            # 添加连接
            zero_weights = (layer.weights == 0)
            if np.any(zero_weights):
                i, j = np.where(zero_weights)
                idx = np.random.randint(len(i))
                layer.weights[i[idx], j[idx]] = np.random.normal(0, 0.1)
        else:
            # 删除连接
            nonzero_weights = (layer.weights != 0)
            if np.any(nonzero_weights):
                i, j = np.where(nonzero_weights)
                idx = np.random.randint(len(i))
                layer.weights[i[idx], j[idx]] = 0
```

### 2. 🎓 强化学习
```python
class ReinforcementLearning:
    """基于奖励的学习系统"""
    
    def __init__(self):
        self.learning_rate = 0.01
        self.discount_factor = 0.95
        self.eligibility_traces = {}
    
    def update_policy(self, agent, action, reward, next_state):
        """政策梯度更新"""
        
        # 计算时序差分误差
        current_value = agent.brain.evaluate_state(agent.current_state)
        next_value = agent.brain.evaluate_state(next_state)
        
        td_error = reward + self.discount_factor * next_value - current_value
        
        # 更新神经网络权重
        gradients = agent.brain.compute_policy_gradients(
            agent.current_state, action
        )
        
        for layer_idx, layer in enumerate(agent.brain.layers):
            layer.weights += (
                self.learning_rate * 
                td_error * 
                gradients[layer_idx]
            )
    
    def calculate_reward(self, agent, action, outcome):
        """奖励函数设计"""
        reward = 0.0
        
        # 基础生存奖励
        if agent.alive:
            reward += 0.1
        
        # 能量变化奖励
        energy_change = outcome['energy_after'] - outcome['energy_before']
        reward += energy_change * 0.01
        
        # 健康变化奖励  
        health_change = outcome['health_after'] - outcome['health_before']
        reward += health_change * 0.02
        
        # 行为特定奖励
        if action['type'] == 'forage' and outcome['food_found']:
            reward += 1.0  # 成功觅食大奖励
        
        if action['type'] == 'social' and outcome['interaction_success']:
            reward += 0.5  # 社交成功奖励
        
        if action['type'] == 'reproduction' and outcome['reproduction_success']:
            reward += 2.0  # 繁殖成功巨大奖励
        
        # 探索奖励
        if outcome['discovered_new_area']:
            reward += 0.3
        
        # 生存时间奖励
        reward += agent.age * 0.001
        
        return reward
```

---

## 🌟 涌现行为观察

通过这些复杂的算法交互，Cogvrs中会观察到以下涌现现象：

### 1. 🧠 **群体智慧涌现**
- **信息传播**: 成功觅食位置在群体中传播
- **集体决策**: 迁移方向由多个智能体"投票"决定
- **分工合作**: 不同智能体专精不同任务

### 2. 🏘️ **社会结构形成**
- **领导者出现**: 高社交能力智能体成为中心节点
- **群体分化**: 基于行为偏好的亚群体形成
- **文化传承**: 行为模式在世代间传递

### 3. 🧬 **进化压力**
- **适者生存**: 高效觅食策略被保留
- **性选择**: 优秀基因通过繁殖优势传播
- **环境适应**: 种群特征随环境变化而演化

### 4. 🎭 **个性发展**
- **行为特化**: 个体发展独特的行为偏好
- **学习能力分化**: 不同智能体的学习速度差异
- **风险偏好**: 保守vs冒险的行为策略

这个系统展现了从简单规则到复杂行为的涌现过程，是研究人工生命和意识的理想平台！🚀