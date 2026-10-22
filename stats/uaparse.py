"""从 User-Agent 和前端上报的触屏点数判断设备类型、系统和浏览器。只保留这三个结果，不保存原始 UA。"""
import re

BOT = re.compile(r"bot|spider|crawl|slurp|headless|lighthouse|curl|wget|python-|go-http|java/|okhttp|httpclient|preview|monitor", re.I)


def is_bot(ua: str) -> bool:
    return not ua or bool(BOT.search(ua))


def parse(ua: str, touch: int = 0):
    ua = ua or ""
    # iPadOS 13 以后 Safari 默认伪装成 Mac，靠触屏点数区分
    if "iPad" in ua or ("Macintosh" in ua and touch and touch > 1):
        dtype, os_ = "iPad", "iPadOS"
    elif "iPhone" in ua or "iPod" in ua:
        dtype, os_ = "手机", "iOS"
    elif "Android" in ua:
        dtype = "手机" if "Mobile" in ua else "平板"
        os_ = "Android"
    elif "HarmonyOS" in ua or "OpenHarmony" in ua:
        dtype, os_ = ("手机" if "Mobile" in ua else "平板"), "HarmonyOS"
    elif "Windows" in ua:
        dtype, os_ = "电脑", "Windows"
    elif "Macintosh" in ua or "Mac OS X" in ua:
        dtype, os_ = "电脑", "macOS"
    elif "CrOS" in ua:
        dtype, os_ = "电脑", "ChromeOS"
    elif "Linux" in ua:
        dtype, os_ = "电脑", "Linux"
    else:
        dtype, os_ = "其他", "其他"

    rules = [
        ("MicroMessenger", "微信"), ("QQBrowser|MQQBrowser", "QQ浏览器"), (r"\bQQ/", "QQ"),
        ("Quark", "夸克"), ("UCBrowser|UCWEB", "UC"), ("baiduboxapp|BaiduHD", "百度"),
        ("DingTalk", "钉钉"), ("Weibo", "微博"), ("XiaoHongShu|xhsdiscover", "小红书"),
        ("bilibili", "哔哩哔哩"), ("HuaweiBrowser", "华为浏览器"), ("MiuiBrowser|XiaoMi", "小米浏览器"),
        ("EdgiOS|EdgA|Edg/", "Edge"), ("FxiOS|Firefox/", "Firefox"), ("CriOS|Chrome/", "Chrome"),
        ("Safari/", "Safari"),
    ]
    browser = "其他"
    for pat, name in rules:
        if re.search(pat, ua):
            browser = name
            break
    return dtype, os_, browser
