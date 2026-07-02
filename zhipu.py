"""智谱 AI (GLM) API — 对话/内容生成"""
import requests, json

API_KEY = "1051f7ec541643f9b35398dfcab333a3.N5lLd3mzeGsKolIM"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def chat(prompt, model="glm-4-flash", system="你是 XFieldMate 草坪养护专家，回答专业简洁。"):
    """调用智谱 GLM 对话"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    try:
        r = requests.post(API_URL, headers=headers, json=data, timeout=30)
        result = r.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"[智谱AI] 调用失败: {str(e)[:100]}"

def generate_article(topic, style="专业"):
    """智谱生成文章"""
    prompt = f"请以{style}风格写一篇草坪养护技术文章，主题：{topic}。要求500字以上，分段，实用性强。"
    return chat(prompt)

def diagnose(prompt):
    """智谱诊断草坪问题"""
    return chat(prompt, system="你是草坪病虫害诊断专家。请分析用户描述的草坪症状，给出：1)可能的病害/虫害/杂草名称 2)诊断依据 3)防治建议 4)预防措施。用中文回答。")
