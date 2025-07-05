"""
Cogvrs - Time Manager
时间管理器：控制模拟的时间流逝和事件调度

Author: Ben Hsu & Claude
"""

import time
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScheduledEvent:
    """计划事件"""
    event_id: str
    trigger_time: int
    callback: Callable
    recurring: bool = False
    interval: int = 0
    data: Dict = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class TimeManager:
    """
    时间管理器
    
    Features:
    - 时间步进控制
    - 事件调度系统
    - 时间加速/减速
    - 暂停和恢复
    - 性能监控
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.dt = config.get('dt', 0.1)  # 时间步长
        self.target_fps = config.get('target_fps', 60)
        self.real_time = config.get('real_time', False)
        self.max_steps = config.get('max_steps', 10000)
        
        # 时间状态
        self.current_step = 0
        self.current_time = 0.0
        self.is_paused = False
        self.speed_multiplier = 1.0
        
        # 事件调度
        self.scheduled_events: List[ScheduledEvent] = []
        self.event_history: List[Dict] = []
        
        # 性能统计
        self.step_times: List[float] = []
        self.last_step_time = time.time()
        self.actual_fps = 0.0
        
        # 时间里程碑
        self.milestones = {}
        
        logger.info(f"TimeManager initialized: dt={self.dt}, fps={self.target_fps}")
    
    def step(self) -> bool:
        """
        执行一个时间步
        
        Returns:
            bool: 是否继续模拟
        """
        if self.is_paused:
            return True
        
        start_time = time.time()
        
        # 检查是否达到最大步数
        if self.current_step >= self.max_steps:
            logger.info(f"Reached maximum steps: {self.max_steps}")
            return False
        
        # 处理计划事件
        self._process_scheduled_events()
        
        # 更新时间
        self.current_step += 1
        self.current_time += self.dt * self.speed_multiplier
        
        # 记录性能
        step_duration = time.time() - start_time
        self.step_times.append(step_duration)
        
        # 保持最近100步的性能数据
        if len(self.step_times) > 100:
            self.step_times.pop(0)
        
        # 计算实际FPS
        self._update_fps_stats()
        
        # 实时模式的帧率控制
        if self.real_time:
            self._maintain_target_fps(step_duration)
        
        return True
    
    def _process_scheduled_events(self):
        """处理计划事件"""
        current_events = []
        
        for event in self.scheduled_events:
            if event.trigger_time <= self.current_step:
                # 执行事件
                try:
                    event.callback(self.current_step, event.data)
                    
                    # 记录事件历史
                    self.event_history.append({
                        'event_id': event.event_id,
                        'trigger_time': event.trigger_time,
                        'execution_time': self.current_step,
                        'data': event.data.copy() if event.data else {}
                    })
                    
                    logger.debug(f"Executed event: {event.event_id} at step {self.current_step}")
                    
                    # 处理重复事件
                    if event.recurring and event.interval > 0:
                        event.trigger_time = self.current_step + event.interval
                        current_events.append(event)
                        
                except Exception as e:
                    logger.error(f"Error executing event {event.event_id}: {e}")
            else:
                current_events.append(event)
        
        self.scheduled_events = current_events
    
    def _update_fps_stats(self):
        """更新FPS统计"""
        current_time = time.time()
        time_since_last = current_time - self.last_step_time
        
        if time_since_last > 0:
            instant_fps = 1.0 / time_since_last
            
            # 平滑FPS计算
            if self.actual_fps == 0:
                self.actual_fps = instant_fps
            else:
                # 指数移动平均
                self.actual_fps = 0.9 * self.actual_fps + 0.1 * instant_fps
        
        self.last_step_time = current_time
    
    def _maintain_target_fps(self, step_duration: float):
        """维持目标FPS"""
        target_step_time = 1.0 / self.target_fps
        sleep_time = target_step_time - step_duration
        
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    def schedule_event(self, event_id: str, delay: int, callback: Callable, 
                      recurring: bool = False, interval: int = 0, data: Dict = None):
        """
        调度事件
        
        Args:
            event_id: 事件唯一标识
            delay: 延迟步数
            callback: 回调函数
            recurring: 是否重复
            interval: 重复间隔
            data: 事件数据
        """
        event = ScheduledEvent(
            event_id=event_id,
            trigger_time=self.current_step + delay,
            callback=callback,
            recurring=recurring,
            interval=interval,
            data=data or {}
        )
        
        self.scheduled_events.append(event)
        logger.debug(f"Scheduled event: {event_id} at step {event.trigger_time}")
    
    def cancel_event(self, event_id: str):
        """取消事件"""
        self.scheduled_events = [
            event for event in self.scheduled_events 
            if event.event_id != event_id
        ]
        logger.debug(f"Cancelled event: {event_id}")
    
    def pause(self):
        """暂停模拟"""
        self.is_paused = True
        logger.info("Simulation paused")
    
    def resume(self):
        """恢复模拟"""
        self.is_paused = False
        self.last_step_time = time.time()
        logger.info("Simulation resumed")
    
    def set_speed(self, multiplier: float):
        """设置时间速度倍数"""
        self.speed_multiplier = max(0.1, min(10.0, multiplier))
        logger.info(f"Time speed set to {self.speed_multiplier}x")
    
    def add_milestone(self, name: str, step: int, description: str = ""):
        """添加时间里程碑"""
        self.milestones[name] = {
            'step': step,
            'description': description,
            'reached': False
        }
    
    def check_milestone(self, name: str) -> bool:
        """检查里程碑是否达到"""
        if name in self.milestones:
            milestone = self.milestones[name]
            if not milestone['reached'] and self.current_step >= milestone['step']:
                milestone['reached'] = True
                logger.info(f"Milestone reached: {name} at step {self.current_step}")
                return True
        return False
    
    def get_time_stats(self) -> Dict:
        """获取时间统计信息"""
        avg_step_time = sum(self.step_times) / len(self.step_times) if self.step_times else 0
        
        return {
            'current_step': self.current_step,
            'current_time': self.current_time,
            'is_paused': self.is_paused,
            'speed_multiplier': self.speed_multiplier,
            'actual_fps': self.actual_fps,
            'target_fps': self.target_fps,
            'avg_step_time': avg_step_time,
            'total_events': len(self.event_history),
            'pending_events': len(self.scheduled_events),
            'progress': self.current_step / self.max_steps if self.max_steps > 0 else 0
        }
    
    def get_recent_events(self, count: int = 10) -> List[Dict]:
        """获取最近的事件历史"""
        return self.event_history[-count:] if self.event_history else []
    
    def reset(self):
        """重置时间管理器"""
        self.current_step = 0
        self.current_time = 0.0
        self.is_paused = False
        self.speed_multiplier = 1.0
        
        self.scheduled_events.clear()
        self.event_history.clear()
        self.step_times.clear()
        
        for milestone in self.milestones.values():
            milestone['reached'] = False
        
        self.last_step_time = time.time()
        self.actual_fps = 0.0
        
        logger.info("TimeManager reset")
    
    def save_state(self) -> Dict:
        """保存时间状态"""
        return {
            'current_step': self.current_step,
            'current_time': self.current_time,
            'speed_multiplier': self.speed_multiplier,
            'milestones': self.milestones.copy(),
            'event_history': self.event_history.copy()
        }
    
    def load_state(self, state: Dict):
        """加载时间状态"""
        self.current_step = state.get('current_step', 0)
        self.current_time = state.get('current_time', 0.0)
        self.speed_multiplier = state.get('speed_multiplier', 1.0)
        self.milestones = state.get('milestones', {})
        self.event_history = state.get('event_history', [])
        
        logger.info(f"TimeManager state loaded: step {self.current_step}")


# 时间相关的工具函数
def format_simulation_time(time_step: int, dt: float = 0.1) -> str:
    """格式化模拟时间显示"""
    total_seconds = time_step * dt
    
    days = int(total_seconds // (24 * 3600))
    hours = int((total_seconds % (24 * 3600)) // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    
    if days > 0:
        return f"{days}d {hours:02d}h {minutes:02d}m"
    elif hours > 0:
        return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
    else:
        return f"{minutes:02d}m {seconds:02d}s"


def calculate_eta(current_step: int, max_steps: int, avg_step_time: float) -> str:
    """计算预计完成时间"""
    remaining_steps = max_steps - current_step
    if remaining_steps <= 0 or avg_step_time <= 0:
        return "完成"
    
    eta_seconds = remaining_steps * avg_step_time
    
    if eta_seconds < 60:
        return f"{int(eta_seconds)}秒"
    elif eta_seconds < 3600:
        return f"{int(eta_seconds // 60)}分钟"
    else:
        hours = int(eta_seconds // 3600)
        minutes = int((eta_seconds % 3600) // 60)
        return f"{hours}小时{minutes}分钟"