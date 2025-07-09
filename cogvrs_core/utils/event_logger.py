"""
Cogvrs - Centralized Event Logging System
中央事件记录系统：统一记录模拟中的所有重要事件

Author: Ben Hsu & Claude
"""

import time
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """事件类型"""
    # 部落事件
    TRIBE_FORMATION = "tribe_formation"
    TRIBE_DISSOLUTION = "tribe_dissolution"
    TRIBE_LEADERSHIP_CHANGE = "tribe_leadership_change"
    TRIBE_ALLIANCE = "tribe_alliance"
    TRIBE_CONFLICT = "tribe_conflict"
    TRIBE_TRADE = "tribe_trade"
    TRIBE_CULTURAL_DEVELOPMENT = "tribe_cultural_development"
    TRIBE_CIVILIZATION_ADVANCEMENT = "tribe_civilization_advancement"
    TRIBE_MIGRATION = "tribe_migration"
    
    # 智能体事件
    AGENT_BIRTH = "agent_birth"
    AGENT_DEATH = "agent_death"
    AGENT_REPRODUCTION = "agent_reproduction"
    AGENT_EVOLUTION = "agent_evolution"
    AGENT_LEARNING_MILESTONE = "agent_learning_milestone"
    AGENT_SOCIAL_INTERACTION = "agent_social_interaction"
    AGENT_RESOURCE_DISCOVERY = "agent_resource_discovery"
    
    # 气候事件
    CLIMATE_EPOCH_CHANGE = "climate_epoch_change"
    CLIMATE_ZONE_SHIFT = "climate_zone_shift"
    CLIMATE_EXTREME_EVENT = "climate_extreme_event"
    CLIMATE_SEASONAL_CHANGE = "climate_seasonal_change"
    
    # 世界事件
    WORLD_RESOURCE_DEPLETION = "world_resource_depletion"
    WORLD_RESOURCE_REGENERATION = "world_resource_regeneration"
    WORLD_POPULATION_MILESTONE = "world_population_milestone"
    WORLD_MASS_EXTINCTION = "world_mass_extinction"
    WORLD_ECOLOGICAL_SHIFT = "world_ecological_shift"
    
    # 文明事件
    CIVILIZATION_EMERGENCE = "civilization_emergence"
    CIVILIZATION_COLLAPSE = "civilization_collapse"
    CIVILIZATION_TECHNOLOGY_BREAKTHROUGH = "civilization_technology_breakthrough"
    CIVILIZATION_CULTURAL_REVOLUTION = "civilization_cultural_revolution"
    CIVILIZATION_EXPANSION = "civilization_expansion"
    
    # 系统事件
    SYSTEM_SIMULATION_START = "system_simulation_start"
    SYSTEM_SIMULATION_END = "system_simulation_end"
    SYSTEM_MILESTONE_REACHED = "system_milestone_reached"
    SYSTEM_PERFORMANCE_ALERT = "system_performance_alert"


class EventSeverity(Enum):
    """事件严重程度"""
    LOW = "low"           # 日常事件
    MEDIUM = "medium"     # 重要事件
    HIGH = "high"         # 重大事件
    CRITICAL = "critical" # 关键事件


@dataclass
class Event:
    """事件数据结构"""
    event_id: str
    event_type: EventType
    timestamp: float
    simulation_step: int
    severity: EventSeverity
    title: str
    description: str
    data: Dict[str, Any]
    location: Optional[tuple] = None
    participants: Optional[List[str]] = None
    impact_score: float = 0.0
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.participants is None:
            self.participants = []


class EventLogger:
    """中央事件记录器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.events: List[Event] = []
        self.event_counters: Dict[EventType, int] = {}
        self.event_subscribers: Dict[EventType, List[Callable]] = {}
        self.max_events = self.config.get('max_events', 10000)
        self.auto_save = self.config.get('auto_save', True)
        self.save_interval = self.config.get('save_interval', 100)
        
        # 统计数据
        self.total_events = 0
        self.events_this_session = 0
        self.start_time = time.time()
        
        # 事件过滤器
        self.severity_filter = self.config.get('min_severity', EventSeverity.LOW)
        self.type_filters = self.config.get('type_filters', [])
        
        print(f"📝 事件记录器初始化完成")
        print(f"   最大事件数: {self.max_events}")
        print(f"   自动保存: {self.auto_save}")
        
        # 记录系统启动事件
        self.log_event(
            event_type=EventType.SYSTEM_SIMULATION_START,
            severity=EventSeverity.HIGH,
            title="模拟开始",
            description="Cogvrs模拟系统启动",
            data={"config": self.config}
        )
    
    def log_event(self, event_type: EventType, severity: EventSeverity, 
                  title: str, description: str, data: Dict = None,
                  location: tuple = None, participants: List[str] = None,
                  impact_score: float = 0.0, tags: List[str] = None,
                  simulation_step: int = None):
        """记录事件"""
        
        # 检查过滤器
        if not self._should_log_event(event_type, severity):
            return
        
        # 生成事件ID
        event_id = f"{event_type.value}_{int(time.time() * 1000)}"
        
        # 创建事件
        event = Event(
            event_id=event_id,
            event_type=event_type,
            timestamp=time.time(),
            simulation_step=simulation_step or 0,
            severity=severity,
            title=title,
            description=description,
            data=data or {},
            location=location,
            participants=participants or [],
            impact_score=impact_score,
            tags=tags or []
        )
        
        # 添加到事件列表
        self.events.append(event)
        self.total_events += 1
        self.events_this_session += 1
        
        # 更新计数器
        if event_type not in self.event_counters:
            self.event_counters[event_type] = 0
        self.event_counters[event_type] += 1
        
        # 限制事件数量
        if len(self.events) > self.max_events:
            self.events.pop(0)
        
        # 触发订阅者
        self._notify_subscribers(event)
        
        # 自动保存
        if self.auto_save and self.total_events % self.save_interval == 0:
            self._auto_save()
        
        # 记录到日志
        logger.info(f"Event logged: {event_type.value} - {title}")
    
    def _should_log_event(self, event_type: EventType, severity: EventSeverity) -> bool:
        """检查是否应该记录事件"""
        # 严重程度过滤
        severity_levels = {
            EventSeverity.LOW: 0,
            EventSeverity.MEDIUM: 1,
            EventSeverity.HIGH: 2,
            EventSeverity.CRITICAL: 3
        }
        
        if severity_levels[severity] < severity_levels[self.severity_filter]:
            return False
        
        # 类型过滤
        if self.type_filters and event_type not in self.type_filters:
            return False
        
        return True
    
    def _notify_subscribers(self, event: Event):
        """通知订阅者"""
        if event.event_type in self.event_subscribers:
            for callback in self.event_subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event subscriber: {e}")
    
    def _auto_save(self):
        """自动保存事件"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"events_{timestamp}.json"
            self.save_events(filename)
        except Exception as e:
            logger.error(f"Auto-save failed: {e}")
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """订阅事件"""
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        self.event_subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """取消订阅"""
        if event_type in self.event_subscribers:
            self.event_subscribers[event_type].remove(callback)
    
    def get_events(self, event_type: EventType = None, 
                   severity: EventSeverity = None,
                   start_time: float = None, end_time: float = None,
                   limit: int = None) -> List[Event]:
        """获取事件列表"""
        events = self.events
        
        # 事件类型过滤
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # 严重程度过滤
        if severity:
            events = [e for e in events if e.severity == severity]
        
        # 时间范围过滤
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        # 限制数量
        if limit:
            events = events[-limit:]
        
        return events
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """获取事件统计信息"""
        # 按类型统计
        type_stats = {}
        for event_type, count in self.event_counters.items():
            type_stats[event_type.value] = count
        
        # 按严重程度统计
        severity_stats = {}
        for severity in EventSeverity:
            severity_stats[severity.value] = len([
                e for e in self.events if e.severity == severity
            ])
        
        # 时间统计
        session_duration = time.time() - self.start_time
        events_per_minute = self.events_this_session / (session_duration / 60) if session_duration > 0 else 0
        
        return {
            'total_events': self.total_events,
            'events_this_session': self.events_this_session,
            'session_duration': session_duration,
            'events_per_minute': events_per_minute,
            'type_statistics': type_stats,
            'severity_statistics': severity_stats,
            'unique_event_types': len(self.event_counters),
            'average_impact_score': sum(e.impact_score for e in self.events) / len(self.events) if self.events else 0
        }
    
    def get_timeline(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取时间线（最近N小时的事件）"""
        cutoff_time = time.time() - (hours * 3600)
        recent_events = [e for e in self.events if e.timestamp >= cutoff_time]
        
        timeline = []
        for event in sorted(recent_events, key=lambda x: x.timestamp):
            timeline.append({
                'timestamp': event.timestamp,
                'time_str': datetime.fromtimestamp(event.timestamp).strftime('%H:%M:%S'),
                'event_type': event.event_type.value,
                'severity': event.severity.value,
                'title': event.title,
                'description': event.description,
                'location': event.location,
                'participants': event.participants,
                'impact_score': event.impact_score,
                'tags': event.tags
            })
        
        return timeline
    
    def get_major_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取重大事件列表"""
        major_events = [
            e for e in self.events 
            if e.severity in [EventSeverity.HIGH, EventSeverity.CRITICAL]
        ]
        
        # 按影响分数和严重程度排序
        major_events.sort(key=lambda x: (x.severity.value, x.impact_score), reverse=True)
        
        result = []
        for event in major_events[:limit]:
            result.append({
                'timestamp': event.timestamp,
                'time_str': datetime.fromtimestamp(event.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                'event_type': event.event_type.value,
                'severity': event.severity.value,
                'title': event.title,
                'description': event.description,
                'data': event.data,
                'location': event.location,
                'participants': event.participants,
                'impact_score': event.impact_score,
                'tags': event.tags
            })
        
        return result
    
    def save_events(self, filename: str):
        """保存事件到文件"""
        events_data = []
        for event in self.events:
            event_dict = asdict(event)
            event_dict['event_type'] = event.event_type.value
            event_dict['severity'] = event.severity.value
            event_dict['timestamp_str'] = datetime.fromtimestamp(event.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            events_data.append(event_dict)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(events_data)} events to {filename}")
    
    def load_events(self, filename: str):
        """从文件加载事件"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
            
            for event_dict in events_data:
                event = Event(
                    event_id=event_dict['event_id'],
                    event_type=EventType(event_dict['event_type']),
                    timestamp=event_dict['timestamp'],
                    simulation_step=event_dict['simulation_step'],
                    severity=EventSeverity(event_dict['severity']),
                    title=event_dict['title'],
                    description=event_dict['description'],
                    data=event_dict['data'],
                    location=event_dict.get('location'),
                    participants=event_dict.get('participants', []),
                    impact_score=event_dict.get('impact_score', 0.0),
                    tags=event_dict.get('tags', [])
                )
                self.events.append(event)
            
            logger.info(f"Loaded {len(events_data)} events from {filename}")
            
        except Exception as e:
            logger.error(f"Failed to load events from {filename}: {e}")
    
    def clear_events(self):
        """清空事件记录"""
        self.events.clear()
        self.event_counters.clear()
        self.events_this_session = 0
        logger.info("Event log cleared")
    
    def shutdown(self):
        """关闭事件记录器"""
        # 记录系统关闭事件
        self.log_event(
            event_type=EventType.SYSTEM_SIMULATION_END,
            severity=EventSeverity.HIGH,
            title="模拟结束",
            description="Cogvrs模拟系统关闭",
            data=self.get_event_statistics()
        )
        
        # 最终保存
        if self.auto_save:
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"final_events_{timestamp}.json"
                self.save_events(filename)
                print(f"📝 最终事件记录已保存: {filename}")
            except Exception as e:
                logger.error(f"Final save failed: {e}")


# 全局事件记录器实例
_global_event_logger = None


def get_event_logger() -> EventLogger:
    """获取全局事件记录器"""
    global _global_event_logger
    if _global_event_logger is None:
        _global_event_logger = EventLogger()
    return _global_event_logger


def initialize_event_logger(config: Dict = None):
    """初始化全局事件记录器"""
    global _global_event_logger
    _global_event_logger = EventLogger(config)
    return _global_event_logger


def log_event(event_type: EventType, severity: EventSeverity, 
              title: str, description: str, **kwargs):
    """全局事件记录快捷函数"""
    logger = get_event_logger()
    logger.log_event(event_type, severity, title, description, **kwargs)


def log_tribe_event(event_type: EventType, tribe_name: str, 
                    description: str, **kwargs):
    """部落事件记录快捷函数"""
    log_event(
        event_type=event_type,
        severity=EventSeverity.MEDIUM,
        title=f"部落事件: {tribe_name}",
        description=description,
        **kwargs
    )


def log_agent_event(event_type: EventType, agent_id: str, 
                    description: str, **kwargs):
    """智能体事件记录快捷函数"""
    log_event(
        event_type=event_type,
        severity=EventSeverity.LOW,
        title=f"智能体事件: {agent_id}",
        description=description,
        **kwargs
    )


def log_climate_event(event_type: EventType, climate_info: str, 
                      description: str, **kwargs):
    """气候事件记录快捷函数"""
    log_event(
        event_type=event_type,
        severity=EventSeverity.HIGH,
        title=f"气候事件: {climate_info}",
        description=description,
        **kwargs
    )