

def show_workflow_graph(workflow, title="工作流图",logger=None):
    """
    显示工作流图
    学习要点：工作流的可视化
    """
    logger.info(f"📊 显示{title}")
    
    try:
        # 方法1: 使用 LangGraph 内置的可视化
        logger.info("方法1: LangGraph 内置可视化")
        graph_drawable = workflow.get_graph()
        
        # 生成 Mermaid 图
        mermaid_code = graph_drawable.draw_mermaid()
        logger.info("Mermaid 代码:")
        logger.debug(mermaid_code)
        
        # 保存为图片
        try:
            png_image = graph_drawable.draw_mermaid_png()
            with open(f"{title}.png", "wb") as f:
                f.write(png_image)
            logger.info("✅ 工作流图已保存为 workflow_graph.png")
        except Exception as e:
            logger.warning(f"无法生成PNG图片: {e}")
        
        # 保存为SVG
        try:
            svg_image = graph_drawable.draw_mermaid_svg()
            with open(f"{title}.svg", "w", encoding="utf-8") as f:
                f.write(svg_image)
            logger.info("✅ 工作流图已保存为 workflow_graph.svg")
        except Exception as e:
            logger.warning(f"无法生成SVG图片: {e}")
            
    except Exception as e:
        logger.error(f"LangGraph 可视化失败: {e}")
    
