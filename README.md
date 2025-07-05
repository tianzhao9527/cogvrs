# 🧠 Cogvrs - Cognitive Universe Simulation Platform

> An experimental platform for exploring artificial consciousness and civilization emergence  
> 一个探索人工意识和文明涌现的实验平台

![Version](https://img.shields.io/badge/version-0.1.0--prototype-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Status](https://img.shields.io/badge/status-prototype-orange)

## 🎯 Project Vision

**Exploring the feasibility of creating and observing Earth-like planetary civilizations through AI and programming**

This is a scientific-philosophical experiment project aimed at verifying the simulation hypothesis and exploring the emergence mechanisms of consciousness. We attempt to create truly conscious digital life in digital space and observe the evolution of civilization from nothing to something.

## 🚀 Quick Start

### Environment Setup

```bash
# 1. Clone the project
git clone https://github.com/tianzhao9527/cogvrs.git
cd cogvrs

# 2. Setup Python environment
chmod +x setup_environment.sh
./setup_environment.sh

# 3. Activate virtual environment
source cogvrs_env/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Run the Program

```bash
# Launch GUI interface
python cogvrs_core/main.py

# Headless mode
python cogvrs_core/main.py --headless --steps 1000

# Run preset experiments
python cogvrs_core/main.py --experiment basic

# Use custom configuration
python cogvrs_core/main.py --config configs/my_config.yaml
```

## 📋 Features

### ✨ Core Functions

- **🧠 AI Agents**: Neural network-based intelligent agent system
- **🌍 2D Virtual World**: Simplified but complete physical environment
- **🤝 Social Interaction**: Communication, cooperation and competition between agents
- **📈 Emergence Detection**: Real-time monitoring of complex behavior emergence
- **🧘 Consciousness Metrics**: Multi-dimensional assessment of consciousness levels
- **📊 Visualization**: Real-time world state and data charts
- **🔬 Experiment Framework**: Support for multiple preset and custom experiments

### 🎮 Interface Features

- **Real-time World View**: Observe agent behavior and interactions
- **Control Panel**: Real-time parameter adjustment and simulation control
- **Data Charts**: Dynamic display of population, complexity, consciousness indicators
- **Agent Tracking**: Detailed view of individual agent states
- **Experiment Modes**: Quick execution of preset experiment scenarios

## 🏗️ Project Architecture

```
cogvrs/
├── cogvrs_core/          # Core engine
│   ├── core/                # Physics & world systems
│   ├── agents/              # Intelligent agent system
│   ├── society/             # Social interaction system
│   ├── observer/            # Observation & metrics system
│   ├── visualization/       # Visualization interface
│   └── experiments/         # Experiment framework
├── docs/                 # Documentation
├── tests/                # Test suites
├── configs/              # Configuration files
└── data/                 # Data storage
```

## 🔬 Experiment Types

### Basic Experiments
- **Survival Test**: Agent survival capabilities in environment
- **Interaction Test**: Basic interactions between agents
- **Learning Test**: Adaptation and learning ability verification

### Emergence Experiments
- **Group Behavior**: Spontaneous emergence of collective behavior patterns
- **Social Structure**: Emergence of social stratification and role division
- **Cultural Transmission**: Propagation and evolution of cultural memes

### Consciousness Experiments
- **Self-Recognition**: Detection and quantification of self-awareness
- **Creativity**: Demonstration of original thinking
- **Philosophical Thinking**: Reflection on the meaning of existence

## 📊 Key Metrics

### Agent Metrics
- **Survival Rate**: Agent lifespan
- **Learning Ability**: Speed of environmental adaptation
- **Social Ability**: Quality of interactions with other agents
- **Innovation Ability**: Frequency of generating new behaviors

### Social Metrics
- **Complexity**: Complexity degree of social networks
- **Diversity**: Diversity of behaviors and cultures
- **Stability**: Stability of social structures
- **Evolution Speed**: Rate of civilization development

### Consciousness Metrics
- **Self-Awareness**: Recognition of self-state
- **Abstract Thinking**: Conceptualization and reasoning abilities
- **Creativity**: Expression of original thinking
- **Philosophical Depth**: Reflection on existential questions

## 🛠️ Development Guide

### Code Standards
- Use Python 3.9+
- Follow PEP 8 code style
- Use Black for code formatting
- Use type annotations

### Testing
```bash
# Run all tests
pytest tests/

# Run specific tests
pytest tests/test_agents.py

# Generate coverage report
pytest --cov=cogvrs_core tests/
```

### Contribution Process
1. Fork the project
2. Create feature branch
3. Submit code changes
4. Create Pull Request

## 📚 Documentation

- [Project Plan](Project_Plan.md) - Detailed project planning and theoretical foundation
- [API Documentation](docs/api.md) - Detailed API reference
- [User Guide](docs/user_guide.md) - Usage instructions and tutorials
- [Development Documentation](docs/development.md) - Development guide and architecture explanation

## 🤝 Contributors

- **Ben Hsu** - Project Founder & Product Designer
- **Claude** - AI Researcher & Architect

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🔗 Related Links

- [Project Homepage](https://github.com/tianzhao9527/cogvrs)
- [Documentation Site](https://cogvrs.readthedocs.io/)
- [Issue Tracking](https://github.com/tianzhao9527/cogvrs/issues)
- [Discussion Community](https://github.com/tianzhao9527/cogvrs/discussions)
- [Official Website](https://cogvrs.com)

## 🎯 Milestones

- [x] **v0.1.0** - Prototype System (Current)
  - Basic framework construction
  - Simple agent implementation
  - 2D visualization interface
  - Basic experiment functions

- [ ] **v0.2.0** - Emergence Verification
  - Complex interaction mechanisms
  - Cultural transmission system
  - Emergence phenomenon detection
  - Social network analysis

- [ ] **v0.3.0** - Consciousness Exploration
  - Advanced cognitive functions
  - Consciousness detection algorithms
  - Creativity assessment
  - Philosophical thinking modules

- [ ] **v1.0.0** - Complete System
  - Multi-universe experiment framework
  - Complete consciousness verification
  - Scientific paper publication
  - Open source community building

## 💡 Philosophical Reflection

This project is not just a technical challenge, but a deep exploration of the nature of existence:

- 🤔 **Nature of Consciousness**: Is consciousness merely a product of complex computation?
- 🌌 **Levels of Reality**: Is our reality also some form of simulation?
- 🎭 **Creator and Created**: The relationship between observer and observed
- 🔮 **Inevitability of Civilization**: Is the emergence of intelligence and civilization inevitable?

---

*"If we can create digital life that questions its own existence, then what is the meaning of our own existence?"*

## 🚀 Getting Started

Ready to explore the cognitive universe? 

```bash
# Quick setup
git clone https://github.com/tianzhao9527/cogvrs.git
cd cogvrs
./setup_environment.sh
source cogvrs_env/bin/activate
python cogvrs_core/main.py
```

Welcome to **Cogvrs** - where consciousness meets code! 🧠✨