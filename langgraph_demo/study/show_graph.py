from langchain_core.runnables.graph import MermaidDrawMethod

# ============================================================================
# 可视化工具函数
# ============================================================================

def save_mermaid_as_image(mermaid_code: str, filename: str, logger=None, formats=None):
    """
    将 Mermaid 代码保存为指定格式的文件
    
    Args:
        mermaid_code: Mermaid 代码字符串
        filename: 文件名（不包含扩展名）
        logger: 日志器
        formats: 要生成的文件格式列表，可选值: ['png', 'md', 'mmd', 'svg']
    """
    if formats is None:
        formats = ['png', 'md', 'mmd']  # 默认生成这三种格式
    
    if logger:
        logger.info(f"🖼️ 正在生成文件: {filename}，格式: {', '.join(formats)}")
    
    try:
        import subprocess
        
        # 保存 Mermaid 代码到文件 (.mmd)
        if 'mmd' in formats:
            mmd_file = f"{filename}.mmd"
            with open(mmd_file, "w", encoding="utf-8") as f:
                f.write(mermaid_code)
            
            if logger:
                logger.info(f"💾 Mermaid 代码已保存到: {mmd_file}")
        
        # 保存为 Markdown 格式 (.md)
        if 'md' in formats:
            markdown_file = f"{filename}.md"
            markdown_content = f"""# {filename.replace('_', ' ').title()} 工作流程图

## 流程图

```mermaid
{mermaid_code}
```

## 说明

这是一个使用 LangGraph 构建的工作流程图。

### 生成时间

生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*由 LangGraph 可视化工具自动生成*
"""
            
            with open(markdown_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            if logger:
                logger.info(f"📝 Markdown 文件已保存到: {markdown_file}")
        
        # 生成图片格式 (需要 mermaid-cli)
        image_formats = [f for f in formats if f in ['png', 'svg']]
        if image_formats:
            # 检查是否安装了 mermaid-cli
            result = subprocess.run(["mmdc", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                # 确保有 .mmd 文件用于生成图片
                if 'mmd' not in formats:
                    mmd_file = f"{filename}.mmd"
                    with open(mmd_file, "w", encoding="utf-8") as f:
                        f.write(mermaid_code)
                
                for img_format in image_formats:
                    if img_format == 'png':
                        png_file = f"{filename}.png"
                        subprocess.run([
                            "mmdc", 
                            "-i", mmd_file, 
                            "-o", png_file,
                            "-b", "transparent"
                        ])
                        if logger:
                            logger.info(f"🖼️ PNG 图片已生成: {png_file}")
                    
                    elif img_format == 'svg':
                        svg_file = f"{filename}.svg"
                        subprocess.run([
                            "mmdc", 
                            "-i", mmd_file, 
                            "-o", svg_file
                        ])
                        if logger:
                            logger.info(f"🖼️ SVG 图片已生成: {svg_file}")
                
                return True
            else:
                if logger:
                    logger.warning("⚠️ 未安装 mermaid-cli，无法生成图片")
                    logger.info("💡 安装方法: npm install -g @mermaid-js/mermaid-cli")
                return False
                
    except FileNotFoundError:
        if logger:
            logger.warning("⚠️ 未找到 mermaid-cli，无法生成图片")
            logger.info("💡 安装方法: npm install -g @mermaid-js/mermaid-cli")
        return False
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ 生成文件时出错: {e}")
        return False

def print_mermaid_diagram(mermaid_code: str, logger=None):
    """
    打印 Mermaid 代码
    
    Args:
        mermaid_code: Mermaid 代码字符串
        logger: 日志器
    """
    if logger:
        logger.info("📝 Mermaid 代码:")
        logger.info("="*50)
        logger.info(mermaid_code)
        logger.info("="*50)
    else:
        print("📝 Mermaid 代码:")
        print("="*50)
        print(mermaid_code)
        print("="*50)

def save_mermaid_as_markdown(mermaid_code: str, filename: str, title: str = None, description: str = None, logger=None):
    """
    将 Mermaid 代码保存为 Markdown 格式
    
    Args:
        mermaid_code: Mermaid 代码字符串
        filename: 文件名（不包含扩展名）
        title: 标题（可选）
        description: 描述（可选）
        logger: 日志器
    """
    if logger:
        logger.info(f"📝 正在生成 Markdown: {filename}")
    
    try:
        # 如果没有提供标题，使用文件名
        if not title:
            title = filename.replace('_', ' ').title()
        
        # 如果没有提供描述，使用默认描述
        if not description:
            description = "这是一个使用 LangGraph 构建的工作流程图。"
        
        # 生成 Markdown 内容
        markdown_file = f"{filename}.md"
        markdown_content = f"""# {title}

## 流程图

```mermaid
{mermaid_code}
```

## 说明

{description}

### 生成时间

生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*由 LangGraph 可视化工具自动生成*
"""
        
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        if logger:
            logger.info(f"📝 Markdown 文件已保存到: {markdown_file}")
        
        return True
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ 生成 Markdown 时出错: {e}")
        return False


def visualize_workflow(graph, title="工作流图", logger=None, description=None, formats=None):
    try:
        # 生成 Mermaid 图
        mermaid_diagram = graph.get_graph().draw_mermaid()
        logger.info("🎨 Mermaid 图生成成功")
        
        # 打印 Mermaid 代码
        print_mermaid_diagram(mermaid_diagram, logger)
        
        # 保存为指定格式的文件
        save_mermaid_as_image(mermaid_diagram, f"{title}", logger, formats)
        
        # 单独保存为 Markdown（如果需要自定义描述）
        if description and 'md' in (formats or ['png', 'md', 'mmd']):
            save_mermaid_as_markdown(mermaid_diagram, f"{title}", title, description, logger)
        
        # 显示图结构信息
        logger.info("📋 图结构信息:")
        logger.info(f"节点数量: {len(graph.get_graph().nodes)}")
        logger.info(f"边数量: {len(graph.get_graph().edges)}")
        
        # 显示节点和边的详细信息
        logger.info("🔗 节点列表:")
        for node in graph.get_graph().nodes:
            logger.info(f"  - {node}")
            
        logger.info("🔗 边列表:")
        for edge in graph.get_graph().edges:
            logger.info(f"  - {edge.source} → {edge.target}")
        
    except Exception as e:
        logger.warning(f"可视化生成失败: {e}")
        logger.info("📋 手动流程图:")
        logger.info("START → generate_topics → [generate_joke] (并行) → select_best_joke → END")

def show_workflow_graph(workflow, title="工作流图", logger=None, description=None, formats=[]):
    """
    显示工作流图
    学习要点：工作流的可视化
    
    Args:
        workflow: LangGraph 工作流
        title: 图表标题
        logger: 日志器
        description: 自定义描述（可选）
        formats: 要生成的文件格式列表，可选值: ['png', 'md', 'mmd', 'svg']
    """
    logger.info(f"📊 显示{title}")
    
    try:
        # 方法1: 使用 LangGraph 内置的可视化
        logger.info("方法1: LangGraph 内置可视化")
        graph_drawable = workflow.get_graph(xray=True) # xray=True 显示节点信息
        

        if "png" in formats or len(formats) == 0:
            # 保存为图片（默认行为）
            try:
                png_image = graph_drawable.draw_mermaid_png(draw_method=MermaidDrawMethod.API)
                with open(f"{title}.png", "wb") as f:
                    f.write(png_image)
                logger.info(f"✅ 工作流图已保存为 {title}.png")
            except Exception as e:
                logger.warning(f"无法生成PNG图片: {e}")
            
            # 保存为SVG
            try:
                svg_image = graph_drawable.draw_mermaid_svg()
                with open(f"{title}.svg", "w", encoding="utf-8") as f:
                    f.write(svg_image)
                logger.info(f"✅ 工作流图已保存为 {title}.svg")
            except Exception as e:
                logger.warning(f"无法生成SVG图片: {e}")


        # 如果指定了格式，使用自定义可视化函数
        if formats:
            #  # 生成 Mermaid 图
            # mermaid_code = graph_drawable.draw_mermaid()
            # logger.info("Mermaid 代码:")
            # logger.debug(mermaid_code)
        
            # 使用自定义可视化函数
            visualize_workflow(workflow, title, logger, description, formats)


    except Exception as e:
        logger.error(f"LangGraph 可视化失败: {e}")
    
