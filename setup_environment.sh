#!/bin/bash
# 数字宇宙实验室 - 环境配置脚本

echo "🚀 设置数字宇宙实验室开发环境..."

# 检查Python版本
python3 --version

# 创建虚拟环境
echo "📦 创建虚拟环境..."
python3 -m venv digital_universe_env

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source digital_universe_env/bin/activate

# 升级pip
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装核心依赖
echo "📚 安装核心依赖包..."
pip install numpy>=1.21.0
pip install matplotlib>=3.5.0
pip install pygame>=2.1.0
pip install scikit-learn>=1.0.0
pip install networkx>=2.6.0
pip install pandas>=1.3.0
pip install seaborn>=0.11.0
pip install tqdm>=4.62.0
pip install joblib>=1.1.0

# 开发工具
echo "🔨 安装开发工具..."
pip install pytest>=7.0.0
pip install black>=22.0.0
pip install flake8>=4.0.0
pip install mypy>=0.950
pip install jupyter>=1.0.0
pip install ipython>=8.0.0

# 导出依赖列表
echo "📝 导出依赖列表..."
pip freeze > requirements.txt

echo "✅ 环境配置完成！"
echo "💡 使用 'source digital_universe_env/bin/activate' 激活环境"
echo "💡 使用 'deactivate' 退出环境"