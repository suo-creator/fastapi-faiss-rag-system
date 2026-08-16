import requests
from bs4 import BeautifulSoup
import time

# 目标政务页面地址
url = "https://dzzf.dezhou.gov.cn/n47250704/n47330598/n50195556/n74200192/n74200389/n74200527/c76691182/content.html"

# 完整浏览器请求头，政务网站必备，防止拦截
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://dzzf.dezhou.gov.cn/"
}

try:
    # 请求页面，超时15秒
    res = requests.get(url, headers=headers, timeout=15)
    # 自动识别网页真实编码，彻底解决中文乱码
    res.encoding = res.apparent_encoding
    res.raise_for_status()  # 捕获404/403报错

    soup = BeautifulSoup(res.text, "html.parser")

    # 1. 提取文章标题
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "德州中燃工作规则"

    # 2. 提取正文（政务网正文一般在content/main类容器）
    # 先尝试精准定位正文容器
    content_box = soup.find(class_="content") or soup.find(class_="main") or soup.find("div", id="content")
    if content_box:
        # 清理广告、脚本、无用标签
        for tag in content_box(["script", "style", "iframe", "a"]):
            tag.decompose()
        full_text = content_box.get_text(strip=True, separator="\n\n")
        full_text = full_text.replace("\xa0", " ")
    else:
        # 兜底方案：提取页面全部有效文字
        for tag in soup(["script", "style", "header", "footer", "aside"]):
            tag.decompose()
        full_text = soup.get_text(strip=True, separator="\n\n")
        full_text = full_text.replace("\xa0", " ")

    # 拼接标题+正文
    final_content = f"【{title}】\n发布页面：{url}\n\n{full_text}"

    # 保存为txt文件（utf-8编码，打开不乱码）
    with open("德州中燃城市燃气发展有限公司工作规则.txt", "w", encoding="utf-8") as f:
        f.write(final_content)

    print("✅ 爬取完成！文件已保存到当前文件夹")
    print("\n=== 预览前500字 ===")
    print(full_text[:500])

except requests.exceptions.HTTPError as e:
    print(f"❌ 网页访问失败，状态码异常：{e}")
except Exception as e:
    print(f"❌ 程序出错：{e}")

# 礼貌延时，避免频繁访问服务器
time.sleep(1)
