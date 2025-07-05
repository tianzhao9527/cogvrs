"""
Cogvrs - Cognitive Universe Simulation Platform
认知宇宙模拟平台

An experimental platform for exploring artificial consciousness and civilization emergence
一个探索人工意识和文明涌现的实验平台

Author: Ben Hsu & Claude
Version: 0.1.0 (Prototype)
Date: 2024-07-05
"""

__version__ = "0.1.0"
__author__ = "Ben Hsu & Claude"
__description__ = "Cogvrs - Cognitive Universe Simulation Platform"

# 项目信息
PROJECT_INFO = {
    "name": "Cogvrs",
    "full_name": "Cognitive Universe Simulation Platform",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "license": "MIT",
    "python_requires": ">=3.9",
    "homepage": "https://github.com/benhsu/cogvrs",
    "repository": "https://github.com/benhsu/cogvrs.git",
    "documentation": "https://cogvrs.readthedocs.io/",
    "domain": "cogvrs.com",
}

# 导入核心模块
from .core import *
from .agents import *
from .society import *
from .observer import *
from .visualization import *