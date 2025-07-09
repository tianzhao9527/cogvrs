#!/usr/bin/env python3
"""
部落形成系统
展示智能体如何演化成部落文明的过程

Author: Ben Hsu & Claude
"""

import numpy as np
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
import time
import uuid

from ..core.physics_engine import Vector2D

logger = logging.getLogger(__name__)

class TribalStage(Enum):
    """部落发展阶段"""
    INDIVIDUAL = "individual"         # 个体阶段
    PAIR_BONDING = "pair_bonding"     # 配对结合
    SMALL_GROUP = "small_group"       # 小群体
    CLAN = "clan"                     # 氏族
    TRIBE = "tribe"                   # 部落
    CHIEFDOM = "chiefdom"            # 酋长制
    EARLY_STATE = "early_state"       # 早期国家

class RelationshipType(Enum):
    """关系类型"""
    FAMILY = "family"                 # 家族关系
    FRIENDSHIP = "friendship"         # 友谊关系
    ALLIANCE = "alliance"             # 联盟关系
    COOPERATION = "cooperation"       # 合作关系
    COMPETITION = "competition"       # 竞争关系
    CONFLICT = "conflict"             # 冲突关系
    LEADERSHIP = "leadership"         # 领导关系
    TEACHING = "teaching"             # 师徒关系

@dataclass
class Relationship:
    """关系"""
    agent_a: str
    agent_b: str
    relationship_type: RelationshipType
    strength: float                   # 关系强度 (0-1)
    duration: float                   # 持续时间
    interactions: int                 # 互动次数
    created_time: float
    last_interaction: float
    
    def update_strength(self, interaction_quality: float):
        """更新关系强度"""
        # 基于互动质量调整强度
        change = interaction_quality * 0.1 - 0.01  # 自然衰减
        self.strength = max(0, min(1, self.strength + change))
        self.interactions += 1
        self.last_interaction = time.time()
    
    def get_relationship_quality(self) -> float:
        """获取关系质量"""
        # 综合考虑强度、持续时间和互动频率
        recency_factor = max(0.1, 1.0 - (time.time() - self.last_interaction) / 3600)
        duration_factor = min(1.0, self.duration / 1000)
        interaction_factor = min(1.0, self.interactions / 50)
        
        return self.strength * 0.5 + recency_factor * 0.2 + duration_factor * 0.15 + interaction_factor * 0.15

@dataclass
class SocialGroup:
    """社会群体"""
    group_id: str
    name: str
    members: Set[str]
    leader: Optional[str]
    stage: TribalStage
    center_position: Vector2D
    territory_radius: float
    
    # 群体属性
    cohesion: float                   # 凝聚力
    hierarchy_level: float            # 等级化程度
    specialization: float             # 专业化程度
    resource_sharing: float           # 资源共享程度
    decision_making: str              # 决策方式
    
    # 文化特征
    cultural_traits: Dict[str, float]
    traditions: List[str]
    taboos: List[str]
    rituals: List[str]
    
    # 发展历史
    formation_time: float
    milestone_events: List[Dict]
    
    def add_member(self, agent_id: str):
        """添加成员"""
        self.members.add(agent_id)
        self._update_territory()
    
    def remove_member(self, agent_id: str):
        """移除成员"""
        self.members.discard(agent_id)
        if agent_id == self.leader:
            self.leader = None
            self._elect_leader()
        self._update_territory()
    
    def _update_territory(self):
        """更新领土范围"""
        if len(self.members) > 0:
            # 基于成员数量调整领土大小
            base_radius = 5.0
            size_factor = np.sqrt(len(self.members))
            self.territory_radius = base_radius * size_factor
    
    def _elect_leader(self):
        """选举领导者"""
        if not self.members:
            return
        
        # 简单的领导者选举逻辑
        # 实际实现中应该基于智能体的能力、声望等
        self.leader = next(iter(self.members))
    
    def get_development_level(self) -> float:
        """获取发展水平"""
        factors = [
            self.cohesion,
            self.hierarchy_level,
            self.specialization,
            self.resource_sharing,
            len(self.members) / 50.0,  # 规模因子
            len(self.traditions) / 10.0,  # 文化因子
        ]
        return np.mean(factors)
    
    def can_advance_stage(self) -> bool:
        """检查是否可以进入下一阶段"""
        current_level = self.get_development_level()
        member_count = len(self.members)
        
        advancement_requirements = {
            TribalStage.INDIVIDUAL: (2, 0.1),
            TribalStage.PAIR_BONDING: (4, 0.2),
            TribalStage.SMALL_GROUP: (8, 0.3),
            TribalStage.CLAN: (15, 0.4),
            TribalStage.TRIBE: (30, 0.5),
            TribalStage.CHIEFDOM: (50, 0.6),
            TribalStage.EARLY_STATE: (100, 0.7),
        }
        
        if self.stage in advancement_requirements:
            required_members, required_level = advancement_requirements[self.stage]
            return member_count >= required_members and current_level >= required_level
        
        return False

class TribeFormationSystem:
    """部落形成系统"""
    
    def __init__(self):
        self.relationships: Dict[Tuple[str, str], Relationship] = {}
        self.social_groups: Dict[str, SocialGroup] = {}
        self.agent_groups: Dict[str, str] = {}  # agent_id -> group_id
        
        # 形成参数
        self.proximity_threshold = 10.0
        self.interaction_probability = 0.1
        self.group_formation_threshold = 0.6
        self.leadership_threshold = 0.8
        
        # 文化传播参数
        self.cultural_transmission_rate = 0.05
        self.innovation_rate = 0.01
        self.tradition_formation_threshold = 0.7
        
        # 发展事件
        self.formation_events = []
        
        logger.info("部落形成系统初始化完成")
    
    def update_social_dynamics(self, agents: List, dt: float = 1.0):
        """更新社会动态"""
        # 1. 更新智能体间的关系
        self._update_relationships(agents, dt)
        
        # 2. 识别和形成新的社会群体
        self._identify_social_groups(agents)
        
        # 3. 更新现有群体
        self._update_existing_groups(agents, dt)
        
        # 4. 检查群体发展和阶段转换
        self._check_group_advancement()
        
        # 5. 处理群体间的交互
        self._handle_inter_group_interactions()
        
        # 6. 文化传播和创新
        self._process_cultural_evolution(dt)
    
    def _update_relationships(self, agents: List, dt: float):
        """更新智能体间的关系"""
        for i, agent_a in enumerate(agents):
            if not agent_a.alive:
                continue
                
            for agent_b in agents[i+1:]:
                if not agent_b.alive:
                    continue
                
                # 计算距离
                distance = agent_a.position.distance_to(agent_b.position)
                
                # 近距离才可能产生关系
                if distance < self.proximity_threshold:
                    relationship_key = (agent_a.agent_id, agent_b.agent_id)
                    reverse_key = (agent_b.agent_id, agent_a.agent_id)
                    
                    # 检查是否已有关系
                    if relationship_key not in self.relationships and reverse_key not in self.relationships:
                        # 创建新关系的概率
                        if np.random.random() < self.interaction_probability:
                            self._create_relationship(agent_a, agent_b, distance)
                    else:
                        # 更新现有关系
                        existing_key = relationship_key if relationship_key in self.relationships else reverse_key
                        self._update_relationship(existing_key, agent_a, agent_b, distance, dt)
    
    def _create_relationship(self, agent_a, agent_b, distance: float):
        """创建新关系"""
        # 基于智能体特征决定关系类型
        relationship_type = self._determine_relationship_type(agent_a, agent_b)
        
        # 初始关系强度基于距离和兼容性
        compatibility = self._calculate_compatibility(agent_a, agent_b)
        initial_strength = max(0.1, compatibility * (1.0 - distance / self.proximity_threshold))
        
        relationship = Relationship(
            agent_a=agent_a.agent_id,
            agent_b=agent_b.agent_id,
            relationship_type=relationship_type,
            strength=initial_strength,
            duration=0,
            interactions=1,
            created_time=time.time(),
            last_interaction=time.time()
        )
        
        self.relationships[(agent_a.agent_id, agent_b.agent_id)] = relationship
        
        # 记录关系形成事件
        self._record_formation_event(
            event_type="relationship_formed",
            participants=[agent_a.agent_id, agent_b.agent_id],
            details={
                "relationship_type": relationship_type.value,
                "initial_strength": initial_strength,
                "distance": distance
            }
        )
        
        logger.debug(f"新关系形成: {agent_a.agent_id} - {agent_b.agent_id} ({relationship_type.value})")
    
    def _determine_relationship_type(self, agent_a, agent_b) -> RelationshipType:
        """确定关系类型"""
        # 基于智能体特征决定关系类型
        # 这里是简化的逻辑，实际实现应该更复杂
        
        # 年龄相近的可能成为朋友
        age_diff = abs(getattr(agent_a, 'age', 0) - getattr(agent_b, 'age', 0))
        if age_diff < 50:
            return RelationshipType.FRIENDSHIP
        
        # 一个明显年长的可能成为导师
        if age_diff > 100:
            return RelationshipType.TEACHING
        
        # 能量水平相近的可能合作
        energy_diff = abs(agent_a.energy - agent_b.energy)
        if energy_diff < 20:
            return RelationshipType.COOPERATION
        
        # 默认为一般友谊
        return RelationshipType.FRIENDSHIP
    
    def _calculate_compatibility(self, agent_a, agent_b) -> float:
        """计算智能体兼容性"""
        compatibility = 0.5  # 基础兼容性
        
        # 基于行为偏好的兼容性
        if hasattr(agent_a, 'behavior_system') and hasattr(agent_b, 'behavior_system'):
            prefs_a = agent_a.behavior_system.behavior_preferences
            prefs_b = agent_b.behavior_system.behavior_preferences
            
            # 计算行为偏好的相似度
            similarity = 0
            for key in prefs_a:
                if key in prefs_b:
                    similarity += 1 - abs(prefs_a[key] - prefs_b[key])
            
            compatibility += (similarity / len(prefs_a)) * 0.3
        
        # 基于能量水平的兼容性
        energy_similarity = 1 - abs(agent_a.energy - agent_b.energy) / 100.0
        compatibility += energy_similarity * 0.2
        
        return max(0, min(1, compatibility))
    
    def _update_relationship(self, relationship_key: Tuple[str, str], agent_a, agent_b, distance: float, dt: float):
        """更新现有关系"""
        relationship = self.relationships[relationship_key]
        
        # 基于距离和互动质量更新关系
        proximity_factor = 1.0 - (distance / self.proximity_threshold)
        interaction_quality = proximity_factor * 0.5 + np.random.uniform(-0.1, 0.1)
        
        relationship.update_strength(interaction_quality)
        relationship.duration += dt
        
        # 关系强度过低时移除关系
        if relationship.strength < 0.1:
            del self.relationships[relationship_key]
            logger.debug(f"关系消失: {relationship_key[0]} - {relationship_key[1]}")
    
    def _identify_social_groups(self, agents: List):
        """识别和形成社会群体"""
        # 基于关系网络识别群体
        agent_networks = self._build_relationship_networks()
        
        # 寻找紧密连接的群体
        potential_groups = self._find_dense_clusters(agent_networks)
        
        for cluster in potential_groups:
            if len(cluster) >= 2:
                # 检查是否应该形成新群体
                if self._should_form_group(cluster):
                    self._create_social_group(cluster, agents)
    
    def _build_relationship_networks(self) -> Dict[str, List[str]]:
        """构建关系网络"""
        networks = {}
        
        for (agent_a, agent_b), relationship in self.relationships.items():
            if relationship.get_relationship_quality() > self.group_formation_threshold:
                if agent_a not in networks:
                    networks[agent_a] = []
                if agent_b not in networks:
                    networks[agent_b] = []
                
                networks[agent_a].append(agent_b)
                networks[agent_b].append(agent_a)
        
        return networks
    
    def _find_dense_clusters(self, networks: Dict[str, List[str]]) -> List[Set[str]]:
        """寻找密集聚类"""
        clusters = []
        visited = set()
        
        for agent_id in networks:
            if agent_id in visited:
                continue
            
            # 深度优先搜索找到连通组件
            cluster = set()
            stack = [agent_id]
            
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                
                visited.add(current)
                cluster.add(current)
                
                # 添加强连接的邻居
                for neighbor in networks.get(current, []):
                    if neighbor not in visited:
                        # 检查连接强度
                        rel_key = (current, neighbor) if (current, neighbor) in self.relationships else (neighbor, current)
                        if rel_key in self.relationships:
                            rel = self.relationships[rel_key]
                            if rel.get_relationship_quality() > self.group_formation_threshold:
                                stack.append(neighbor)
            
            if len(cluster) >= 2:
                clusters.append(cluster)
        
        return clusters
    
    def _should_form_group(self, cluster: Set[str]) -> bool:
        """判断是否应该形成群体"""
        # 检查聚类中的智能体是否都没有群体或在同一群体
        existing_groups = set()
        for agent_id in cluster:
            if agent_id in self.agent_groups:
                existing_groups.add(self.agent_groups[agent_id])
        
        # 如果所有成员都没有群体，或者来自不同群体且关系足够强
        return len(existing_groups) <= 1
    
    def _create_social_group(self, members: Set[str], agents: List):
        """创建社会群体"""
        # 创建群体ID
        group_id = str(uuid.uuid4())[:8]
        
        # 计算群体中心位置
        agent_dict = {agent.agent_id: agent for agent in agents}
        positions = [agent_dict[agent_id].position for agent_id in members if agent_id in agent_dict]
        
        if not positions:
            return
        
        center_x = np.mean([pos.x for pos in positions])
        center_y = np.mean([pos.y for pos in positions])
        center_position = Vector2D(center_x, center_y)
        
        # 确定群体阶段
        stage = self._determine_group_stage(len(members))
        
        # 选择领导者
        leader = self._select_leader(members, agents)
        
        # 创建群体
        group = SocialGroup(
            group_id=group_id,
            name=f"群体_{group_id}",
            members=members,
            leader=leader,
            stage=stage,
            center_position=center_position,
            territory_radius=5.0 + len(members) * 2.0,
            cohesion=0.5,
            hierarchy_level=0.3,
            specialization=0.2,
            resource_sharing=0.4,
            decision_making="consensus",
            cultural_traits={},
            traditions=[],
            taboos=[],
            rituals=[],
            formation_time=time.time(),
            milestone_events=[]
        )
        
        self.social_groups[group_id] = group
        
        # 更新智能体的群体归属
        for agent_id in members:
            self.agent_groups[agent_id] = group_id
        
        # 记录群体形成事件
        self._record_formation_event(
            event_type="group_formed",
            participants=list(members),
            details={
                "group_id": group_id,
                "stage": stage.value,
                "member_count": len(members),
                "leader": leader
            }
        )
        
        logger.info(f"新群体形成: {group_id} ({stage.value}, {len(members)} 成员)")
    
    def _determine_group_stage(self, member_count: int) -> TribalStage:
        """根据成员数量确定群体阶段"""
        if member_count < 3:
            return TribalStage.PAIR_BONDING
        elif member_count < 8:
            return TribalStage.SMALL_GROUP
        elif member_count < 15:
            return TribalStage.CLAN
        elif member_count < 30:
            return TribalStage.TRIBE
        elif member_count < 50:
            return TribalStage.CHIEFDOM
        else:
            return TribalStage.EARLY_STATE
    
    def _select_leader(self, members: Set[str], agents: List) -> Optional[str]:
        """选择群体领导者"""
        agent_dict = {agent.agent_id: agent for agent in agents}
        
        # 基于多个因素选择领导者
        leadership_scores = {}
        
        for agent_id in members:
            if agent_id not in agent_dict:
                continue
            
            agent = agent_dict[agent_id]
            score = 0
            
            # 年龄因素
            score += min(agent.age / 200.0, 1.0) * 0.3
            
            # 能量因素
            score += (agent.energy / agent.max_energy) * 0.2
            
            # 健康因素
            score += (agent.health / agent.max_health) * 0.2
            
            # 社交网络因素
            connections = sum(1 for key in self.relationships.keys() 
                            if agent_id in key and self.relationships[key].get_relationship_quality() > 0.5)
            score += min(connections / 10.0, 1.0) * 0.3
            
            leadership_scores[agent_id] = score
        
        # 选择得分最高的
        if leadership_scores:
            return max(leadership_scores.keys(), key=lambda x: leadership_scores[x])
        
        return None
    
    def _update_existing_groups(self, agents: List, dt: float):
        """更新现有群体"""
        for group_id, group in self.social_groups.items():
            # 更新群体凝聚力
            self._update_group_cohesion(group, dt)
            
            # 更新群体层级
            self._update_group_hierarchy(group, dt)
            
            # 更新专业化程度
            self._update_group_specialization(group, agents, dt)
            
            # 更新资源共享
            self._update_resource_sharing(group, agents, dt)
            
            # 更新群体中心位置
            self._update_group_center(group, agents)
    
    def _update_group_cohesion(self, group: SocialGroup, dt: float):
        """更新群体凝聚力"""
        # 基于成员间关系强度计算凝聚力
        total_strength = 0
        relationship_count = 0
        
        for member_a in group.members:
            for member_b in group.members:
                if member_a == member_b:
                    continue
                
                rel_key = (member_a, member_b) if (member_a, member_b) in self.relationships else (member_b, member_a)
                if rel_key in self.relationships:
                    total_strength += self.relationships[rel_key].get_relationship_quality()
                    relationship_count += 1
        
        if relationship_count > 0:
            target_cohesion = total_strength / relationship_count
            # 平滑过渡到目标凝聚力
            group.cohesion += (target_cohesion - group.cohesion) * 0.1 * dt
    
    def _update_group_hierarchy(self, group: SocialGroup, dt: float):
        """更新群体层级化程度"""
        # 基于群体大小和发展时间增加层级化
        size_factor = len(group.members) / 100.0
        time_factor = min(1.0, (time.time() - group.formation_time) / 3600.0)
        
        target_hierarchy = min(1.0, size_factor * 0.5 + time_factor * 0.3)
        group.hierarchy_level += (target_hierarchy - group.hierarchy_level) * 0.05 * dt
    
    def _update_group_specialization(self, group: SocialGroup, agents: List, dt: float):
        """更新群体专业化程度"""
        # 基于成员技能多样性计算专业化
        if not hasattr(agents[0], 'skill_specialization'):
            return
        
        specializations = []
        agent_dict = {agent.agent_id: agent for agent in agents}
        
        for member_id in group.members:
            if member_id in agent_dict:
                agent = agent_dict[member_id]
                if hasattr(agent, 'skill_specialization'):
                    specializations.append(agent.skill_specialization)
        
        if specializations:
            # 计算技能分布的多样性
            unique_specializations = len(set(specializations))
            diversity = unique_specializations / len(specializations)
            
            target_specialization = min(1.0, diversity * 1.2)
            group.specialization += (target_specialization - group.specialization) * 0.08 * dt
    
    def _update_resource_sharing(self, group: SocialGroup, agents: List, dt: float):
        """更新资源共享程度"""
        # 基于群体凝聚力和决策方式
        sharing_factor = group.cohesion * 0.7
        
        if group.decision_making == "consensus":
            sharing_factor += 0.2
        elif group.decision_making == "democratic":
            sharing_factor += 0.1
        
        group.resource_sharing += (sharing_factor - group.resource_sharing) * 0.06 * dt
    
    def _update_group_center(self, group: SocialGroup, agents: List):
        """更新群体中心位置"""
        agent_dict = {agent.agent_id: agent for agent in agents if agent.alive}
        positions = [agent_dict[agent_id].position for agent_id in group.members if agent_id in agent_dict]
        
        if positions:
            center_x = np.mean([pos.x for pos in positions])
            center_y = np.mean([pos.y for pos in positions])
            group.center_position = Vector2D(center_x, center_y)
    
    def _check_group_advancement(self):
        """检查群体发展和阶段转换"""
        for group_id, group in self.social_groups.items():
            if group.can_advance_stage():
                old_stage = group.stage
                new_stage = self._get_next_stage(group.stage)
                
                if new_stage:
                    group.stage = new_stage
                    
                    # 记录阶段转换事件
                    self._record_formation_event(
                        event_type="stage_advancement",
                        participants=list(group.members),
                        details={
                            "group_id": group_id,
                            "old_stage": old_stage.value,
                            "new_stage": new_stage.value,
                            "member_count": len(group.members)
                        }
                    )
                    
                    logger.info(f"群体 {group_id} 发展到 {new_stage.value} 阶段")
    
    def _get_next_stage(self, current_stage: TribalStage) -> Optional[TribalStage]:
        """获取下一个发展阶段"""
        stage_order = [
            TribalStage.INDIVIDUAL,
            TribalStage.PAIR_BONDING,
            TribalStage.SMALL_GROUP,
            TribalStage.CLAN,
            TribalStage.TRIBE,
            TribalStage.CHIEFDOM,
            TribalStage.EARLY_STATE
        ]
        
        try:
            current_index = stage_order.index(current_stage)
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def _handle_inter_group_interactions(self):
        """处理群体间的交互"""
        groups = list(self.social_groups.values())
        
        for i, group_a in enumerate(groups):
            for group_b in groups[i+1:]:
                # 计算群体间距离
                distance = group_a.center_position.distance_to(group_b.center_position)
                
                # 近距离群体可能发生交互
                if distance < (group_a.territory_radius + group_b.territory_radius) * 1.5:
                    interaction_type = self._determine_inter_group_interaction(group_a, group_b)
                    self._process_inter_group_interaction(group_a, group_b, interaction_type)
    
    def _determine_inter_group_interaction(self, group_a: SocialGroup, group_b: SocialGroup) -> str:
        """确定群体间交互类型"""
        # 基于群体特征和历史决定交互类型
        resource_competition = abs(group_a.resource_sharing - group_b.resource_sharing)
        cultural_similarity = self._calculate_cultural_similarity(group_a, group_b)
        
        if cultural_similarity > 0.7 and resource_competition < 0.3:
            return "alliance"
        elif cultural_similarity < 0.3 or resource_competition > 0.7:
            return "conflict"
        else:
            return "trade"
    
    def _calculate_cultural_similarity(self, group_a: SocialGroup, group_b: SocialGroup) -> float:
        """计算文化相似度"""
        # 简化的文化相似度计算
        common_traits = set(group_a.cultural_traits.keys()) & set(group_b.cultural_traits.keys())
        
        if not common_traits:
            return 0.5  # 中性相似度
        
        similarity = 0
        for trait in common_traits:
            trait_similarity = 1 - abs(group_a.cultural_traits[trait] - group_b.cultural_traits[trait])
            similarity += trait_similarity
        
        return similarity / len(common_traits)
    
    def _process_inter_group_interaction(self, group_a: SocialGroup, group_b: SocialGroup, interaction_type: str):
        """处理群体间交互"""
        if interaction_type == "alliance":
            # 联盟：增加合作，共享某些文化特征
            self._form_alliance(group_a, group_b)
        elif interaction_type == "conflict":
            # 冲突：竞争资源，可能导致群体分裂或合并
            self._handle_conflict(group_a, group_b)
        elif interaction_type == "trade":
            # 贸易：文化交流，技术传播
            self._handle_trade(group_a, group_b)
    
    def _form_alliance(self, group_a: SocialGroup, group_b: SocialGroup):
        """形成联盟"""
        # 增加两个群体的合作程度
        group_a.cultural_traits['alliance_' + group_b.group_id] = 0.8
        group_b.cultural_traits['alliance_' + group_a.group_id] = 0.8
        
        logger.info(f"群体联盟形成: {group_a.group_id} - {group_b.group_id}")
    
    def _handle_conflict(self, group_a: SocialGroup, group_b: SocialGroup):
        """处理冲突"""
        # 冲突可能导致一方吸收另一方的成员
        if len(group_a.members) > len(group_b.members) * 1.5:
            self._absorb_group(group_a, group_b)
        elif len(group_b.members) > len(group_a.members) * 1.5:
            self._absorb_group(group_b, group_a)
        
        logger.info(f"群体冲突: {group_a.group_id} vs {group_b.group_id}")
    
    def _handle_trade(self, group_a: SocialGroup, group_b: SocialGroup):
        """处理贸易"""
        # 贸易促进文化交流
        for trait, value in group_a.cultural_traits.items():
            if trait not in group_b.cultural_traits:
                group_b.cultural_traits[trait] = value * 0.3
        
        for trait, value in group_b.cultural_traits.items():
            if trait not in group_a.cultural_traits:
                group_a.cultural_traits[trait] = value * 0.3
        
        logger.info(f"群体贸易: {group_a.group_id} - {group_b.group_id}")
    
    def _absorb_group(self, absorbing_group: SocialGroup, absorbed_group: SocialGroup):
        """一个群体吸收另一个群体"""
        # 转移成员
        for member_id in absorbed_group.members:
            absorbing_group.add_member(member_id)
            self.agent_groups[member_id] = absorbing_group.group_id
        
        # 合并文化特征
        for trait, value in absorbed_group.cultural_traits.items():
            if trait in absorbing_group.cultural_traits:
                absorbing_group.cultural_traits[trait] = (
                    absorbing_group.cultural_traits[trait] + value
                ) / 2
            else:
                absorbing_group.cultural_traits[trait] = value * 0.5
        
        # 移除被吸收的群体
        del self.social_groups[absorbed_group.group_id]
        
        logger.info(f"群体吸收: {absorbing_group.group_id} 吸收了 {absorbed_group.group_id}")
    
    def _process_cultural_evolution(self, dt: float):
        """处理文化演进"""
        for group in self.social_groups.values():
            # 文化创新
            if np.random.random() < self.innovation_rate * dt:
                self._create_cultural_innovation(group)
            
            # 传统形成
            if len(group.cultural_traits) > 3 and np.random.random() < self.tradition_formation_threshold * dt:
                self._form_tradition(group)
    
    def _create_cultural_innovation(self, group: SocialGroup):
        """创建文化创新"""
        innovations = [
            "tool_making", "fire_control", "language_complex", "art_expression",
            "ritual_ceremony", "social_hierarchy", "resource_management", "conflict_resolution"
        ]
        
        innovation = np.random.choice(innovations)
        group.cultural_traits[innovation] = np.random.uniform(0.3, 0.8)
        
        logger.info(f"文化创新: {group.group_id} 发展了 {innovation}")
    
    def _form_tradition(self, group: SocialGroup):
        """形成传统"""
        traditions = [
            "成年仪式", "狩猎仪式", "丰收庆典", "祖先崇拜", "领导选举", "技能传承"
        ]
        
        if len(group.traditions) < 5:
            new_tradition = np.random.choice(traditions)
            if new_tradition not in group.traditions:
                group.traditions.append(new_tradition)
                logger.info(f"新传统形成: {group.group_id} - {new_tradition}")
    
    def _record_formation_event(self, event_type: str, participants: List[str], details: Dict):
        """记录形成事件"""
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "participants": participants,
            "details": details
        }
        
        self.formation_events.append(event)
        
        # 限制事件历史大小
        if len(self.formation_events) > 1000:
            self.formation_events = self.formation_events[-800:]
    
    def get_formation_visualization_data(self) -> Dict[str, Any]:
        """获取部落形成可视化数据"""
        return {
            "social_groups": {
                group_id: {
                    "name": group.name,
                    "stage": group.stage.value,
                    "members": list(group.members),
                    "leader": group.leader,
                    "center": [group.center_position.x, group.center_position.y],
                    "territory_radius": group.territory_radius,
                    "cohesion": group.cohesion,
                    "hierarchy_level": group.hierarchy_level,
                    "specialization": group.specialization,
                    "resource_sharing": group.resource_sharing,
                    "cultural_traits": group.cultural_traits,
                    "traditions": group.traditions,
                    "formation_time": group.formation_time,
                    "development_level": group.get_development_level()
                }
                for group_id, group in self.social_groups.items()
            },
            "relationships": {
                f"{key[0]}-{key[1]}": {
                    "type": rel.relationship_type.value,
                    "strength": rel.strength,
                    "quality": rel.get_relationship_quality(),
                    "duration": rel.duration,
                    "interactions": rel.interactions
                }
                for key, rel in self.relationships.items()
            },
            "formation_events": self.formation_events[-50:],  # 最近50个事件
            "statistics": {
                "total_groups": len(self.social_groups),
                "total_relationships": len(self.relationships),
                "stage_distribution": self._get_stage_distribution(),
                "average_group_size": self._get_average_group_size(),
                "cultural_diversity": self._get_cultural_diversity()
            }
        }
    
    def _get_stage_distribution(self) -> Dict[str, int]:
        """获取阶段分布"""
        distribution = {}
        for group in self.social_groups.values():
            stage = group.stage.value
            distribution[stage] = distribution.get(stage, 0) + 1
        return distribution
    
    def _get_average_group_size(self) -> float:
        """获取平均群体大小"""
        if not self.social_groups:
            return 0
        
        total_members = sum(len(group.members) for group in self.social_groups.values())
        return total_members / len(self.social_groups)
    
    def _get_cultural_diversity(self) -> float:
        """获取文化多样性"""
        all_traits = set()
        for group in self.social_groups.values():
            all_traits.update(group.cultural_traits.keys())
        
        return len(all_traits) / max(1, len(self.social_groups))
    
    def get_agent_social_info(self, agent_id: str) -> Dict[str, Any]:
        """获取智能体社会信息"""
        info = {
            "group_id": self.agent_groups.get(agent_id),
            "relationships": [],
            "social_status": "individual"
        }
        
        # 获取关系信息
        for (agent_a, agent_b), relationship in self.relationships.items():
            if agent_a == agent_id or agent_b == agent_id:
                other_agent = agent_b if agent_a == agent_id else agent_a
                info["relationships"].append({
                    "with": other_agent,
                    "type": relationship.relationship_type.value,
                    "strength": relationship.strength,
                    "quality": relationship.get_relationship_quality()
                })
        
        # 获取社会地位
        if info["group_id"]:
            group = self.social_groups.get(info["group_id"])
            if group:
                if group.leader == agent_id:
                    info["social_status"] = "leader"
                else:
                    info["social_status"] = "member"
                
                info["group_info"] = {
                    "stage": group.stage.value,
                    "size": len(group.members),
                    "cohesion": group.cohesion,
                    "traditions": group.traditions
                }
        
        return info