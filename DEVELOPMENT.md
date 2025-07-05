# 🛠️ 开发指南

## 项目管理方式

### 🎯 推荐的项目管理策略

#### 1. **GitHub 作为主要管理平台** ⭐ 推荐
**优势**：
- 完整的版本控制和协作功能
- Issues 和 Projects 进行任务管理
- Actions 实现 CI/CD 自动化
- 文档和 Wiki 功能完善
- 社区支持和开源生态

**设置步骤**：
```bash
# 1. 在GitHub创建新仓库
# 2. 关联本地仓库
git remote add origin https://github.com/username/digital-universe-lab.git
git branch -M main
git push -u origin main

# 3. 设置分支保护规则
# 4. 配置 GitHub Actions
# 5. 启用 Issues 和 Projects
```

#### 2. **替代方案**

**GitLab**：
- 更强的CI/CD功能
- 内置项目管理工具
- 私有仓库支持更好

**自建Git + 项目管理工具**：
- Git + Jira/Trello
- Git + Notion
- Git + Linear

### 📋 项目管理最佳实践

#### 分支管理策略
```
main (主分支)
├── develop (开发分支)
├── feature/智能体系统 (功能分支)
├── feature/可视化界面 (功能分支)
├── hotfix/紧急修复 (热修复分支)
└── release/v0.1.0 (发布分支)
```

#### 提交规范
```
类型(范围): 简短描述

详细描述 (可选)

相关Issue: #123
```

**提交类型**：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具更新

#### 任务管理
**使用 GitHub Issues + Projects**：
```
📋 Product Backlog
├── 🚀 Sprint 1: 基础框架 (2周)
│   ├── #001 物理引擎实现
│   ├── #002 智能体系统
│   └── #003 基础可视化
├── 🔬 Sprint 2: 社会交互 (2周)
│   ├── #004 交互机制
│   ├── #005 文化传播
│   └── #006 涌现检测
└── 🧠 Sprint 3: 意识探索 (2周)
    ├── #007 意识度量
    ├── #008 创造性检测
    └── #009 哲学思考模块
```

## 开发工作流

### 🔄 日常开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/新功能名称

# 2. 开发和测试
# ... 编写代码 ...
python -m pytest tests/

# 3. 代码质量检查
black digital_universe_prototype/
flake8 digital_universe_prototype/
mypy digital_universe_prototype/

# 4. 提交更改
git add .
git commit -m "feat(agents): 实现基础智能体神经网络

- 添加多层感知机实现
- 实现前向传播和反向传播
- 添加基础的学习算法

Closes #002"

# 5. 推送和创建PR
git push origin feature/新功能名称
# 在GitHub创建Pull Request

# 6. 代码审查和合并
# 通过GitHub进行代码审查
# 合并到develop分支
```

### 🧪 测试策略

**测试金字塔**：
```
    /\     E2E测试 (少量)
   /  \    集成测试 (适量)  
  /____\   单元测试 (大量)
```

**测试命令**：
```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_agents.py

# 生成覆盖率报告
pytest --cov=digital_universe_prototype --cov-report=html

# 性能测试
pytest tests/performance/ --benchmark-only
```

### 📊 持续集成/持续部署

**GitHub Actions 配置** (`.github/workflows/ci.yml`):
```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: pytest --cov=digital_universe_prototype
    
    - name: Code quality checks
      run: |
        black --check digital_universe_prototype/
        flake8 digital_universe_prototype/
        mypy digital_universe_prototype/
```

## 协作规范

### 👥 团队协作

**角色分工**：
- **架构师** (Claude): 系统设计、核心算法
- **产品经理** (徐斌): 需求分析、用户体验
- **开发者**: 功能实现、测试
- **研究员**: 理论验证、实验设计

**协作工具**：
- **代码**: GitHub
- **文档**: GitHub Wiki / Notion
- **沟通**: GitHub Discussions / Slack
- **项目管理**: GitHub Projects
- **设计**: Figma (如需要)

### 📝 文档规范

**代码文档**：
```python
def consciousness_detector(agent: Agent) -> float:
    """
    检测智能体的意识水平
    
    Args:
        agent: 要检测的智能体实例
        
    Returns:
        意识水平评分 (0.0-1.0)
        
    Raises:
        ValueError: 当智能体状态无效时
        
    Examples:
        >>> agent = SimpleAgent()
        >>> score = consciousness_detector(agent)
        >>> assert 0.0 <= score <= 1.0
    """
```

**提交消息**：
```
feat(consciousness): 实现基础意识检测算法

- 添加自我意识评估指标
- 实现创造性思维检测
- 集成抽象思维能力测试

这为后续的哲学思考模块奠定了基础。

Closes #007
See also #008, #009
```

## 质量保证

### 🔍 代码审查清单

**功能性**：
- [ ] 功能是否按预期工作
- [ ] 边界条件是否处理正确
- [ ] 错误处理是否完善

**代码质量**：
- [ ] 代码风格是否一致
- [ ] 命名是否清晰
- [ ] 注释和文档是否充分

**性能**：
- [ ] 算法复杂度是否合理
- [ ] 内存使用是否优化
- [ ] 是否存在性能瓶颈

**测试**：
- [ ] 测试覆盖率是否足够
- [ ] 测试用例是否有意义
- [ ] 集成测试是否通过

### 📈 质量指标

**目标指标**：
- 代码覆盖率: > 80%
- 代码质量评分: > 8/10
- 构建成功率: > 95%
- 平均修复时间: < 2天

## 发布管理

### 🚀 版本发布流程

**语义化版本控制** (SemVer):
- `v0.1.0`: 原型版本
- `v0.2.0`: 涌现验证版本
- `v0.3.0`: 意识探索版本
- `v1.0.0`: 正式版本

**发布步骤**：
```bash
# 1. 创建发布分支
git checkout -b release/v0.1.0

# 2. 更新版本号和变更日志
# 编辑 __init__.py 和 CHANGELOG.md

# 3. 最终测试
pytest
python main.py --experiment basic

# 4. 合并到main并打标签
git checkout main
git merge release/v0.1.0
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin main --tags

# 5. 发布到PyPI (如需要)
python -m build
python -m twine upload dist/*
```

## 风险管理

### ⚠️ 常见风险和应对

**技术风险**：
- 依赖库兼容性 → 固定版本 + 定期更新
- 性能瓶颈 → 持续性能监控
- 数据丢失 → 自动备份机制

**项目风险**：
- 进度延误 → 敏捷开发 + 里程碑检查
- 需求变更 → 灵活的架构设计
- 团队沟通 → 定期同步会议

**质量风险**：
- Bug增多 → 持续集成 + 自动化测试
- 代码腐化 → 代码审查 + 重构
- 文档过时 → 文档自动化生成

---

**下一步建议**：
1. 在GitHub创建仓库并推送代码
2. 设置GitHub Projects进行任务管理
3. 配置GitHub Actions自动化流程
4. 开始第一个Sprint的开发工作