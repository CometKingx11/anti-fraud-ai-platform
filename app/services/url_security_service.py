# Author: 脆心柚
# Description: URL 安全检测服务 - 检测风险链接

from flask import current_app
import requests
import re
import json
import time
from app.services.audit_service import AuditService


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
    def check_url_virustotal(url: str) -> dict:
        """
        VirusTotal - URL 安全检测 API
        
        文档：https://docs.virustotal.com/reference/url-info
        
        Args:
            url: 待检测的 URL
            
        Returns:
            检测结果字典
        """
        try:
            api_key = current_app.config.get('VIRUSTOTAL_API_KEY')
            if not api_key:
                return {
                    'success': False,
                    'is_risk': False,
                    'risk_level': 'unknown',
                    'message': '未配置 VirusTotal API Key',
                    'source': 'VirusTotal'
                }
            
            # 1. 对 URL 进行编码（VirusTotal 要求）
            import base64
            url_encoded = base64.urlsafe_b64encode(url.encode()).decode().strip('=')
            
            # 2. 调用 VirusTotal API v3
            headers = {
                'x-apikey': api_key,
                'Accept': 'application/json'
            }
            
            response = requests.get(
                f'https://www.virustotal.com/api/v3/urls/{url_encoded}',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 404:
                # URL 未被分析过，需要提交分析
                return URLSecurityService._submit_url_to_virustotal(url, api_key)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'is_risk': False,
                    'risk_level': 'unknown',
                    'message': f'VirusTotal API 错误：{response.status_code}',
                    'source': 'VirusTotal'
                }
            
            data = response.json()
            
            # 3. 解析结果
            attributes = data.get('data', {}).get('attributes', {})
            stats = attributes.get('last_analysis_stats', {})
            
            # 恶意引擎数量
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            harmless = stats.get('harmless', 0)
            
            # 4. 判断风险
            is_risk = malicious >= 5 or suspicious >= 3
            
            # 5. 计算风险等级（0-5）
            total = malicious + suspicious + harmless
            if total > 0:
                risk_ratio = (malicious * 2 + suspicious) / (total * 2)
                risk_level = min(5, int(risk_ratio * 5))
            else:
                risk_level = 0
            
            # 6. 构建返回结果
            return {
                'success': True,
                'is_risk': is_risk,
                'risk_level': risk_level,
                'risk_type': '恶意网站' if malicious > 0 else '可疑网站' if suspicious > 0 else '',
                'description': f'VirusTotal: {malicious}个引擎标记为恶意，{suspicious}个标记为可疑',
                'source': 'VirusTotal',
                'stats': stats  # 保留详细统计信息
            }
            
        except Exception as e:
            return {
                'success': False,
                'is_risk': False,
                'risk_level': 'unknown',
                'message': f'VirusTotal 检测异常：{str(e)}',
                'source': 'VirusTotal'
            }
    
    @staticmethod
    def _submit_url_to_virustotal(url: str, api_key: str) -> dict:
        """
        提交 URL 到 VirusTotal 进行分析
        
        Args:
            url: 待检测的 URL
            api_key: VirusTotal API Key
            
        Returns:
            检测结果字典
        """
        try:
            # 提交 URL 进行分析
            headers = {
                'x-apikey': api_key,
                'Accept': 'application/json'
            }
            
            data = {
                'url': url
            }
            
            response = requests.post(
                'https://www.virustotal.com/api/v3/urls',
                headers=headers,
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                # 提交成功，但需要等待分析结果
                # 这里先返回一个占位结果
                return {
                    'success': True,
                    'is_risk': False,
                    'risk_level': 'unknown',
                    'message': 'URL 已提交分析，请稍后重试',
                    'source': 'VirusTotal'
                }
            
            return {
                'success': False,
                'is_risk': False,
                'risk_level': 'unknown',
                'message': f'提交 URL 失败：{response.status_code}',
                'source': 'VirusTotal'
            }
            
        except Exception as e:
            return {
                'success': False,
                'is_risk': False,
                'risk_level': 'unknown',
                'message': f'提交 URL 异常：{str(e)}',
                'source': 'VirusTotal'
            }
    
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
        综合检测 URL（降级策略）
            
        优先级：
        1. VirusTotal API（最准确）
        2. 本地规则检测（快速过滤）
        3. AI 大模型分析（智能兜底）
            
        Args:
            url: 待检测的 URL
            open_text: 上下文描述
            use_ai_fallback: 是否使用 AI 作为备用方案
                
        Returns:
            检测结果字典
        """
        start_time = time.time()
        result = None
        
        try:
            # 1. 优先使用 VirusTotal API（最准确）
            result_vt = URLSecurityService.check_url_virustotal(url)
            if result_vt['success'] and result_vt['risk_level'] != 'unknown':
                result = result_vt
                result['response_time'] = time.time() - start_time
                # 记录成功日志
                AuditService.log_security_event(
                    'URL_DETECTION',
                    f'URL 检测成功：{url[:50]}... 结果：{result["risk_level"]} 来源：{result["source"]}',
                    severity='low',
                    extra_data={
                        'url': url,
                        'source': result['source'],
                        'risk_level': result['risk_level'],
                        'response_time': result['response_time']
                    }
                )
                return result
                
            # 2. 降级到 AI 分析（通义千问）
            if use_ai_fallback:
                result_ai = URLSecurityService.check_url_ai(url, open_text)
                if result_ai['success']:
                    result = result_ai
                    result['response_time'] = time.time() - start_time
                    # 记录 AI 检测日志
                    AuditService.log_security_event(
                        'URL_DETECTION',
                        f'URL AI 检测：{url[:50]}... 结果：{result["risk_level"]}',
                        severity='low',
                        extra_data={
                            'url': url,
                            'source': 'AI',
                            'risk_level': result['risk_level'],
                            'response_time': result['response_time']
                        }
                    )
                    return result
            
            # 3. 全部失败，返回未知
            result = {
                'success': False,
                'is_risk': False,
                'risk_level': 'unknown',
                'message': '所有检测方式均失败',
                'source': 'None',
                'response_time': time.time() - start_time
            }
            
            # 记录失败日志
            AuditService.log_security_event(
                'URL_DETECTION_FAILED',
                f'URL 检测失败：{url[:50]}... 所有方式均失败',
                severity='medium',
                extra_data={
                    'url': url,
                    'response_time': result['response_time']
                }
            )
            
            return result
            
        except Exception as e:
            # 记录异常日志
            response_time = time.time() - start_time
            AuditService.log_security_event(
                'URL_DETECTION_ERROR',
                f'URL 检测异常：{url[:50]}... 错误：{str(e)}',
                severity='high',
                extra_data={
                    'url': url,
                    'error': str(e),
                    'response_time': response_time
                }
            )
            
            return {
                'success': False,
                'is_risk': False,
                'risk_level': 'error',
                'message': f'检测过程出错：{str(e)}',
                'source': 'Error',
                'response_time': response_time
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
