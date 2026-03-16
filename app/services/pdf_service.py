# Author: 小土豆233
# Date: 2026-03-16 23:42:18
# LastEditTime: 2026-03-16 23:42:27
# LastEditors: 小土豆233
# Description: PDF 服务，处理评估报告的 PDF 导出功能
# FilePath: flask_anti_project\app\services\pdf_service.py

import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from flask import send_file


class PDFService:
    """
    PDF服务类
    负责生成评估报告PDF
    """

    @staticmethod
    def generate_report_pdf(assessment_data):
        """
        生成评估报告PDF

        Args:
            assessment_data (dict): 评估数据

        Returns:
            BytesIO: PDF文件流
        """
        # 创建PDF缓冲区
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        elements = []

        # 注册中文字体
        try:
            pdfmetrics.registerFont(
                TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
            font_name = 'SimSun'
        except:
            font_name = 'Helvetica'

        # 定义样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontName=font_name,
            fontSize=18
        )
        heading_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=14
        )
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=11
        )

        # 添加标题
        elements.append(Paragraph("大学生反诈风险评估报告", title_style))
        elements.append(Spacer(1, 24))

        # 风险等级
        elements.append(
            Paragraph(f"风险等级：{assessment_data.get('risk_level', '未知')}", heading_style))
        elements.append(Spacer(1, 12))

        # 分数信息
        elements.append(
            Paragraph(f"基础分：{assessment_data.get('base_score', 0)}/100", normal_style))
        elements.append(
            Paragraph(f"最终分：{assessment_data.get('final_score', 0)}/130", normal_style))
        elements.append(Spacer(1, 12))

        # 维度得分表格
        elements.append(Paragraph("维度得分详情", heading_style))
        dim_table = Table([
            ['维度', '得分', '说明'],
            ['认知维度', f"{assessment_data.get('cognitive', 0)}/40", '（越高越安全）'],
            ['行为维度', f"{assessment_data.get('behavior', 0)}/40", '（越高风险越大）'],
            ['经历维度', f"{assessment_data.get('experience', 0)}/20", '（越高风险越大）']
        ], colWidths=[2*inch, 1.5*inch, 3*inch])
        dim_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
        ]))
        elements.append(dim_table)
        elements.append(Spacer(1, 12))

        # 开放描述
        elements.append(Paragraph("开放描述", heading_style))
        elements.append(Paragraph(assessment_data.get(
            'open_text', '无'), normal_style))
        elements.append(Spacer(1, 12))

        # 风险点分析
        elements.append(Paragraph("风险点分析", heading_style))
        risk_points = assessment_data.get('risk_points', [])
        if risk_points:
            elements.append(Paragraph(" • ".join(risk_points), normal_style))
        else:
            elements.append(Paragraph("暂无识别出具体风险点", normal_style))
        elements.append(Spacer(1, 12))

        # 详细分析总结
        elements.append(Paragraph("详细分析总结", heading_style))
        elements.append(Paragraph(assessment_data.get(
            'analysis', '暂无分析内容'), normal_style))
        elements.append(Spacer(1, 12))

        # 个性化建议
        elements.append(Paragraph("个性化反诈建议", heading_style))
        suggestions = assessment_data.get('suggestions', [])
        if suggestions:
            for i, sug in enumerate(suggestions, 1):
                elements.append(Paragraph(f"{i}. {sug}", normal_style))
        else:
            elements.append(Paragraph("暂无个性化建议", normal_style))
        elements.append(Spacer(1, 12))

        # 推荐推送内容
        elements.append(Paragraph("推荐推送内容", heading_style))
        push_contents = assessment_data.get('push_contents', [])
        if push_contents:
            for i, p in enumerate(push_contents, 1):
                elements.append(Paragraph(f"{i}. {p}", normal_style))
        else:
            elements.append(Paragraph("暂无推荐推送内容", normal_style))

        # 生成PDF
        doc.build(elements)
        buffer.seek(0)

        return buffer
