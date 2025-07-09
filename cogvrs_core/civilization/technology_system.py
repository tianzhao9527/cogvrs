#!/usr/bin/env python3
"""
科技发展系统
管理个体和部落的科技发展、技能解锁、科技树进展

Author: Ben Hsu & Claude
"""

import numpy as np
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import logging
import json

logger = logging.getLogger(__name__)

class TechnologyCategory(Enum):
    """科技类别"""
    SURVIVAL = "survival"              # 生存技术
    AGRICULTURE = "agriculture"        # 农业技术
    CRAFTING = "crafting"             # 制造技术
    SOCIAL = "social"                 # 社会技术
    MILITARY = "military"             # 军事技术
    KNOWLEDGE = "knowledge"           # 知识技术
    TRANSPORTATION = "transportation" # 交通技术
    MEDICINE = "medicine"             # 医疗技术
    ASTRONOMY = "astronomy"           # 天文技术
    NAVIGATION = "navigation"         # 导航技术

class TechnologyTier(Enum):
    """科技等级"""
    PRIMITIVE = 1      # 原始技术
    BASIC = 2          # 基础技术
    INTERMEDIATE = 3   # 中级技术
    ADVANCED = 4       # 高级技术
    SOPHISTICATED = 5  # 精密技术

@dataclass
class TechnologyEffect:
    """科技效果"""
    attribute: str           # 影响的属性
    modifier: float          # 修正值
    bonus_type: str          # 加成类型: 'multiplier', 'additive', 'unlock'
    description: str         # 效果描述

@dataclass
class Technology:
    """科技定义"""
    tech_id: str
    name: str
    category: TechnologyCategory
    tier: TechnologyTier
    
    # 研发需求
    research_points: int
    prerequisites: List[str]  # 前置科技
    terrain_requirements: List[str]  # 地形要求
    
    # 科技效果
    effects: List[TechnologyEffect]
    
    # 描述信息
    description: str
    flavor_text: str
    
    # 解锁条件
    min_population: int = 1
    special_requirements: List[str] = None

class TechnologyTree:
    """科技树系统"""
    
    def __init__(self):
        self.technologies: Dict[str, Technology] = {}
        self.tech_dependencies: Dict[str, List[str]] = {}
        self._initialize_technology_tree()
        
        logger.info(f"科技树初始化完成，共 {len(self.technologies)} 项科技")
    
    def _initialize_technology_tree(self):
        """初始化科技树"""
        
        # 生存技术线
        self._add_survival_technologies()
        
        # 农业技术线
        self._add_agriculture_technologies()
        
        # 制造技术线
        self._add_crafting_technologies()
        
        # 社会技术线
        self._add_social_technologies()
        
        # 军事技术线
        self._add_military_technologies()
        
        # 知识技术线
        self._add_knowledge_technologies()
        
        # 交通技术线
        self._add_transportation_technologies()
        
        # 医疗技术线
        self._add_medicine_technologies()
        
        # 天文技术线
        self._add_astronomy_technologies()
        
        # 导航技术线
        self._add_navigation_technologies()
    
    def _add_survival_technologies(self):
        """添加生存技术"""
        techs = [
            Technology(
                tech_id="fire_making",
                name="生火技术",
                category=TechnologyCategory.SURVIVAL,
                tier=TechnologyTier.PRIMITIVE,
                research_points=10,
                prerequisites=[],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("energy_efficiency", 1.2, "multiplier", "提高能量利用效率"),
                    TechnologyEffect("shelter_value", 0.3, "additive", "提高庇护效果"),
                ],
                description="掌握生火技术，提高生存能力",
                flavor_text="火光带来了希望，也带来了文明的曙光"
            ),
            Technology(
                tech_id="basic_shelter",
                name="基础庇护",
                category=TechnologyCategory.SURVIVAL,
                tier=TechnologyTier.PRIMITIVE,
                research_points=15,
                prerequisites=["fire_making"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("health_regen", 1.5, "multiplier", "提高健康恢复速度"),
                    TechnologyEffect("energy_conservation", 0.8, "multiplier", "降低能量消耗"),
                ],
                description="建造简单的庇护所",
                flavor_text="一个简单的庇护所，却是安全的象征"
            ),
            Technology(
                tech_id="food_preservation",
                name="食物保存",
                category=TechnologyCategory.SURVIVAL,
                tier=TechnologyTier.BASIC,
                research_points=25,
                prerequisites=["fire_making"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("resource_efficiency", 1.3, "multiplier", "提高资源利用效率"),
                    TechnologyEffect("food_storage", 1.0, "unlock", "解锁食物储存能力"),
                ],
                description="学会保存食物，减少浪费",
                flavor_text="今天的富余，是明天的希望"
            ),
            Technology(
                tech_id="advanced_shelter",
                name="高级庇护",
                category=TechnologyCategory.SURVIVAL,
                tier=TechnologyTier.INTERMEDIATE,
                research_points=50,
                prerequisites=["basic_shelter", "food_preservation"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("health_bonus", 10, "additive", "增加最大健康值"),
                    TechnologyEffect("weather_resistance", 0.5, "multiplier", "提高天气抗性"),
                ],
                description="建造更加坚固的庇护所",
                flavor_text="真正的家园，不只是避风的港湾"
            ),
        ]
        
        for tech in techs:
            self.technologies[tech.tech_id] = tech
    
    def _add_agriculture_technologies(self):
        """添加农业技术"""
        techs = [
            Technology(
                tech_id="plant_cultivation",
                name="植物栽培",
                category=TechnologyCategory.AGRICULTURE,
                tier=TechnologyTier.PRIMITIVE,
                research_points=20,
                prerequisites=[],
                terrain_requirements=["grassland", "forest"],
                effects=[
                    TechnologyEffect("food_production", 1.5, "multiplier", "提高食物产量"),
                    TechnologyEffect("resource_food", 0.2, "additive", "增加食物资源获取"),
                ],
                description="学会种植植物获取食物",
                flavor_text="种子埋入土中，希望也随之发芽"
            ),
            Technology(
                tech_id="animal_husbandry",
                name="畜牧技术",
                category=TechnologyCategory.AGRICULTURE,
                tier=TechnologyTier.BASIC,
                research_points=35,
                prerequisites=["plant_cultivation"],
                terrain_requirements=["grassland"],
                effects=[
                    TechnologyEffect("food_production", 1.8, "multiplier", "大幅提高食物产量"),
                    TechnologyEffect("material_production", 1.2, "multiplier", "提高材料产量"),
                ],
                description="驯化动物，稳定食物来源",
                flavor_text="与动物的和谐相处，是智慧的体现"
            ),
            Technology(
                tech_id="irrigation",
                name="灌溉技术",
                category=TechnologyCategory.AGRICULTURE,
                tier=TechnologyTier.INTERMEDIATE,
                research_points=60,
                prerequisites=["animal_husbandry"],
                terrain_requirements=["river"],
                effects=[
                    TechnologyEffect("crop_yield", 2.0, "multiplier", "大幅提高农作物产量"),
                    TechnologyEffect("drought_resistance", 0.7, "multiplier", "提高干旱抗性"),
                ],
                description="利用水源灌溉农田",
                flavor_text="水到渠成，文明的根基由此奠定"
            ),
            Technology(
                tech_id="crop_rotation",
                name="轮作技术",
                category=TechnologyCategory.AGRICULTURE,
                tier=TechnologyTier.ADVANCED,
                research_points=80,
                prerequisites=["irrigation"],
                terrain_requirements=["grassland"],
                effects=[
                    TechnologyEffect("soil_fertility", 1.5, "multiplier", "提高土壤肥力"),
                    TechnologyEffect("sustainable_farming", 1.0, "unlock", "解锁可持续农业"),
                ],
                description="通过轮作保持土壤肥力",
                flavor_text="大地需要休息，智慧在于知道何时停止"
            ),
        ]
        
        for tech in techs:
            self.technologies[tech.tech_id] = tech
    
    def _add_crafting_technologies(self):
        """添加制造技术"""
        techs = [
            Technology(
                tech_id="stone_tools",
                name="石器制作",
                category=TechnologyCategory.CRAFTING,
                tier=TechnologyTier.PRIMITIVE,
                research_points=15,
                prerequisites=[],
                terrain_requirements=["mountain", "hill"],
                effects=[
                    TechnologyEffect("tool_efficiency", 1.3, "multiplier", "提高工具效率"),
                    TechnologyEffect("material_gathering", 1.2, "multiplier", "提高材料收集效率"),
                ],
                description="制作简单的石制工具",
                flavor_text="第一把石斧，开启了技术的大门"
            ),
            Technology(
                tech_id="woodworking",
                name="木工技术",
                category=TechnologyCategory.CRAFTING,
                tier=TechnologyTier.BASIC,
                research_points=30,
                prerequisites=["stone_tools"],
                terrain_requirements=["forest"],
                effects=[
                    TechnologyEffect("construction_speed", 1.4, "multiplier", "提高建造速度"),
                    TechnologyEffect("wood_efficiency", 1.3, "multiplier", "提高木材利用效率"),
                ],
                description="学会加工木材制作工具",
                flavor_text="木头在巧手中焕发新生"
            ),
            Technology(
                tech_id="pottery",
                name="陶器制作",
                category=TechnologyCategory.CRAFTING,
                tier=TechnologyTier.BASIC,
                research_points=40,
                prerequisites=["fire_making"],
                terrain_requirements=["river", "swamp"],
                effects=[
                    TechnologyEffect("storage_capacity", 1.5, "multiplier", "提高储存能力"),
                    TechnologyEffect("food_preservation", 1.2, "multiplier", "提高食物保存效果"),
                ],
                description="制作陶器用于储存",
                flavor_text="泥土经过火的洗礼，变成永恒的容器"
            ),
            Technology(
                tech_id="metalworking",
                name="金属加工",
                category=TechnologyCategory.CRAFTING,
                tier=TechnologyTier.INTERMEDIATE,
                research_points=70,
                prerequisites=["pottery", "woodworking"],
                terrain_requirements=["mountain"],
                effects=[
                    TechnologyEffect("tool_durability", 2.0, "multiplier", "大幅提高工具耐久度"),
                    TechnologyEffect("weapon_effectiveness", 1.5, "multiplier", "提高武器效果"),
                ],
                description="掌握金属冶炼和加工技术",
                flavor_text="金属的光芒，照亮了进步的道路"
            ),
        ]
        
        for tech in techs:
            self.technologies[tech.tech_id] = tech
    
    def _add_social_technologies(self):
        """添加社会技术"""
        techs = [
            Technology(
                tech_id="language",
                name="语言系统",
                category=TechnologyCategory.SOCIAL,
                tier=TechnologyTier.PRIMITIVE,
                research_points=25,
                prerequisites=[],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("communication_range", 1.5, "multiplier", "提高通信范围"),
                    TechnologyEffect("knowledge_sharing", 1.3, "multiplier", "提高知识传播效率"),
                ],
                description="发展复杂的语言系统",
                flavor_text="语言是思想的翅膀，让智慧飞翔"
            ),
            Technology(
                tech_id="tribal_organization",
                name="部落组织",
                category=TechnologyCategory.SOCIAL,
                tier=TechnologyTier.BASIC,
                research_points=45,
                prerequisites=["language"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("group_efficiency", 1.4, "multiplier", "提高群体效率"),
                    TechnologyEffect("leadership_bonus", 0.2, "additive", "增加领导力加成"),
                ],
                description="建立有序的部落组织结构",
                flavor_text="团结就是力量，组织就是智慧"
            ),
            Technology(
                tech_id="trade_system",
                name="贸易系统",
                category=TechnologyCategory.SOCIAL,
                tier=TechnologyTier.INTERMEDIATE,
                research_points=65,
                prerequisites=["tribal_organization"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("trade_efficiency", 1.6, "multiplier", "提高贸易效率"),
                    TechnologyEffect("resource_exchange", 1.0, "unlock", "解锁资源交换"),
                ],
                description="建立部落间的贸易网络",
                flavor_text="交换创造价值，贸易连接世界"
            ),
            Technology(
                tech_id="governance",
                name="治理制度",
                category=TechnologyCategory.SOCIAL,
                tier=TechnologyTier.ADVANCED,
                research_points=90,
                prerequisites=["trade_system"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("population_growth", 1.3, "multiplier", "提高人口增长"),
                    TechnologyEffect("conflict_resolution", 0.7, "multiplier", "降低冲突概率"),
                ],
                description="发展复杂的治理体系",
                flavor_text="秩序是文明的基石，治理是智慧的结晶"
            ),
        ]
        
        for tech in techs:
            self.technologies[tech.tech_id] = tech
    
    def _add_military_technologies(self):
        """添加军事技术"""
        techs = [
            Technology(
                tech_id="basic_weapons",
                name="基础武器",
                category=TechnologyCategory.MILITARY,
                tier=TechnologyTier.PRIMITIVE,
                research_points=20,
                prerequisites=["stone_tools"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("combat_effectiveness", 1.3, "multiplier", "提高战斗效率"),
                    TechnologyEffect("hunting_success", 1.2, "multiplier", "提高狩猎成功率"),
                ],
                description="制作简单的武器",
                flavor_text="武器是力量的延伸，也是和平的保障"
            ),
            Technology(
                tech_id="defensive_structures",
                name="防御建筑",
                category=TechnologyCategory.MILITARY,
                tier=TechnologyTier.BASIC,
                research_points=50,
                prerequisites=["basic_weapons", "woodworking"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("defense_bonus", 1.5, "multiplier", "提高防御能力"),
                    TechnologyEffect("territory_control", 1.2, "multiplier", "增强领土控制"),
                ],
                description="建造防御性建筑",
                flavor_text="最好的攻击是防御，最好的防御是准备"
            ),
            Technology(
                tech_id="tactics",
                name="战术学",
                category=TechnologyCategory.MILITARY,
                tier=TechnologyTier.INTERMEDIATE,
                research_points=60,
                prerequisites=["defensive_structures", "tribal_organization"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("group_combat", 1.4, "multiplier", "提高群体战斗力"),
                    TechnologyEffect("strategic_planning", 1.0, "unlock", "解锁战略规划"),
                ],
                description="发展战术和战略思维",
                flavor_text="智慧比蛮力更强大，战术比勇气更重要"
            ),
        ]
        
        for tech in techs:
            self.technologies[tech.tech_id] = tech
    
    def _add_knowledge_technologies(self):
        """添加知识技术"""
        techs = [
            Technology(
                tech_id="oral_tradition",
                name="口述传统",
                category=TechnologyCategory.KNOWLEDGE,
                tier=TechnologyTier.PRIMITIVE,
                research_points=30,
                prerequisites=["language"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("knowledge_retention", 1.4, "multiplier", "提高知识保存"),
                    TechnologyEffect("cultural_unity", 1.2, "multiplier", "增强文化认同"),
                ],
                description="通过口述传承知识",
                flavor_text="故事是智慧的载体，传说是历史的回声"
            ),
            Technology(
                tech_id="symbolic_writing",
                name="符号文字",
                category=TechnologyCategory.KNOWLEDGE,
                tier=TechnologyTier.BASIC,
                research_points=55,
                prerequisites=["oral_tradition"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("information_storage", 1.6, "multiplier", "提高信息储存"),
                    TechnologyEffect("long_distance_communication", 1.3, "multiplier", "改善远距通信"),
                ],
                description="发展符号和文字系统",
                flavor_text="文字是思想的翅膀，让知识跨越时空"
            ),
            Technology(
                tech_id="mathematics",
                name="数学",
                category=TechnologyCategory.KNOWLEDGE,
                tier=TechnologyTier.INTERMEDIATE,
                research_points=70,
                prerequisites=["symbolic_writing"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("calculation_accuracy", 1.5, "multiplier", "提高计算精度"),
                    TechnologyEffect("advanced_construction", 1.0, "unlock", "解锁高级建造"),
                ],
                description="掌握基础数学概念",
                flavor_text="数字是宇宙的语言，计算是思维的艺术"
            ),
        ]
        
        for tech in techs:
            self.technologies[tech.tech_id] = tech
    
    def _add_transportation_technologies(self):
        """添加交通技术"""
        techs = [
            Technology(
                tech_id="path_making",
                name="道路开拓",
                category=TechnologyCategory.TRANSPORTATION,
                tier=TechnologyTier.PRIMITIVE,
                research_points=25,
                prerequisites=[],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("movement_speed", 1.2, "multiplier", "提高移动速度"),
                    TechnologyEffect("terrain_traversal", 0.8, "multiplier", "降低地形阻碍"),
                ],
                description="开拓道路，改善交通",
                flavor_text="路是脚踏出来的，也是希望铺就的"
            ),
            Technology(
                tech_id="simple_vehicles",
                name="简单载具",
                category=TechnologyCategory.TRANSPORTATION,
                tier=TechnologyTier.BASIC,
                research_points=40,
                prerequisites=["path_making", "woodworking"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("cargo_capacity", 1.5, "multiplier", "提高载货能力"),
                    TechnologyEffect("travel_efficiency", 1.3, "multiplier", "提高旅行效率"),
                ],
                description="制作简单的运输工具",
                flavor_text="轮子的转动，推动着文明的前进"
            ),
            Technology(
                tech_id="boats",
                name="船只建造",
                category=TechnologyCategory.TRANSPORTATION,
                tier=TechnologyTier.INTERMEDIATE,
                research_points=60,
                prerequisites=["simple_vehicles"],
                terrain_requirements=["river", "ocean", "coast"],
                effects=[
                    TechnologyEffect("water_travel", 1.0, "unlock", "解锁水上交通"),
                    TechnologyEffect("fishing_efficiency", 1.4, "multiplier", "提高捕鱼效率"),
                ],
                description="建造船只用于水上交通",
                flavor_text="船是征服海洋的工具，也是连接世界的桥梁"
            ),
        ]
        
        for tech in techs:
            self.technologies[tech.tech_id] = tech
    
    def _add_medicine_technologies(self):
        """添加医疗技术"""
        techs = [
            Technology(
                tech_id="herbalism",
                name="草药学",
                category=TechnologyCategory.MEDICINE,
                tier=TechnologyTier.PRIMITIVE,
                research_points=35,
                prerequisites=[],
                terrain_requirements=["forest", "swamp"],
                effects=[
                    TechnologyEffect("healing_effectiveness", 1.3, "multiplier", "提高治疗效果"),
                    TechnologyEffect("disease_resistance", 1.2, "multiplier", "增强疾病抗性"),
                ],
                description="识别和使用草药治疗",
                flavor_text="自然是最好的医生，草药是她的处方"
            ),
            Technology(
                tech_id="basic_surgery",
                name="基础外科",
                category=TechnologyCategory.MEDICINE,
                tier=TechnologyTier.BASIC,
                research_points=50,
                prerequisites=["herbalism", "stone_tools"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("injury_recovery", 1.5, "multiplier", "提高伤病恢复"),
                    TechnologyEffect("survival_rate", 1.3, "multiplier", "提高存活率"),
                ],
                description="掌握基础的外科治疗",
                flavor_text="巧手能够逆转命运，医术能够挽救生命"
            ),
        ]
        
        for tech in techs:
            self.technologies[tech.tech_id] = tech
    
    def _add_astronomy_technologies(self):
        """添加天文技术"""
        techs = [
            Technology(
                tech_id="star_observation",
                name="观星术",
                category=TechnologyCategory.ASTRONOMY,
                tier=TechnologyTier.BASIC,
                research_points=45,
                prerequisites=["oral_tradition"],
                terrain_requirements=["desert", "mountain"],
                effects=[
                    TechnologyEffect("navigation_accuracy", 1.3, "multiplier", "提高导航精度"),
                    TechnologyEffect("seasonal_prediction", 1.0, "unlock", "解锁季节预测"),
                ],
                description="观察星象，预测时令",
                flavor_text="星空是天然的历书，智慧的眼睛能读懂它"
            ),
            Technology(
                tech_id="calendar_system",
                name="历法系统",
                category=TechnologyCategory.ASTRONOMY,
                tier=TechnologyTier.INTERMEDIATE,
                research_points=65,
                prerequisites=["star_observation", "mathematics"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("time_management", 1.4, "multiplier", "提高时间管理"),
                    TechnologyEffect("agricultural_timing", 1.2, "multiplier", "优化农业时机"),
                ],
                description="建立准确的历法系统",
                flavor_text="时间是最公平的裁判，历法是智慧的结晶"
            ),
        ]
        
        for tech in techs:
            self.technologies[tech.tech_id] = tech
    
    def _add_navigation_technologies(self):
        """添加导航技术"""
        techs = [
            Technology(
                tech_id="landmark_navigation",
                name="地标导航",
                category=TechnologyCategory.NAVIGATION,
                tier=TechnologyTier.PRIMITIVE,
                research_points=20,
                prerequisites=[],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("exploration_efficiency", 1.3, "multiplier", "提高探索效率"),
                    TechnologyEffect("return_navigation", 1.0, "unlock", "解锁返回导航"),
                ],
                description="利用地标进行导航",
                flavor_text="山川是天然的路标，记忆是最好的指南针"
            ),
            Technology(
                tech_id="celestial_navigation",
                name="天文导航",
                category=TechnologyCategory.NAVIGATION,
                tier=TechnologyTier.INTERMEDIATE,
                research_points=55,
                prerequisites=["landmark_navigation", "star_observation"],
                terrain_requirements=[],
                effects=[
                    TechnologyEffect("long_distance_travel", 1.5, "multiplier", "提高长距离旅行效率"),
                    TechnologyEffect("weather_prediction", 1.2, "multiplier", "改善天气预测"),
                ],
                description="利用天体进行精确导航",
                flavor_text="星辰指引方向，智慧照亮前路"
            ),
        ]
        
        for tech in techs:
            self.technologies[tech.tech_id] = tech
    
    def get_technology(self, tech_id: str) -> Optional[Technology]:
        """获取科技信息"""
        return self.technologies.get(tech_id)
    
    def get_available_technologies(self, unlocked_techs: Set[str]) -> List[Technology]:
        """获取可研究的科技"""
        available = []
        
        for tech_id, tech in self.technologies.items():
            if tech_id in unlocked_techs:
                continue
            
            # 检查前置条件
            if all(prereq in unlocked_techs for prereq in tech.prerequisites):
                available.append(tech)
        
        return available
    
    def get_tech_tree_data(self) -> Dict[str, Any]:
        """获取完整的科技树数据"""
        return {
            "technologies": {
                tech_id: {
                    "name": tech.name,
                    "category": tech.category.value,
                    "tier": tech.tier.value,
                    "research_points": tech.research_points,
                    "prerequisites": tech.prerequisites,
                    "terrain_requirements": tech.terrain_requirements,
                    "description": tech.description,
                    "effects": [
                        {
                            "attribute": effect.attribute,
                            "modifier": effect.modifier,
                            "bonus_type": effect.bonus_type,
                            "description": effect.description
                        }
                        for effect in tech.effects
                    ]
                }
                for tech_id, tech in self.technologies.items()
            }
        }

class TechnologyProgress:
    """科技进展追踪"""
    
    def __init__(self, owner_id: str, owner_type: str = "individual"):
        self.owner_id = owner_id
        self.owner_type = owner_type  # "individual" or "tribe"
        
        # 科技状态
        self.unlocked_technologies: Set[str] = set()
        self.research_progress: Dict[str, float] = {}  # 研究进度
        self.current_research: Optional[str] = None
        
        # 研究能力
        self.research_points_per_turn = 1.0
        self.research_bonuses: Dict[str, float] = {}
        
        # 科技效果
        self.active_effects: Dict[str, List[TechnologyEffect]] = {}
        
        logger.debug(f"科技进展追踪初始化: {owner_type} {owner_id}")
    
    def start_research(self, tech_id: str, tech_tree: TechnologyTree) -> bool:
        """开始研究科技"""
        tech = tech_tree.get_technology(tech_id)
        if not tech:
            return False
        
        # 检查前置条件
        if not all(prereq in self.unlocked_technologies for prereq in tech.prerequisites):
            return False
        
        # 检查是否已经解锁
        if tech_id in self.unlocked_technologies:
            return False
        
        self.current_research = tech_id
        if tech_id not in self.research_progress:
            self.research_progress[tech_id] = 0.0
        
        logger.info(f"{self.owner_type} {self.owner_id} 开始研究 {tech.name}")
        return True
    
    def advance_research(self, tech_tree: TechnologyTree, bonus_multiplier: float = 1.0) -> Optional[str]:
        """推进研究进度"""
        if not self.current_research:
            return None
        
        tech = tech_tree.get_technology(self.current_research)
        if not tech:
            return None
        
        # 计算研究点数
        research_points = self.research_points_per_turn * bonus_multiplier
        
        # 应用研究加成
        for category, bonus in self.research_bonuses.items():
            if tech.category.value == category:
                research_points *= (1 + bonus)
        
        # 更新进度
        self.research_progress[self.current_research] += research_points
        
        # 检查是否完成
        if self.research_progress[self.current_research] >= tech.research_points:
            completed_tech = self.current_research
            self.unlock_technology(completed_tech, tech_tree)
            self.current_research = None
            return completed_tech
        
        return None
    
    def unlock_technology(self, tech_id: str, tech_tree: TechnologyTree):
        """解锁科技"""
        if tech_id in self.unlocked_technologies:
            return
        
        tech = tech_tree.get_technology(tech_id)
        if not tech:
            return
        
        self.unlocked_technologies.add(tech_id)
        self.active_effects[tech_id] = tech.effects
        
        logger.info(f"{self.owner_type} {self.owner_id} 解锁科技: {tech.name}")
    
    def get_research_status(self, tech_tree: TechnologyTree) -> Dict[str, Any]:
        """获取研究状态"""
        status = {
            "unlocked_count": len(self.unlocked_technologies),
            "unlocked_technologies": list(self.unlocked_technologies),
            "current_research": self.current_research,
            "research_progress": self.research_progress.copy(),
            "research_points_per_turn": self.research_points_per_turn,
            "available_technologies": []
        }
        
        # 获取可研究的科技
        available = tech_tree.get_available_technologies(self.unlocked_technologies)
        status["available_technologies"] = [
            {
                "tech_id": tech.tech_id,
                "name": tech.name,
                "category": tech.category.value,
                "tier": tech.tier.value,
                "research_points": tech.research_points,
                "progress": self.research_progress.get(tech.tech_id, 0.0)
            }
            for tech in available
        ]
        
        return status
    
    def get_technology_effects(self) -> Dict[str, float]:
        """获取所有科技效果的汇总"""
        effects = {}
        
        for tech_effects in self.active_effects.values():
            for effect in tech_effects:
                if effect.bonus_type == "multiplier":
                    current = effects.get(effect.attribute, 1.0)
                    effects[effect.attribute] = current * effect.modifier
                elif effect.bonus_type == "additive":
                    current = effects.get(effect.attribute, 0.0)
                    effects[effect.attribute] = current + effect.modifier
                elif effect.bonus_type == "unlock":
                    effects[effect.attribute] = 1.0  # 解锁状态
        
        return effects
    
    def has_technology(self, tech_id: str) -> bool:
        """检查是否拥有特定科技"""
        return tech_id in self.unlocked_technologies
    
    def get_research_efficiency(self, category: TechnologyCategory) -> float:
        """获取特定类别的研究效率"""
        base_efficiency = 1.0
        category_bonus = self.research_bonuses.get(category.value, 0.0)
        return base_efficiency + category_bonus

class TechnologyManager:
    """科技管理器"""
    
    def __init__(self):
        self.tech_tree = TechnologyTree()
        self.individual_progress: Dict[str, TechnologyProgress] = {}
        self.tribe_progress: Dict[str, TechnologyProgress] = {}
        
        logger.info("科技管理器初始化完成")
    
    def get_individual_progress(self, agent_id: str) -> TechnologyProgress:
        """获取个体科技进展"""
        if agent_id not in self.individual_progress:
            self.individual_progress[agent_id] = TechnologyProgress(agent_id, "individual")
        return self.individual_progress[agent_id]
    
    def get_tribe_progress(self, tribe_id: str) -> TechnologyProgress:
        """获取部落科技进展"""
        if tribe_id not in self.tribe_progress:
            self.tribe_progress[tribe_id] = TechnologyProgress(tribe_id, "tribe")
        return self.tribe_progress[tribe_id]
    
    def update_research(self, dt: float = 1.0):
        """更新所有研究进度"""
        completed_techs = []
        
        # 更新个体研究
        for agent_id, progress in self.individual_progress.items():
            completed = progress.advance_research(self.tech_tree, dt)
            if completed:
                completed_techs.append(("individual", agent_id, completed))
        
        # 更新部落研究
        for tribe_id, progress in self.tribe_progress.items():
            completed = progress.advance_research(self.tech_tree, dt)
            if completed:
                completed_techs.append(("tribe", tribe_id, completed))
        
        return completed_techs
    
    def get_technology_tree_data(self) -> Dict[str, Any]:
        """获取科技树数据"""
        return self.tech_tree.get_tech_tree_data()
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        return {
            "total_technologies": len(self.tech_tree.technologies),
            "individual_researchers": len(self.individual_progress),
            "tribe_researchers": len(self.tribe_progress),
            "categories": len(TechnologyCategory),
            "tiers": len(TechnologyTier)
        }