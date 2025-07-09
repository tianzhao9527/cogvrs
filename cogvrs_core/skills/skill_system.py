#!/usr/bin/env python3
"""
技能发展系统
管理个体智能体和部落的技能发展、专业化和技能传承

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

class SkillCategory(Enum):
    """技能类别"""
    SURVIVAL = "survival"           # 生存技能
    CRAFTING = "crafting"          # 制造技能
    SOCIAL = "social"              # 社交技能
    INTELLECTUAL = "intellectual"   # 智力技能
    PHYSICAL = "physical"          # 体能技能
    ARTISTIC = "artistic"          # 艺术技能
    LEADERSHIP = "leadership"      # 领导技能
    SPIRITUAL = "spiritual"        # 精神技能
    TECHNICAL = "technical"        # 技术技能
    CULTURAL = "cultural"          # 文化技能

class SkillType(Enum):
    """技能类型"""
    # 生存技能
    HUNTING = "hunting"
    GATHERING = "gathering"
    FORAGING = "foraging"
    FISHING = "fishing"
    SHELTER_BUILDING = "shelter_building"
    FIRE_MAKING = "fire_making"
    FOOD_PREPARATION = "food_preparation"
    WEATHER_PREDICTION = "weather_prediction"
    
    # 制造技能
    TOOL_MAKING = "tool_making"
    POTTERY = "pottery"
    WEAVING = "weaving"
    METALWORKING = "metalworking"
    CONSTRUCTION = "construction"
    WOODWORKING = "woodworking"
    STONE_CUTTING = "stone_cutting"
    
    # 社交技能
    COMMUNICATION = "communication"
    NEGOTIATION = "negotiation"
    EMPATHY = "empathy"
    COOPERATION = "cooperation"
    CONFLICT_RESOLUTION = "conflict_resolution"
    TEACHING = "teaching"
    MENTORING = "mentoring"
    
    # 智力技能
    PROBLEM_SOLVING = "problem_solving"
    PATTERN_RECOGNITION = "pattern_recognition"
    MEMORY_ENHANCEMENT = "memory_enhancement"
    LOGICAL_REASONING = "logical_reasoning"
    ABSTRACT_THINKING = "abstract_thinking"
    CALCULATION = "calculation"
    ANALYSIS = "analysis"
    
    # 体能技能
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    AGILITY = "agility"
    SPEED = "speed"
    COORDINATION = "coordination"
    BALANCE = "balance"
    PERCEPTION = "perception"
    
    # 艺术技能
    MUSIC = "music"
    DANCE = "dance"
    VISUAL_ART = "visual_art"
    STORYTELLING = "storytelling"
    POETRY = "poetry"
    SCULPTURE = "sculpture"
    DECORATION = "decoration"
    
    # 领导技能
    DECISION_MAKING = "decision_making"
    STRATEGIC_PLANNING = "strategic_planning"
    TEAM_MANAGEMENT = "team_management"
    INSPIRATION = "inspiration"
    DELEGATION = "delegation"
    DIPLOMACY = "diplomacy"
    
    # 精神技能
    MEDITATION = "meditation"
    WISDOM = "wisdom"
    INTUITION = "intuition"
    EMOTIONAL_CONTROL = "emotional_control"
    SELF_AWARENESS = "self_awareness"
    SPIRITUAL_GUIDANCE = "spiritual_guidance"
    
    # 技术技能
    INNOVATION = "innovation"
    EXPERIMENTATION = "experimentation"
    ENGINEERING = "engineering"
    MEDICINE = "medicine"
    ASTRONOMY = "astronomy"
    MATHEMATICS = "mathematics"
    
    # 文化技能
    TRADITION_KEEPING = "tradition_keeping"
    RITUAL_PERFORMANCE = "ritual_performance"
    CULTURAL_TRANSMISSION = "cultural_transmission"
    LANGUAGE_DEVELOPMENT = "language_development"
    CEREMONY_ORGANIZATION = "ceremony_organization"

@dataclass
class Skill:
    """技能定义"""
    skill_type: SkillType
    category: SkillCategory
    level: float                 # 技能等级 (0-100)
    experience: float            # 技能经验
    talent_modifier: float       # 天赋修正 (0.5-2.0)
    learning_rate: float         # 学习速度
    decay_rate: float            # 技能衰减速度
    prerequisites: List[SkillType] # 前置技能
    related_skills: List[SkillType] # 相关技能
    mastery_threshold: float     # 精通阈值
    
    def gain_experience(self, amount: float, difficulty: float = 1.0):
        """获得技能经验"""
        # 基于天赋和难度计算经验增长
        adjusted_amount = amount * self.talent_modifier * difficulty
        
        # 技能等级越高，经验增长越慢
        level_penalty = 1.0 - (self.level / 100.0) * 0.5
        
        self.experience += adjusted_amount * self.learning_rate * level_penalty
        
        # 更新技能等级
        self._update_level()
    
    def _update_level(self):
        """更新技能等级"""
        # 简单的经验-等级转换公式
        new_level = min(100.0, np.sqrt(self.experience * 10))
        self.level = new_level
    
    def decay_skill(self, dt: float = 1.0):
        """技能衰减"""
        if self.level > 0:
            decay_amount = self.decay_rate * dt
            self.level = max(0, self.level - decay_amount)
            self.experience = max(0, self.experience - decay_amount * 2)
    
    def is_mastered(self) -> bool:
        """检查是否已精通"""
        return self.level >= self.mastery_threshold
    
    def get_efficiency_bonus(self) -> float:
        """获取效率加成"""
        return 1.0 + (self.level / 100.0) * 0.5

@dataclass
class SkillProgress:
    """技能进展追踪"""
    skill_type: SkillType
    start_time: float
    end_time: Optional[float]
    initial_level: float
    final_level: float
    total_experience: float
    milestones: List[str]

class SkillSystem:
    """技能发展系统"""
    
    def __init__(self, owner_id: str, owner_type: str = "individual"):
        self.owner_id = owner_id
        self.owner_type = owner_type  # "individual" or "tribe"
        
        # 技能集合
        self.skills: Dict[SkillType, Skill] = {}
        
        # 技能天赋（基因决定）
        self.skill_talents = self._generate_skill_talents()
        
        # 技能发展历史
        self.skill_progress: Dict[SkillType, List[SkillProgress]] = {}
        
        # 专业化倾向
        self.specialization_tendency = np.random.choice([
            SkillCategory.SURVIVAL, SkillCategory.CRAFTING, SkillCategory.SOCIAL,
            SkillCategory.INTELLECTUAL, SkillCategory.ARTISTIC
        ])
        
        # 技能传承网络（针对部落）
        self.skill_network: Dict[str, List[SkillType]] = {}
        
        # 技能组合效果
        self.skill_synergies = self._define_skill_synergies()
        
        # 初始化基础技能
        self._initialize_basic_skills()
        
        logger.debug(f"技能系统初始化 - {owner_type} {owner_id}")
    
    def _generate_skill_talents(self) -> Dict[SkillType, float]:
        """生成技能天赋"""
        talents = {}
        
        # 为每个技能类型生成天赋值
        for skill_type in SkillType:
            # 基础天赋在0.8-1.2之间
            base_talent = np.random.uniform(0.8, 1.2)
            
            # 某些技能可能有特殊天赋
            if np.random.random() < 0.1:  # 10%概率获得特殊天赋
                base_talent *= np.random.uniform(1.2, 2.0)
            
            talents[skill_type] = base_talent
        
        return talents
    
    def _define_skill_synergies(self) -> Dict[Tuple[SkillType, ...], float]:
        """定义技能协同效应"""
        return {
            # 生存技能协同
            (SkillType.HUNTING, SkillType.TOOL_MAKING): 1.3,
            (SkillType.GATHERING, SkillType.FORAGING): 1.2,
            (SkillType.FIRE_MAKING, SkillType.FOOD_PREPARATION): 1.4,
            
            # 制造技能协同
            (SkillType.TOOL_MAKING, SkillType.METALWORKING): 1.5,
            (SkillType.POTTERY, SkillType.FIRE_MAKING): 1.3,
            (SkillType.CONSTRUCTION, SkillType.WOODWORKING): 1.4,
            
            # 社交技能协同
            (SkillType.COMMUNICATION, SkillType.TEACHING): 1.3,
            (SkillType.NEGOTIATION, SkillType.DIPLOMACY): 1.4,
            (SkillType.EMPATHY, SkillType.CONFLICT_RESOLUTION): 1.3,
            
            # 智力技能协同
            (SkillType.PROBLEM_SOLVING, SkillType.LOGICAL_REASONING): 1.4,
            (SkillType.PATTERN_RECOGNITION, SkillType.ANALYSIS): 1.3,
            (SkillType.ABSTRACT_THINKING, SkillType.MATHEMATICS): 1.5,
            
            # 艺术技能协同
            (SkillType.MUSIC, SkillType.DANCE): 1.3,
            (SkillType.VISUAL_ART, SkillType.SCULPTURE): 1.4,
            (SkillType.STORYTELLING, SkillType.POETRY): 1.3,
            
            # 跨类别协同
            (SkillType.DECISION_MAKING, SkillType.STRATEGIC_PLANNING, SkillType.INSPIRATION): 1.6,
            (SkillType.MEDICINE, SkillType.GATHERING, SkillType.ANALYSIS): 1.4,
            (SkillType.ASTRONOMY, SkillType.MATHEMATICS, SkillType.PATTERN_RECOGNITION): 1.5,
        }
    
    def _initialize_basic_skills(self):
        """初始化基础技能"""
        basic_skills = [
            SkillType.HUNTING, SkillType.GATHERING, SkillType.COMMUNICATION,
            SkillType.PROBLEM_SOLVING, SkillType.PERCEPTION
        ]
        
        for skill_type in basic_skills:
            self.add_skill(skill_type)
    
    def add_skill(self, skill_type: SkillType, initial_level: float = 0.0):
        """添加新技能"""
        if skill_type in self.skills:
            return
        
        # 获取技能信息
        category = self._get_skill_category(skill_type)
        talent = self.skill_talents.get(skill_type, 1.0)
        
        # 创建技能
        skill = Skill(
            skill_type=skill_type,
            category=category,
            level=initial_level,
            experience=initial_level ** 2 / 10,
            talent_modifier=talent,
            learning_rate=0.1 * talent,
            decay_rate=0.001,
            prerequisites=self._get_skill_prerequisites(skill_type),
            related_skills=self._get_related_skills(skill_type),
            mastery_threshold=80.0
        )
        
        self.skills[skill_type] = skill
        
        # 记录技能开始
        self.skill_progress[skill_type] = [SkillProgress(
            skill_type=skill_type,
            start_time=time.time(),
            end_time=None,
            initial_level=initial_level,
            final_level=initial_level,
            total_experience=0.0,
            milestones=[]
        )]
        
        logger.debug(f"{self.owner_type} {self.owner_id} 获得技能: {skill_type.value}")
    
    def _get_skill_category(self, skill_type: SkillType) -> SkillCategory:
        """获取技能类别"""
        category_mapping = {
            # 生存技能
            SkillType.HUNTING: SkillCategory.SURVIVAL,
            SkillType.GATHERING: SkillCategory.SURVIVAL,
            SkillType.FORAGING: SkillCategory.SURVIVAL,
            SkillType.FISHING: SkillCategory.SURVIVAL,
            SkillType.SHELTER_BUILDING: SkillCategory.SURVIVAL,
            SkillType.FIRE_MAKING: SkillCategory.SURVIVAL,
            SkillType.FOOD_PREPARATION: SkillCategory.SURVIVAL,
            SkillType.WEATHER_PREDICTION: SkillCategory.SURVIVAL,
            
            # 制造技能
            SkillType.TOOL_MAKING: SkillCategory.CRAFTING,
            SkillType.POTTERY: SkillCategory.CRAFTING,
            SkillType.WEAVING: SkillCategory.CRAFTING,
            SkillType.METALWORKING: SkillCategory.CRAFTING,
            SkillType.CONSTRUCTION: SkillCategory.CRAFTING,
            SkillType.WOODWORKING: SkillCategory.CRAFTING,
            SkillType.STONE_CUTTING: SkillCategory.CRAFTING,
            
            # 社交技能
            SkillType.COMMUNICATION: SkillCategory.SOCIAL,
            SkillType.NEGOTIATION: SkillCategory.SOCIAL,
            SkillType.EMPATHY: SkillCategory.SOCIAL,
            SkillType.COOPERATION: SkillCategory.SOCIAL,
            SkillType.CONFLICT_RESOLUTION: SkillCategory.SOCIAL,
            SkillType.TEACHING: SkillCategory.SOCIAL,
            SkillType.MENTORING: SkillCategory.SOCIAL,
            
            # 智力技能
            SkillType.PROBLEM_SOLVING: SkillCategory.INTELLECTUAL,
            SkillType.PATTERN_RECOGNITION: SkillCategory.INTELLECTUAL,
            SkillType.MEMORY_ENHANCEMENT: SkillCategory.INTELLECTUAL,
            SkillType.LOGICAL_REASONING: SkillCategory.INTELLECTUAL,
            SkillType.ABSTRACT_THINKING: SkillCategory.INTELLECTUAL,
            SkillType.CALCULATION: SkillCategory.INTELLECTUAL,
            SkillType.ANALYSIS: SkillCategory.INTELLECTUAL,
            
            # 其他类别映射...
        }
        
        return category_mapping.get(skill_type, SkillCategory.SURVIVAL)
    
    def _get_skill_prerequisites(self, skill_type: SkillType) -> List[SkillType]:
        """获取技能前置要求"""
        prerequisites = {
            SkillType.METALWORKING: [SkillType.FIRE_MAKING, SkillType.TOOL_MAKING],
            SkillType.POTTERY: [SkillType.FIRE_MAKING],
            SkillType.CONSTRUCTION: [SkillType.TOOL_MAKING, SkillType.WOODWORKING],
            SkillType.TEACHING: [SkillType.COMMUNICATION, SkillType.EMPATHY],
            SkillType.STRATEGIC_PLANNING: [SkillType.PROBLEM_SOLVING, SkillType.LOGICAL_REASONING],
            SkillType.MEDICINE: [SkillType.GATHERING, SkillType.ANALYSIS],
            SkillType.ASTRONOMY: [SkillType.PATTERN_RECOGNITION, SkillType.MATHEMATICS],
            SkillType.MATHEMATICS: [SkillType.LOGICAL_REASONING, SkillType.ABSTRACT_THINKING],
        }
        
        return prerequisites.get(skill_type, [])
    
    def _get_related_skills(self, skill_type: SkillType) -> List[SkillType]:
        """获取相关技能"""
        related_skills = {
            SkillType.HUNTING: [SkillType.TOOL_MAKING, SkillType.PERCEPTION],
            SkillType.GATHERING: [SkillType.FORAGING, SkillType.PATTERN_RECOGNITION],
            SkillType.COMMUNICATION: [SkillType.EMPATHY, SkillType.TEACHING],
            SkillType.PROBLEM_SOLVING: [SkillType.LOGICAL_REASONING, SkillType.ABSTRACT_THINKING],
            SkillType.TOOL_MAKING: [SkillType.CONSTRUCTION, SkillType.INNOVATION],
        }
        
        return related_skills.get(skill_type, [])
    
    def practice_skill(self, skill_type: SkillType, intensity: float = 1.0, 
                      duration: float = 1.0, difficulty: float = 1.0) -> bool:
        """练习技能"""
        if skill_type not in self.skills:
            # 检查是否可以学习新技能
            if self._can_learn_skill(skill_type):
                self.add_skill(skill_type)
            else:
                return False
        
        skill = self.skills[skill_type]
        
        # 计算经验增长
        experience_gain = intensity * duration * difficulty
        
        # 应用协同效应
        synergy_bonus = self._calculate_synergy_bonus(skill_type)
        experience_gain *= synergy_bonus
        
        # 获得经验
        skill.gain_experience(experience_gain, difficulty)
        
        # 更新进展记录
        if self.skill_progress[skill_type]:
            progress = self.skill_progress[skill_type][-1]
            progress.final_level = skill.level
            progress.total_experience += experience_gain
            
            # 检查里程碑
            self._check_skill_milestones(skill_type, skill)
        
        return True
    
    def _can_learn_skill(self, skill_type: SkillType) -> bool:
        """检查是否可以学习新技能"""
        prerequisites = self._get_skill_prerequisites(skill_type)
        
        # 检查前置技能
        for prereq in prerequisites:
            if prereq not in self.skills or self.skills[prereq].level < 20:
                return False
        
        return True
    
    def _calculate_synergy_bonus(self, skill_type: SkillType) -> float:
        """计算协同效应加成"""
        total_bonus = 1.0
        
        for synergy_skills, bonus in self.skill_synergies.items():
            if skill_type in synergy_skills:
                # 检查其他技能是否具备
                other_skills = [s for s in synergy_skills if s != skill_type]
                if all(s in self.skills and self.skills[s].level > 10 for s in other_skills):
                    total_bonus *= bonus
        
        return total_bonus
    
    def _check_skill_milestones(self, skill_type: SkillType, skill: Skill):
        """检查技能里程碑"""
        progress = self.skill_progress[skill_type][-1]
        
        milestones = []
        if skill.level >= 25 and "apprentice" not in progress.milestones:
            milestones.append("apprentice")
        if skill.level >= 50 and "journeyman" not in progress.milestones:
            milestones.append("journeyman")
        if skill.level >= 75 and "expert" not in progress.milestones:
            milestones.append("expert")
        if skill.level >= 90 and "master" not in progress.milestones:
            milestones.append("master")
        if skill.level >= 100 and "grandmaster" not in progress.milestones:
            milestones.append("grandmaster")
        
        for milestone in milestones:
            progress.milestones.append(milestone)
            logger.info(f"{self.owner_type} {self.owner_id} 达成技能里程碑: {skill_type.value} - {milestone}")
    
    def update_skills(self, dt: float = 1.0):
        """更新技能状态"""
        for skill in self.skills.values():
            skill.decay_skill(dt)
    
    def get_skill_level(self, skill_type: SkillType) -> float:
        """获取技能等级"""
        if skill_type in self.skills:
            return self.skills[skill_type].level
        return 0.0
    
    def get_mastered_skills(self) -> List[SkillType]:
        """获取精通的技能"""
        return [skill_type for skill_type, skill in self.skills.items() 
                if skill.is_mastered()]
    
    def get_skill_categories_summary(self) -> Dict[SkillCategory, Dict[str, Any]]:
        """获取技能类别摘要"""
        summary = {}
        
        for category in SkillCategory:
            category_skills = [skill for skill in self.skills.values() 
                             if skill.category == category]
            
            if category_skills:
                avg_level = np.mean([skill.level for skill in category_skills])
                max_level = max([skill.level for skill in category_skills])
                skill_count = len(category_skills)
                mastered_count = sum(1 for skill in category_skills if skill.is_mastered())
                
                summary[category] = {
                    'average_level': avg_level,
                    'max_level': max_level,
                    'skill_count': skill_count,
                    'mastered_count': mastered_count,
                    'specialization_score': avg_level * (mastered_count + 1)
                }
        
        return summary
    
    def get_specialization(self) -> Tuple[SkillCategory, float]:
        """获取专业化方向"""
        summary = self.get_skill_categories_summary()
        
        if not summary:
            return self.specialization_tendency, 0.0
        
        # 找到得分最高的类别
        best_category = max(summary.keys(), 
                          key=lambda c: summary[c]['specialization_score'])
        
        score = summary[best_category]['specialization_score']
        
        return best_category, score
    
    def teach_skill(self, student_skill_system: 'SkillSystem', skill_type: SkillType,
                   teaching_intensity: float = 1.0) -> bool:
        """教授技能给其他智能体"""
        if skill_type not in self.skills:
            return False
        
        teacher_skill = self.skills[skill_type]
        
        # 检查教师技能等级
        if teacher_skill.level < 30:
            return False
        
        # 检查是否有教学技能
        teaching_bonus = 1.0
        if SkillType.TEACHING in self.skills:
            teaching_bonus = 1.0 + self.skills[SkillType.TEACHING].level / 100.0
        
        # 学生练习技能
        learning_intensity = teaching_intensity * teaching_bonus * 0.8
        success = student_skill_system.practice_skill(
            skill_type, learning_intensity, difficulty=0.7
        )
        
        if success:
            # 教师也获得教学经验
            if SkillType.TEACHING in self.skills:
                self.practice_skill(SkillType.TEACHING, teaching_intensity * 0.5)
        
        return success
    
    def get_skill_report(self) -> Dict[str, Any]:
        """获取技能报告"""
        specialization, spec_score = self.get_specialization()
        
        return {
            'owner_id': self.owner_id,
            'owner_type': self.owner_type,
            'total_skills': len(self.skills),
            'mastered_skills': len(self.get_mastered_skills()),
            'specialization': specialization.value,
            'specialization_score': spec_score,
            'skill_categories': {
                category.value: data for category, data in 
                self.get_skill_categories_summary().items()
            },
            'top_skills': [
                {
                    'skill': skill_type.value,
                    'level': skill.level,
                    'category': skill.category.value,
                    'mastered': skill.is_mastered()
                }
                for skill_type, skill in sorted(
                    self.skills.items(), 
                    key=lambda x: x[1].level, 
                    reverse=True
                )[:10]
            ],
            'skill_talents': {
                skill_type.value: talent for skill_type, talent in 
                self.skill_talents.items() if talent > 1.2
            }
        }
    
    def save_state(self) -> Dict[str, Any]:
        """保存技能系统状态"""
        return {
            'owner_id': self.owner_id,
            'owner_type': self.owner_type,
            'skills': {
                skill_type.value: {
                    'level': skill.level,
                    'experience': skill.experience,
                    'talent_modifier': skill.talent_modifier
                }
                for skill_type, skill in self.skills.items()
            },
            'skill_talents': {
                skill_type.value: talent for skill_type, talent in self.skill_talents.items()
            },
            'specialization_tendency': self.specialization_tendency.value,
            'skill_progress': {
                skill_type.value: [
                    {
                        'start_time': progress.start_time,
                        'end_time': progress.end_time,
                        'initial_level': progress.initial_level,
                        'final_level': progress.final_level,
                        'total_experience': progress.total_experience,
                        'milestones': progress.milestones
                    }
                    for progress in progress_list
                ]
                for skill_type, progress_list in self.skill_progress.items()
            }
        }
    
    def load_state(self, state: Dict[str, Any]):
        """加载技能系统状态"""
        self.owner_id = state['owner_id']
        self.owner_type = state['owner_type']
        self.specialization_tendency = SkillCategory(state['specialization_tendency'])
        
        # 恢复技能数据
        for skill_name, skill_data in state['skills'].items():
            skill_type = SkillType(skill_name)
            self.add_skill(skill_type, skill_data['level'])
            
            skill = self.skills[skill_type]
            skill.experience = skill_data['experience']
            skill.talent_modifier = skill_data['talent_modifier']

class SkillManager:
    """技能管理器"""
    
    def __init__(self):
        self.individual_skills: Dict[str, SkillSystem] = {}
        self.tribe_skills: Dict[str, SkillSystem] = {}
        self.skill_transfer_network = {}
        
        logger.info("技能管理器初始化完成")
    
    def get_individual_skills(self, agent_id: str) -> SkillSystem:
        """获取个体技能系统"""
        if agent_id not in self.individual_skills:
            self.individual_skills[agent_id] = SkillSystem(agent_id, "individual")
        return self.individual_skills[agent_id]
    
    def get_tribe_skills(self, tribe_id: str) -> SkillSystem:
        """获取部落技能系统"""
        if tribe_id not in self.tribe_skills:
            self.tribe_skills[tribe_id] = SkillSystem(tribe_id, "tribe")
        return self.tribe_skills[tribe_id]
    
    def update_all_skills(self, dt: float = 1.0):
        """更新所有技能系统"""
        for skill_system in self.individual_skills.values():
            skill_system.update_skills(dt)
        
        for skill_system in self.tribe_skills.values():
            skill_system.update_skills(dt)
    
    def facilitate_skill_transfer(self, teacher_id: str, student_id: str,
                                skill_type: SkillType, intensity: float = 1.0) -> bool:
        """促进技能传授"""
        teacher_skills = self.get_individual_skills(teacher_id)
        student_skills = self.get_individual_skills(student_id)
        
        return teacher_skills.teach_skill(student_skills, skill_type, intensity)
    
    def get_skill_distribution_report(self) -> Dict[str, Any]:
        """获取技能分布报告"""
        # 统计所有技能
        all_skills = {}
        specializations = {}
        
        for skill_system in self.individual_skills.values():
            for skill_type, skill in skill_system.skills.items():
                if skill_type not in all_skills:
                    all_skills[skill_type] = {'levels': [], 'count': 0}
                
                all_skills[skill_type]['levels'].append(skill.level)
                all_skills[skill_type]['count'] += 1
            
            # 统计专业化
            spec, score = skill_system.get_specialization()
            if spec not in specializations:
                specializations[spec] = 0
            specializations[spec] += 1
        
        # 计算统计数据
        skill_stats = {}
        for skill_type, data in all_skills.items():
            skill_stats[skill_type.value] = {
                'average_level': np.mean(data['levels']),
                'max_level': max(data['levels']),
                'practitioners': data['count'],
                'mastery_rate': sum(1 for level in data['levels'] if level >= 80) / len(data['levels'])
            }
        
        return {
            'total_individuals': len(self.individual_skills),
            'total_tribes': len(self.tribe_skills),
            'skill_statistics': skill_stats,
            'specialization_distribution': {
                spec.value: count for spec, count in specializations.items()
            },
            'most_common_skills': sorted(
                skill_stats.items(), 
                key=lambda x: x[1]['practitioners'], 
                reverse=True
            )[:10],
            'highest_level_skills': sorted(
                skill_stats.items(), 
                key=lambda x: x[1]['max_level'], 
                reverse=True
            )[:10]
        }