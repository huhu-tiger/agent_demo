# -*- coding: utf-8 -*-
"""
LangGraph 工作流可视化工具
提供多种方式显示工作流图

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
import logging
from typing import Dict, List, Any

# 可视化组件
try:
    import matplotlib.pyplot as plt
    import networkx as nx
    from IPython.display import display, Image
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("警告: 可视化组件未安装，请运行: pip install matplotlib networkx ipython")

import config

# 获取日志器
logger = config.logger

class WorkflowVisualizer:
    """工作流可视化器"""
    
    def __init__(self):
        self.visualization_available = VISUALIZATION_AVAILABLE
    
    def show_langgraph_builtin(self, workflow, save_path="workflow_graph"):
        """
        使用 LangGraph 内置可视化
        """
        logger.info("📊 使用 LangGraph 内置可视化")
        
        try:
            # 获取可绘制图
            graph_drawable = workflow.get_graph()
            
            # 生成 Mermaid 代码
            mermaid_code = graph_drawable.draw_mermaid()
            logger.info("Mermaid 代码:")
            logger.info(mermaid_code)
            
            # 保存 Mermaid 代码
            with open(f"{save_path}.md", "w", encoding="utf-8") as f:
                f.write("# 工作流 Mermaid 图\n\n")
                f.write("```mermaid\n")
                f.write(mermaid_code)
                f.write("\n```\n")
            logger.info(f"✅ Mermaid 代码已保存为 {save_path}.md")
            
            # 生成 PNG 图片
            try:
                png_image = graph_drawable.draw_mermaid_png()
                with open(f"{save_path}.png", "wb") as f:
                    f.write(png_image)
                logger.info(f"✅ PNG 图片已保存为 {save_path}.png")
            except Exception as e:
                logger.warning(f"无法生成PNG图片: {e}")
            
            # 生成 SVG 图片
            try:
                svg_image = graph_drawable.draw_mermaid_svg()
                with open(f"{save_path}.svg", "w", encoding="utf-8") as f:
                    f.write(svg_image)
                logger.info(f"✅ SVG 图片已保存为 {save_path}.svg")
            except Exception as e:
                logger.warning(f"无法生成SVG图片: {e}")
                
            return True
            
        except Exception as e:
            logger.error(f"LangGraph 内置可视化失败: {e}")
            return False
    
    def show_networkx_custom(self, workflow, title="工作流图", save_path="workflow_custom"):
        """
        使用 NetworkX 自定义可视化
        """
        if not self.visualization_available:
            logger.error("NetworkX 不可用，请安装: pip install matplotlib networkx")
            return False
        
        logger.info("📊 使用 NetworkX 自定义可视化")
        
        try:
            # 创建有向图
            G = nx.DiGraph()
            
            # 构建工作流图
            self._build_workflow_graph(G, workflow)
            
            # 绘制图
            self._draw_workflow_graph(G, title, save_path)
            
            return True
            
        except Exception as e:
            logger.error(f"NetworkX 可视化失败: {e}")
            return False
    
    def _build_workflow_graph(self, G, workflow):
        """构建工作流图结构"""
        try:
            # 获取节点信息
            nodes = list(workflow.nodes.keys())
            
            # 添加节点
            for node_name in nodes:
                G.add_node(node_name, label=node_name, type="node")
            
            # 添加开始和结束节点
            G.add_node("START", label="START", type="start")
            G.add_node("END", label="END", type="end")
            
            # 添加边
            edges = workflow.edges
            for edge in edges:
                if hasattr(edge, 'from_node') and hasattr(edge, 'to_node'):
                    G.add_edge(edge.from_node, edge.to_node)
                elif isinstance(edge, tuple) and len(edge) == 2:
                    G.add_edge(edge[0], edge[1])
            
            # 添加从开始到入口点的边
            entry_point = workflow.entry_point
            if entry_point:
                G.add_edge("START", entry_point)
            
            # 添加条件边（如果有的话）
            conditional_edges = workflow.conditional_edges
            for source, (condition_func, edge_map) in conditional_edges.items():
                for condition, target in edge_map.items():
                    G.add_edge(source, target, condition=condition)
            
        except Exception as e:
            logger.warning(f"无法获取完整工作流结构: {e}")
            # 使用默认结构
            self._build_default_graph(G)
    
    def _build_default_graph(self, G):
        """构建默认图结构"""
        # 添加默认节点
        default_nodes = [
            ("input_processor", "输入处理"),
            ("response_generator", "响应生成"),
            ("message_logger", "消息记录")
        ]
        
        for node_name, label in default_nodes:
            G.add_node(node_name, label=label, type="node")
        
        # 添加开始和结束节点
        G.add_node("START", label="START", type="start")
        G.add_node("END", label="END", type="end")
        
        # 添加默认边
        default_edges = [
            ("START", "input_processor"),
            ("input_processor", "response_generator"),
            ("response_generator", "message_logger"),
            ("message_logger", "END")
        ]
        
        for from_node, to_node in default_edges:
            G.add_edge(from_node, to_node)
    
    def _draw_workflow_graph(self, G, title, save_path):
        """绘制工作流图"""
        plt.figure(figsize=(14, 10))
        
        # 使用分层布局
        pos = nx.spring_layout(G, k=4, iterations=100)
        
        # 定义节点颜色
        node_colors = []
        node_sizes = []
        
        for node in G.nodes():
            node_type = G.nodes[node].get('type', 'node')
            if node_type == 'start':
                node_colors.append('lightgreen')
                node_sizes.append(4000)
            elif node_type == 'end':
                node_colors.append('lightcoral')
                node_sizes.append(4000)
            else:
                node_colors.append('lightblue')
                node_sizes.append(3000)
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, 
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.8,
                              edgecolors='black',
                              linewidths=2)
        
        # 绘制边
        nx.draw_networkx_edges(G, pos, 
                              edge_color='gray',
                              arrows=True,
                              arrowsize=25,
                              arrowstyle='->',
                              width=2,
                              alpha=0.7)
        
        # 绘制节点标签
        labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels, 
                               font_size=11, 
                               font_weight='bold',
                               font_family='SimHei')
        
        # 绘制边标签（条件）
        edge_labels = {}
        for edge in G.edges(data=True):
            if 'condition' in edge[2]:
                edge_labels[(edge[0], edge[1])] = edge[2]['condition']
        
        if edge_labels:
            nx.draw_networkx_edge_labels(G, pos, edge_labels, 
                                        font_size=8,
                                        font_color='red')
        
        # 设置标题和样式
        plt.title(f"{title}\n节点和边的连接关系", 
                 fontsize=16, 
                 fontweight='bold',
                 pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(f"{save_path}.png", 
                   dpi=300, 
                   bbox_inches='tight',
                   facecolor='white',
                   edgecolor='none')
        logger.info(f"✅ 自定义工作流图已保存为 {save_path}.png")
        
        # 显示图
        plt.show()
    
    def show_workflow_info(self, workflow):
        """显示工作流信息"""
        logger.info("📋 工作流信息:")
        logger.info("=" * 50)
        
        try:
            # 节点信息
            nodes = list(workflow.nodes.keys())
            logger.info(f"节点数量: {len(nodes)}")
            logger.info(f"节点列表: {nodes}")
            
            # 边信息
            edges = workflow.edges
            logger.info(f"边数量: {len(edges)}")
            
            # 入口点
            entry_point = workflow.entry_point
            logger.info(f"入口点: {entry_point}")
            
            # 条件边
            conditional_edges = workflow.conditional_edges
            if conditional_edges:
                logger.info(f"条件边数量: {len(conditional_edges)}")
                for source, (func, edge_map) in conditional_edges.items():
                    logger.info(f"  {source} -> {list(edge_map.keys())}")
            
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"获取工作流信息失败: {e}")
    
    def show_all_visualizations(self, workflow, title="工作流图"):
        """显示所有可视化方法"""
        logger.info(f"🎨 显示 {title} 的所有可视化方法")
        logger.info("=" * 60)
        
        # 显示工作流信息
        self.show_workflow_info(workflow)
        
        # 方法1: LangGraph 内置可视化
        logger.info("\n方法1: LangGraph 内置可视化")
        self.show_langgraph_builtin(workflow, f"{title.replace(' ', '_')}_builtin")
        
        # 方法2: NetworkX 自定义可视化
        logger.info("\n方法2: NetworkX 自定义可视化")
        self.show_networkx_custom(workflow, title, f"{title.replace(' ', '_')}_custom")
        
        logger.info("\n✅ 所有可视化方法完成")

# 便捷函数
def visualize_workflow(workflow, title="工作流图"):
    """便捷函数：可视化工作流"""
    visualizer = WorkflowVisualizer()
    visualizer.show_all_visualizations(workflow, title)

def show_simple_graph(workflow, title="工作流图"):
    """简单可视化：只显示内置方法"""
    visualizer = WorkflowVisualizer()
    visualizer.show_langgraph_builtin(workflow, f"{title.replace(' ', '_')}")
    visualizer.show_workflow_info(workflow) 