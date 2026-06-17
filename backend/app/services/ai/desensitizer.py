import re


SECURITY_CATEGORIES = {
    "WAF/API 日常巡检": ["waf", "api", "巡检", "设备", "服务状态", "资源占用"],
    "WAF 告警监测": ["waf", "告警", "攻击", "拦截", "源ip", "top"],
    "蜜罐告警监测": ["蜜罐", "探针", "攻击源", "攻击行为"],
    "告警分析与上报": ["告警", "研判", "误报", "上报", "态势同步"],
    "安全事件排查": ["sql注入", "目录穿越", "扫描", "信息泄露", "弱口令", "应急"],
    "重保/攻防演练": ["重保", "攻防", "演练", "值守", "复盘"],
    "站点接入与变更": ["站点", "端口", "证书", "网络测试", "连通性"],
    "策略优化": ["策略", "规则", "拦截模式", "优化"],
    "工单处理": ["工单", "天眼", "态势", "闭环"],
    "自动化与报表": ["周报", "报表", "excel", "脚本", "自动化"],
    "会议与沟通": ["会议", "沟通", "方案", "对接"],
    "加班与值守": ["加班", "值守", "夜间", "周末"],
}

NORMALIZATION_MAP = {
    "看了一下 WAF 告警": "WAF 告警监测及分析",
    "看了一下waf告警": "WAF 告警监测及分析",
    "查了蜜罐日志": "蜜罐告警日志分析",
    "处理天眼单子": "态势感知平台工单处理",
    "跟业务打网": "网络连通性测试",
    "加站点": "站点接入配置",
    "换证书": "证书替换及配置验证",
    "开拦截": "WAF 拦截策略调整",
    "写周报": "安全运营周报编写与输出",
}


def normalize_security_terms(text: str) -> str:
    result = text
    for source, target in NORMALIZATION_MAP.items():
        result = result.replace(source, target)
    return result


def classify_security_work(text: str) -> str:
    normalized = text.lower()
    for category, keywords in SECURITY_CATEGORIES.items():
        if any(keyword.lower() in normalized for keyword in keywords):
            return category
    return "其他工作"


def desensitize_text(text: str) -> str:
    if not text:
        return text
    result = text
    result = re.sub(r"\b10\.(?:\d{1,3}\.){2}\d{1,3}\b", "10.x.x.x", result)
    result = re.sub(r"\b172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}\b", "172.x.x.x", result)
    result = re.sub(r"\b192\.168\.\d{1,3}\.\d{1,3}\b", "192.168.x.x", result)
    result = re.sub(r"\b(?!(?:10|172|192)\.)\d{1,3}(?:\.\d{1,3}){3}\b", "x.x.x.x", result)
    result = re.sub(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b", "某业务域名", result)
    result = re.sub(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?[\w\-\.]{8,}", r"\1=[已脱敏]", result)
    result = re.sub(r"(?i)(password|passwd|pwd|密码)\s*[:=：]\s*['\"]?[^,\s，。;；]+", r"\1=[密码已脱敏]", result)
    result = re.sub(r"(?i)(账号|account|username|user)\s*[:=：]\s*['\"]?[^,\s，。;；]+", r"\1=[账号已脱敏]", result)
    result = re.sub(r"[\u4e00-\u9fa5]{2,3}(?=(同事|接口人|老师|经理|主任|负责人))", "某接口人", result)
    result = re.sub(r"[\u4e00-\u9fa5A-Za-z0-9_-]{2,30}系统", "某系统", result)
    return result


def preview_desensitization(text: str) -> dict[str, str]:
    return {"before": text, "after": desensitize_text(text)}
