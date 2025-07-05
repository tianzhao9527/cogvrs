"""
数字宇宙实验室 - 配置管理
Configuration Management for Digital Universe Laboratory
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Union

# 默认配置
DEFAULT_CONFIG = {
    # 项目信息
    "name": "Digital Universe Laboratory - Prototype",
    "version": "0.1.0",
    "description": "探索人工意识和文明涌现的实验平台",
    
    # 世界配置
    "world": {
        "size": (100, 100),           # 世界尺寸 (宽, 高)
        "max_agents": 50,             # 最大智能体数量
        "initial_agents": 20,         # 初始智能体数量
        "resource_density": 0.1,      # 资源密度
        "interaction_radius": 5,      # 交互半径
        "boundary_type": "toroidal",  # 边界类型: toroidal, reflective, absorbing
    },
    
    # 物理引擎配置
    "physics": {
        "gravity": 0.0,               # 重力
        "friction": 0.1,              # 摩擦力
        "energy_conservation": True,   # 能量守恒
        "entropy_increase": True,      # 熵增
        "max_speed": 2.0,             # 最大速度
        "collision_detection": True,   # 碰撞检测
    },
    
    # 时间管理配置
    "time": {
        "dt": 0.1,                    # 时间步长
        "max_steps": 10000,           # 最大步数
        "real_time": False,           # 实时模式
        "target_fps": 60,             # 目标帧率
    },
    
    # 智能体配置
    "agents": {
        "neural_network": {
            "input_size": 20,         # 输入层大小
            "hidden_sizes": [32, 16], # 隐藏层大小
            "output_size": 8,         # 输出层大小
            "activation": "tanh",     # 激活函数
            "learning_rate": 0.01,    # 学习率
        },
        "memory": {
            "capacity": 100,          # 记忆容量
            "decay_rate": 0.99,       # 记忆衰减率
            "consolidation": True,    # 记忆巩固
        },
        "behavior": {
            "mutation_rate": 0.1,     # 变异率
            "reproduction_threshold": 80, # 繁殖阈值
            "energy_decay": 0.02,     # 能量衰减
            "social_tendency": 0.5,   # 社交倾向
        },
    },
    
    # 社会系统配置
    "society": {
        "communication": {
            "enabled": True,          # 启用交流
            "range": 10,              # 交流范围
            "bandwidth": 8,           # 信息带宽
            "noise_level": 0.05,      # 噪声水平
        },
        "culture": {
            "enabled": True,          # 启用文化
            "mutation_rate": 0.01,    # 文化变异率
            "transmission_rate": 0.8, # 文化传播率
            "innovation_rate": 0.05,  # 创新率
        },
        "emergence": {
            "detection_threshold": 0.7, # 涌现检测阈值
            "pattern_window": 100,    # 模式检测窗口
            "novelty_threshold": 0.5, # 新颖性阈值
        },
    },
    
    # 观察系统配置
    "observer": {
        "consciousness_metrics": {
            "self_awareness": True,   # 自我意识检测
            "creativity": True,       # 创造性检测
            "abstraction": True,      # 抽象思维检测
            "theory_of_mind": True,   # 心理理论检测
        },
        "data_collection": {
            "enabled": True,          # 启用数据收集
            "interval": 10,           # 收集间隔
            "metrics": ["population", "complexity", "consciousness", "emergence"],
            "save_to_file": True,     # 保存到文件
        },
        "visualization": {
            "real_time_update": True, # 实时更新
            "update_interval": 100,   # 更新间隔(ms)
            "max_history": 1000,      # 最大历史记录
        },
    },
    
    # 可视化配置
    "visualization": {
        "window": {
            "width": 1200,            # 窗口宽度
            "height": 800,            # 窗口高度
            "title": "数字宇宙实验室",
            "resizable": True,        # 可调整大小
        },
        "colors": {
            "background": (20, 20, 30),     # 背景色
            "agent": (100, 150, 255),       # 智能体颜色
            "resource": (50, 255, 50),      # 资源颜色
            "connection": (255, 255, 100),  # 连接线颜色
            "emergence": (255, 100, 100),   # 涌现现象颜色
        },
        "gui": {
            "show_fps": True,         # 显示FPS
            "show_metrics": True,     # 显示指标
            "control_panel": True,    # 显示控制面板
            "charts": True,           # 显示图表
        },
    },
    
    # 实验配置
    "experiments": {
        "save_results": True,         # 保存实验结果
        "output_directory": "data/experiments",
        "checkpoint_interval": 1000,  # 检查点间隔
        "parallel_runs": 1,           # 并行运行数量
    },
    
    # 日志配置
    "logging": {
        "level": "INFO",              # 日志级别
        "file": "logs/digital_universe.log",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "rotation": "1GB",            # 日志轮转大小
    },
}


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    从文件加载配置
    
    Args:
        config_path: 配置文件路径，支持 .yaml, .yml, .json 格式
        
    Returns:
        配置字典
        
    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 配置文件格式错误
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                config = yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                config = json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")
                
        # 合并默认配置
        merged_config = merge_configs(DEFAULT_CONFIG, config)
        return merged_config
        
    except Exception as e:
        raise ValueError(f"配置文件解析错误: {e}")


def save_config(config: Dict[str, Any], config_path: Union[str, Path]):
    """
    保存配置到文件
    
    Args:
        config: 配置字典
        config_path: 配置文件路径
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        elif config_path.suffix.lower() == '.json':
            json.dump(config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")


def merge_configs(base_config: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并配置字典，用户配置会覆盖基础配置
    
    Args:
        base_config: 基础配置
        user_config: 用户配置
        
    Returns:
        合并后的配置
    """
    merged = base_config.copy()
    
    for key, value in user_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
            
    return merged


def validate_config(config: Dict[str, Any]) -> bool:
    """
    验证配置的有效性
    
    Args:
        config: 配置字典
        
    Returns:
        配置是否有效
    """
    required_keys = [
        'world', 'physics', 'time', 'agents', 
        'society', 'observer', 'visualization'
    ]
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"缺少必需的配置项: {key}")
    
    # 验证数值范围
    world_config = config['world']
    if world_config['max_agents'] <= 0:
        raise ValueError("max_agents必须大于0")
    
    if world_config['size'][0] <= 0 or world_config['size'][1] <= 0:
        raise ValueError("世界尺寸必须大于0")
    
    return True


# 预设配置
PRESET_CONFIGS = {
    "minimal": {
        "world": {"max_agents": 10, "size": (50, 50)},
        "time": {"max_steps": 500},
        "agents": {"neural_network": {"hidden_sizes": [16]}},
    },
    
    "standard": DEFAULT_CONFIG,
    
    "large_scale": {
        "world": {"max_agents": 200, "size": (200, 200)},
        "time": {"max_steps": 50000},
        "agents": {"neural_network": {"hidden_sizes": [64, 32, 16]}},
    },
    
    "consciousness_focus": {
        "observer": {
            "consciousness_metrics": {
                "self_awareness": True,
                "creativity": True,
                "abstraction": True,
                "theory_of_mind": True,
            }
        },
        "agents": {
            "neural_network": {"hidden_sizes": [64, 32]},
            "memory": {"capacity": 200},
        },
    },
}


def get_preset_config(preset_name: str) -> Dict[str, Any]:
    """
    获取预设配置
    
    Args:
        preset_name: 预设名称
        
    Returns:
        预设配置
    """
    if preset_name not in PRESET_CONFIGS:
        raise ValueError(f"未知的预设配置: {preset_name}")
    
    base = DEFAULT_CONFIG.copy()
    preset = PRESET_CONFIGS[preset_name]
    
    return merge_configs(base, preset)