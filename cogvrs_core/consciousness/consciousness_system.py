#!/usr/bin/env python3
"""
意识发展系统
管理个体智能体的意识等级、认知能力和心理状态发展

Author: Ben Hsu & Claude
"""

import numpy as np
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import logging
import json
import time

logger = logging.getLogger(__name__)

class ConsciousnessLevel(Enum):
    """意识等级"""
    INSTINCTIVE = 1      # 本能反应
    REACTIVE = 2         # 反应性意识
    ADAPTIVE = 3         # 适应性意识
    REFLECTIVE = 4       # 反思性意识
    ABSTRACT = 5         # 抽象思维
    METACOGNITIVE = 6    # 元认知意识
    TRANSCENDENT = 7     # 超越性意识

class CognitiveAbility(Enum):
    """认知能力类型"""
    PERCEPTION = "perception"           # 感知能力
    MEMORY = "memory"                  # 记忆能力
    REASONING = "reasoning"            # 推理能力
    CREATIVITY = "creativity"          # 创造能力
    SELF_AWARENESS = "self_awareness"  # 自我意识
    EMPATHY = "empathy"               # 共情能力
    ABSTRACTION = "abstraction"       # 抽象能力
    METACOGNITION = "metacognition"   # 元认知能力
    THEORY_OF_MIND = "theory_of_mind" # 心理理论
    INTROSPECTION = "introspection"   # 内省能力

@dataclass
class ConsciousnessMetric:
    """意识度量指标"""
    name: str
    value: float             # 当前值 (0-1)
    growth_rate: float       # 成长速度
    max_value: float         # 最大值
    threshold: float         # 激活阈值
    decay_rate: float        # 衰减速度
    description: str
    
    def update(self, stimulus: float, dt: float = 1.0):
        """更新度量值"""
        # 基于刺激增长
        growth = self.growth_rate * stimulus * dt
        
        # 自然衰减
        decay = self.decay_rate * dt
        
        # 更新值
        self.value = np.clip(self.value + growth - decay, 0, self.max_value)
    
    def is_active(self) -> bool:
        """检查是否达到激活阈值"""
        return self.value >= self.threshold

@dataclass
class ConsciousnessState:
    """意识状态"""
    level: ConsciousnessLevel
    cognitive_abilities: Dict[CognitiveAbility, float]
    emotional_state: Dict[str, float]
    awareness_span: float        # 意识范围
    focus_intensity: float       # 专注强度
    self_reflection_depth: float # 自我反思深度
    
    def get_overall_consciousness(self) -> float:
        """获取整体意识水平"""
        ability_avg = np.mean(list(self.cognitive_abilities.values()))
        emotional_stability = 1.0 - np.std(list(self.emotional_state.values()))
        
        return (ability_avg + emotional_stability + self.awareness_span + 
                self.focus_intensity + self.self_reflection_depth) / 5.0

class ConsciousnessSystem:
    """意识发展系统"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.current_level = ConsciousnessLevel.INSTINCTIVE
        self.consciousness_experience = 0.0
        self.development_history = []
        
        # 初始化意识度量
        self.metrics = {
            'self_awareness': ConsciousnessMetric(
                name="自我意识",
                value=0.1,
                growth_rate=0.02,
                max_value=1.0,
                threshold=0.3,
                decay_rate=0.001,
                description="对自身存在和状态的认知"
            ),
            'environmental_awareness': ConsciousnessMetric(
                name="环境意识",
                value=0.2,
                growth_rate=0.03,
                max_value=1.0,
                threshold=0.4,
                decay_rate=0.002,
                description="对周围环境的感知和理解"
            ),
            'social_awareness': ConsciousnessMetric(
                name="社会意识",
                value=0.05,
                growth_rate=0.01,
                max_value=1.0,
                threshold=0.5,
                decay_rate=0.001,
                description="对他者和社会关系的理解"
            ),
            'temporal_awareness': ConsciousnessMetric(
                name="时间意识",
                value=0.0,
                growth_rate=0.005,
                max_value=1.0,
                threshold=0.6,
                decay_rate=0.0005,
                description="对时间流逝和因果关系的理解"
            ),
            'abstract_thinking': ConsciousnessMetric(
                name="抽象思维",
                value=0.0,
                growth_rate=0.008,
                max_value=1.0,
                threshold=0.7,
                decay_rate=0.001,
                description="处理抽象概念和符号的能力"
            ),
            'metacognition': ConsciousnessMetric(
                name="元认知",
                value=0.0,
                growth_rate=0.003,
                max_value=1.0,
                threshold=0.8,
                decay_rate=0.0008,
                description="对自己思维过程的思考"
            ),
            'existential_awareness': ConsciousnessMetric(
                name="存在意识",
                value=0.0,
                growth_rate=0.001,
                max_value=1.0,
                threshold=0.9,
                decay_rate=0.0005,
                description="对存在意义和生命价值的思考"
            )
        }
        
        # 认知能力
        self.cognitive_abilities = {
            CognitiveAbility.PERCEPTION: 0.5,
            CognitiveAbility.MEMORY: 0.3,
            CognitiveAbility.REASONING: 0.2,
            CognitiveAbility.CREATIVITY: 0.1,
            CognitiveAbility.SELF_AWARENESS: 0.1,
            CognitiveAbility.EMPATHY: 0.05,
            CognitiveAbility.ABSTRACTION: 0.0,
            CognitiveAbility.METACOGNITION: 0.0,
            CognitiveAbility.THEORY_OF_MIND: 0.0,
            CognitiveAbility.INTROSPECTION: 0.0
        }
        
        # 情绪状态
        self.emotional_state = {
            'curiosity': 0.7,
            'anxiety': 0.3,
            'satisfaction': 0.4,
            'frustration': 0.2,
            'wonder': 0.1,
            'loneliness': 0.3,
            'confidence': 0.3
        }
        
        # 意识触发器
        self.consciousness_triggers = {
            'survival_success': 0.1,
            'social_interaction': 0.15,
            'problem_solving': 0.2,
            'creative_act': 0.25,
            'self_reflection': 0.3,
            'existential_moment': 0.5
        }
        
        # 发展里程碑
        self.milestones = {
            'first_self_recognition': False,
            'first_other_recognition': False,
            'first_abstract_thought': False,
            'first_metacognitive_moment': False,
            'first_existential_question': False,
            'consciousness_breakthrough': False
        }
        
        logger.debug(f"意识系统初始化 - Agent {agent_id}")
    
    def update_consciousness(self, stimuli: Dict[str, float], dt: float = 1.0):
        """更新意识状态"""
        # 更新各项意识度量
        for metric_name, metric in self.metrics.items():
            stimulus = stimuli.get(metric_name, 0.0)
            metric.update(stimulus, dt)
        
        # 检查意识等级提升
        self._check_level_progression()
        
        # 更新认知能力
        self._update_cognitive_abilities(stimuli, dt)
        
        # 更新情绪状态
        self._update_emotional_state(stimuli, dt)
        
        # 检查里程碑
        self._check_milestones()
        
        # 累积经验
        self.consciousness_experience += sum(stimuli.values()) * dt
    
    def _check_level_progression(self):
        """检查意识等级提升"""
        current_level_value = self.current_level.value
        
        # 定义升级条件
        upgrade_conditions = {
            ConsciousnessLevel.REACTIVE: (
                self.metrics['self_awareness'].is_active() and
                self.metrics['environmental_awareness'].is_active()
            ),
            ConsciousnessLevel.ADAPTIVE: (
                self.metrics['social_awareness'].is_active() and
                self.cognitive_abilities[CognitiveAbility.REASONING] > 0.3
            ),
            ConsciousnessLevel.REFLECTIVE: (
                self.metrics['temporal_awareness'].is_active() and
                self.cognitive_abilities[CognitiveAbility.SELF_AWARENESS] > 0.5
            ),
            ConsciousnessLevel.ABSTRACT: (
                self.metrics['abstract_thinking'].is_active() and
                self.cognitive_abilities[CognitiveAbility.ABSTRACTION] > 0.6
            ),
            ConsciousnessLevel.METACOGNITIVE: (
                self.metrics['metacognition'].is_active() and
                self.cognitive_abilities[CognitiveAbility.METACOGNITION] > 0.7
            ),
            ConsciousnessLevel.TRANSCENDENT: (
                self.metrics['existential_awareness'].is_active() and
                self.cognitive_abilities[CognitiveAbility.INTROSPECTION] > 0.8
            )
        }
        
        # 检查是否可以升级
        for level, condition in upgrade_conditions.items():
            if level.value == current_level_value + 1 and condition:
                self._upgrade_consciousness_level(level)
                break
    
    def _upgrade_consciousness_level(self, new_level: ConsciousnessLevel):
        """升级意识等级"""
        old_level = self.current_level
        self.current_level = new_level
        
        # 记录发展历史
        self.development_history.append({
            'timestamp': time.time(),
            'from_level': old_level.name,
            'to_level': new_level.name,
            'consciousness_experience': self.consciousness_experience,
            'triggered_by': self._get_dominant_metric()
        })
        
        # 提升认知能力
        self._boost_cognitive_abilities(new_level)
        
        logger.info(f"Agent {self.agent_id} 意识等级提升: {old_level.name} -> {new_level.name}")
    
    def _boost_cognitive_abilities(self, new_level: ConsciousnessLevel):
        """根据新意识等级提升认知能力"""
        level_boosts = {
            ConsciousnessLevel.REACTIVE: {
                CognitiveAbility.PERCEPTION: 0.1,
                CognitiveAbility.MEMORY: 0.1
            },
            ConsciousnessLevel.ADAPTIVE: {
                CognitiveAbility.REASONING: 0.15,
                CognitiveAbility.EMPATHY: 0.1
            },
            ConsciousnessLevel.REFLECTIVE: {
                CognitiveAbility.SELF_AWARENESS: 0.2,
                CognitiveAbility.INTROSPECTION: 0.1
            },
            ConsciousnessLevel.ABSTRACT: {
                CognitiveAbility.ABSTRACTION: 0.25,
                CognitiveAbility.CREATIVITY: 0.15
            },
            ConsciousnessLevel.METACOGNITIVE: {
                CognitiveAbility.METACOGNITION: 0.3,
                CognitiveAbility.THEORY_OF_MIND: 0.2
            },
            ConsciousnessLevel.TRANSCENDENT: {
                ability: 0.1 for ability in CognitiveAbility
            }
        }
        
        boosts = level_boosts.get(new_level, {})
        for ability, boost in boosts.items():
            self.cognitive_abilities[ability] = min(
                1.0, self.cognitive_abilities[ability] + boost
            )
    
    def _update_cognitive_abilities(self, stimuli: Dict[str, float], dt: float):
        """更新认知能力"""
        # 基于刺激和使用频率更新能力
        ability_growth = {
            CognitiveAbility.PERCEPTION: stimuli.get('environmental_awareness', 0) * 0.01,
            CognitiveAbility.MEMORY: stimuli.get('self_awareness', 0) * 0.008,
            CognitiveAbility.REASONING: stimuli.get('problem_solving', 0) * 0.012,
            CognitiveAbility.CREATIVITY: stimuli.get('creative_act', 0) * 0.015,
            CognitiveAbility.SELF_AWARENESS: stimuli.get('self_awareness', 0) * 0.01,
            CognitiveAbility.EMPATHY: stimuli.get('social_awareness', 0) * 0.008,
            CognitiveAbility.ABSTRACTION: stimuli.get('abstract_thinking', 0) * 0.01,
            CognitiveAbility.METACOGNITION: stimuli.get('metacognition', 0) * 0.008,
            CognitiveAbility.THEORY_OF_MIND: stimuli.get('social_interaction', 0) * 0.006,
            CognitiveAbility.INTROSPECTION: stimuli.get('self_reflection', 0) * 0.01
        }
        
        for ability, growth in ability_growth.items():
            self.cognitive_abilities[ability] = min(
                1.0, self.cognitive_abilities[ability] + growth * dt
            )
    
    def _update_emotional_state(self, stimuli: Dict[str, float], dt: float):
        """更新情绪状态"""
        # 基于刺激和当前状态更新情绪
        emotion_changes = {
            'curiosity': stimuli.get('environmental_awareness', 0) * 0.1 - 0.01,
            'anxiety': stimuli.get('survival_threat', 0) * 0.2 - 0.015,
            'satisfaction': stimuli.get('survival_success', 0) * 0.15 - 0.008,
            'frustration': stimuli.get('failure', 0) * 0.2 - 0.012,
            'wonder': stimuli.get('abstract_thinking', 0) * 0.3 - 0.005,
            'loneliness': -stimuli.get('social_interaction', 0) * 0.2 + 0.01,
            'confidence': stimuli.get('problem_solving', 0) * 0.1 - 0.008
        }
        
        for emotion, change in emotion_changes.items():
            self.emotional_state[emotion] = np.clip(
                self.emotional_state[emotion] + change * dt, 0, 1
            )
    
    def _check_milestones(self):
        """检查发展里程碑"""
        if (not self.milestones['first_self_recognition'] and 
            self.metrics['self_awareness'].value > 0.4):
            self.milestones['first_self_recognition'] = True
            logger.info(f"Agent {self.agent_id} 达成里程碑: 首次自我认知")
        
        if (not self.milestones['first_other_recognition'] and 
            self.metrics['social_awareness'].value > 0.3):
            self.milestones['first_other_recognition'] = True
            logger.info(f"Agent {self.agent_id} 达成里程碑: 首次他者认知")
        
        if (not self.milestones['first_abstract_thought'] and 
            self.metrics['abstract_thinking'].value > 0.5):
            self.milestones['first_abstract_thought'] = True
            logger.info(f"Agent {self.agent_id} 达成里程碑: 首次抽象思维")
        
        if (not self.milestones['first_metacognitive_moment'] and 
            self.metrics['metacognition'].value > 0.6):
            self.milestones['first_metacognitive_moment'] = True
            logger.info(f"Agent {self.agent_id} 达成里程碑: 首次元认知")
        
        if (not self.milestones['first_existential_question'] and 
            self.metrics['existential_awareness'].value > 0.7):
            self.milestones['first_existential_question'] = True
            logger.info(f"Agent {self.agent_id} 达成里程碑: 首次存在思考")
        
        if (not self.milestones['consciousness_breakthrough'] and 
            self.current_level.value >= 6):
            self.milestones['consciousness_breakthrough'] = True
            logger.info(f"Agent {self.agent_id} 达成里程碑: 意识突破")
    
    def _get_dominant_metric(self) -> str:
        """获取主导的意识度量"""
        return max(self.metrics.keys(), key=lambda k: self.metrics[k].value)
    
    def trigger_consciousness_event(self, event_type: str, intensity: float = 1.0):
        """触发意识事件"""
        if event_type in self.consciousness_triggers:
            stimulus_value = self.consciousness_triggers[event_type] * intensity
            
            # 创建刺激字典
            stimuli = {metric: 0.0 for metric in self.metrics.keys()}
            
            # 根据事件类型分配刺激
            if event_type == 'survival_success':
                stimuli['self_awareness'] = stimulus_value
                stimuli['environmental_awareness'] = stimulus_value * 0.5
            elif event_type == 'social_interaction':
                stimuli['social_awareness'] = stimulus_value
                stimuli['self_awareness'] = stimulus_value * 0.3
            elif event_type == 'problem_solving':
                stimuli['abstract_thinking'] = stimulus_value
                stimuli['self_awareness'] = stimulus_value * 0.4
            elif event_type == 'creative_act':
                stimuli['abstract_thinking'] = stimulus_value
                stimuli['metacognition'] = stimulus_value * 0.6
            elif event_type == 'self_reflection':
                stimuli['self_awareness'] = stimulus_value
                stimuli['metacognition'] = stimulus_value * 0.8
            elif event_type == 'existential_moment':
                stimuli['existential_awareness'] = stimulus_value
                stimuli['metacognition'] = stimulus_value * 0.7
            
            # 更新意识状态
            self.update_consciousness(stimuli)
    
    def get_consciousness_state(self) -> ConsciousnessState:
        """获取当前意识状态"""
        return ConsciousnessState(
            level=self.current_level,
            cognitive_abilities=self.cognitive_abilities.copy(),
            emotional_state=self.emotional_state.copy(),
            awareness_span=self.metrics['environmental_awareness'].value,
            focus_intensity=self.metrics['self_awareness'].value,
            self_reflection_depth=self.metrics['metacognition'].value
        )
    
    def get_consciousness_report(self) -> Dict[str, Any]:
        """获取意识发展报告"""
        state = self.get_consciousness_state()
        
        return {
            'agent_id': self.agent_id,
            'current_level': self.current_level.name,
            'level_value': self.current_level.value,
            'overall_consciousness': state.get_overall_consciousness(),
            'consciousness_experience': self.consciousness_experience,
            'metrics': {
                name: {
                    'value': metric.value,
                    'is_active': metric.is_active(),
                    'description': metric.description
                }
                for name, metric in self.metrics.items()
            },
            'cognitive_abilities': {
                ability.value: value 
                for ability, value in self.cognitive_abilities.items()
            },
            'emotional_state': self.emotional_state.copy(),
            'milestones': self.milestones.copy(),
            'development_history': self.development_history[-10:],  # 最近10个发展事件
            'dominant_metric': self._get_dominant_metric()
        }
    
    def save_state(self) -> Dict[str, Any]:
        """保存意识系统状态"""
        return {
            'agent_id': self.agent_id,
            'current_level': self.current_level.name,
            'consciousness_experience': self.consciousness_experience,
            'development_history': self.development_history,
            'metrics': {
                name: {
                    'value': metric.value,
                    'growth_rate': metric.growth_rate,
                    'max_value': metric.max_value,
                    'threshold': metric.threshold,
                    'decay_rate': metric.decay_rate
                }
                for name, metric in self.metrics.items()
            },
            'cognitive_abilities': self.cognitive_abilities.copy(),
            'emotional_state': self.emotional_state.copy(),
            'milestones': self.milestones.copy()
        }
    
    def load_state(self, state: Dict[str, Any]):
        """加载意识系统状态"""
        self.agent_id = state['agent_id']
        self.current_level = ConsciousnessLevel[state['current_level']]
        self.consciousness_experience = state['consciousness_experience']
        self.development_history = state['development_history']
        
        # 恢复度量数据
        for name, metric_data in state['metrics'].items():
            if name in self.metrics:
                self.metrics[name].value = metric_data['value']
                self.metrics[name].growth_rate = metric_data['growth_rate']
                self.metrics[name].max_value = metric_data['max_value']
                self.metrics[name].threshold = metric_data['threshold']
                self.metrics[name].decay_rate = metric_data['decay_rate']
        
        self.cognitive_abilities = state['cognitive_abilities']
        self.emotional_state = state['emotional_state']
        self.milestones = state['milestones']

class ConsciousnessManager:
    """意识管理器"""
    
    def __init__(self):
        self.agent_consciousness: Dict[str, ConsciousnessSystem] = {}
        self.global_consciousness_events = []
        self.collective_consciousness_metrics = {}
        
        logger.info("意识管理器初始化完成")
    
    def get_agent_consciousness(self, agent_id: str) -> ConsciousnessSystem:
        """获取智能体的意识系统"""
        if agent_id not in self.agent_consciousness:
            self.agent_consciousness[agent_id] = ConsciousnessSystem(agent_id)
        return self.agent_consciousness[agent_id]
    
    def update_all_consciousness(self, agent_stimuli: Dict[str, Dict[str, float]], dt: float = 1.0):
        """更新所有智能体的意识状态"""
        for agent_id, stimuli in agent_stimuli.items():
            consciousness = self.get_agent_consciousness(agent_id)
            consciousness.update_consciousness(stimuli, dt)
    
    def get_collective_consciousness_report(self) -> Dict[str, Any]:
        """获取集体意识报告"""
        if not self.agent_consciousness:
            return {}
        
        # 统计各等级的智能体数量
        level_distribution = {}
        for consciousness in self.agent_consciousness.values():
            level = consciousness.current_level.name
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        # 计算平均意识水平
        avg_consciousness = np.mean([
            consciousness.get_consciousness_state().get_overall_consciousness()
            for consciousness in self.agent_consciousness.values()
        ])
        
        # 统计里程碑达成情况
        milestone_stats = {}
        for consciousness in self.agent_consciousness.values():
            for milestone, achieved in consciousness.milestones.items():
                if milestone not in milestone_stats:
                    milestone_stats[milestone] = 0
                if achieved:
                    milestone_stats[milestone] += 1
        
        return {
            'total_agents': len(self.agent_consciousness),
            'level_distribution': level_distribution,
            'average_consciousness': avg_consciousness,
            'milestone_achievements': milestone_stats,
            'highest_level': max(c.current_level.value for c in self.agent_consciousness.values()),
            'consciousness_events': len(self.global_consciousness_events)
        }
    
    def get_top_conscious_agents(self, n: int = 5) -> List[Dict[str, Any]]:
        """获取意识最高的N个智能体"""
        agents_with_consciousness = [
            (agent_id, consciousness.get_consciousness_state().get_overall_consciousness())
            for agent_id, consciousness in self.agent_consciousness.items()
        ]
        
        agents_with_consciousness.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {
                'agent_id': agent_id,
                'consciousness_level': consciousness,
                'full_report': self.agent_consciousness[agent_id].get_consciousness_report()
            }
            for agent_id, consciousness in agents_with_consciousness[:n]
        ]