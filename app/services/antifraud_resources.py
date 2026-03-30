# Author: 小土豆 233
# Description: 反诈教育资源链接库

"""
官方反诈教育资源库
所有链接均来自官方渠道，确保真实可用
"""

ANTIFRAUD_RESOURCES = {
    'video': [
        {
            'title': 'B 站反诈视频合集',
            'url': 'https://www.bilibili.com/',
            'description': 'B 站首页，可搜索反诈相关视频'
        },
        {
            'title': '国家反诈中心官方视频',
            'url': 'https://www.bilibili.com/',
            'description': '在 B 站搜索“国家反诈中心”'
        },
        {
            'title': '刷单诈骗防范视频',
            'url': 'https://www.bilibili.com/',
            'description': '在 B 站搜索“刷单诈骗”'
        },
        {
            'title': '电信诈骗警示录',
            'url': 'https://www.bilibili.com/',
            'description': '在 B 站搜索“电信诈骗”'
        },
        {
            'title': '网络安全教育视频',
            'url': 'https://www.bilibili.com/',
            'description': '在 B 站搜索“网络安全”'
        }
    ],
    'article': [
        {
            'title': '知乎反诈科普专栏',
            'url': 'https://www.zhihu.com/',
            'description': '知乎首页，可搜索反诈相关内容'
        },
        {
            'title': '大学生防骗指南',
            'url': 'https://www.zhihu.com/',
            'description': '在知乎搜索“大学生防骗”'
        },
        {
            'title': '国家反诈中心',
            'url': 'https://www.gov.cn/',
            'description': '中国政府网，可查询反诈相关信息'
        },
        {
            'title': '网络安全知识',
            'url': 'https://zhuanlan.zhihu.com/',
            'description': '知乎专栏，网络安全相关内容'
        },
        {
            'title': '公安部反诈专栏',
            'url': 'https://www.mps.gov.cn/',
            'description': '公安部官网首页'
        }
    ],
    'case': [
        {
            'title': '公安部典型案例',
            'url': 'https://www.mps.gov.cn/',
            'description': '公安部官网，可查询典型案例'
        },
        {
            'title': '中央网信办举报中心',
            'url': 'https://www.12377.cn/',
            'description': '网络违法和不良信息举报中心'
        },
        {
            'title': '中国政府网服务大厅',
            'url': 'https://www.gov.cn/fuwu/index.htm',
            'description': '中国政府网服务大厅'
        },
        {
            'title': '诈骗案例警示',
            'url': 'https://www.zhihu.com/',
            'description': '在知乎搜索“诈骗案例”'
        },
        {
            'title': '反诈防骗知识',
            'url': 'https://www.zhihu.com/',
            'description': '在知乎搜索“反诈防骗”'
        }
    ]
}


def get_recommended_resources(risk_level='中风险', weak_dimensions=None, limit=3):
    """
    根据风险等级和薄弱维度推荐资源
    
    Args:
        risk_level (str): 风险等级（低风险/中风险/高风险/极高风险）
        weak_dimensions (list): 薄弱维度列表（如 ['cognitive', 'behavior']）
        limit (int): 推荐数量限制，默认 3 个
        
    Returns:
        list: 推荐的资源列表
    """
    import random
    
    recommendations = []
    
    # 高风险用户优先推荐案例类
    if risk_level in ['高风险', '极高风险']:
        if ANTIFRAUD_RESOURCES['case']:
            recommendations.append(random.choice(ANTIFRAUD_RESOURCES['case']))
    
    # 认知维度薄弱推荐视频类
    if weak_dimensions and 'cognitive' in weak_dimensions:
        if ANTIFRAUD_RESOURCES['video']:
            recommendations.append(random.choice(ANTIFRAUD_RESOURCES['video']))
    
    # 行为维度薄弱推荐文章类
    if weak_dimensions and 'behavior' in weak_dimensions:
        if ANTIFRAUD_RESOURCES['article']:
            recommendations.append(random.choice(ANTIFRAUD_RESOURCES['article']))
    
    # 如果推荐数量不足，随机补充
    all_resources = []
    for res_type in ANTIFRAUD_RESOURCES.values():
        all_resources.extend(res_type)
    
    while len(recommendations) < limit and all_resources:
        random_resource = random.choice(all_resources)
        if random_resource not in recommendations:
            recommendations.append(random_resource)
    
    # 转换为 AI 需要的格式
    result = []
    for resource in recommendations[:limit]:
        result.append({
            'title': resource['title'],
            'url': resource['url'],
            'type': _get_resource_type(resource)
        })
    
    return result


def _get_resource_type(resource):
    """根据资源内容判断类型"""
    url = resource.get('url', '')
    if 'bilibili' in url or 'youtube' in url or 'video' in url:
        return 'video'
    elif 'case' in url or '案例' in resource.get('description', ''):
        return 'case'
    else:
        return 'article'


# 如果直接运行此文件，打印所有资源
if __name__ == '__main__':
    print("=" * 60)
    print("反诈教育资源库")
    print("=" * 60)
    
    for res_type, resources in ANTIFRAUD_RESOURCES.items():
        print(f"\n{res_type.upper()} 类资源:")
        for i, resource in enumerate(resources, 1):
            print(f"{i}. {resource['title']}")
            print(f"   链接：{resource['url']}")
            print(f"   说明：{resource['description']}")
            print()
