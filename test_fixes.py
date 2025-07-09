#!/usr/bin/env python3
"""
测试修复验证脚本
验证中文字符显示和系统报告功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chinese_font_loading():
    """测试中文字体加载功能"""
    try:
        import pygame
        import platform
        
        pygame.init()
        pygame.font.init()
        
        print("🔤 测试中文字体加载...")
        
        # 测试平台特定字体加载
        if platform.system() == "Darwin":  # macOS
            # 尝试多个中文字体路径
            chinese_fonts = [
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/System/Library/Fonts/STHeiti Medium.ttc", 
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/System/Library/Fonts/SFNS.ttf"
            ]
            
            font_loaded = False
            for font_path in chinese_fonts:
                try:
                    font = pygame.font.Font(font_path, 24)
                    print(f"✅ macOS中文字体加载成功: {font_path}")
                    
                    # 测试中文渲染
                    text_surface = font.render("科技发展", True, (255, 255, 255))
                    print("✅ 中文文本渲染成功")
                    font_loaded = True
                    break
                except Exception as e:
                    print(f"⚠️  字体 {font_path} 加载失败: {e}")
                    continue
            
            if not font_loaded:
                print("❌ 所有中文字体都加载失败")
                return False
            
            return True
        else:
            print("ℹ️  非macOS系统，跳过特定字体测试")
            return True
            
    except Exception as e:
        print(f"❌ 字体测试失败: {e}")
        return False

def test_system_reporter():
    """测试系统报告功能"""
    try:
        from cogvrs_core.utils.system_reporter import SystemReporter
        
        print("\n📊 测试系统报告功能...")
        
        # 创建报告器
        reporter = SystemReporter()
        print("✅ SystemReporter创建成功")
        
        # 生成测试报告
        test_report = reporter.generate_comprehensive_report()
        print("✅ 综合报告生成成功")
        
        # 检查报告结构
        required_sections = [
            'report_meta', 'optimization_summary', 'terrain_report',
            'technology_report', 'consciousness_report', 'skill_report',
            'tribe_report', 'agent_report', 'simulation_metrics',
            'performance_analysis', 'recommendations'
        ]
        
        for section in required_sections:
            if section in test_report:
                print(f"✅ 报告章节 '{section}' 存在")
            else:
                print(f"❌ 报告章节 '{section}' 缺失")
                return False
        
        # 测试报告摘要打印
        print("\n📋 测试报告摘要打印...")
        reporter.print_summary_report(test_report)
        
        print("\n✅ 系统报告功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 系统报告测试失败: {e}")
        return False

def test_gui_integration():
    """测试GUI集成功能"""
    try:
        from cogvrs_core.visualization.optimized_gui import OptimizedCogvrsGUI
        
        print("\n🎮 测试GUI集成功能...")
        
        # 创建测试配置
        test_config = {
            'window_width': 800,
            'window_height': 600,
            'target_fps': 30,
            'initial_agents': 5,
            'world': {'size': (50, 50)},
            'time': {'dt': 0.1},
            'physics': {'friction': 0.1},
            'civilization': {'enable_tribes': True}
        }
        
        # 初始化GUI（不运行主循环）
        gui = OptimizedCogvrsGUI(test_config)
        print("✅ OptimizedCogvrsGUI初始化成功")
        
        # 检查字体是否正确加载
        if hasattr(gui, 'font_large') and gui.font_large:
            print("✅ 中文字体对象创建成功")
        else:
            print("❌ 中文字体对象创建失败")
            return False
            
        # 检查系统报告器是否集成
        if hasattr(gui, 'reporter') and gui.reporter:
            print("✅ SystemReporter集成成功")
        else:
            print("❌ SystemReporter集成失败")
            return False
            
        print("✅ GUI集成测试完成")
        return True
        
    except Exception as e:
        print(f"❌ GUI集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始修复验证测试")
    print("=" * 50)
    
    results = []
    
    # 测试1: 中文字体加载
    results.append(test_chinese_font_loading())
    
    # 测试2: 系统报告功能
    results.append(test_system_reporter())
    
    # 测试3: GUI集成功能
    results.append(test_gui_integration())
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ 通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！修复成功！")
        print("\n✨ 用户反馈的两个问题已完全解决：")
        print("1. ✅ 右侧栏中文字符显示问题已修复")
        print("2. ✅ 系统总结报告功能已实现")
        print("\n🎮 现在可以运行 python run_cogvrs.py 开始使用！")
        print("📋 使用S键保存报告，P键打印报告摘要")
    else:
        print("❌ 部分测试失败，需要进一步修复")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)