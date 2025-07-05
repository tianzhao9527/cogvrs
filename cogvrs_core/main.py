#!/usr/bin/env python3
"""
数字宇宙实验室 - 主程序入口
Digital Universe Laboratory - Main Entry Point

运行方式:
    python main.py                    # 启动GUI界面
    python main.py --headless         # 无界面模式
    python main.py --experiment basic # 运行预设实验
    python main.py --config custom.yaml # 使用自定义配置
"""

import argparse
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from configs.settings import load_config, DEFAULT_CONFIG
from core.physics_engine import PhysicsEngine
from core.world import World2D
from core.time_manager import TimeManager
from visualization.gui import DigitalUniverseGUI
from experiments.basic_test import BasicExperiment


def setup_logging(level="INFO"):
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/digital_universe.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="数字宇宙实验室 - 探索人工意识和文明涌现",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py                           # 启动GUI界面
  python main.py --headless --steps 1000   # 无界面运行1000步
  python main.py --experiment emergence    # 运行涌现实验
  python main.py --config experiments/custom.yaml  # 自定义配置
        """
    )
    
    parser.add_argument('--headless', action='store_true',
                       help='无界面模式运行')
    parser.add_argument('--config', type=str, default=None,
                       help='配置文件路径')
    parser.add_argument('--experiment', type=str, default=None,
                       choices=['basic', 'emergence', 'consciousness'],
                       help='运行预设实验')
    parser.add_argument('--steps', type=int, default=1000,
                       help='模拟步数 (默认: 1000)')
    parser.add_argument('--agents', type=int, default=50,
                       help='智能体数量 (默认: 50)')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别 (默认: INFO)')
    parser.add_argument('--save-data', action='store_true',
                       help='保存实验数据')
    parser.add_argument('--output-dir', type=str, default='data/output',
                       help='输出目录 (默认: data/output)')
    
    return parser.parse_args()


def run_headless_simulation(config, args):
    """无界面模式运行"""
    logger = logging.getLogger(__name__)
    logger.info(f"开始无界面模拟 - {args.steps}步, {args.agents}个智能体")
    
    # 创建核心组件
    physics = PhysicsEngine(config['physics'])
    world = World2D(config['world'])
    time_manager = TimeManager(config['time'])
    
    # 运行模拟
    for step in range(args.steps):
        if step % 100 == 0:
            logger.info(f"模拟进度: {step}/{args.steps}")
        
        # 执行一个时间步
        time_manager.step()
        world.update()
        physics.update()
    
    logger.info("模拟完成")


def run_gui_mode(config, args):
    """GUI模式运行"""
    logger = logging.getLogger(__name__)
    logger.info("启动图形界面模式")
    
    try:
        # 创建并启动GUI
        gui = DigitalUniverseGUI(config)
        gui.run()
    except Exception as e:
        logger.error(f"GUI启动失败: {e}")
        sys.exit(1)


def run_experiment(config, experiment_type, args):
    """运行预设实验"""
    logger = logging.getLogger(__name__)
    logger.info(f"运行预设实验: {experiment_type}")
    
    if experiment_type == 'basic':
        experiment = BasicExperiment(config)
        results = experiment.run(steps=args.steps)
        logger.info(f"实验完成，结果: {results}")
    else:
        logger.warning(f"未实现的实验类型: {experiment_type}")


def main():
    """主函数"""
    args = parse_arguments()
    
    # 设置日志
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # 加载配置
    try:
        if args.config:
            config = load_config(args.config)
        else:
            config = DEFAULT_CONFIG.copy()
            
        # 应用命令行参数覆盖
        if args.agents:
            config['world']['max_agents'] = args.agents
            
    except Exception as e:
        logger.error(f"配置加载失败: {e}")
        sys.exit(1)
    
    logger.info("🚀 数字宇宙实验室启动")
    logger.info(f"配置: {config.get('name', 'default')}")
    logger.info(f"版本: {config.get('version', '0.1.0')}")
    
    try:
        # 根据运行模式执行
        if args.experiment:
            run_experiment(config, args.experiment, args)
        elif args.headless:
            run_headless_simulation(config, args)
        else:
            run_gui_mode(config, args)
            
    except KeyboardInterrupt:
        logger.info("用户中断，程序退出")
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        sys.exit(1)
    
    logger.info("🎯 数字宇宙实验室关闭")


if __name__ == "__main__":
    main()