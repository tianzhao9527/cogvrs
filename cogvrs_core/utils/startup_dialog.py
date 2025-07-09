#!/usr/bin/env python3
"""
Cogvrs启动配置对话框
让用户在启动前选择初始智能体数量和性能设置

Author: Ben Hsu & Claude
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional

class StartupDialog:
    """启动配置对话框"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.result = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        self.root.title("Cogvrs - Startup Configuration")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 使窗口居中
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="🧠 Cogvrs Configuration", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 智能体数量选择
        agents_frame = ttk.LabelFrame(main_frame, text="Initial Agent Count", padding="10")
        agents_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 预设选项
        self.agent_preset = tk.StringVar(value="normal")
        
        presets = [
            ("快速测试 (10 agents)", "fast", 10),
            ("正常运行 (50 agents)", "normal", 50),
            ("中等规模 (100 agents)", "medium", 100),
            ("大规模 (200 agents)", "large", 200),
            ("自定义数量", "custom", 50)
        ]
        
        for i, (text, value, count) in enumerate(presets):
            rb = ttk.Radiobutton(agents_frame, text=text, variable=self.agent_preset, 
                               value=value, command=self.on_preset_change)
            rb.grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # 自定义数量输入
        custom_frame = ttk.Frame(agents_frame)
        custom_frame.grid(row=len(presets), column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(custom_frame, text="Custom count:").grid(row=0, column=0)
        self.custom_count = tk.IntVar(value=50)
        custom_spinbox = ttk.Spinbox(custom_frame, from_=1, to=500, width=10,
                                   textvariable=self.custom_count)
        custom_spinbox.grid(row=0, column=1, padx=(10, 0))
        self.custom_spinbox = custom_spinbox
        
        # 性能设置
        perf_frame = ttk.LabelFrame(main_frame, text="Performance Settings", padding="10")
        perf_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 目标FPS
        ttk.Label(perf_frame, text="Target FPS:").grid(row=0, column=0, sticky=tk.W)
        self.target_fps = tk.IntVar(value=30)
        fps_spinbox = ttk.Spinbox(perf_frame, from_=10, to=60, width=10,
                                textvariable=self.target_fps)
        fps_spinbox.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        # 渲染质量
        ttk.Label(perf_frame, text="Rendering:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.rendering_quality = tk.StringVar(value="normal")
        quality_combo = ttk.Combobox(perf_frame, textvariable=self.rendering_quality,
                                   values=["low", "normal", "high"], state="readonly", width=15)
        quality_combo.grid(row=1, column=1, padx=(10, 0), sticky=tk.W, pady=(5, 0))
        
        # 多尺度渲染
        self.multi_scale = tk.BooleanVar(value=True)
        multi_scale_cb = ttk.Checkbutton(perf_frame, text="Enable Multi-Scale Rendering",
                                       variable=self.multi_scale)
        multi_scale_cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # 高级设置
        advanced_frame = ttk.LabelFrame(main_frame, text="Advanced Settings", padding="10")
        advanced_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 世界大小
        ttk.Label(advanced_frame, text="World Size:").grid(row=0, column=0, sticky=tk.W)
        self.world_size = tk.StringVar(value="100x100")
        size_combo = ttk.Combobox(advanced_frame, textvariable=self.world_size,
                                values=["50x50", "100x100", "150x150", "200x200"], 
                                state="readonly", width=15)
        size_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        
        # 资源密度
        ttk.Label(advanced_frame, text="Resource Density:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.resource_density = tk.DoubleVar(value=0.2)
        density_scale = ttk.Scale(advanced_frame, from_=0.1, to=0.5, orient=tk.HORIZONTAL,
                                variable=self.resource_density, length=150)
        density_scale.grid(row=1, column=1, padx=(10, 0), sticky=tk.W, pady=(5, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # 按钮
        ttk.Button(button_frame, text="Start Simulation", 
                  command=self.start_simulation).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel).grid(row=0, column=1)
        
        # 信息标签
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        info_text = ("💡 Tip: Start with 'Fast Test' for quick testing,\n"
                    "or 'Normal' for balanced performance and features.")
        info_label = ttk.Label(info_frame, text=info_text, font=("Arial", 9),
                             foreground="gray", justify=tk.CENTER)
        info_label.grid(row=0, column=0)
        
        # 初始化状态
        self.on_preset_change()
        
    def on_preset_change(self):
        """预设选项改变时的处理"""
        preset = self.agent_preset.get()
        if preset == "custom":
            self.custom_spinbox.config(state="normal")
        else:
            self.custom_spinbox.config(state="disabled")
            # 更新自定义数量以匹配预设
            preset_counts = {
                "fast": 10,
                "normal": 50, 
                "medium": 100,
                "large": 200
            }
            if preset in preset_counts:
                self.custom_count.set(preset_counts[preset])
    
    def get_agent_count(self) -> int:
        """获取智能体数量"""
        preset = self.agent_preset.get()
        if preset == "custom":
            return self.custom_count.get()
        else:
            preset_counts = {
                "fast": 10,
                "normal": 50,
                "medium": 100, 
                "large": 200
            }
            return preset_counts.get(preset, 50)
    
    def get_world_size(self) -> tuple:
        """获取世界大小"""
        size_str = self.world_size.get()
        w, h = map(int, size_str.split('x'))
        return (w, h)
    
    def start_simulation(self):
        """开始模拟"""
        agent_count = self.get_agent_count()
        
        # 验证输入
        if agent_count < 1 or agent_count > 500:
            messagebox.showerror("Error", "Agent count must be between 1 and 500")
            return
            
        world_size = self.get_world_size()
        
        # 创建配置
        self.result = {
            'initial_agents': agent_count,
            'target_fps': self.target_fps.get(),
            'rendering_quality': self.rendering_quality.get(),
            'enable_multi_scale': self.multi_scale.get(),
            'world_size': world_size,
            'resource_density': self.resource_density.get()
        }
        
        self.root.destroy()
    
    def cancel(self):
        """取消"""
        self.result = None
        self.root.destroy()
    
    def show(self) -> Optional[Dict]:
        """显示对话框并返回结果"""
        self.root.mainloop()
        return self.result


def show_startup_dialog() -> Optional[Dict]:
    """显示启动配置对话框"""
    try:
        dialog = StartupDialog()
        return dialog.show()
    except ImportError as e:
        if '_tkinter' in str(e):
            print("ℹ️  GUI dialog not available (tkinter missing), using command line interface...")
            from .cli_config import show_cli_config
            return show_cli_config()
        else:
            raise e
    except Exception as e:
        print(f"❌ 启动对话框错误: {e}")
        print("🔄 Falling back to command line interface...")
        try:
            from .cli_config import show_cli_config
            return show_cli_config()
        except Exception as cli_error:
            print(f"❌ CLI配置也失败: {cli_error}")
            # 返回默认配置
            return {
                'initial_agents': 50,
                'target_fps': 30,
                'rendering_quality': 'normal',
                'enable_multi_scale': True,
                'world_size': (100, 100),
                'resource_density': 0.2
            }


if __name__ == "__main__":
    # 测试对话框
    result = show_startup_dialog()
    if result:
        print("用户配置:", result)
    else:
        print("用户取消了配置")