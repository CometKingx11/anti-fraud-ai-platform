# Author: 小土豆233
# Date: 2026-03-18
# Description: URL 安全检测服务 - 检测风险链接
# FilePath: flask_anti_project\app\services\url_security_service.py

from flask import current_app
import requests
import re
import json


class URLSecurityService:
    """
    URL 安全检测服务
    提供多种 URL 检测方式的降级策略
    """
    
    @staticmethod
    def extract_urls_from_text(text: str) -> list:
        """
        从文本中提取 URL
        
        Args:
            text (str): 输入文本
            
        Returns:
            list: URL 列表
        """
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return urls
    
    @staticmethod
    def check_url_tencent(url: str) -> dict:
        """
        腾讯安全开放平台 - 网址安全检测API（占位实现）
        
        注意：此 API 需要申请，以下为示例代码
        实际使用时需要替换为真实的 API 调用
        
        Args:
            url: 待检测的 URL
            
        Returns:
            检测结果字典
        """
        # TODO: 实现真实的腾讯 API 调用
        # 这里先返回一个占位结果
        return {
            'success': False,
            'is_risk': False,
            'risk_level': 'unknown',
            'message': '腾讯 API 未配置',
            'source': 'Tencent'
        }
    
    @staticmethod
    def check_url_ai(url: str, open_text: str = "") -> dict:
        """
        使用 AI 大模型进行 URL 风险分析（备用方案）
        
        Args:
            url: 待检测的 URL
            open_text: 上下文描述
            
        Returns:
            检测结果字典
        """
        try:
            from dashscope import MultiModalConversation
            
            api_key = current_app.config.get('DASHSCOPE_API_KEY')
            if not api_key:
                return {
                    'success': False,
                    'is_risk': False,
                    'risk_level': 'unknown',
                    'message': '未配置通义千问 API Key',
                    'source': 'AI'
                }
            
            prompt = f"""
你是网络安全专家。请分析以下 URL是否为可疑诈骗链接：

URL: {url}
上下文描述：{open_text[:200] if open_text else '无'}

常见诈骗链接特征：
1. 虚假投资平台（高回报、低风险）
2. 钓鱼网站（冒充银行、电商、政府）
3. 刷单返利平台
4. 虚假贷款平台
5. 木马病毒下载链接
6. 短链接隐藏真实地址

请判断该 URL 的风险等级，返回严格 JSON 格式：
{{
  "is_risk": true/false,
  "risk_level": 0-5 (0=安全，5=极高风险),
  "risk_type": "诈骗类型",
  "reason": "判断理由（50 字以内）"
}}
"""
            
            content = [{'text': prompt}]
            messages = [{'role': 'user', 'content': content}]
            
            response = MultiModalConversation.call(
                model='qwen-vl-plus-latest',
                messages=messages,
                api_key=api_key,
                result_format='message'
            )
            
            model_output = response.output.choices[0].message.content[0]['text'].strip()
            
            # 解析 JSON
            cleaned = model_output.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:].strip()
            if cleaned.startswith('```'):
                cleaned = cleaned[3:].strip()
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3].strip()
            
            result = json.loads(cleaned)
            
            return {
                'success': True,
                'is_risk': result.get('is_risk', False),
                'risk_level': result.get('risk_level', 0),
                'risk_type': result.get('risk_type', ''),
                'description': result.get('reason', ''),
                'source': 'AI'
            }
            
        except Exception as e:
            return {
                'success': False,
                'is_risk': False,
                'risk_level': 'unknown',
                'message': f'AI 分析异常：{str(e)}',
                'source': 'AI'
            }
    
    @staticmethod
    def check_url(url: str, open_text: str = "", use_ai_fallback: bool = True) -> dict:
        """
        综合检测URL（降级策略）
        
        Args:
            url: 待检测的 URL
            open_text: 上下文描述
            use_ai_fallback: 是否使用 AI 作为备用方案
            
        Returns:
            检测结果字典
        """
        # 1. 优先使用腾讯 API（需申请）
        result_tencent = URLSecurityService.check_url_tencent(url)
        if result_tencent['success'] and result_tencent['risk_level'] != 'unknown':
            return result_tencent
        
        # 2. 降级到 AI 分析（通义千问）
        if use_ai_fallback:
            result_ai = URLSecurityService.check_url_ai(url, open_text)
            if result_ai['success']:
                return result_ai
        
        # 3. 全部失败，返回未知
        return {
            'success': False,
            'is_risk': False,
            'risk_level': 'unknown',
            'message': '所有检测方式均失败',
            'source': 'None'
        }
    
    @staticmethod
    def batch_check_urls(urls: list, open_text: str = "") -> list:
        """
        批量检测URLs
        
        Args:
            urls: URL 列表
            open_text: 上下文描述
            
        Returns:
            检测结果列表
        """
        results = []
        for url in urls:
            result = URLSecurityService.check_url(url, open_text)
            result['url'] = url
            results.append(result)
        return results
    
    @staticmethod
    def calculate_risk_score(url_results: list) -> int:
        """
        根据 URL 检测结果计算风险加分
        
        Args:
            url_results: URL 检测结果列表
            
        Returns:
            风险加分（每个风险链接 +10 分，上限 20 分）
        """
        risk_count = sum(1 for r in url_results if r.get('is_risk', False))
        return min(risk_count * 10, 20)
