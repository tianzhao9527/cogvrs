# 🏘️ Cogvrs 部落扩展设计方案

> 从个体智能体到部落集群，再到多部落宏观文明模拟的完整扩展架构

![Version](https://img.shields.io/badge/expansion-tribal--system-green)
![Stage](https://img.shields.io/badge/stage-design--phase-blue)
![Complexity](https://img.shields.io/badge/complexity-multi--scale-orange)

---

## 🎯 扩展目标与愿景

### 📋 总体目标
1. **个体聚合**: 将现有个体智能体自然聚合成部落单位
2. **部落智能**: 开发部落级别的集体决策和行为系统
3. **宏观模拟**: 实现多部落间的复杂交互和文明演化
4. **层次化管理**: 建立个体→部落→文明的多层次架构

### 🌟 愿景阶段
```
阶段1: 部落形成 (Individual → Tribe)
┌─────────────────────────────────────┐
│  👤 👤 👤 → 🏘️ 小型部落 (5-15人)    │
│  自然聚集    基础合作                │
└─────────────────────────────────────┘

阶段2: 部落发展 (Tribe Growth)
┌─────────────────────────────────────┐
│  🏘️ → 🏘️+ 中型部落 (15-50人)       │
│  专业分工    复杂社会结构             │
└─────────────────────────────────────┘

阶段3: 多部落互动 (Inter-Tribal)
┌─────────────────────────────────────┐
│  🏘️ ←→ 🏘️ 部落间交互               │
│  贸易  战争  联盟  竞争              │
└─────────────────────────────────────┘

阶段4: 文明涌现 (Civilization)
┌─────────────────────────────────────┐
│  🏘️🏘️🏘️ → 🏛️ 文明体               │
│  政治结构    技术传播    文化演化     │
└─────────────────────────────────────┘
```

---

## 🏗️ 架构设计方案

### 🔄 1. 渐进式扩展策略 (推荐)

我建议采用**渐进式多层架构**，原因如下：

#### ✅ 优势
- **平滑过渡**: 现有系统无需大幅改动
- **灵活切换**: 可以在不同抽象层次间动态切换
- **调试友好**: 每个层次都可以独立观察和调试
- **计算效率**: 根据需要选择合适的仿真粒度

#### 🏛️ 多层架构设计

```python
class MultiScaleSimulation:
    """多尺度仿真系统"""
    
    def __init__(self):
        # 三个抽象层次
        self.individual_layer = IndividualSimulation()    # 个体层
        self.tribal_layer = TribalSimulation()           # 部落层  
        self.civilization_layer = CivilizationSimulation() # 文明层
        
        # 当前激活的层次
        self.active_layers = ['individual']  # 开始只有个体层
        self.scale_threshold = {
            'tribal_formation': 5,        # 5个人形成部落
            'civilization_emergence': 3   # 3个部落形成文明
        }
    
    def update(self, dt: float):
        """多层次更新"""
        # 1. 个体层更新（如果激活）
        if 'individual' in self.active_layers:
            self.individual_layer.update(dt)
            
            # 检查是否需要激活部落层
            if self._should_activate_tribal_layer():
                self._activate_tribal_layer()
        
        # 2. 部落层更新（如果激活）
        if 'tribal' in self.active_layers:
            self.tribal_layer.update(dt)
            
            # 检查是否需要激活文明层
            if self._should_activate_civilization_layer():
                self._activate_civilization_layer()
        
        # 3. 文明层更新（如果激活）
        if 'civilization' in self.active_layers:
            self.civilization_layer.update(dt)
    
    def _should_activate_tribal_layer(self) -> bool:
        """判断是否应该激活部落层"""
        # 当有足够数量的个体聚集时
        clusters = self.individual_layer.detect_agent_clusters()
        large_clusters = [c for c in clusters if len(c) >= self.scale_threshold['tribal_formation']]
        return len(large_clusters) > 0
```

---

## 🏘️ 部落系统设计

### 🧬 1. 部落形成机制

#### **自然聚合算法**
```python
class TribalFormation:
    """部落自然形成系统"""
    
    def __init__(self):
        self.formation_criteria = {
            'spatial_proximity': 20.0,      # 空间距离阈值
            'social_affinity': 0.6,         # 社交亲和度阈值
            'resource_sharing': 0.7,        # 资源共享意愿
            'cooperation_history': 0.5,     # 合作历史分数
            'min_tribe_size': 5,            # 最小部落规模
            'max_tribe_size': 50            # 最大部落规模
        }
    
    def detect_potential_tribes(self, agents: List[SimpleAgent]) -> List[List[SimpleAgent]]:
        """检测潜在的部落形成"""
        potential_tribes = []
        unassigned_agents = agents.copy()
        
        while len(unassigned_agents) >= self.formation_criteria['min_tribe_size']:
            # 寻找种子智能体（最具领导力的）
            seed_agent = self._find_leadership_candidate(unassigned_agents)
            if not seed_agent:
                break
            
            # 基于种子智能体形成部落
            tribe_members = self._form_tribe_around_seed(seed_agent, unassigned_agents)
            
            if len(tribe_members) >= self.formation_criteria['min_tribe_size']:
                potential_tribes.append(tribe_members)
                for member in tribe_members:
                    unassigned_agents.remove(member)
            else:
                break
        
        return potential_tribes
    
    def _find_leadership_candidate(self, agents: List[SimpleAgent]) -> SimpleAgent:
        """寻找领导力候选者"""
        leadership_scores = {}
        
        for agent in agents:
            score = 0
            
            # 社交活跃度
            score += agent.social_interactions / 100.0
            
            # 生存能力（年龄、健康）
            score += (agent.age / 200.0) * 0.5
            score += (agent.health / 100.0) * 0.3
            
            # 资源获取能力
            score += (agent.energy / agent.max_energy) * 0.4
            
            # 个性特征（领导倾向）
            if hasattr(agent, 'behavior_system'):
                personality = agent.behavior_system.behavior_preferences
                score += personality.get('social_activity', 0) * 0.6
                score += personality.get('cooperation', 0) * 0.4
            
            leadership_scores[agent] = score
        
        return max(leadership_scores.items(), key=lambda x: x[1])[0] if leadership_scores else None
    
    def _form_tribe_around_seed(self, seed_agent: SimpleAgent, 
                               available_agents: List[SimpleAgent]) -> List[SimpleAgent]:
        """围绕种子智能体形成部落"""
        tribe_members = [seed_agent]
        candidates = [a for a in available_agents if a != seed_agent]
        
        # 根据亲和度排序候选者
        affinity_scores = []
        for candidate in candidates:
            affinity = self._calculate_affinity(seed_agent, candidate)
            affinity_scores.append((candidate, affinity))
        
        # 按亲和度排序
        affinity_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 选择最亲和的智能体加入部落
        for candidate, affinity in affinity_scores:
            if (len(tribe_members) < self.formation_criteria['max_tribe_size'] and
                affinity > self.formation_criteria['social_affinity']):
                
                # 检查空间距离
                distance = seed_agent.position.distance_to(candidate.position)
                if distance <= self.formation_criteria['spatial_proximity']:
                    tribe_members.append(candidate)
        
        return tribe_members
    
    def _calculate_affinity(self, agent1: SimpleAgent, agent2: SimpleAgent) -> float:
        """计算两个智能体的亲和度"""
        affinity = 0.0
        
        # 个性相似度
        if (hasattr(agent1, 'behavior_system') and 
            hasattr(agent2, 'behavior_system')):
            
            prefs1 = agent1.behavior_system.behavior_preferences
            prefs2 = agent2.behavior_system.behavior_preferences
            
            similarity = 0
            for trait in prefs1:
                if trait in prefs2:
                    similarity += 1 - abs(prefs1[trait] - prefs2[trait])
            
            affinity += similarity / len(prefs1)
        
        # 年龄相近度
        age_similarity = 1 - abs(agent1.age - agent2.age) / 200.0
        affinity += age_similarity * 0.3
        
        # 能量水平相似度
        energy_diff = abs(agent1.energy - agent2.energy) / max(agent1.max_energy, agent2.max_energy)
        energy_similarity = 1 - energy_diff
        affinity += energy_similarity * 0.2
        
        return affinity / 1.5  # 归一化
```

### 🎭 2. 部落智能体设计

#### **Tribe类架构**
```python
class Tribe:
    """部落智能体类"""
    
    def __init__(self, members: List[SimpleAgent], leader: SimpleAgent):
        self.tribe_id = f"tribe_{int(time.time())}_{random.randint(1000, 9999)}"
        self.members = members
        self.leader = leader
        self.creation_time = time.time()
        
        # 部落属性
        self.territory_center = self._calculate_territory_center()
        self.territory_radius = self._calculate_territory_radius()
        self.resources = TribalResources()
        self.culture = TribalCulture()
        self.technology = TribalTechnology()
        
        # 部落统计
        self.population = len(members)
        self.avg_age = sum(m.age for m in members) / len(members)
        self.total_energy = sum(m.energy for m in members)
        self.total_health = sum(m.health for m in members)
        
        # 部落行为系统
        self.tribal_behavior = TribalBehaviorSystem()
        self.decision_maker = CollectiveDecisionMaker(members, leader)
        
        # 部落关系
        self.allies = []        # 盟友部落
        self.enemies = []       # 敌对部落
        self.trade_partners = [] # 贸易伙伴
        
        # 专业分工
        self.roles = self._assign_tribal_roles()
        
    def update(self, dt: float, world_state: Dict):
        """部落更新循环"""
        # 1. 更新个体成员
        self._update_members(dt, world_state)
        
        # 2. 集体决策
        tribal_decision = self.decision_maker.make_collective_decision(world_state)
        
        # 3. 执行部落行动
        self._execute_tribal_action(tribal_decision)
        
        # 4. 更新部落状态
        self._update_tribal_state()
        
        # 5. 处理成员变化
        self._handle_membership_changes()
    
    def _assign_tribal_roles(self) -> Dict[str, List[SimpleAgent]]:
        """分配部落角色"""
        roles = {
            'leader': [self.leader],
            'hunters': [],
            'gatherers': [],
            'defenders': [],
            'caretakers': [],
            'scouts': []
        }
        
        # 基于个性特征分配角色
        for member in self.members:
            if member == self.leader:
                continue
                
            if hasattr(member, 'behavior_system'):
                prefs = member.behavior_system.behavior_preferences
                
                # 根据个性分配最适合的角色
                role_scores = {
                    'hunters': prefs.get('aggression', 0) + prefs.get('risk_taking', 0),
                    'gatherers': prefs.get('exploration', 0) + prefs.get('curiosity', 0),
                    'defenders': prefs.get('aggression', 0) + (1 - prefs.get('risk_taking', 0.5)),
                    'caretakers': prefs.get('cooperation', 0) + (1 - prefs.get('aggression', 0.5)),
                    'scouts': prefs.get('exploration', 0) + prefs.get('risk_taking', 0)
                }
                
                best_role = max(role_scores.items(), key=lambda x: x[1])[0]
                roles[best_role].append(member)
        
        return roles
    
    def _calculate_territory_center(self) -> Vector2D:
        """计算部落领土中心"""
        total_x = sum(member.position.x for member in self.members)
        total_y = sum(member.position.y for member in self.members)
        
        return Vector2D(total_x / len(self.members), total_y / len(self.members))
    
    def _calculate_territory_radius(self) -> float:
        """计算部落领土半径"""
        center = self.territory_center
        max_distance = 0
        
        for member in self.members:
            distance = center.distance_to(member.position)
            max_distance = max(max_distance, distance)
        
        # 领土半径 = 最远成员距离 × 1.5 + 基础缓冲
        return max_distance * 1.5 + 20.0
```

#### **集体决策系统**
```python
class CollectiveDecisionMaker:
    """集体决策制定系统"""
    
    def __init__(self, members: List[SimpleAgent], leader: SimpleAgent):
        self.members = members
        self.leader = leader
        self.decision_history = []
        
        # 决策模式
        self.decision_modes = {
            'autocratic': 0.3,      # 独裁式（领导者决定）
            'democratic': 0.4,      # 民主式（投票决定）
            'consensus': 0.2,       # 共识式（一致同意）
            'expertise': 0.1        # 专家式（最有经验者决定）
        }
    
    def make_collective_decision(self, world_state: Dict) -> TribalAction:
        """制定集体决策"""
        
        # 1. 识别当前面临的主要问题
        problems = self._identify_problems(world_state)
        
        if not problems:
            return TribalAction(TribalActionType.MAINTAIN, priority=0.1)
        
        # 2. 选择最重要的问题
        primary_problem = max(problems.items(), key=lambda x: x[1])[0]
        
        # 3. 生成解决方案
        solutions = self._generate_solutions(primary_problem, world_state)
        
        # 4. 选择决策模式
        decision_mode = self._select_decision_mode(primary_problem)
        
        # 5. 根据决策模式选择最佳方案
        chosen_solution = self._choose_solution(solutions, decision_mode)
        
        # 6. 记录决策
        decision_record = {
            'timestamp': time.time(),
            'problem': primary_problem,
            'solutions_considered': len(solutions),
            'decision_mode': decision_mode,
            'chosen_solution': chosen_solution
        }
        self.decision_history.append(decision_record)
        
        return chosen_solution
    
    def _identify_problems(self, world_state: Dict) -> Dict[str, float]:
        """识别当前面临的问题"""
        problems = {}
        
        # 资源短缺问题
        avg_energy = sum(m.energy for m in self.members) / len(self.members)
        if avg_energy < 40:
            problems['resource_shortage'] = 1.0 - (avg_energy / 100.0)
        
        # 健康危机
        avg_health = sum(m.health for m in self.members) / len(self.members)
        if avg_health < 60:
            problems['health_crisis'] = 1.0 - (avg_health / 100.0)
        
        # 人口问题
        if len(self.members) < 3:
            problems['population_decline'] = 1.0 - (len(self.members) / 10.0)
        elif len(self.members) > 30:
            problems['overpopulation'] = (len(self.members) - 30) / 20.0
        
        # 领土威胁
        nearby_tribes = world_state.get('nearby_tribes', [])
        hostile_tribes = [t for t in nearby_tribes if self._is_hostile(t)]
        if hostile_tribes:
            problems['territorial_threat'] = len(hostile_tribes) / 5.0
        
        return problems
    
    def _generate_solutions(self, problem: str, world_state: Dict) -> List[TribalAction]:
        """为问题生成解决方案"""
        solutions = []
        
        if problem == 'resource_shortage':
            solutions.extend([
                TribalAction(TribalActionType.FORAGE, priority=0.8),
                TribalAction(TribalActionType.MIGRATE, priority=0.6),
                TribalAction(TribalActionType.TRADE, priority=0.7),
                TribalAction(TribalActionType.RAID, priority=0.4)
            ])
        
        elif problem == 'health_crisis':
            solutions.extend([
                TribalAction(TribalActionType.REST, priority=0.9),
                TribalAction(TribalActionType.SEEK_MEDICINE, priority=0.7),
                TribalAction(TribalActionType.ISOLATE_SICK, priority=0.6)
            ])
        
        elif problem == 'population_decline':
            solutions.extend([
                TribalAction(TribalActionType.ENCOURAGE_REPRODUCTION, priority=0.8),
                TribalAction(TribalActionType.RECRUIT_OUTSIDERS, priority=0.6),
                TribalAction(TribalActionType.MERGE_WITH_ALLY, priority=0.5)
            ])
        
        elif problem == 'territorial_threat':
            solutions.extend([
                TribalAction(TribalActionType.FORTIFY_TERRITORY, priority=0.7),
                TribalAction(TribalActionType.FORM_ALLIANCE, priority=0.8),
                TribalAction(TribalActionType.PREEMPTIVE_ATTACK, priority=0.4),
                TribalAction(TribalActionType.MIGRATE, priority=0.6)
            ])
        
        return solutions
    
    def _choose_solution(self, solutions: List[TribalAction], decision_mode: str) -> TribalAction:
        """根据决策模式选择解决方案"""
        
        if decision_mode == 'autocratic':
            # 领导者偏好决定
            leader_personality = self.leader.behavior_system.behavior_preferences
            
            for solution in solutions:
                # 根据领导者个性调整方案优先级
                if solution.type == TribalActionType.RAID and leader_personality.get('aggression', 0) > 0.7:
                    solution.priority *= 1.5
                elif solution.type == TribalActionType.TRADE and leader_personality.get('cooperation', 0) > 0.7:
                    solution.priority *= 1.3
            
            return max(solutions, key=lambda s: s.priority)
        
        elif decision_mode == 'democratic':
            # 投票决定
            votes = {}
            for solution in solutions:
                votes[solution] = 0
                
                for member in self.members:
                    member_vote = self._member_vote_for_solution(member, solution)
                    votes[solution] += member_vote
            
            return max(votes.items(), key=lambda x: x[1])[0]
        
        elif decision_mode == 'consensus':
            # 寻找所有人都能接受的方案
            acceptable_solutions = []
            
            for solution in solutions:
                all_accept = True
                for member in self.members:
                    if self._member_vote_for_solution(member, solution) < 0.5:
                        all_accept = False
                        break
                
                if all_accept:
                    acceptable_solutions.append(solution)
            
            if acceptable_solutions:
                return max(acceptable_solutions, key=lambda s: s.priority)
            else:
                # 如果没有共识，退回到民主投票
                return self._choose_solution(solutions, 'democratic')
        
        else:  # expertise
            # 选择最有经验的成员的偏好
            most_experienced = max(self.members, key=lambda m: m.age)
            expert_choice = max(solutions, key=lambda s: self._member_vote_for_solution(most_experienced, s))
            return expert_choice
```

---

## 🌍 多部落宏观系统

### 🗺️ 1. 部落间交互系统

#### **部落关系动态**
```python
class InterTribalRelations:
    """部落间关系管理系统"""
    
    def __init__(self):
        self.relationship_matrix = {}  # (tribe1_id, tribe2_id) -> relationship_score
        self.interaction_history = []
        self.territorial_disputes = []
        self.trade_routes = []
        self.alliances = []
        
        # 关系类型定义
        self.relationship_types = {
            'hostile': (-1.0, -0.6),      # 敌对
            'unfriendly': (-0.6, -0.2),   # 不友好
            'neutral': (-0.2, 0.2),       # 中性
            'friendly': (0.2, 0.6),       # 友好
            'allied': (0.6, 1.0)          # 同盟
        }
    
    def update_tribal_relations(self, tribes: List[Tribe], dt: float):
        """更新部落间关系"""
        
        for i, tribe1 in enumerate(tribes):
            for tribe2 in tribes[i+1:]:
                # 计算部落间距离
                distance = tribe1.territory_center.distance_to(tribe2.territory_center)
                
                # 检查是否在交互范围内
                interaction_range = tribe1.territory_radius + tribe2.territory_radius + 50
                
                if distance <= interaction_range:
                    # 处理部落间交互
                    self._process_tribal_interaction(tribe1, tribe2, distance)
    
    def _process_tribal_interaction(self, tribe1: Tribe, tribe2: Tribe, distance: float):
        """处理两个部落间的交互"""
        
        # 获取当前关系状态
        current_relationship = self._get_relationship_score(tribe1.tribe_id, tribe2.tribe_id)
        
        # 检测交互类型
        interaction_type = self._determine_interaction_type(tribe1, tribe2, current_relationship)
        
        # 执行交互
        if interaction_type == 'trade':
            self._handle_trade_interaction(tribe1, tribe2)
        elif interaction_type == 'territorial_dispute':
            self._handle_territorial_dispute(tribe1, tribe2)
        elif interaction_type == 'alliance_formation':
            self._handle_alliance_formation(tribe1, tribe2)
        elif interaction_type == 'conflict':
            self._handle_tribal_conflict(tribe1, tribe2)
        elif interaction_type == 'cultural_exchange':
            self._handle_cultural_exchange(tribe1, tribe2)
    
    def _determine_interaction_type(self, tribe1: Tribe, tribe2: Tribe, relationship: float) -> str:
        """确定交互类型"""
        
        # 基于关系状态和部落特征决定交互类型
        tribe1_aggression = tribe1.leader.behavior_system.behavior_preferences.get('aggression', 0.3)
        tribe2_aggression = tribe2.leader.behavior_system.behavior_preferences.get('aggression', 0.3)
        
        # 资源状况影响
        tribe1_resources = tribe1.total_energy / len(tribe1.members)
        tribe2_resources = tribe2.total_energy / len(tribe2.members)
        
        # 决策逻辑
        if relationship < -0.5 or (tribe1_aggression > 0.7 and tribe1_resources < 30):
            return 'conflict'
        elif relationship > 0.5 and abs(tribe1_resources - tribe2_resources) < 20:
            return 'alliance_formation'
        elif relationship > 0.0 and tribe1_resources > 50 and tribe2_resources > 50:
            return 'trade'
        elif abs(tribe1.territory_center.distance_to(tribe2.territory_center)) < max(tribe1.territory_radius, tribe2.territory_radius):
            return 'territorial_dispute'
        else:
            return 'cultural_exchange'
    
    def _handle_trade_interaction(self, tribe1: Tribe, tribe2: Tribe):
        """处理贸易交互"""
        
        # 计算贸易收益
        trade_benefit = min(tribe1.total_energy * 0.1, tribe2.total_energy * 0.1)
        
        # 资源交换
        if tribe1.total_energy > tribe2.total_energy:
            # tribe1 给 tribe2 资源
            self._transfer_resources(tribe1, tribe2, trade_benefit)
        else:
            # tribe2 给 tribe1 资源
            self._transfer_resources(tribe2, tribe1, trade_benefit)
        
        # 改善关系
        self._modify_relationship(tribe1.tribe_id, tribe2.tribe_id, +0.1)
        
        # 记录贸易
        trade_record = {
            'timestamp': time.time(),
            'tribe1': tribe1.tribe_id,
            'tribe2': tribe2.tribe_id,
            'type': 'trade',
            'benefit': trade_benefit
        }
        self.interaction_history.append(trade_record)
    
    def _handle_tribal_conflict(self, tribe1: Tribe, tribe2: Tribe):
        """处理部落冲突"""
        
        # 计算战斗力
        tribe1_strength = self._calculate_military_strength(tribe1)
        tribe2_strength = self._calculate_military_strength(tribe2)
        
        # 战斗结果
        total_strength = tribe1_strength + tribe2_strength
        tribe1_win_probability = tribe1_strength / total_strength
        
        if random.random() < tribe1_win_probability:
            # tribe1 获胜
            winner, loser = tribe1, tribe2
        else:
            # tribe2 获胜
            winner, loser = tribe2, tribe1
        
        # 应用冲突结果
        self._apply_conflict_results(winner, loser)
        
        # 恶化关系
        self._modify_relationship(tribe1.tribe_id, tribe2.tribe_id, -0.3)
    
    def _calculate_military_strength(self, tribe: Tribe) -> float:
        """计算部落军事实力"""
        
        # 基础实力 = 人口 × 平均健康 × 平均能量
        base_strength = len(tribe.members) * (tribe.total_health / len(tribe.members)) * (tribe.total_energy / len(tribe.members))
        
        # 领导力加成
        leadership_bonus = tribe.leader.behavior_system.behavior_preferences.get('aggression', 0.3) * 0.2
        
        # 战士比例加成
        warriors = tribe.roles.get('defenders', []) + tribe.roles.get('hunters', [])
        warrior_ratio = len(warriors) / len(tribe.members)
        warrior_bonus = warrior_ratio * 0.3
        
        # 技术水平加成（如果实现了技术系统）
        tech_bonus = getattr(tribe.technology, 'military_tech_level', 1.0) * 0.1
        
        total_strength = base_strength * (1 + leadership_bonus + warrior_bonus + tech_bonus)
        
        return total_strength
```

### 🏛️ 2. 文明层次涌现

#### **文明形成检测**
```python
class CivilizationEmergence:
    """文明涌现检测和管理系统"""
    
    def __init__(self):
        self.civilizations = []
        self.emergence_criteria = {
            'min_tribes': 3,                    # 最少部落数量
            'min_total_population': 100,        # 最少总人口
            'trade_network_density': 0.6,       # 贸易网络密度
            'cultural_similarity': 0.4,         # 文化相似度
            'territorial_stability': 0.7,       # 领土稳定性
            'technological_advancement': 0.5     # 技术发展水平
        }
    
    def detect_civilization_emergence(self, tribes: List[Tribe]) -> List[Civilization]:
        """检测文明涌现"""
        
        potential_civilizations = []
        
        # 寻找连通的部落群
        tribal_clusters = self._find_tribal_clusters(tribes)
        
        for cluster in tribal_clusters:
            if self._meets_civilization_criteria(cluster):
                civilization = self._form_civilization(cluster)
                potential_civilizations.append(civilization)
        
        return potential_civilizations
    
    def _find_tribal_clusters(self, tribes: List[Tribe]) -> List[List[Tribe]]:
        """寻找连通的部落群"""
        clusters = []
        visited = set()
        
        for tribe in tribes:
            if tribe.tribe_id not in visited:
                cluster = self._bfs_tribal_connections(tribe, tribes, visited)
                if len(cluster) >= self.emergence_criteria['min_tribes']:
                    clusters.append(cluster)
        
        return clusters
    
    def _meets_civilization_criteria(self, tribal_cluster: List[Tribe]) -> bool:
        """检查是否满足文明形成条件"""
        
        # 1. 部落数量检查
        if len(tribal_cluster) < self.emergence_criteria['min_tribes']:
            return False
        
        # 2. 总人口检查
        total_population = sum(len(tribe.members) for tribe in tribal_cluster)
        if total_population < self.emergence_criteria['min_total_population']:
            return False
        
        # 3. 贸易网络密度检查
        trade_density = self._calculate_trade_network_density(tribal_cluster)
        if trade_density < self.emergence_criteria['trade_network_density']:
            return False
        
        # 4. 文化相似度检查
        cultural_similarity = self._calculate_cultural_similarity(tribal_cluster)
        if cultural_similarity < self.emergence_criteria['cultural_similarity']:
            return False
        
        # 5. 领土稳定性检查
        territorial_stability = self._calculate_territorial_stability(tribal_cluster)
        if territorial_stability < self.emergence_criteria['territorial_stability']:
            return False
        
        return True
    
    def _form_civilization(self, tribal_cluster: List[Tribe]) -> 'Civilization':
        """形成文明"""
        
        civilization = Civilization(
            founding_tribes=tribal_cluster,
            formation_time=time.time()
        )
        
        # 确定文明中心
        civilization.capital = self._determine_civilization_capital(tribal_cluster)
        
        # 建立政治结构
        civilization.government = self._establish_government(tribal_cluster)
        
        # 合并技术和文化
        civilization.technology = self._merge_tribal_technologies(tribal_cluster)
        civilization.culture = self._merge_tribal_cultures(tribal_cluster)
        
        return civilization
```

#### **文明类设计**
```python
class Civilization:
    """文明实体类"""
    
    def __init__(self, founding_tribes: List[Tribe], formation_time: float):
        self.civilization_id = f"civ_{int(formation_time)}_{random.randint(1000, 9999)}"
        self.founding_tribes = founding_tribes
        self.formation_time = formation_time
        
        # 文明属性
        self.name = self._generate_civilization_name()
        self.capital = None  # 首都部落
        self.territory = self._calculate_total_territory()
        self.population = sum(len(tribe.members) for tribe in founding_tribes)
        
        # 政治系统
        self.government = None
        self.ruler = None
        self.political_stability = 0.5
        
        # 经济系统
        self.economy = CivilizationEconomy()
        self.trade_networks = []
        self.resource_distribution = {}
        
        # 技术与文化
        self.technology = CivilizationTechnology()
        self.culture = CivilizationCulture()
        self.knowledge_level = self._calculate_initial_knowledge()
        
        # 军事系统
        self.military = CivilizationMilitary(founding_tribes)
        self.defensive_strength = self._calculate_defensive_strength()
        
        # 外交关系
        self.diplomatic_relations = {}  # 与其他文明的关系
        self.expansion_pressure = 0.3
        
    def update(self, dt: float, world_state: Dict):
        """文明更新循环"""
        
        # 1. 更新组成部落
        for tribe in self.founding_tribes:
            tribe.update(dt, world_state)
        
        # 2. 文明级决策
        civilization_decision = self._make_civilization_decision(world_state)
        
        # 3. 执行文明行动
        self._execute_civilization_action(civilization_decision)
        
        # 4. 更新文明属性
        self._update_civilization_state()
        
        # 5. 处理内政和外交
        self._handle_internal_affairs()
        self._handle_foreign_relations(world_state)
    
    def _make_civilization_decision(self, world_state: Dict) -> CivilizationAction:
        """制定文明级决策"""
        
        # 识别文明面临的挑战
        challenges = self._identify_civilization_challenges(world_state)
        
        if not challenges:
            return CivilizationAction(CivilizationActionType.MAINTAIN_STATUS_QUO)
        
        # 选择最紧迫的挑战
        primary_challenge = max(challenges.items(), key=lambda x: x[1])[0]
        
        # 基于政府类型和统治者特征制定决策
        if primary_challenge == 'resource_scarcity':
            return self._decide_resource_strategy(world_state)
        elif primary_challenge == 'external_threat':
            return self._decide_military_strategy(world_state)
        elif primary_challenge == 'internal_conflict':
            return self._decide_political_strategy()
        elif primary_challenge == 'technological_lag':
            return self._decide_development_strategy()
        else:
            return CivilizationAction(CivilizationActionType.EXPLORE_AND_EXPAND)
    
    def _calculate_civilization_power(self) -> float:
        """计算文明总体实力"""
        
        # 人口实力
        population_power = self.population / 1000.0
        
        # 经济实力
        economic_power = self.economy.calculate_gdp() / 10000.0
        
        # 军事实力
        military_power = self.military.calculate_total_strength() / 5000.0
        
        # 技术实力
        tech_power = self.technology.calculate_tech_level() / 100.0
        
        # 文化实力
        cultural_power = self.culture.calculate_influence() / 100.0
        
        # 政治稳定性
        political_power = self.political_stability
        
        total_power = (population_power * 0.25 + 
                      economic_power * 0.2 + 
                      military_power * 0.2 + 
                      tech_power * 0.15 + 
                      cultural_power * 0.1 + 
                      political_power * 0.1)
        
        return total_power
```

---

## 🎮 用户界面扩展

### 📊 1. 多尺度可视化

#### **缩放级别设计**
```python
class MultiScaleVisualization:
    """多尺度可视化系统"""
    
    def __init__(self):
        self.zoom_levels = {
            'individual': {
                'scale': 1.0,
                'min_zoom': 0.5,
                'max_zoom': 3.0,
                'focus': 'agent_detail'
            },
            'tribal': {
                'scale': 0.3,
                'min_zoom': 0.1,
                'max_zoom': 1.0,
                'focus': 'tribal_territory'
            },
            'civilization': {
                'scale': 0.05,
                'min_zoom': 0.01,
                'max_zoom': 0.2,
                'focus': 'civilization_map'
            },
            'world': {
                'scale': 0.01,
                'min_zoom': 0.001,
                'max_zoom': 0.05,
                'focus': 'global_overview'
            }
        }
        
        self.current_level = 'individual'
        self.transition_animation = None
    
    def render_current_scale(self, screen: pygame.Surface, world_state: Dict):
        """根据当前缩放级别渲染"""
        
        if self.current_level == 'individual':
            self._render_individual_view(screen, world_state)
        elif self.current_level == 'tribal':
            self._render_tribal_view(screen, world_state)
        elif self.current_level == 'civilization':
            self._render_civilization_view(screen, world_state)
        elif self.current_level == 'world':
            self._render_world_view(screen, world_state)
    
    def _render_tribal_view(self, screen: pygame.Surface, world_state: Dict):
        """渲染部落级视图"""
        
        tribes = world_state.get('tribes', [])
        
        for tribe in tribes:
            # 绘制部落领土
            territory_color = self._get_tribe_color(tribe)
            pygame.draw.circle(screen, territory_color, 
                             tribe.territory_center.to_pygame_coords(),
                             int(tribe.territory_radius * self.zoom_levels['tribal']['scale']))
            
            # 绘制部落中心
            center_pos = tribe.territory_center.to_pygame_coords()
            pygame.draw.circle(screen, (255, 255, 255), center_pos, 5)
            
            # 显示部落信息
            tribe_info = f"{tribe.name} ({len(tribe.members)})"
            font = pygame.font.Font(None, 24)
            text_surface = font.render(tribe_info, True, (255, 255, 255))
            screen.blit(text_surface, (center_pos[0] + 10, center_pos[1] - 10))
            
            # 绘制部落间关系线
            self._draw_tribal_relations(screen, tribe, tribes)
    
    def _render_civilization_view(self, screen: pygame.Surface, world_state: Dict):
        """渲染文明级视图"""
        
        civilizations = world_state.get('civilizations', [])
        
        for civilization in civilizations:
            # 绘制文明边界
            civ_color = self._get_civilization_color(civilization)
            
            # 绘制文明领土（由多个部落领土组成）
            for tribe in civilization.founding_tribes:
                pygame.draw.circle(screen, civ_color + (100,),  # 半透明
                                 tribe.territory_center.to_pygame_coords(),
                                 int(tribe.territory_radius * self.zoom_levels['civilization']['scale']))
            
            # 绘制首都
            if civilization.capital:
                capital_pos = civilization.capital.territory_center.to_pygame_coords()
                pygame.draw.circle(screen, (255, 215, 0), capital_pos, 8)  # 金色首都
                
                # 显示文明信息
                civ_info = f"{civilization.name} (Pop: {civilization.population})"
                font = pygame.font.Font(None, 28)
                text_surface = font.render(civ_info, True, (255, 255, 255))
                screen.blit(text_surface, (capital_pos[0] + 15, capital_pos[1] - 15))
```

### 📈 2. 多层次统计面板

#### **部落统计面板**
```python
class TribalStatsPanel:
    """部落统计面板"""
    
    def generate_tribal_stats_html(self, tribes: List[Tribe]) -> str:
        """生成部落统计HTML"""
        
        html_content = f"""
        <div style="font-family: monospace; font-size: 11px; color: #E0E0E0;">
            <h3 style="color: #FF6B35;">🏘️ 部落统计</h3>
            
            <div style="margin-bottom: 8px;">
                <span style="color: #4CAF50;">部落数量:</span> {len(tribes)}<br>
                <span style="color: #2196F3;">总人口:</span> {sum(len(t.members) for t in tribes)}<br>
                <span style="color: #FF9800;">平均规模:</span> {sum(len(t.members) for t in tribes) / len(tribes):.1f}<br>
            </div>
            
            <h4 style="color: #9C27B0;">活跃部落</h4>
            <div style="max-height: 120px; overflow-y: auto;">
        """
        
        # 按人口排序显示前5个部落
        sorted_tribes = sorted(tribes, key=lambda t: len(t.members), reverse=True)[:5]
        
        for i, tribe in enumerate(sorted_tribes):
            leader_name = f"Agent_{tribe.leader.agent_id[-4:]}"
            avg_energy = sum(m.energy for m in tribe.members) / len(tribe.members)
            
            energy_color = "#4CAF50" if avg_energy > 70 else "#FF9800" if avg_energy > 40 else "#F44336"
            
            html_content += f"""
                <div style="margin: 2px 0; padding: 2px; background: rgba(255,255,255,0.1);">
                    <span style="color: #FFC107;">#{i+1}</span>
                    <span style="color: #E91E63;">👑{leader_name}</span><br>
                    <span style="color: #03DAC6;">人口: {len(tribe.members)}</span>
                    <span style="color: {energy_color};">能量: {avg_energy:.0f}</span>
                </div>
            """
        
        html_content += """
            </div>
        </div>
        """
        
        return html_content
```

---

## 🚀 实现路线图

### 📅 分阶段实施计划

#### **阶段1: 部落基础 (2-3周)**
```python
# 优先实现的核心功能
PHASE_1_FEATURES = [
    "TribalFormation",           # 部落形成机制
    "Tribe",                     # 基础部落类
    "CollectiveDecisionMaker",   # 集体决策
    "TribalStatsPanel",          # 部落统计面板
    "MultiScaleVisualization"    # 多尺度可视化基础
]

# 实现顺序
implementation_order = [
    "1. 扩展现有Agent类，添加tribal_affiliation属性",
    "2. 实现TribalFormation.detect_potential_tribes()",
    "3. 创建基础Tribe类和成员管理",
    "4. 添加部落可视化到现有GUI",
    "5. 实现简单的集体决策机制",
    "6. 测试部落形成和基本功能"
]
```

#### **阶段2: 部落互动 (3-4周)**
```python
PHASE_2_FEATURES = [
    "InterTribalRelations",      # 部落间关系
    "TribalConflictSystem",      # 冲突系统
    "TradeSystem",               # 贸易系统
    "TerritorialManagement",     # 领土管理
    "AdvancedTribalAI"          # 高级部落AI
]
```

#### **阶段3: 文明涌现 (4-5周)**
```python
PHASE_3_FEATURES = [
    "CivilizationEmergence",     # 文明涌现检测
    "Civilization",              # 文明类
    "CivilizationGovernment",    # 政治系统
    "CivilizationEconomy",       # 经济系统
    "DiplomaticSystem"           # 外交系统
]
```

### 🔧 技术实现建议

#### **1. 向后兼容性**
```python
# 保持现有API兼容
class SimpleAgent:
    def __init__(self, config: Dict):
        # 现有初始化代码
        self.tribal_affiliation = None  # 新增部落归属
        self.tribal_role = None         # 新增部落角色
        
    def update(self, dt: float, world_state: Dict, nearby_agents: List, nearby_resources: List):
        # 现有更新逻辑
        
        # 新增部落行为
        if self.tribal_affiliation:
            self._update_tribal_behavior(dt, world_state)
```

#### **2. 配置扩展**
```python
# 扩展配置系统
TRIBAL_CONFIG = {
    'tribal_formation': {
        'enabled': True,
        'min_tribe_size': 5,
        'max_tribe_size': 50,
        'formation_probability': 0.1,
        'leadership_selection': 'merit_based'  # 'random', 'age_based', 'merit_based'
    },
    
    'inter_tribal': {
        'enabled': True,
        'interaction_range_multiplier': 2.0,
        'conflict_probability': 0.05,
        'trade_probability': 0.3,
        'alliance_probability': 0.1
    },
    
    'civilization': {
        'enabled': False,  # 默认关闭，需要手动启用
        'min_tribes_for_civilization': 3,
        'emergence_check_interval': 100
    }
}
```

这个扩展方案采用渐进式设计，可以在不破坏现有系统的基础上，逐步添加部落和文明功能。你觉得这个方向如何？需要我详细实现其中的某个部分吗？