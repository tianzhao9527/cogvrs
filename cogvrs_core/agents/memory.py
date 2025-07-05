"""
Cogvrs - Memory System
记忆系统：智能体的短期和长期记忆管理

Author: Ben Hsu & Claude
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    """记忆项"""
    content: Any
    timestamp: int
    importance: float
    access_count: int = 0
    emotional_value: float = 0.0
    
    def decay(self, decay_rate: float = 0.01):
        """记忆衰减"""
        self.importance *= (1 - decay_rate)
    
    def access(self):
        """访问记忆（增强重要性）"""
        self.access_count += 1
        self.importance = min(1.0, self.importance * 1.1)


@dataclass
class SpatialMemory:
    """空间记忆"""
    location: Tuple[float, float]
    content: str
    value: float
    last_updated: int


class MemorySystem:
    """
    智能体记忆系统
    
    Features:
    - 短期工作记忆
    - 长期情节记忆
    - 空间位置记忆
    - 记忆巩固和遗忘
    - 联想检索
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.capacity = config.get('capacity', 100)
        self.decay_rate = config.get('decay_rate', 0.99)
        self.consolidation_threshold = config.get('consolidation_threshold', 0.7)
        
        # 短期记忆（工作记忆）
        self.working_memory: deque = deque(maxlen=10)
        
        # 长期记忆
        self.long_term_memory: List[MemoryItem] = []
        
        # 空间记忆
        self.spatial_memory: List[SpatialMemory] = []
        
        # 情感记忆映射
        self.emotional_associations: Dict[str, float] = {}
        
        # 记忆统计
        self.total_memories_created = 0
        self.total_memories_forgotten = 0
        
        logger.debug(f"Memory system initialized: capacity={self.capacity}")
    
    def store_experience(self, content: Any, importance: float = 0.5, 
                        emotional_value: float = 0.0, timestamp: int = 0):
        """存储经验到记忆"""
        memory_item = MemoryItem(
            content=content,
            timestamp=timestamp,
            importance=importance,
            emotional_value=emotional_value
        )
        
        # 先放入工作记忆
        self.working_memory.append(memory_item)
        
        # 如果重要性足够高，直接进入长期记忆
        if importance >= self.consolidation_threshold:
            self._consolidate_to_long_term(memory_item)
        
        self.total_memories_created += 1
    
    def store_spatial_memory(self, location: Tuple[float, float], 
                           content: str, value: float, timestamp: int):
        """存储空间记忆"""
        # 检查是否已有相近位置的记忆
        for spatial_mem in self.spatial_memory:
            distance = np.sqrt((spatial_mem.location[0] - location[0])**2 + 
                             (spatial_mem.location[1] - location[1])**2)
            if distance < 2.0:  # 相近位置，更新现有记忆
                spatial_mem.content = content
                spatial_mem.value = value
                spatial_mem.last_updated = timestamp
                return
        
        # 创建新的空间记忆
        spatial_mem = SpatialMemory(location, content, value, timestamp)
        self.spatial_memory.append(spatial_mem)
        
        # 限制空间记忆数量
        if len(self.spatial_memory) > self.capacity:
            self.spatial_memory.sort(key=lambda x: x.value, reverse=True)
            self.spatial_memory = self.spatial_memory[:self.capacity]
    
    def recall_recent(self, count: int = 5) -> List[MemoryItem]:
        """回忆最近的记忆"""
        recent_memories = []
        
        # 从工作记忆获取
        recent_memories.extend(list(self.working_memory)[-count:])
        
        # 从长期记忆获取最近的
        recent_long_term = sorted(
            self.long_term_memory, 
            key=lambda x: x.timestamp, 
            reverse=True
        )[:count]
        
        recent_memories.extend(recent_long_term)
        
        # 访问这些记忆
        for memory in recent_memories:
            memory.access()
        
        return recent_memories[:count]
    
    def recall_important(self, count: int = 5) -> List[MemoryItem]:
        """回忆重要的记忆"""
        important_memories = sorted(
            self.long_term_memory,
            key=lambda x: x.importance,
            reverse=True
        )[:count]
        
        # 访问这些记忆
        for memory in important_memories:
            memory.access()
        
        return important_memories
    
    def recall_emotional(self, emotion_threshold: float = 0.5) -> List[MemoryItem]:
        """回忆情感强烈的记忆"""
        emotional_memories = [
            memory for memory in self.long_term_memory
            if abs(memory.emotional_value) >= emotion_threshold
        ]
        
        # 按情感强度排序
        emotional_memories.sort(key=lambda x: abs(x.emotional_value), reverse=True)
        
        # 访问这些记忆
        for memory in emotional_memories:
            memory.access()
        
        return emotional_memories[:10]
    
    def recall_spatial(self, location: Tuple[float, float], 
                      radius: float = 5.0) -> List[SpatialMemory]:
        """回忆空间位置相关的记忆"""
        nearby_memories = []
        
        for spatial_mem in self.spatial_memory:
            distance = np.sqrt((spatial_mem.location[0] - location[0])**2 + 
                             (spatial_mem.location[1] - location[1])**2)
            if distance <= radius:
                nearby_memories.append(spatial_mem)
        
        # 按价值排序
        nearby_memories.sort(key=lambda x: x.value, reverse=True)
        return nearby_memories
    
    def associate_emotion(self, content_key: str, emotional_value: float):
        """建立情感关联"""
        if content_key in self.emotional_associations:
            # 平滑更新情感值
            self.emotional_associations[content_key] = \
                0.7 * self.emotional_associations[content_key] + 0.3 * emotional_value
        else:
            self.emotional_associations[content_key] = emotional_value
    
    def get_emotional_association(self, content_key: str) -> float:
        """获取情感关联强度"""
        return self.emotional_associations.get(content_key, 0.0)
    
    def consolidate_memories(self):
        """记忆巩固过程"""
        # 从工作记忆向长期记忆转移
        for memory in list(self.working_memory):
            if memory.importance >= self.consolidation_threshold:
                self._consolidate_to_long_term(memory)
        
        # 记忆衰减
        for memory in self.long_term_memory:
            memory.decay(self.decay_rate)
        
        # 清理低重要性记忆
        self._forget_unimportant_memories()
    
    def _consolidate_to_long_term(self, memory_item: MemoryItem):
        """巩固到长期记忆"""
        # 检查是否已存在相似记忆
        for existing_memory in self.long_term_memory:
            if self._memories_similar(memory_item, existing_memory):
                # 合并记忆
                existing_memory.importance = max(
                    existing_memory.importance, memory_item.importance
                )
                existing_memory.access_count += 1
                return
        
        # 添加新记忆
        self.long_term_memory.append(memory_item)
        
        # 限制长期记忆容量
        if len(self.long_term_memory) > self.capacity:
            self._forget_least_important()
    
    def _memories_similar(self, mem1: MemoryItem, mem2: MemoryItem) -> bool:
        """判断两个记忆是否相似"""
        # 简化实现：检查内容类型和时间接近度
        if type(mem1.content) != type(mem2.content):
            return False
        
        time_diff = abs(mem1.timestamp - mem2.timestamp)
        if time_diff < 10:  # 时间很接近
            return True
        
        # 如果是字符串内容，检查相似度
        if isinstance(mem1.content, str) and isinstance(mem2.content, str):
            return mem1.content == mem2.content
        
        return False
    
    def _forget_unimportant_memories(self):
        """遗忘不重要的记忆"""
        threshold = 0.1
        before_count = len(self.long_term_memory)
        
        self.long_term_memory = [
            memory for memory in self.long_term_memory
            if memory.importance >= threshold
        ]
        
        forgotten_count = before_count - len(self.long_term_memory)
        self.total_memories_forgotten += forgotten_count
    
    def _forget_least_important(self):
        """遗忘最不重要的记忆"""
        if len(self.long_term_memory) > self.capacity:
            # 按重要性排序，保留最重要的记忆
            self.long_term_memory.sort(key=lambda x: x.importance, reverse=True)
            forgotten = self.long_term_memory[self.capacity:]
            self.long_term_memory = self.long_term_memory[:self.capacity]
            self.total_memories_forgotten += len(forgotten)
    
    def get_memory_summary(self) -> Dict:
        """获取记忆系统摘要"""
        avg_importance = np.mean([m.importance for m in self.long_term_memory]) \
                        if self.long_term_memory else 0.0
        
        spatial_coverage = len(set([
            (int(sm.location[0] // 5), int(sm.location[1] // 5))
            for sm in self.spatial_memory
        ]))
        
        return {
            'working_memory_size': len(self.working_memory),
            'long_term_memory_size': len(self.long_term_memory),
            'spatial_memory_size': len(self.spatial_memory),
            'avg_importance': avg_importance,
            'total_created': self.total_memories_created,
            'total_forgotten': self.total_memories_forgotten,
            'retention_rate': (self.total_memories_created - self.total_memories_forgotten) / max(1, self.total_memories_created),
            'spatial_coverage': spatial_coverage,
            'emotional_associations': len(self.emotional_associations)
        }
    
    def search_memories(self, query: str, max_results: int = 5) -> List[MemoryItem]:
        """搜索记忆"""
        matching_memories = []
        
        for memory in self.long_term_memory:
            if isinstance(memory.content, str) and query.lower() in memory.content.lower():
                matching_memories.append(memory)
            elif isinstance(memory.content, dict) and any(
                query.lower() in str(v).lower() for v in memory.content.values()
            ):
                matching_memories.append(memory)
        
        # 按重要性和访问次数排序
        matching_memories.sort(
            key=lambda x: x.importance * (1 + x.access_count), 
            reverse=True
        )
        
        return matching_memories[:max_results]
    
    def clear_memories(self):
        """清空所有记忆"""
        self.working_memory.clear()
        self.long_term_memory.clear()
        self.spatial_memory.clear()
        self.emotional_associations.clear()
        self.total_memories_created = 0
        self.total_memories_forgotten = 0
        
        logger.info("All memories cleared")
    
    def save_state(self) -> Dict:
        """保存记忆状态"""
        return {
            'config': self.config,
            'working_memory': [
                {
                    'content': mem.content,
                    'timestamp': mem.timestamp,
                    'importance': mem.importance,
                    'emotional_value': mem.emotional_value
                }
                for mem in self.working_memory
            ],
            'long_term_memory': [
                {
                    'content': mem.content,
                    'timestamp': mem.timestamp,
                    'importance': mem.importance,
                    'access_count': mem.access_count,
                    'emotional_value': mem.emotional_value
                }
                for mem in self.long_term_memory
            ],
            'spatial_memory': [
                {
                    'location': sm.location,
                    'content': sm.content,
                    'value': sm.value,
                    'last_updated': sm.last_updated
                }
                for sm in self.spatial_memory
            ],
            'emotional_associations': self.emotional_associations.copy(),
            'stats': {
                'total_created': self.total_memories_created,
                'total_forgotten': self.total_memories_forgotten
            }
        }
    
    def load_state(self, state: Dict):
        """加载记忆状态"""
        self.config = state.get('config', self.config)
        
        # 恢复工作记忆
        self.working_memory.clear()
        for mem_data in state.get('working_memory', []):
            memory = MemoryItem(
                content=mem_data['content'],
                timestamp=mem_data['timestamp'],
                importance=mem_data['importance'],
                emotional_value=mem_data.get('emotional_value', 0.0)
            )
            self.working_memory.append(memory)
        
        # 恢复长期记忆
        self.long_term_memory = []
        for mem_data in state.get('long_term_memory', []):
            memory = MemoryItem(
                content=mem_data['content'],
                timestamp=mem_data['timestamp'],
                importance=mem_data['importance'],
                access_count=mem_data.get('access_count', 0),
                emotional_value=mem_data.get('emotional_value', 0.0)
            )
            self.long_term_memory.append(memory)
        
        # 恢复空间记忆
        self.spatial_memory = []
        for sm_data in state.get('spatial_memory', []):
            spatial_mem = SpatialMemory(
                location=tuple(sm_data['location']),
                content=sm_data['content'],
                value=sm_data['value'],
                last_updated=sm_data['last_updated']
            )
            self.spatial_memory.append(spatial_mem)
        
        # 恢复情感关联
        self.emotional_associations = state.get('emotional_associations', {})
        
        # 恢复统计
        stats = state.get('stats', {})
        self.total_memories_created = stats.get('total_created', 0)
        self.total_memories_forgotten = stats.get('total_forgotten', 0)