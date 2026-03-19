"""
数据导出服务
提供 CSV、Excel、AI 报告 格式的数据导出功能
"""

import io
import csv
from datetime import datetime
from flask import send_file
from app.models.submission import Submission
from app.models.user import User


class ExportService:
    """
    导出服务类
    负责将数据导出为不同格式
    """

    @staticmethod
    def export_to_csv(submissions=None, start_date=None, end_date=None, risk_level=None):
        """
        导出提交记录为 CSV 格式

        Args:
            submissions: 提交记录列表，如果为 None 则查询所有记录
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            risk_level: 风险等级筛选（可选）

        Returns:
            BytesIO: CSV 文件流
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow([
            'ID', '学号', '姓名', '基础分', '最终分', '风险等级',
            '认知维度', '行为维度', '经历维度', '提交时间', 'IP 地址', '数据状态'
        ])

        # 如果没有指定 submissions，则查询数据库
        if submissions is None:
            submissions = Submission.query.join(User).order_by(
                Submission.submitted_at.desc()
            )

            # 应用筛选条件
            if start_date:
                submissions = submissions.filter(
                    Submission.submitted_at >= datetime.strptime(
                        start_date, '%Y-%m-%d')
                )
            if end_date:
                submissions = submissions.filter(
                    Submission.submitted_at <= datetime.strptime(
                        end_date, '%Y-%m-%d')
                )
            if risk_level:
                submissions = submissions.filter(
                    Submission.risk_level == risk_level)

            submissions = submissions.all()

        # 写入数据行
        for sub in submissions:
            writer.writerow([
                sub.id,
                sub.user.student_id if sub.user else 'Unknown',
                sub.user.name if sub.user else 'Unknown',
                sub.base_score,
                sub.final_score,
                sub.risk_level,
                sub.cognitive,
                sub.behavior,
                sub.experience,
                sub.submitted_at.strftime(
                    '%Y-%m-%d %H:%M:%S') if sub.submitted_at else '',
                sub.ip_address or '',
                '有效' if sub.is_valid else '无效'
            ])

        # 创建 BytesIO 对象
        buffer = io.BytesIO()
        buffer.write(output.getvalue().encode('utf-8-sig'))  # 使用 BOM 编码支持中文
        buffer.seek(0)

        return buffer

    @staticmethod
    def export_to_excel(submissions=None, start_date=None, end_date=None, risk_level=None):
        """
        导出提交记录为 Excel 格式（使用 reportlab 生成 PDF 格式的表格）

        Args:
            submissions: 提交记录列表
            start_date: 开始日期
            end_date: 结束日期
            risk_level: 风险等级

        Returns:
            BytesIO: PDF 文件流
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        # 注册中文字体
        try:
            pdfmetrics.registerFont(
                TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
            font_name = 'SimSun'
        except:
            font_name = 'Helvetica'

        # 标题
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title', parent=styles['Title'], fontName=font_name, fontSize=16)
        elements.append(Paragraph("反诈风险评估数据导出报告", title_style))
        elements.append(Spacer(1, 20))

        # 筛选信息
        filter_info = f"导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if start_date:
            filter_info += f" | 开始日期：{start_date}"
        if end_date:
            filter_info += f" | 结束日期：{end_date}"
        if risk_level:
            filter_info += f" | 风险等级：{risk_level}"

        elements.append(Paragraph(filter_info, styles['Normal']))
        elements.append(Spacer(1, 20))

        # 如果没有指定 submissions，则查询数据库
        if submissions is None:
            submissions = Submission.query.join(User).order_by(
                Submission.submitted_at.desc()
            )

            if start_date:
                submissions = submissions.filter(
                    Submission.submitted_at >= datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                submissions = submissions.filter(
                    Submission.submitted_at <= datetime.strptime(end_date, '%Y-%m-%d'))
            if risk_level:
                submissions = submissions.filter(
                    Submission.risk_level == risk_level)

            submissions = submissions.all()

        # 创建表格数据
        data = [
            ['ID', '学号', '姓名', '分数', '风险等级', '提交时间', '状态']
        ]

        for sub in submissions:
            data.append([
                str(sub.id),
                sub.user.student_id if sub.user else 'Unknown',
                sub.user.name if sub.user else 'Unknown',
                str(sub.final_score),
                sub.risk_level,
                sub.submitted_at.strftime(
                    '%Y-%m-%d') if sub.submitted_at else '',
                '有效' if sub.is_valid else '无效'
            ])

        # 创建表格
        table = Table(data, colWidths=[30, 80, 60, 40, 60, 100, 40])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.lightgrey])
        ]))

        elements.append(table)

        # 生成 PDF
        doc.build(elements)
        buffer.seek(0)

        return buffer

    @staticmethod
    def get_export_filename(format_type='csv'):
        """
        生成导出文件名

        Args:
            format_type: 文件格式（csv 或 excel）

        Returns:
            str: 文件名
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if format_type == 'csv':
            return f"反诈评估数据_{timestamp}.csv"
        elif format_type == 'excel':
            return f"反诈评估数据_{timestamp}.pdf"
        else:
            return f"export_{timestamp}.{format_type}"

    @staticmethod
    def export_ai_report_to_pdf(ai_report_content):
        """
        导出 AI 统计报告为 PDF 格式

        Args:
            ai_report_content: AI 生成的报告内容（字符串）

        Returns:
            BytesIO: PDF 文件流
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=50, rightMargin=50)
        elements = []

        # 注册中文字体
        try:
            pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
            pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))
            font_song = 'SimSun'
            font_hei = 'SimHei'
        except:
            font_song = 'Helvetica'
            font_hei = 'Helvetica-Bold'

        # 标题样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontName=font_hei,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20
        )

        # 正文样式
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontName=font_song,
            fontSize=12,
            alignment=TA_LEFT,
            leading=20  # 行间距
        )

        # 添加标题
        elements.append(Paragraph("大学生反诈风险评估统计分析报告", title_style))
        elements.append(Spacer(1, 10))

        # 添加生成时间
        timestamp = datetime.now().strftime('%Y年%m月%d日 %H:%M')
        time_paragraph = Paragraph(f"<b>报告生成时间：</b>{timestamp}", normal_style)
        elements.append(time_paragraph)
        elements.append(Spacer(1, 20))

        # 分割报告内容为段落
        # 假设 AI 报告使用换行符分隔段落
        paragraphs = ai_report_content.split('\n')
        
        for para in paragraphs:
            if para.strip():  # 跳过空行
                # 处理标题（如果有的话）
                if para.startswith('#'):
                    heading_style = ParagraphStyle(
                        'Heading',
                        parent=styles['Heading1'],
                        fontName=font_hei,
                        fontSize=14,
                        spaceBefore=15,
                        spaceAfter=10
                    )
                    elements.append(Paragraph(para.replace('#', '').strip(), heading_style))
                else:
                    # 普通段落
                    elements.append(Paragraph(para.strip(), normal_style))
                elements.append(Spacer(1, 5))

        # 添加页脚信息
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontName=font_song,
            fontSize=10,
            alignment=TA_CENTER,
            textColor='gray'
        )
        elements.append(Paragraph("── 报告结束 ──", footer_style))

        # 生成 PDF
        doc.build(elements)
        buffer.seek(0)

        return buffer
