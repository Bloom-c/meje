import streamlit as st
import requests
import json
from openai import OpenAI
import pandas as pd
import time
import re
import os
from datetime import datetime
import hashlib
from difflib import SequenceMatcher

# ===== 页面配置 =====
st.set_page_config(
    page_title="觅镜 Meje - 智能商业发现引擎",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ===== 自定义CSS（省略，和之前一样） =====
# ============================================================
st.markdown("""
<style>
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e8edf5 100%); }
    .main { padding: 0 1.5rem; }
    .navbar {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255,255,255,0.3);
        padding: 12px 32px;
        margin: -16px -16px 24px -16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .nav-brand { display: flex; align-items: center; gap: 12px; }
    .nav-logo {
        width: 40px; height: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: 700; color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35);
    }
    .nav-title {
        font-size: 22px; font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    .nav-sub { font-size: 13px; font-weight: 400; color: #7c8ba0; -webkit-text-fill-color: #7c8ba0; margin-left: 4px; }
    .nav-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; font-size: 10px; font-weight: 600;
        padding: 2px 10px; border-radius: 20px;
        letter-spacing: 0.5px; text-transform: uppercase;
    }
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px; padding: 28px 36px; margin-bottom: 24px;
        color: white; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.30);
        position: relative; overflow: hidden;
    }
    .hero::before {
        content: ''; position: absolute; top: -50%; right: -20%;
        width: 400px; height: 400px; background: rgba(255,255,255,0.08); border-radius: 50%;
    }
    .hero::after {
        content: ''; position: absolute; bottom: -40%; left: -10%;
        width: 300px; height: 300px; background: rgba(255,255,255,0.05); border-radius: 50%;
    }
    .hero-content { position: relative; z-index: 1; }
    .hero-title { font-size: 26px; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
    .hero-desc { font-size: 15px; opacity: 0.9; margin: 6px 0 0 0; font-weight: 400; }
    .hero-tags { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
    .hero-tag {
        background: rgba(255,255,255,0.20); backdrop-filter: blur(10px);
        padding: 4px 14px; border-radius: 20px; font-size: 12px;
        font-weight: 500; border: 1px solid rgba(255,255,255,0.15);
    }
    .card-glass {
        background: rgba(255,255,255,0.75); backdrop-filter: blur(12px);
        border-radius: 16px; padding: 20px 24px;
        border: 1px solid rgba(255,255,255,0.5);
        box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    .card-glass:hover { box-shadow: 0 8px 30px rgba(0,0,0,0.08); border-color: rgba(102, 126, 234, 0.2); }
    .card-title { font-size: 16px; font-weight: 600; color: #1a2332; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 14px; margin: 14px 0; }
    .stat-item-glass {
        background: rgba(255,255,255,0.6); backdrop-filter: blur(8px);
        border-radius: 14px; padding: 16px 18px; text-align: center;
        border: 1px solid rgba(255,255,255,0.5); transition: all 0.3s ease;
    }
    .stat-item-glass:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
    .stat-number {
        font-size: 28px; font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .stat-label { font-size: 13px; color: #7c8ba0; margin-top: 4px; font-weight: 500; }
    .company-card-glass {
        background: rgba(255,255,255,0.8); backdrop-filter: blur(12px);
        border-radius: 14px; padding: 16px 20px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.5); transition: all 0.3s ease; cursor: default;
    }
    .company-card-glass:hover { border-color: #667eea; box-shadow: 0 4px 20px rgba(102, 126, 234, 0.12); transform: translateX(4px); }
    .company-name { font-size: 17px; font-weight: 700; color: #1a2332; }
    .company-score {
        font-size: 24px; font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .priority-badge { font-size: 11px; font-weight: 600; padding: 3px 14px; border-radius: 20px; display: inline-block; letter-spacing: 0.3px; }
    .priority-high { background: #e8f5e9; color: #2e7d32; }
    .priority-mid { background: #fff3e0; color: #e65100; }
    .priority-low { background: #fbe9e7; color: #c62828; }
    .tag-glass {
        display: inline-block; font-size: 12px; font-weight: 500;
        padding: 2px 12px; border-radius: 12px; margin: 2px 4px 2px 0;
        background: rgba(102, 126, 234, 0.10); color: #667eea;
        border: 1px solid rgba(102, 126, 234, 0.08);
    }
    .stButton > button { border-radius: 10px !important; font-weight: 600 !important; transition: all 0.3s ease !important; border: none !important; }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important; box-shadow: 0 4px 16px rgba(102, 126, 234, 0.30) !important;
    }
    .stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 28px rgba(102, 126, 234, 0.40) !important; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px; background: rgba(255,255,255,0.5); backdrop-filter: blur(8px);
        border-radius: 14px; padding: 4px; border: 1px solid rgba(255,255,255,0.3);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important; padding: 8px 22px !important;
        font-weight: 500 !important; color: #7c8ba0 !important;
        transition: all 0.3s ease !important; cursor: pointer !important;
    }
    .stTabs [aria-selected="true"] { background: white !important; color: #667eea !important; box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important; }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 10px !important; border: 1px solid #e8ecf0 !important;
        transition: all 0.3s ease !important; background: rgba(255,255,255,0.7) !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important; background: white !important;
    }
    .legal-footer {
        background: rgba(255,255,255,0.6); backdrop-filter: blur(8px);
        border-radius: 16px; padding: 20px 24px 16px 24px; margin-top: 32px;
        border: 1px solid rgba(255,255,255,0.3); font-size: 12px; color: #9aa0a6; line-height: 1.8;
    }
    .legal-footer strong { color: #7c8ba0; font-weight: 600; }
    .legal-footer a { color: #667eea; text-decoration: none; }
    .legal-footer a:hover { text-decoration: underline; }
    @media (max-width: 768px) {
        .navbar { padding: 10px 16px; flex-direction: column; align-items: flex-start; }
        .hero { padding: 20px 18px; }
        .hero-title { font-size: 20px; }
        .stat-grid { grid-template-columns: repeat(2, 1fr); }
        .company-card-glass { padding: 12px 14px; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# ===== 配置 =====
# ============================================================
import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

MONITOR_FILE = "monitor_data.json"
HISTORY_FILE = "monitor_history.json"

# ============================================================
# ===== 工具函数 =====
# ============================================================
def is_similar(name1, name2, threshold=0.8):
    if name1 == name2:
        return True
    suffixes = ["公司", "集团", "有限", "科技", "技术", "股份", "网络", "信息", "智能", "软件", "服务", "平台"]
    clean1, clean2 = name1, name2
    for s in suffixes:
        clean1 = clean1.replace(s, "")
        clean2 = clean2.replace(s, "")
    if clean1 == clean2:
        return True
    return SequenceMatcher(None, name1, name2).ratio() >= threshold

def parse_user_need(need_description, mode="销售"):
    mode_prompt = "重点关注：目标客户行业、规模、决策者、采购信号" if mode == "销售" else "重点关注：目标公司行业、规模、技术栈、文化氛围"
    prompt = f"""
分析以下用户需求，提取关键信息并生成精准搜索词。
用户需求：{need_description}
场景：{mode}模式
{mode_prompt}

输出JSON：{{"industry":"行业","keywords":["关键词"],"search_terms":["搜索词"],"tech_stack":[],"target_scale":"规模","signal_keywords":[]}}
"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": "你是需求分析专家。"}, {"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        result = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"industry": "科技", "keywords": [], "search_terms": []}
    except:
        return {"industry": "科技", "keywords": [], "search_terms": []}

def extract_company_name(title, snippet):
    patterns = [
        r'(.+?)(公司|集团|有限|科技|技术|股份|网络|信息|智能|软件|服务|平台|电商|医疗|教育|金融|能源)',
        r'「(.+?)」', r'《(.+?)》', r'【(.+?)】', r'(.+?)的', r'(.+?)：', r'(.+?) -', r'(.+?) 招聘', r'(.+?) 融资'
    ]
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            name = re.sub(r'^[0-9、.()（）：:]+', '', match.group(1).strip())
            if 2 < len(name) < 30:
                return name
    if len(title) > 3:
        name = title[:8].strip()
        return name if len(name) > 2 else None
    return None

# ============================================================
# ===== 搜索（通过 SerpApi 百度引擎） =====
# ============================================================
def search_from_serpapi(search_terms, industry, limit=10):
    all_companies = []
    seen_names = set()
    
    if not search_terms:
        search_terms = [f"{industry} 公司"]
    
    expanded_terms = []
    for term in search_terms[:4]:
        expanded_terms.extend([term, f"{term} 融资", f"{term} 招聘", f"{term} 简介"])
    expanded_terms = list(set(expanded_terms))[:6]
    
    for search_term in expanded_terms:
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": search_term,
                "api_key": SERPAPI_KEY,
                "source": "baidu",
                "num": limit
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                for item in result.get("organic_results", []):
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    link = item.get("link", "")
                    
                    name = extract_company_name(title, snippet)
                    if name and 2 < len(name) < 50:
                        dup = False
                        for existing in seen_names:
                            if is_similar(name, existing):
                                dup = True
                                break
                        if not dup:
                            seen_names.add(name)
                            all_companies.append({
                                "name": name,
                                "title": title,
                                "snippet": snippet,
                                "link": link,
                                "source": "百度搜索"
                            })
            else:
                st.warning(f"SerpApi百度搜索失败: {response.status_code}")
                
        except Exception as e:
            st.error(f"搜索异常: {str(e)}")
            continue
        
        time.sleep(0.3)
    
    return all_companies

# ============================================================
# ===== 获取公司详情（通过 SerpApi 百度引擎） =====
# ============================================================
def get_company_details(company_name, mode="销售"):
    details = {"name": company_name, "description": "", "financing": "暂无公开融资信息", "news": [], "jobs": [], "founder": "", "founded": ""}
    
    try:
        url = "https://serpapi.com/search"
        params = {
            "q": f"{company_name} 公司 简介 融资 招聘 创始人",
            "api_key": SERPAPI_KEY,
            "source": "baidu",
            "num": 15
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            for item in result.get("organic_results", []):
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                
                if "百科" in title or "baike" in link:
                    details["description"] = snippet[:500]
                elif "融资" in title or "投资" in title:
                    details["financing"] = snippet[:400]
                elif "招聘" in title or "岗位" in title:
                    details["jobs"].append({"title": title})
                elif "新闻" in title or "报道" in title:
                    details["news"].append({"title": title})
                
                if not details["description"] and len(snippet) > 30:
                    details["description"] = snippet[:400]
                
                fm = re.search(r'创始人[：:]\s*([^，,。\s]{2,6})', snippet)
                if fm and not details["founder"]:
                    details["founder"] = fm.group(1)
                fd = re.search(r'成立于?\s*([0-9]{4})', snippet)
                if fd and not details["founded"]:
                    details["founded"] = fd.group(1) + "年"
    except:
        pass
    
    return details

# ============================================================
# ===== AI 打分 =====
# ============================================================
def score_company(company_name, need_analysis, company_details, mode="销售"):
    dim = "1.业务匹配度(30%) 2.需求信号(25%) 3.决策可及性(25%) 4.时效性(20%)" if mode == "销售" else "1.岗位匹配度(30%) 2.发展前景(25%) 3.文化匹配(25%) 4.可入职性(20%)"
    prompt = f"评估匹配度(0-100)。场景:{mode} 需求:{json.dumps(need_analysis)} 公司:{company_name} 描述:{company_details.get('description','')} 融资:{company_details.get('financing','')} 创始人:{company_details.get('founder','')} 成立:{company_details.get('founded','')} 维度:{dim} 输出JSON:{{'total_score':0-100,'match_score':0-100,'signal_score':0-100,'priority':'高/中/低','reason':'理由','action':'建议'}}"
    try:
        resp = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": "你是专业评估专家。"}, {"role": "user", "content": prompt}], temperature=0.3, max_tokens=600)
        result = resp.choices[0].message.content
        jm = re.search(r'\{.*\}', result, re.DOTALL)
        return json.loads(jm.group()) if jm else {"total_score": 50, "priority": "中", "reason": "分析完成"}
    except:
        return {"total_score": 50, "priority": "中", "reason": "分析中"}

# ============================================================
# ===== 搜索主函数 =====
# ============================================================
def search_companies(search_terms, industry, keywords, limit=10):
    all_companies = search_from_serpapi(search_terms, industry, limit)
    
    if keywords:
        for kw in keywords[:2]:
            extra_results = search_from_serpapi([f"{kw} 招聘"], industry, limit//2)
            for comp in extra_results:
                if comp['name'] not in [c['name'] for c in all_companies]:
                    all_companies.append(comp)
            
            fin_results = search_from_serpapi([f"{kw} 融资"], industry, limit//2)
            for comp in fin_results:
                if comp['name'] not in [c['name'] for c in all_companies]:
                    all_companies.append(comp)
    
    return all_companies

def quick_search(need_description, mode="销售"):
    results = []
    status = st.status("🔍 正在搜索...", expanded=True)
    
    status.write("🤔 分析需求...")
    need_data = parse_user_need(need_description, mode)
    if not need_data.get('search_terms'):
        need_data['search_terms'] = [f"{need_data.get('industry', '科技')} 公司"]
    
    status.write("📡 SerpApi百度搜索中...")
    companies = search_companies(need_data.get('search_terms', []), need_data.get('industry', '科技'), need_data.get('keywords', []), 10)
    
    if not companies:
        status.update(label="❌ 未找到结果", state="error")
        return pd.DataFrame()
    
    status.write(f"✅ 找到 {len(companies)} 家公司，正在分析...")
    
    for idx, company in enumerate(companies[:25]):
        status.write(f"📋 分析 {company['name']} ({idx+1}/{min(len(companies), 25)})")
        details = get_company_details(company['name'], mode)
        score_data = score_company(company['name'], need_data, details, mode)
        results.append({
            "公司名称": company['name'],
            "综合评分": score_data.get('total_score', 50),
            "匹配度": score_data.get('match_score', 50),
            "优先级": score_data.get('priority', '中'),
            "理由": score_data.get('reason', ''),
            "建议动作": score_data.get('action', ''),
            "创始人": details.get('founder', ''),
            "成立时间": details.get('founded', ''),
            "融资动态": details.get('financing', '暂无')[:100],
            "招聘数": len(details.get('jobs', [])),
            "数据来源": company.get('source', '百度搜索')
        })
        time.sleep(0.15)
    
    status.update(label=f"✅ 完成！共 {len(results)} 家公司", state="complete")
    return pd.DataFrame(results)

# ============================================================
# ===== 企业深度分析 =====
# ============================================================
def analyze_company(company_name):
    details = get_company_details(company_name)
    prompt = f"""对{company_name}深度分析：
描述:{details.get('description','暂无')} 创始人:{details.get('founder','暂无')} 成立:{details.get('founded','暂无')} 融资:{details.get('financing','暂无')}
按格式输出：
## 📌 企业概况
## 🚀 最新运营方向
## 🤝 适合合作的方向
## 👨‍💻 适合就职的人才
## 💡 一句话建议"""
    try:
        resp = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "system", "content": "你是资深商业分析师。"}, {"role": "user", "content": prompt}], temperature=0.4, max_tokens=1500)
        return resp.choices[0].message.content
    except Exception as e:
        return f"分析失败: {str(e)}"

# ============================================================
# ===== 监控函数 =====
# ============================================================
def load_monitor_data():
    if os.path.exists(MONITOR_FILE):
        with open(MONITOR_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"monitors": []}

def save_monitor_data(data):
    with open(MONITOR_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"detected": [], "seen_companies": []}

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def detect_signals(company_name, company_details):
    signals = []
    if "融资" in company_details.get('financing', ''):
        signals.append({"type": "💰 融资", "company": company_name, "detail": company_details.get('financing', '')[:200]})
    if company_details.get('jobs'):
        for job in company_details.get('jobs', [])[:2]:
            signals.append({"type": "💼 招聘", "company": company_name, "detail": job.get('title', '')[:100]})
    return signals

def run_monitor(monitor_config):
    need_desc = monitor_config.get('need_description', '')
    mode = monitor_config.get('mode', '销售')
    need_data = parse_user_need(need_desc, mode)
    companies = search_companies(need_data.get('search_terms', []), need_data.get('industry', '科技'), need_data.get('keywords', []), 6)
    if not companies:
        return []
    history = load_history()
    seen = set(history.get('seen_companies', []))
    all_signals = []
    for company in companies[:15]:
        name = company['name']
        is_new = name not in seen
        details = get_company_details(name, mode)
        for s in detect_signals(name, details):
            s['is_new'] = is_new
            s['timestamp'] = datetime.now().isoformat()
            all_signals.append(s)
        if is_new:
            seen.add(name)
    history['seen_companies'] = list(seen)
    new_signals = [s for s in all_signals if s.get('is_new', False)]
    if new_signals:
        history['detected'].extend(new_signals)
        save_history(history)
    return new_signals

# ============================================================
# ===== 主界面 =====
# ============================================================

if 'main_input' not in st.session_state:
    st.session_state.main_input = ""

st.markdown("""
<div class="navbar">
    <div class="nav-brand">
        <div class="nav-logo">觅</div>
        <div>
            <span class="nav-title">觅镜</span>
            <span class="nav-sub">Meje</span>
        </div>
        <span class="nav-badge">v3.0</span>
    </div>
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
        <span style="font-size:13px;color:#7c8ba0;font-weight:500;">🔍 SerpApi百度搜索</span>
        <span style="font-size:13px;color:#7c8ba0;font-weight:500;">💼 招聘</span>
        <span style="font-size:13px;color:#7c8ba0;font-weight:500;">💰 融资</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-content">
        <div class="hero-title">🔍 觅镜 · 智能商业发现</div>
        <div class="hero-desc">输入你的需求，AI 自动筛选并排序最适合你的潜在客户或雇主</div>
        <div class="hero-tags">
            <span class="hero-tag">🎯 销售模式</span>
            <span class="hero-tag">🎓 求职模式</span>
            <span class="hero-tag">📡 持续监控</span>
            <span class="hero-tag">🏢 企业分析</span>
            <span class="hero-tag">🤖 AI 写需求</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tab_main, tab_company, tab_monitor = st.tabs(["🎯 发现引擎", "🏢 企业深度分析", "📡 持续监控"])

# ============================================================
# TAB 1: 发现引擎
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col_mode1, col_mode2 = st.columns(2)
    with col_mode1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales_card"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col_mode2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job_card"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    
    if mode_key == "销售":
        st.markdown("""
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:12px 24px;border-radius:12px;font-weight:700;font-size:18px;text-align:center;box-shadow:0 4px 20px rgba(102,126,234,0.35);margin:8px 0 12px 0;">
            ✅ 当前模式：💼 销售模式 — 正在寻找潜在客户
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:12px 24px;border-radius:12px;font-weight:700;font-size:18px;text-align:center;box-shadow:0 4px 20px rgba(102,126,234,0.35);margin:8px 0 12px 0;">
            ✅ 当前模式：🎓 求职模式 — 正在寻找理想雇主
        </div>
        """, unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.markdown("""
        <div style="background: #f0f4ff; padding: 12px 16px; border-radius: 10px; margin-bottom: 12px; font-size: 14px; color: #1a2332;">
            💡 简单描述你的业务情况，AI 会自动生成一段专业完整的需求描述，直接填入上方输入框。
        </div>
        """, unsafe_allow_html=True)
        
        if mode_key == "销售":
            st.markdown("##### 📝 简单描述你的业务")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                product = st.text_input("你卖什么产品/服务", placeholder="例如：AI客服系统", key="ai_product")
                target_industry = st.text_input("目标客户行业", placeholder="例如：电商、零售", key="ai_industry")
            with col_s2:
                target_size = st.text_input("目标客户规模", placeholder="例如：500人以上", key="ai_size")
                pain_point = st.text_input("客户痛点", placeholder="例如：客服响应慢、成本高", key="ai_pain")
            extra_info = st.text_area("补充信息（可选）", placeholder="例如：最近有融资的优先、有客服团队的优先", key="ai_extra", height=50)
        else:
            st.markdown("##### 📝 简单描述你的求职情况")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                skill = st.text_input("你的核心技能", placeholder="例如：前端开发", key="ai_skill")
                tech_stack = st.text_input("技术栈", placeholder="例如：React、TypeScript", key="ai_tech")
            with col_s2:
                target_industry_job = st.text_input("目标行业", placeholder="例如：互联网、金融科技", key="ai_industry_job")
                job_level = st.text_input("目标职级", placeholder="例如：中级、高级", key="ai_job_level")
            extra_info_job = st.text_area("补充信息（可选）", placeholder="例如：希望公司已盈利、有良好的技术氛围", key="ai_extra_job", height=50)
        
        if st.button("🚀 生成需求描述", key="generate_need_btn", use_container_width=True):
            if mode_key == "销售":
                user_input = f"""
产品/服务：{product or '未填写'}
目标行业：{target_industry or '未填写'}
目标规模：{target_size or '未填写'}
客户痛点：{pain_point or '未填写'}
补充信息：{extra_info or '无'}
"""
                gen_prompt = f"""
你是一位资深的商业需求分析师。请根据用户提供的信息，生成一段专业、完整、可直接使用的需求描述。

用户信息：
{user_input}

要求：
1. 用流畅的段落文字描述，200字左右
2. 包含：我销售什么产品、目标客户是谁、客户有什么特征、什么信号表示客户有需求
3. 风格专业、简洁、有说服力
4. 直接输出需求描述，不要有其他内容
"""
            else:
                user_input = f"""
核心技能：{skill or '未填写'}
技术栈：{tech_stack or '未填写'}
目标行业：{target_industry_job or '未填写'}
目标职级：{job_level or '未填写'}
补充信息：{extra_info_job or '无'}
"""
                gen_prompt = f"""
你是一位资深的职业规划师。请根据用户提供的信息，生成一段专业、完整、可直接使用的求职需求描述。

用户信息：
{user_input}

要求：
1. 用流畅的段落文字描述，200字左右
2. 包含：我的核心技能是什么、想找什么行业/类型的公司、理想公司的特征、什么信号表示公司值得去
3. 风格专业、简洁、有说服力
4. 直接输出需求描述，不要有其他内容
"""
            
            with st.spinner("🤖 AI 正在生成需求描述..."):
                try:
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "你是专业的文案生成助手，擅长将零散信息整合成流畅的专业描述。"},
                            {"role": "user", "content": gen_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = response.choices[0].message.content
                    
                    st.markdown("##### ✅ 生成的需求描述：")
                    st.markdown(f"""
                    <div style="
                        background: white;
                        border-radius: 10px;
                        padding: 16px 20px;
                        border: 2px solid #667eea;
                        margin: 8px 0 12px 0;
                        line-height: 1.8;
                        color: #1a2332;
                    ">
                        {generated_text}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📥 一键填入输入框", key="fill_need_btn", use_container_width=True):
                        # 直接写入 session_state
                        st.session_state.main_input = generated_text
                        st.session_state.fill_done = True
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    need_description = st.text_area(
        "📝 描述你的需求",
        height=100,
        placeholder="示例（销售模式）：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="main_input",
        value=st.session_state.main_input
    )
    
    # 显示填入成功提示
    if st.session_state.get('fill_done', False):
        st.success("✅ 已填入输入框！")
        st.session_state.fill_done = False
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        if not need_description:
            st.error("⚠️ 请先输入需求描述，或使用「AI 帮我写需求」功能生成")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                st.markdown(f"""
                <div class="stat-grid">
                    <div class="stat-item-glass"><div class="stat-number">{len(result_df)}</div><div class="stat-label">🏢 公司总数</div></div>
                    <div class="stat-item-glass"><div class="stat-number">{len(result_df[result_df['优先级'].str.contains('高')])}</div><div class="stat-label">🔥 高优先级</div></div>
                    <div class="stat-item-glass"><div class="stat-number">{int(result_df['综合评分'].mean())}</div><div class="stat-label">📊 平均评分</div></div>
                    <div class="stat-item-glass"><div class="stat-number">{len(result_df['数据来源'].unique())}</div><div class="stat-label">📡 数据源</div></div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card-glass">
                        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                            <div>
                                <span class="company-name">{row['公司名称']}</span>
                                <span class="priority-badge {p_class}" style="margin-left:10px;">{p_label}</span>
                            </div>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:13px;color:#7c8ba0;">评分</span>
                                <span class="company-score">{score}</span>
                            </div>
                        </div>
                        <div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag-glass">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag-glass">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag-glass">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag-glass">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag-glass">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:8px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="margin-top:4px;font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_发现结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)

# ============================================================
# TAB 2: 企业深度分析
# ============================================================
with tab_company:
    st.markdown("""
    <div class="card-glass">
        <div class="card-title">🏢 企业深度分析</div>
        <p style="color:#7c8ba0;margin:0;">输入企业名称，AI 自动分析其运营方向、合作机会和人才需求</p>
    </div>
    """, unsafe_allow_html=True)
    
    company_input = st.text_input(
        "企业名称",
        placeholder="例如：字节跳动、宁德时代、比亚迪、深信服",
        key="company_input"
    )
    
    if st.button("📊 开始分析", use_container_width=True, type="primary"):
        if not company_input:
            st.error("⚠️ 请输入企业名称")
        else:
            with st.spinner(f"🔍 正在深度分析 {company_input}..."):
                result = analyze_company(company_input)
                st.markdown("---")
                st.markdown(f"### 🏢 {company_input} 深度分析报告")
                st.markdown("---")
                st.markdown(result)
                st.markdown("---")
                st.caption("📌 基于公开信息 · 仅供参考 · 数据来源：SerpApi百度搜索")
                
                report = f"===== 觅镜 · {company_input} 深度分析报告 =====\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{result}\n\n===== 数据来源 =====\nSerpApi百度搜索"
                st.download_button("📥 下载报告 (TXT)", data=report.encode('utf-8'), file_name=f"{company_input}_分析报告.txt", mime="text/plain", use_container_width=True)

# ============================================================
# TAB 3: 持续监控
# ============================================================
with tab_monitor:
    st.markdown("""
    <div class="card-glass">
        <div class="card-title">📡 持续监控</div>
        <p style="color:#7c8ba0;margin:0;">设置监控条件，系统自动追踪目标公司的融资、招聘、新闻等信号</p>
    </div>
    """, unsafe_allow_html=True)
    
    monitor_data = load_monitor_data()
    tm1, tm2, tm3 = st.tabs(["🔔 信号看板", "➕ 创建监控", "📋 历史记录"])
    
    with tm2:
        m_name = st.text_input("监控名称", placeholder=f"监控-{datetime.now().strftime('%Y%m%d')}")
        m_need = st.text_area("描述目标客户/雇主画像", height=90, placeholder="例如：我销售AI客服系统，目标客户是电商和零售公司...", key="monitor_input")
        if st.button("🚀 创建监控任务", use_container_width=True, type="primary"):
            if not m_need:
                st.error("⚠️ 请先输入需求描述")
            else:
                nm = {"id": hashlib.md5(f"{m_need}{time.time()}".encode()).hexdigest()[:8], "name": m_name or f"监控-{datetime.now().strftime('%Y%m%d')}", "mode": "销售", "need_description": m_need, "created_at": datetime.now().isoformat(), "status": "active"}
                monitor_data['monitors'].append(nm)
                save_monitor_data(monitor_data)
                st.success("✅ 监控创建成功！")
                with st.spinner("🔄 首次扫描中..."):
                    results = run_monitor(nm)
                st.success(f"🎯 发现 {len(results)} 个新信号！" if results else "📭 暂无新信号")
    
    with tm1:
        history = load_history()
        detected = history.get('detected', [])
        if detected:
            for signal in sorted(detected, key=lambda x: x.get('timestamp', ''), reverse=True)[:15]:
                st.markdown(f"{signal.get('type', '📌')} **{signal.get('company', '')}** {'🆕' if signal.get('is_new') else ''}")
                st.caption(signal.get('detail', '')[:150])
                st.caption(f"🕐 {signal.get('timestamp', '')[:16]}")
                st.markdown("---")
        else:
            st.info("📭 暂无信号")
    
    with tm3:
        history = load_history()
        detected = history.get('detected', [])
        if detected:
            st.metric("📊 总信号", len(detected))
            df = pd.DataFrame(detected)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 导出历史", csv, "监控历史.csv", "text/csv")
        else:
            st.info("📭 暂无历史记录")

# ===== 侧边栏 =====
st.sidebar.markdown("""
<div style="padding:8px 0 16px 0;border-bottom:1px solid rgba(0,0,0,0.06);margin-bottom:16px;">
    <div style="font-size:20px;font-weight:800;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">觅镜 Meje</div>
    <div style="font-size:12px;color:#7c8ba0;">v3.0 · 智能商业发现引擎</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
### 🚀 核心功能
- **🎯 发现引擎**：输入需求，AI自动找客户/雇主
- **🤖 AI 写需求**：简单描述业务，自动生成专业需求
- **🏢 企业深度分析**：输入企业名，生成分析报告
- **📡 持续监控**：自动追踪融资、招聘、新闻信号

### 🔌 数据源
- 🔍 SerpApi 百度搜索
- 💼 百度招聘
- 💰 百度融资新闻

### 🤖 AI 引擎
- DeepSeek 大模型
""")

st.sidebar.markdown("""
---
<div style="font-size:12px;color:#9aa0a6;text-align:center;padding-top:8px;">
    基于公开信息 · 仅供参考
</div>
""", unsafe_allow_html=True)

# ===== 底部法律条款 =====
st.markdown("""
<div class="legal-footer">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;">
        <div>
            <strong>📌 免责声明</strong><br>
            觅镜（Meje）提供的信息均来源于 SerpApi 百度搜索等公开渠道，仅作为参考信息使用，不构成任何形式的投资建议、合作建议或雇佣建议。用户应自行核实信息的准确性和时效性，并承担据此做出决策的全部风险。
        </div>
        <div>
            <strong>📡 数据来源</strong><br>
            本平台通过 SerpApi 获取百度搜索的公开信息，包括但不限于企业简介、融资新闻、招聘信息等。所有数据均为公开网络信息，觅镜不对数据的真实性、完整性承担法律责任。
        </div>
        <div>
            <strong>🔒 隐私与合规</strong><br>
            觅镜不存储用户的个人身份信息，不进行数据倒卖或商业转售。本平台仅作为信息整合工具，不涉及对任何企业或个人名誉的贬损或商业诋毁。
        </div>
        <div>
            <strong>⚠️ 使用限制</strong><br>
            本平台仅供个人学习、研究及商业调研参考使用。禁止将本平台用于大规模数据抓取或任何违反《中华人民共和国网络安全法》的行为。
        </div>
        <div>
            <strong>© 版权声明</strong><br>
            觅镜（Meje）保留对本平台的所有权利。平台中涉及的企业名称、商标、Logo等均为其各自所有者的财产。
        </div>
        <div>
            <strong>⏰ 时效性说明</strong><br>
            由于公开网络信息的更新频率差异，觅镜展示的信息可能与实际情况存在时间差，建议通过官方渠道核实。
        </div>
    </div>
    <div style="text-align:center;margin-top:14px;padding-top:12px;border-top:1px solid rgba(0,0,0,0.05);font-size:11px;color:#b0b8c0;">
        觅镜 Meje v3.0 · 基于公开信息 · 数据来源：SerpApi百度搜索 · 仅供调研参考
    </div>
</div>
""", unsafe_allow_html=True)
