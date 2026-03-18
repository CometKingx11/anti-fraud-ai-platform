"""
URL 安全检测服务
集成 360、腾讯等第三方安全 API，提供网址风险检测能力
"""

import re
import requests
from typing import List, Dict
from flask import current_app


class URLSecurityService:
    """URL 安全检测服务类"""
    
    @staticmethod
    def extract_urls_from_text(text: str) -> List[str]:
        """
        从文本中提取 URL
        
        Args:
            text: 输入文本
            
        Returns:
            URL 列表
        """
        # URL 匹配正则表达式
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # 标准化 URL（为 www. 开头添加 http://）
        normalized_urls = []
        for url in urls:
            if url.startswith('www.'):
                url = 'http://' + url
            normalized_urls.append(url)
        
        return list(set(normalized_urls))  # 去重
    
    @staticmethod
    def check_url_360(url: str) -> Dict:
        """
        360 网址安全检测 API
        
        API 文档：https://openapi.360.cn/doc.html
        
        Args:
            url: 待检测的 URL
            
        Returns:
            检测结果字典
        """
        api_key = current_app.config.get('360_API_KEY')
        
        if not api_key:
            return {
                'success': False,
                'is_risk': False,
                'risk_level': 'unknown',
                'message': '未配置 360 API Key',
                'source': '360'
            }
        
        try:
            # 360 URL 安全检测 API 端点
            api_url = "https://openapi.360.cn/urlcheck"
            
            params = {
                'url': url,
                'key': api_key,
                'format': 'json'
            }
            
            response = requests.get(api_url, params=params, timeout=5)
            result = response.json()
            
            # 解析 360 API 响应
            if result.get('code') == 0:
                data = result.get('data', {})
                is_risk = data.get('level', 0) >= 2  # 风险等级>=2 视为风险
                
                risk_info = {
                    'success': True,
                    'is_risk': is_risk,
                    'risk_level': data.get('level', 0),
                    'risk_type': data.get('type', ''),
                    'description': data.get('desc', ''),
                    'source': '360'
                }
                
                return risk_info
            else:
                return {
                    'success': False,
                    'is_risk': False,
                    'risk_level': 'unknown',
                    'message': result.get('msg', 'API 调用失败'),
                    'source': '360'
                }
                
        except Exception as e:
            return {
                'success': False,
                'is_risk': False,
                'risk_level': 'unknown',
                'message': f'360 API 异常：{str(e)}',
                'source': '360'
            }
    
    @staticmethod
    def check_url_tencent(url: str) -> Dict:
        """
        腾讯电脑管家 URL 安全检测 API
        
        API 文档：https://open.qq.com/
        
        Args:
            url: 待检测的 URL
            
        Returns:
            检测结果字典
        """
        api_key = current_app.config.get('TENCENT_API_KEY')
        
        if not api_key:
            return {
                'success': False,
                'is_risk': False,
                'risk_level': 'unknown',
                'message': '未配置腾讯 API Key',
                'source': 'Tencent'
            }
        
        try:
            # 腾讯 URL 安全检测 API 端点
            api_url = "https://openapi.guanjia.qq.com/url_check"
            
            params = {
                'url': url,
                'key': api_key,
                'output': 'json'
            }
            
            response = requests.get(api_url, params=params, timeout=5)
            result = response.json()
            
            # 解析腾讯 API 响应
            if result.get('code') == 0:
                data = result.get('data', {})
                is_risk = data.get('evil_level', 0) > 0
                
                risk_info = {
                    'success': True,
                    'is_risk': is_risk,
                    'risk_level': data.get('evil_level', 0),
                    'risk_type': data.get('evil_type', ''),
                    'description': data.get('desc', ''),
                    'source': 'Tencent'
                }
                
                return risk_info
            else:
                return {
                    'success': False,
                    'is_risk': False,
                    'risk_level': 'unknown',
                    'message': result.get('msg', 'API 调用失败'),
                    'source': 'Tencent'
                }
                
        except Exception as e:
            return {
                'success': False,
                'is_risk': False,
                'risk_level': 'unknown',
                'message': f'腾讯 API 异常：{str(e)}',
                'source': 'Tencent'
            }
    
    @staticmethod
    def check_url_ai(url: str, open_text: str = "") -> Dict:
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
你是网络安全专家。请分析以下 URL 是否为可疑诈骗链接：

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
            import json
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
    def check_url(url: str, open_text: str = "", use_ai_fallback: bool = True) -> Dict:
        """
        综合检测 URL（优先第三方 API，失败时降级到 AI）
        
        Args:
            url: 待检测的 URL
            open_text: 上下文描述
            use_ai_fallback: 是否使用 AI 作为备用方案
            
        Returns:
            检测结果字典
        """
        # 1. 优先使用 360 API
        result_360 = URLSecurityService.check_url_360(url)
        if result_360['success'] and result_360['risk_level'] != 'unknown':
            return result_360
        
        # 2. 尝试腾讯 API
        result_tencent = URLSecurityService.check_url_tencent(url)
        if result_tencent['success'] and result_tencent['risk_level'] != 'unknown':
            return result_tencent
        
        # 3. 降级到 AI 分析
        if use_ai_fallback:
            result_ai = URLSecurityService.check_url_ai(url, open_text)
            if result_ai['success']:
                return result_ai
        
        # 4. 全部失败，返回未知
        return {
            'success': False,
            'is_risk': False,
            'risk_level': 'unknown',
            'message': '所有检测方式均失败',
            'source': 'None'
        }
    
    @staticmethod
    def batch_check_urls(urls: List[str], open_text: str = "") -> List[Dict]:
        """
        批量检测多个 URL
        
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
    def calculate_risk_score(url_results: List[Dict]) -> int:
        """
        根据 URL 检测结果计算风险加分
        
        Args:
            url_results: URL 检测结果列表
            
        Returns:
            风险加分（0-20 分）
        """
        if not url_results:
            return 0
        
        risk_count = sum(1 for r in url_results if r.get('is_risk', False))
        
        if risk_count == 0:
            return 0
        elif risk_count == 1:
            return 10  # 发现 1 个风险链接 +10 分
        else:
            return min(20, risk_count * 10)  # 每多 1 个加 10 分，最多 20 分
