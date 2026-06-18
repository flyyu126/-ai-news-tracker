"""
翻译模块 - 百度翻译 API 封装
功能：调用百度翻译 API 将英文标题/摘要翻译为中文
注意：使用前需在百度翻译开放平台 (https://fanyi-api.baidu.com/) 申请 AppID 和密钥
      免费版每月有 100 万字符额度
"""

import hashlib
import json
import random
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# 缓存已翻译结果，避免重复调用 API
_translation_cache = {}


def baidu_translate(text, appid, secret_key, from_lang="en", to_lang="zh"):
    """
    百度翻译 API 调用函数
    参数：
        text: 待翻译文本
        appid: 百度翻译应用 ID
        secret_key: 百度翻译密钥
        from_lang: 源语言（默认 en）
        to_lang: 目标语言（默认 zh）
    返回：
        翻译后的文本，失败时返回原文
    """
    if not text or not text.strip():
        return text

    # 检查缓存
    cache_key = f"{text}_{from_lang}_{to_lang}"
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]

    # 如果内容以中文为主(超过30%是中文字符)，直接返回原文
    chinese_chars = sum(1 for c in text if '一' <= c <= '鿿')
    if chinese_chars > len(text) * 0.3:
        _translation_cache[cache_key] = text
        return text

    # 如果文本很短且看起来已经是中文，直接返回
    if len(text) < 5 and chinese_chars > 0:
        _translation_cache[cache_key] = text
        return text

    try:
        salt = str(random.randint(32768, 65536))
        sign_str = appid + text + salt + secret_key
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

        params = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appid': appid,
            'salt': salt,
            'sign': sign,
        }

        url = 'https://fanyi-api.baidu.com/api/trans/vip/translate?' + urlencode(params)
        req = Request(url, headers={'User-Agent': 'AI-News-Tracker/1.0'})

        with urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if 'trans_result' in result:
                translated = ''.join(item['dst'] for item in result['trans_result'])
                _translation_cache[cache_key] = translated
                time.sleep(0.3)  # 控制请求频率（免费版限制）
                return translated
            else:
                print(f"翻译失败: {result.get('error_msg', '未知错误')}")
                return text
    except Exception as e:
        print(f"翻译异常: {e}")
        return text


def batch_translate(items, text_field, appid, secret_key, from_lang="en", to_lang="zh"):
    """
    批量翻译函数 - 对列表中的每个对象翻译指定字段
    参数：
        items: 对象列表
        text_field: 要翻译的字段名
        appid: 百度翻译 AppID
        secret_key: 百度翻译密钥
    返回：
        翻译后的对象列表（新增 xxx_cn 字段存储中文）
    """
    result_field = f"{text_field}_cn"
    for item in items:
        original_text = item.get(text_field, "")
        if original_text:
            item[result_field] = baidu_translate(
                original_text, appid, secret_key, from_lang, to_lang
            )
        else:
            item[result_field] = ""
    return items


if __name__ == "__main__":
    # 测试翻译功能
    test_text = "Artificial intelligence is transforming the world."
    print(f"原文: {test_text}")
    # 注意：需要设置环境变量 BAIDU_APPID 和 BAIDU_SECRET_KEY
    import os
    appid = os.environ.get("BAIDU_APPID", "")
    secret = os.environ.get("BAIDU_SECRET_KEY", "")
    if appid and secret:
        result = baidu_translate(test_text, appid, secret)
        print(f"译文: {result}")
    else:
        print("请设置 BAIDU_APPID 和 BAIDU_SECRET_KEY 环境变量后再测试")
