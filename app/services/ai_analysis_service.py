'''
Author: 小土豆233
Date: 2026-03-16 23:42:18
LastEditTime: 2026-03-16 23:42:27
LastEditors: 小土豆233
Description: AI分析服务
处理与通义千问API的交互，生成评估分析结果
FilePath: \flask_anti_project\app\__init__.py
'''

import json
import base64
import os
from dashscope import MultiModalConversation
from app import db
from flask import current_app


class AIAnalysisService:
    """
    AI分析服务类
    负责与大模型交互并生成评估结果
    """

    def analyze_assessment(self, assessment_data):
        """
        对评估数据进行AI分析

        Args:
            assessment_data (dict): 评估数据

        Returns:
            dict: AI分析结果
        """
        # 准备API调用参数
        api_key = current_app.config.get('DASHSCOPE_API_KEY')
        if not api_key:
            # 如果没有API密钥，返回基于规则的结果
            return self._get_rule_based_result(assessment_data)

        # 构建提示词
        prompt_text = self._build_prompt(assessment_data)

        # 准备图像数据
        content = [{'text': prompt_text}]

        # 添加上传的图像
        uploaded_images = assessment_data.get('uploaded_images', [])
        for img_path in uploaded_images[:3]:  # 最多使用3张图片
            try:
                with open(img_path, 'rb') as f:
                    base64_img = base64.b64encode(f.read()).decode('utf-8')
                content.append(
                    {'image': f'data:image/jpeg;base64,{base64_img}'})
            except Exception as e:
                print(f"读取图片失败 {img_path}: {e}")

        # 构建消息
        messages = [{'role': 'user', 'content': content}]

        try:
            # 调用大模型
            response = MultiModalConversation.call(
                model='qwen-vl-plus-latest',
                messages=messages,
                api_key=api_key,
                result_format='message'
            )

            # 解析响应
            model_output = response.output.choices[0].message.content[0]['text'].strip(
            )
            return self._parse_model_response(model_output)

        except Exception as e:
            print(f"大模型调用异常：{str(e)}")
            # 发生异常时返回基于规则的结果
            return self._get_rule_based_result(assessment_data)

    def _build_prompt(self, assessment_data):
        """
        构建AI提示词

        Args:
            assessment_data (dict): 评估数据

        Returns:
            str: 构建的提示词
        """
        base_score = assessment_data['base_score']
        cognitive = assessment_data['cognitive']
        behavior = assessment_data['behavior']
        experience = assessment_data['experience']
        open_text = assessment_data.get('open_text', '')

        prompt = f"""
你是大学生反诈风险评估专家。
基础风险分（问卷规则计算）：{base_score}/100
维度分：认知 {cognitive}/40，行为 {behavior}/40，经历 {experience}/20
开放描述：{open_text}

请综合所有信息（包括上传的图片），给出最终风险分（0-130），并输出严格JSON格式，不要任何多余文字或解释：
{{
  "final_score": int,
  "risk_level": "低风险" or "中风险" or "高风险" or "极高风险",
  "risk_points": ["风险点1", "风险点2", ...],
  "analysis": "150-200字中文分析，指出主要风险来源和原因",
  "suggestions": ["建议1", "建议2", ...],
  "push_contents": ["推送案例1", "推送视频2", ...]
}}
"""
        return prompt

    def _parse_model_response(self, model_output):
        """
        解析模型响应

        Args:
            model_output (str): 模型原始输出

        Returns:
            dict: 解析后的结果
        """
        # 清洗输出
        cleaned = model_output.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:].strip()
        if cleaned.startswith('```'):
            cleaned = cleaned[3:].strip()
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3].strip()
        cleaned = cleaned.strip()

        try:
            result = json.loads(cleaned)
            return result
        except json.JSONDecodeError as e:
            print(f"JSON解析失败：{str(e)}")
            print(f"原始输出：{model_output}")
            return {}

    def _get_rule_based_result(self, assessment_data):
        """
        基于规则的分析结果（备用方案）

        Args:
            assessment_data (dict): 评估数据

        Returns:
            dict: 基于规则的分析结果
        """
        base_score = assessment_data['base_score']

        # 简单的风险等级判断
        if base_score <= 30:
            risk_level = "低风险"
        elif base_score <= 55:
            risk_level = "中风险"
        elif base_score <= 80:
            risk_level = "高风险"
        else:
            risk_level = "极高风险"

        # 返回基于规则的结果
        return {
            'final_score': base_score,
            'risk_level': risk_level,
            'risk_points': [],
            'analysis': '基于规则的分析：根据问卷得分计算得出的风险评估结果。',
            'suggestions': ['加强反诈知识学习', '提高警惕意识'],
            'push_contents': ['反诈宣传视频', '典型案例分析']
        }
