"""
Cogvrs - Neural Network Brain
神经网络大脑：智能体的决策和学习系统

Author: Ben Hsu & Claude
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


def sigmoid(x: np.ndarray) -> np.ndarray:
    """Sigmoid激活函数"""
    return 1 / (1 + np.exp(-np.clip(x, -250, 250)))


def tanh(x: np.ndarray) -> np.ndarray:
    """Tanh激活函数"""
    return np.tanh(x)


def relu(x: np.ndarray) -> np.ndarray:
    """ReLU激活函数"""
    return np.maximum(0, x)


def softmax(x: np.ndarray) -> np.ndarray:
    """Softmax激活函数"""
    exp_x = np.exp(x - np.max(x))
    return exp_x / np.sum(exp_x)


@dataclass
class NeuralLayer:
    """神经网络层"""
    weights: np.ndarray
    biases: np.ndarray
    activation: str = 'tanh'
    
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """前向传播"""
        z = np.dot(inputs, self.weights) + self.biases
        
        if self.activation == 'sigmoid':
            return sigmoid(z)
        elif self.activation == 'tanh':
            return tanh(z)
        elif self.activation == 'relu':
            return relu(z)
        elif self.activation == 'softmax':
            return softmax(z)
        else:
            return z  # linear


class NeuralBrain:
    """
    神经网络大脑
    
    Features:
    - 多层感知机架构
    - 可配置的网络结构
    - 学习和适应能力
    - 记忆整合
    - 创造性决策
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.input_size = config.get('input_size', 20)
        self.hidden_sizes = config.get('hidden_sizes', [32, 16])
        self.output_size = config.get('output_size', 8)
        self.activation = config.get('activation', 'tanh')
        self.learning_rate = config.get('learning_rate', 0.01)
        
        # 构建网络层
        self.layers: List[NeuralLayer] = []
        self._build_network()
        
        # 学习相关
        self.last_inputs: Optional[np.ndarray] = None
        self.last_outputs: Optional[np.ndarray] = None
        self.learning_history: List[Dict] = []
        
        # 性能统计
        self.total_predictions = 0
        self.successful_actions = 0
        
        logger.debug(f"NeuralBrain initialized: {self.input_size}→{self.hidden_sizes}→{self.output_size}")
    
    def _build_network(self):
        """构建神经网络"""
        layer_sizes = [self.input_size] + self.hidden_sizes + [self.output_size]
        
        for i in range(len(layer_sizes) - 1):
            input_size = layer_sizes[i]
            output_size = layer_sizes[i + 1]
            
            # Xavier初始化
            weight_range = np.sqrt(6.0 / (input_size + output_size))
            weights = np.random.uniform(-weight_range, weight_range, (input_size, output_size))
            biases = np.zeros(output_size)
            
            # 最后一层使用sigmoid，其他层使用配置的激活函数
            activation = 'sigmoid' if i == len(layer_sizes) - 2 else self.activation
            
            layer = NeuralLayer(weights, biases, activation)
            self.layers.append(layer)
    
    def predict(self, inputs: np.ndarray) -> np.ndarray:
        """前向传播预测"""
        current_input = inputs.copy()
        
        # 通过所有层
        for layer in self.layers:
            current_input = layer.forward(current_input)
        
        # 记录输入输出用于学习
        self.last_inputs = inputs.copy()
        self.last_outputs = current_input.copy()
        self.total_predictions += 1
        
        return current_input
    
    def learn_from_feedback(self, reward: float, target_action: Optional[np.ndarray] = None):
        """从反馈中学习"""
        if self.last_inputs is None or self.last_outputs is None:
            return
        
        # 简化的强化学习：调整权重基于奖励
        error_signal = reward - 0.5  # 期望奖励为0.5
        
        if target_action is not None:
            # 监督学习：有目标动作
            error = target_action - self.last_outputs
            self._backpropagate(error)
        else:
            # 强化学习：基于奖励调整
            self._reinforce(error_signal)
        
        # 记录学习历史
        self.learning_history.append({
            'reward': reward,
            'error_signal': error_signal,
            'prediction': self.last_outputs.copy(),
            'input': self.last_inputs.copy()
        })
        
        # 保持历史记录大小
        if len(self.learning_history) > 1000:
            self.learning_history.pop(0)
        
        if reward > 0.7:  # 定义成功阈值
            self.successful_actions += 1
    
    def _backpropagate(self, output_error: np.ndarray):
        """反向传播（简化版本）"""
        # 简化的反向传播：只调整最后一层
        if len(self.layers) > 0 and self.last_inputs is not None:
            last_layer = self.layers[-1]
            
            # 计算梯度
            if len(self.layers) > 1:
                # 获取倒数第二层的输出
                hidden_output = self.last_inputs
                for layer in self.layers[:-1]:
                    hidden_output = layer.forward(hidden_output)
                input_to_last = hidden_output
            else:
                input_to_last = self.last_inputs
            
            # 更新权重和偏置
            weight_gradient = np.outer(input_to_last, output_error)
            last_layer.weights += self.learning_rate * weight_gradient
            last_layer.biases += self.learning_rate * output_error
            
            # 添加权重衰减
            last_layer.weights *= 0.9999
    
    def _reinforce(self, reward_signal: float):
        """基于奖励的强化学习"""
        if self.last_inputs is None or self.last_outputs is None:
            return
        
        # 简单的策略梯度：增强好的动作，减弱坏的动作
        for layer in self.layers:
            # 对权重添加小的随机扰动，方向由奖励决定
            weight_noise = np.random.normal(0, 0.01, layer.weights.shape)
            bias_noise = np.random.normal(0, 0.01, layer.biases.shape)
            
            layer.weights += reward_signal * self.learning_rate * weight_noise
            layer.biases += reward_signal * self.learning_rate * bias_noise
    
    def mutate(self, mutation_rate: float = 0.1, mutation_strength: float = 0.05):
        """基因变异（用于进化算法）"""
        for layer in self.layers:
            # 权重变异
            weight_mask = np.random.random(layer.weights.shape) < mutation_rate
            layer.weights += weight_mask * np.random.normal(0, mutation_strength, layer.weights.shape)
            
            # 偏置变异
            bias_mask = np.random.random(layer.biases.shape) < mutation_rate
            layer.biases += bias_mask * np.random.normal(0, mutation_strength, layer.biases.shape)
    
    def crossover(self, other_brain: 'NeuralBrain') -> 'NeuralBrain':
        """与另一个大脑杂交"""
        child_config = self.config.copy()
        child_brain = NeuralBrain(child_config)
        
        # 随机选择每层的权重来源
        for i, (self_layer, other_layer, child_layer) in enumerate(
            zip(self.layers, other_brain.layers, child_brain.layers)
        ):
            # 权重杂交
            crossover_mask = np.random.random(self_layer.weights.shape) < 0.5
            child_layer.weights = np.where(crossover_mask, self_layer.weights, other_layer.weights)
            
            # 偏置杂交
            bias_mask = np.random.random(self_layer.biases.shape) < 0.5
            child_layer.biases = np.where(bias_mask, self_layer.biases, other_layer.biases)
        
        return child_brain
    
    def add_noise(self, noise_strength: float = 0.01):
        """添加神经噪声（模拟创造性）"""
        for layer in self.layers:
            layer.weights += np.random.normal(0, noise_strength, layer.weights.shape)
            layer.biases += np.random.normal(0, noise_strength, layer.biases.shape)
    
    def get_activation_pattern(self, inputs: np.ndarray) -> List[np.ndarray]:
        """获取所有层的激活模式"""
        activations = []
        current_input = inputs.copy()
        
        for layer in self.layers:
            current_input = layer.forward(current_input)
            activations.append(current_input.copy())
        
        return activations
    
    def calculate_complexity(self) -> float:
        """计算网络复杂度"""
        total_connections = sum(layer.weights.size for layer in self.layers)
        total_weights = sum(np.sum(np.abs(layer.weights)) for layer in self.layers)
        
        # 复杂度 = 连接数 × 平均权重强度
        if total_connections > 0:
            avg_weight = total_weights / total_connections
            return total_connections * avg_weight
        return 0.0
    
    def get_performance_metrics(self) -> Dict:
        """获取性能指标"""
        success_rate = self.successful_actions / max(1, self.total_predictions)
        
        # 学习效果：最近的奖励趋势
        recent_rewards = [h['reward'] for h in self.learning_history[-100:]]
        avg_recent_reward = np.mean(recent_rewards) if recent_rewards else 0.0
        
        return {
            'total_predictions': self.total_predictions,
            'success_rate': success_rate,
            'avg_recent_reward': avg_recent_reward,
            'network_complexity': self.calculate_complexity(),
            'learning_history_size': len(self.learning_history)
        }
    
    def save_state(self) -> Dict:
        """保存大脑状态"""
        return {
            'config': self.config,
            'layers': [
                {
                    'weights': layer.weights.tolist(),
                    'biases': layer.biases.tolist(),
                    'activation': layer.activation
                }
                for layer in self.layers
            ],
            'performance_metrics': self.get_performance_metrics(),
            'learning_history': self.learning_history[-100:]  # 只保存最近100条
        }
    
    def load_state(self, state: Dict):
        """加载大脑状态"""
        self.config = state['config']
        
        # 重建网络层
        self.layers = []
        for layer_data in state['layers']:
            layer = NeuralLayer(
                weights=np.array(layer_data['weights']),
                biases=np.array(layer_data['biases']),
                activation=layer_data['activation']
            )
            self.layers.append(layer)
        
        # 恢复学习历史
        self.learning_history = state.get('learning_history', [])
        
        # 恢复性能统计
        metrics = state.get('performance_metrics', {})
        self.total_predictions = metrics.get('total_predictions', 0)
        self.successful_actions = int(metrics.get('success_rate', 0) * self.total_predictions)
    
    def clone(self) -> 'NeuralBrain':
        """克隆大脑"""
        clone = NeuralBrain(self.config.copy())
        
        # 复制权重
        for original_layer, clone_layer in zip(self.layers, clone.layers):
            clone_layer.weights = original_layer.weights.copy()
            clone_layer.biases = original_layer.biases.copy()
        
        return clone