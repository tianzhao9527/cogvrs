#!/usr/bin/env python3
"""
系统集成模块
整合地形、科技、意识、技能等系统，协调它们之间的交互

Author: Ben Hsu & Claude
"""

import numpy as np
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
import logging
import time

from ..environment.terrain_system import TerrainSystem
from ..civilization.technology_system import TechnologyManager
from ..consciousness.consciousness_system import ConsciousnessManager
from ..skills.skill_system import SkillManager, SkillType
from ..agents.simple_agent import SimpleAgent

logger = logging.getLogger(__name__)

@dataclass
class SystemSynergy:
    """系统协同效应"""
    systems: List[str]
    effect_type: str
    effect_value: float
    description: str

class SystemIntegration:
    """系统集成管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # 各子系统引用（由外部设置）
        self.terrain_system = None
        self.technology_manager = None
        self.consciousness_manager = None
        self.skill_manager = None
        
        # 系统间协同关系
        self.system_synergies = self._define_system_synergies()
        
        # 集成状态跟踪
        self.integration_metrics = {
            'terrain_tech_synergy': 0.0,
            'consciousness_skill_synergy': 0.0,
            'tech_skill_synergy': 0.0,
            'overall_complexity': 0.0
        }
        
        # 事件系统
        self.system_events = []
        
        logger.info("系统集成管理器初始化完成")
    
    def _define_system_synergies(self) -> List[SystemSynergy]:
        """定义系统协同效应"""
        return [
            SystemSynergy(
                systems=['terrain', 'technology'],
                effect_type='terrain_tech_boost',
                effect_value=1.5,
                description='地形特性加速相关科技研发'
            ),
            SystemSynergy(
                systems=['consciousness', 'skill'],
                effect_type='consciousness_skill_boost',
                effect_value=1.3,
                description='意识水平提升技能学习效率'
            ),
            SystemSynergy(
                systems=['technology', 'skill'],
                effect_type='tech_skill_unlock',
                effect_value=1.4,
                description='科技解锁新技能学习机会'
            ),
            SystemSynergy(
                systems=['terrain', 'consciousness'],
                effect_type='environment_awareness',
                effect_value=1.2,
                description='地形复杂性促进环境意识发展'
            ),
            SystemSynergy(
                systems=['skill', 'technology'],
                effect_type='skill_tech_innovation',
                effect_value=1.6,
                description='技能精通促进科技创新'
            )
        ]
    
    def update_agent_systems(self, agent: SimpleAgent, world_state: Dict[str, Any], dt: float = 1.0):
        """更新单个智能体的所有系统"""
        agent_id = agent.agent_id
        
        # 获取智能体位置和状态
        agent_position = agent.position
        agent_state = self._get_agent_state(agent)
        
        # 1. 地形系统影响
        terrain_effects = self.terrain_system.get_terrain_effects_at_position(agent_position)
        
        # 2. 更新技能系统
        skill_system = self.skill_manager.get_individual_skills(agent_id)
        self._update_agent_skills(agent, skill_system, terrain_effects, dt)
        
        # 3. 更新科技系统
        tech_progress = self.technology_manager.get_individual_progress(agent_id)
        self._update_agent_technology(agent, tech_progress, terrain_effects, skill_system, dt)
        
        # 4. 更新意识系统
        consciousness_system = self.consciousness_manager.get_agent_consciousness(agent_id)
        self._update_agent_consciousness(agent, consciousness_system, terrain_effects, 
                                       skill_system, tech_progress, dt)
        
        # 5. 应用系统协同效应
        self._apply_system_synergies(agent, terrain_effects, skill_system, 
                                   tech_progress, consciousness_system)
        
        # 6. 更新智能体属性
        self._update_agent_attributes(agent, terrain_effects, skill_system, 
                                    tech_progress, consciousness_system)
    
    def _get_agent_state(self, agent: SimpleAgent) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            'position': [agent.position.x, agent.position.y],
            'energy': agent.energy,
            'health': agent.health,
            'age': agent.age,
            'offspring_count': agent.offspring_count,
            'social_interactions': agent.social_interactions,
            'total_distance_traveled': agent.total_distance_traveled
        }
    
    def _update_agent_skills(self, agent: SimpleAgent, skill_system, 
                           terrain_effects: Dict[str, Any], dt: float):
        """更新智能体技能"""
        # 基于地形的技能练习机会
        terrain_skill_opportunities = {
            'ocean': [SkillType.FISHING, SkillType.ENDURANCE],
            'river': [SkillType.FISHING, SkillType.AGILITY],
            'mountain': [SkillType.STRENGTH, SkillType.STONE_CUTTING, SkillType.METALWORKING],
            'forest': [SkillType.HUNTING, SkillType.GATHERING, SkillType.WOODWORKING],
            'grassland': [SkillType.HUNTING, SkillType.SPEED],
            'desert': [SkillType.ENDURANCE, SkillType.PERCEPTION],
            'swamp': [SkillType.MEDICINE, SkillType.BALANCE]
        }
        
        # 获取当前地形
        current_terrain = terrain_effects.get('terrain_type', 'grassland')
        
        # 自动技能练习
        if current_terrain in terrain_skill_opportunities:
            available_skills = terrain_skill_opportunities[current_terrain]
            for skill_type in available_skills:
                if np.random.random() < 0.3:  # 30%概率练习
                    terrain_bonus = terrain_effects.get('skill_learning_bonus', 1.0)
                    skill_system.practice_skill(skill_type, 
                                              intensity=0.5 * terrain_bonus, 
                                              duration=dt)
        
        # 基于行为的技能练习
        if hasattr(agent, 'last_action'):
            self._practice_skills_from_action(agent, skill_system, dt)
    
    def _practice_skills_from_action(self, agent: SimpleAgent, skill_system, dt: float):
        """根据行为练习技能"""
        if not agent.last_action:
            return
        
        action_skill_mapping = {
            'move': SkillType.ENDURANCE,
            'eat': SkillType.FORAGING,
            'explore': SkillType.PERCEPTION,
            'communicate': SkillType.COMMUNICATION,
            'cooperate': SkillType.COOPERATION,
            'attack': SkillType.COMBAT,
            'reproduce': SkillType.EMPATHY
        }
        
        action_type = agent.last_action.type.value
        if action_type in action_skill_mapping:
            skill_type = action_skill_mapping[action_type]
            skill_system.practice_skill(skill_type, intensity=0.3, duration=dt)
    
    def _update_agent_technology(self, agent: SimpleAgent, tech_progress, 
                               terrain_effects: Dict[str, Any], skill_system, dt: float):
        """更新智能体科技"""
        # 基于地形的科技研发加速
        terrain_tech_bonuses = {
            'river': ['irrigation', 'pottery', 'boats'],
            'mountain': ['metalworking', 'stone_tools', 'mining'],
            'forest': ['woodworking', 'herbalism', 'hunting_tools'],
            'ocean': ['boats', 'celestial_navigation', 'fishing_techniques'],
            'grassland': ['animal_husbandry', 'plant_cultivation', 'trade_routes']
        }
        
        current_terrain = terrain_effects.get('terrain_type', 'grassland')
        
        # 基于技能的科技研发
        skill_tech_mapping = {
            SkillType.TOOL_MAKING: ['stone_tools', 'basic_weapons'],
            SkillType.FIRE_MAKING: ['pottery', 'metalworking'],
            SkillType.COMMUNICATION: ['language', 'symbolic_writing'],
            SkillType.PROBLEM_SOLVING: ['mathematics', 'logical_systems'],
            SkillType.PATTERN_RECOGNITION: ['astronomy', 'calendar_system']
        }
        
        # 计算研发加速
        research_bonus = 1.0
        
        # 地形加速
        if current_terrain in terrain_tech_bonuses:
            bonus_techs = terrain_tech_bonuses[current_terrain]
            if tech_progress.current_research in bonus_techs:
                research_bonus *= 1.5
        
        # 技能加速
        for skill_type, tech_list in skill_tech_mapping.items():
            if tech_progress.current_research in tech_list:
                skill_level = skill_system.get_skill_level(skill_type)
                research_bonus *= (1.0 + skill_level / 100.0)
        
        # 推进研发
        if tech_progress.current_research:
            tech_progress.advance_research(self.technology_manager.tech_tree, research_bonus * dt)
    
    def _update_agent_consciousness(self, agent: SimpleAgent, consciousness_system, 
                                  terrain_effects: Dict[str, Any], skill_system, 
                                  tech_progress, dt: float):
        """更新智能体意识"""
        # 构建意识刺激
        stimuli = {
            'self_awareness': 0.0,
            'environmental_awareness': 0.0,
            'social_awareness': 0.0,
            'temporal_awareness': 0.0,
            'abstract_thinking': 0.0,
            'metacognition': 0.0,
            'existential_awareness': 0.0
        }
        
        # 地形复杂性影响环境意识
        terrain_complexity = terrain_effects.get('complexity', 0.5)
        stimuli['environmental_awareness'] += terrain_complexity * 0.2
        
        # 技能发展影响自我意识
        skill_mastery = len(skill_system.get_mastered_skills())
        stimuli['self_awareness'] += skill_mastery * 0.1
        
        # 科技发展影响抽象思维
        tech_count = len(tech_progress.unlocked_technologies)
        stimuli['abstract_thinking'] += tech_count * 0.05
        
        # 社交互动影响社会意识
        social_interactions = getattr(agent, 'social_interactions', 0)
        stimuli['social_awareness'] += min(social_interactions * 0.01, 0.5)
        
        # 年龄影响时间意识
        age_factor = min(agent.age / 200.0, 1.0)
        stimuli['temporal_awareness'] += age_factor * 0.1
        
        # 生存经历影响存在意识
        survival_experience = agent.total_distance_traveled / 1000.0
        stimuli['existential_awareness'] += min(survival_experience * 0.02, 0.3)
        
        # 更新意识
        consciousness_system.update_consciousness(stimuli, dt)
    
    def _apply_system_synergies(self, agent: SimpleAgent, terrain_effects, 
                              skill_system, tech_progress, consciousness_system):
        """应用系统协同效应"""
        synergy_effects = {}
        
        for synergy in self.system_synergies:
            effect_active = False
            
            if synergy.effect_type == 'terrain_tech_boost':
                # 地形-科技协同
                terrain_type = terrain_effects.get('terrain_type', 'grassland')
                if terrain_type in ['mountain', 'river', 'forest']:
                    effect_active = True
                    synergy_effects['tech_research_bonus'] = synergy.effect_value
            
            elif synergy.effect_type == 'consciousness_skill_boost':
                # 意识-技能协同
                consciousness_level = consciousness_system.current_level.value
                if consciousness_level >= 3:  # 适应性意识以上
                    effect_active = True
                    synergy_effects['skill_learning_bonus'] = synergy.effect_value
            
            elif synergy.effect_type == 'tech_skill_unlock':
                # 科技-技能解锁
                tech_count = len(tech_progress.unlocked_technologies)
                if tech_count >= 3:
                    effect_active = True
                    synergy_effects['new_skill_unlock'] = synergy.effect_value
            
            if effect_active:
                self._log_synergy_event(agent.agent_id, synergy)
    
    def _log_synergy_event(self, agent_id: str, synergy: SystemSynergy):
        """记录协同效应事件"""
        event = {
            'timestamp': time.time(),
            'agent_id': agent_id,
            'synergy_type': synergy.effect_type,
            'systems': synergy.systems,
            'effect_value': synergy.effect_value,
            'description': synergy.description
        }
        
        self.system_events.append(event)
        
        # 保持事件列表大小
        if len(self.system_events) > 1000:
            self.system_events = self.system_events[-800:]
    
    def _update_agent_attributes(self, agent: SimpleAgent, terrain_effects, 
                               skill_system, tech_progress, consciousness_system):
        """更新智能体属性"""
        # 基于地形的属性修正
        terrain_modifiers = terrain_effects.get('agent_modifiers', {})
        
        # 基于技能的属性提升
        skill_categories = skill_system.get_skill_categories_summary()
        
        # 体能技能影响
        if 'PHYSICAL' in skill_categories:
            physical_bonus = skill_categories['PHYSICAL'].get('average_level', 0) / 100.0
            agent.max_energy = min(200, agent.max_energy * (1 + physical_bonus * 0.2))
        
        # 智力技能影响
        if 'INTELLECTUAL' in skill_categories:
            intellectual_bonus = skill_categories['INTELLECTUAL'].get('average_level', 0) / 100.0
            # 提升感知范围
            agent.perception_radius = min(15, agent.perception_radius * (1 + intellectual_bonus * 0.3))
        
        # 社交技能影响
        if 'SOCIAL' in skill_categories:
            social_bonus = skill_categories['SOCIAL'].get('average_level', 0) / 100.0
            # 提升交流范围
            agent.communication_radius = min(10, agent.communication_radius * (1 + social_bonus * 0.5))
        
        # 意识水平影响
        consciousness_level = consciousness_system.current_level.value
        consciousness_bonus = consciousness_level / 7.0  # 最高等级为7
        
        # 提升学习速度
        agent.learning_rate = min(0.1, agent.learning_rate * (1 + consciousness_bonus * 0.3))
        
        # 科技水平影响
        tech_level = len(tech_progress.unlocked_technologies) / 10.0  # 假设10个科技为满级
        agent.technology_level = min(1.0, tech_level)
    
    def get_integration_report(self) -> Dict[str, Any]:
        """获取系统集成报告"""
        # 收集各系统数据
        terrain_stats = self.terrain_system.get_terrain_distribution()
        tech_stats = self.technology_manager.get_system_stats()
        consciousness_stats = self.consciousness_manager.get_collective_consciousness_report()
        skill_stats = self.skill_manager.get_skill_distribution_report()
        
        # 计算集成度量
        self._calculate_integration_metrics(terrain_stats, tech_stats, 
                                          consciousness_stats, skill_stats)
        
        return {
            'integration_metrics': self.integration_metrics,
            'system_synergies': len(self.system_synergies),
            'recent_synergy_events': self.system_events[-10:],
            'subsystem_stats': {
                'terrain': terrain_stats,
                'technology': tech_stats,
                'consciousness': consciousness_stats,
                'skills': skill_stats
            },
            'complexity_indicators': {
                'terrain_variety': len(terrain_stats),
                'tech_diversity': tech_stats.get('total_technologies', 0),
                'consciousness_levels': consciousness_stats.get('highest_level', 0),
                'skill_specializations': len(skill_stats.get('specialization_distribution', {}))
            }
        }
    
    def _calculate_integration_metrics(self, terrain_stats, tech_stats, 
                                     consciousness_stats, skill_stats):
        """计算集成度量"""
        # 地形-科技协同度
        terrain_variety = len(terrain_stats)
        tech_diversity = tech_stats.get('total_technologies', 0)
        self.integration_metrics['terrain_tech_synergy'] = min(1.0, 
                                                             (terrain_variety * tech_diversity) / 100.0)
        
        # 意识-技能协同度
        avg_consciousness = consciousness_stats.get('average_consciousness', 0)
        skill_diversity = len(skill_stats.get('most_common_skills', []))
        self.integration_metrics['consciousness_skill_synergy'] = min(1.0, 
                                                                    avg_consciousness * skill_diversity / 10.0)
        
        # 科技-技能协同度
        individual_researchers = tech_stats.get('individual_researchers', 0)
        skill_individuals = skill_stats.get('total_individuals', 0)
        if skill_individuals > 0:
            self.integration_metrics['tech_skill_synergy'] = min(1.0, 
                                                               individual_researchers / skill_individuals)
        
        # 整体复杂性
        complexity_factors = [
            terrain_variety / 10.0,
            tech_diversity / 30.0,
            avg_consciousness,
            skill_diversity / 20.0
        ]
        self.integration_metrics['overall_complexity'] = np.mean(complexity_factors)
    
    def get_system_recommendations(self) -> List[Dict[str, Any]]:
        """获取系统优化建议"""
        recommendations = []
        
        # 分析集成度量
        if self.integration_metrics['terrain_tech_synergy'] < 0.3:
            recommendations.append({
                'type': 'terrain_tech_improvement',
                'priority': 'high',
                'description': '地形-科技协同度较低，建议增加地形特定的科技研发奖励',
                'suggested_actions': [
                    '在特定地形增加科技研发点数',
                    '为地形相关科技提供额外资源',
                    '创建地形-科技关联任务'
                ]
            })
        
        if self.integration_metrics['consciousness_skill_synergy'] < 0.4:
            recommendations.append({
                'type': 'consciousness_skill_improvement',
                'priority': 'medium',
                'description': '意识-技能协同度需要提升，建议加强意识发展对技能学习的促进',
                'suggested_actions': [
                    '提高高意识等级的技能学习加成',
                    '为意识突破提供技能奖励',
                    '创建意识-技能关联事件'
                ]
            })
        
        if self.integration_metrics['overall_complexity'] < 0.5:
            recommendations.append({
                'type': 'complexity_enhancement',
                'priority': 'low',
                'description': '系统整体复杂性较低，建议增加系统间的交互深度',
                'suggested_actions': [
                    '增加更多系统协同效应',
                    '创建跨系统的发展路径',
                    '增加系统间的反馈机制'
                ]
            })
        
        return recommendations
    
    def trigger_system_event(self, event_type: str, agent_id: str, parameters: Dict[str, Any]):
        """触发系统事件"""
        if event_type == 'breakthrough':
            # 突破性发现事件
            self._handle_breakthrough_event(agent_id, parameters)
        elif event_type == 'collaboration':
            # 协作事件
            self._handle_collaboration_event(agent_id, parameters)
        elif event_type == 'innovation':
            # 创新事件
            self._handle_innovation_event(agent_id, parameters)
        elif event_type == 'crisis':
            # 危机事件
            self._handle_crisis_event(agent_id, parameters)
    
    def _handle_breakthrough_event(self, agent_id: str, parameters: Dict[str, Any]):
        """处理突破性发现事件"""
        # 同时提升多个系统
        skill_system = self.skill_manager.get_individual_skills(agent_id)
        consciousness_system = self.consciousness_manager.get_agent_consciousness(agent_id)
        tech_progress = self.technology_manager.get_individual_progress(agent_id)
        
        # 技能突破
        if 'skill_type' in parameters:
            skill_type = parameters['skill_type']
            skill_system.practice_skill(skill_type, intensity=5.0, difficulty=2.0)
        
        # 意识突破
        consciousness_system.trigger_consciousness_event('creative_act', intensity=2.0)
        
        # 科技突破
        if tech_progress.current_research:
            tech_progress.advance_research(self.technology_manager.tech_tree, 3.0)
        
        logger.info(f"Agent {agent_id} 经历突破性发现事件")
    
    def _handle_collaboration_event(self, agent_id: str, parameters: Dict[str, Any]):
        """处理协作事件"""
        # 提升社交技能和意识
        skill_system = self.skill_manager.get_individual_skills(agent_id)
        consciousness_system = self.consciousness_manager.get_agent_consciousness(agent_id)
        
        # 社交技能提升
        skill_system.practice_skill(SkillType.COOPERATION, intensity=2.0)
        skill_system.practice_skill(SkillType.COMMUNICATION, intensity=1.5)
        
        # 社会意识提升
        consciousness_system.trigger_consciousness_event('social_interaction', intensity=1.5)
        
        logger.info(f"Agent {agent_id} 参与协作事件")
    
    def _handle_innovation_event(self, agent_id: str, parameters: Dict[str, Any]):
        """处理创新事件"""
        # 提升创新相关技能和意识
        skill_system = self.skill_manager.get_individual_skills(agent_id)
        consciousness_system = self.consciousness_manager.get_agent_consciousness(agent_id)
        
        # 创新技能提升
        skill_system.practice_skill(SkillType.INNOVATION, intensity=3.0)
        skill_system.practice_skill(SkillType.PROBLEM_SOLVING, intensity=2.0)
        
        # 抽象思维提升
        consciousness_system.trigger_consciousness_event('creative_act', intensity=2.0)
        
        logger.info(f"Agent {agent_id} 产生创新事件")
    
    def _handle_crisis_event(self, agent_id: str, parameters: Dict[str, Any]):
        """处理危机事件"""
        # 提升生存技能和危机意识
        skill_system = self.skill_manager.get_individual_skills(agent_id)
        consciousness_system = self.consciousness_manager.get_agent_consciousness(agent_id)
        
        # 生存技能提升
        skill_system.practice_skill(SkillType.PROBLEM_SOLVING, intensity=3.0)
        skill_system.practice_skill(SkillType.ENDURANCE, intensity=2.0)
        
        # 自我意识提升
        consciousness_system.trigger_consciousness_event('survival_success', intensity=2.0)
        
        logger.info(f"Agent {agent_id} 面临危机事件")
    
    def save_integration_state(self) -> Dict[str, Any]:
        """保存集成状态"""
        return {
            'integration_metrics': self.integration_metrics,
            'system_events': self.system_events[-100:],  # 保存最近100个事件
            'synergy_definitions': [
                {
                    'systems': synergy.systems,
                    'effect_type': synergy.effect_type,
                    'effect_value': synergy.effect_value,
                    'description': synergy.description
                }
                for synergy in self.system_synergies
            ]
        }
    
    def load_integration_state(self, state: Dict[str, Any]):
        """加载集成状态"""
        self.integration_metrics = state.get('integration_metrics', self.integration_metrics)
        self.system_events = state.get('system_events', [])
        
        # 恢复协同效应定义
        synergy_data = state.get('synergy_definitions', [])
        self.system_synergies = [
            SystemSynergy(
                systems=data['systems'],
                effect_type=data['effect_type'],
                effect_value=data['effect_value'],
                description=data['description']
            )
            for data in synergy_data
        ]