from flask import Blueprint, request, jsonify
import os

# 复用统一 AI Service（基于 openai SDK，支持多轮对话）
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ai_service import ask as ai_ask, get_ai_config, SYSTEM_PROMPT

ai_bp = Blueprint('ai', __name__)

# 兼容旧引用（如外部代码曾 import get_llm_config）
def get_llm_config():
    return get_ai_config()

tourism_knowledge = {
    'best_time': {
        'keywords': ['最佳时间', '什么时候去', '旅游时间', '季节', '几月', '合适', '推荐时间', '什么时候', '时间'],
        'answer': '四川气候多样，不同季节有不同的美景：\n\n春季（3-5月）：气温适宜，花开遍野，适合赏花踏青，推荐成都、都江堰、乐山大佛、嘉阳小火车。\n\n夏季（6-8月）：清凉避暑，草原花海，推荐峨眉山、青城山、四姑娘山、若尔盖草原。\n\n秋季（9-11月）：红叶满山，色彩斑斓，推荐九寨沟、稻城亚丁、新都桥、米亚罗。\n\n冬季（12-2月）：冰雪世界，温泉养生，推荐海螺沟、西岭雪山、峨眉山、瓦屋山。'
    },
    'spring': {
        'keywords': ['春季', '春天', '3月', '4月', '5月', '赏花', '油菜花'],
        'answer': '春季（3-5月）是四川赏花踏青的好时节：\n\n🌸 成都 - 赏花踏青\n🏛️ 都江堰 - 清明放水节\n🗿 乐山大佛 - 春光明媚\n🚂 嘉阳小火车 - 油菜花盛开\n\n春季气温适宜，花开遍野，是游览四川的好时机。'
    },
    'summer': {
        'keywords': ['夏季', '夏天', '6月', '7月', '8月', '避暑', '清凉'],
        'answer': '夏季（6-8月）是四川清凉避暑的好时节：\n\n⛰️ 峨眉山 - 避暑胜地\n🏔️ 青城山 - 清凉幽静\n🌸 四姑娘山 - 花海盛开\n🌿 若尔盖草原 - 最美季节\n\n夏季草原花海盛开，高山景区清凉宜人，是避暑度假的最佳选择。'
    },
    'autumn': {
        'keywords': ['秋季', '秋天', '9月', '10月', '11月', '红叶', '彩林'],
        'answer': '秋季（9-11月）是四川红叶满山的好时节：\n\n🍂 九寨沟 - 彩林倒映，色彩斑斓\n🌾 稻城亚丁 - 金色秋天，神山圣湖\n📸 新都桥 - 摄影家天堂\n🍁 米亚罗 - 红叶长廊\n\n秋季是四川最美的季节，层林尽染，色彩缤纷。'
    },
    'winter': {
        'keywords': ['冬季', '冬天', '12月', '1月', '2月', '滑雪', '温泉', '雪景'],
        'answer': '冬季（12-2月）是四川冰雪世界的好时节：\n\n❄️ 海螺沟 - 冰川温泉，冰火两重天\n⛷️ 西岭雪山 - 滑雪胜地\n🏔️ 峨眉山 - 雪景佛光，云海奇观\n🏔️ 瓦屋山 - 冰雪童话世界\n\n冬季可以体验冰雪运动和温泉养生，别有一番风味。'
    },
    'transport': {
        'keywords': ['交通', '怎么去', '机场', '高铁', '火车', '自驾', '路线', '班车', '大巴'],
        'answer': '四川交通便利，主要交通方式如下：\n\n✈️ 航空：成都双流国际机场和天府国际机场是主要入境口岸，省内还有绵阳、乐山、宜宾、泸州、稻城亚丁等支线机场。\n\n🚄 铁路：成都是西南地区铁路枢纽，成渝高铁、成贵高铁、西成高铁等线路四通八达。\n\n🚗 公路：四川省高速公路网发达，主要景点都有高速公路连接。\n\n小贴士：成都双流机场距市区约16公里，有机场大巴和地铁直达；天府机场距市区约50公里，有地铁18号线和机场大巴。'
    },
    'air': {
        'keywords': ['飞机', '机场', '航班', '航空', '机票', '双流', '天府'],
        'answer': '✈️ 航空出行指南：\n\n成都双流国际机场和天府国际机场是主要入境口岸，开通了国内外多条航线。\n\n省内支线机场包括：绵阳、乐山、宜宾、泸州、稻城亚丁等。\n\n📍 成都双流国际机场：距离市区约16公里，有机场大巴和地铁直达。\n📍 成都天府国际机场：距离市区约50公里，有地铁18号线和机场大巴。'
    },
    'train': {
        'keywords': ['火车', '高铁', '动车', '铁路', '东站', '南站', '西站'],
        'answer': '🚄 铁路出行指南：\n\n成都是西南地区的铁路枢纽，成渝高铁、成贵高铁、西成高铁等线路四通八达。\n\n主要火车站：\n- 成都东站：主要高铁站\n- 成都南站：城际列车\n- 成都西站：部分普速列车\n\n成都东站有高铁直达峨眉山、乐山、重庆、西安等地。'
    },
    'car': {
        'keywords': ['自驾', '开车', '公路', '高速', '包车', '租车'],
        'answer': '🚗 公路出行指南：\n\n四川省高速公路网发达，主要景点都有高速公路连接。\n\n成都各大客运站有发往省内各地的班车，方便快捷。\n\n景区间交通建议选择旅游专线或包车，高原地区建议选择飞机或包车，避免长时间车程。'
    },
    'route_classic': {
        'keywords': ['经典', '环线', '6天', '8天', '第一次', '成都', '都江堰', '九寨沟', '黄龙'],
        'answer': '🌟 经典环线（6-8天）：\n\n路线：成都 → 都江堰 → 九寨沟 → 黄龙 → 返回成都\n\n这条路线涵盖了四川最著名的景点，从成都出发，游览都江堰水利工程，然后前往九寨沟和黄龙，欣赏世界自然遗产的绝美风光。适合第一次来四川的游客。'
    },
    'route_culture': {
        'keywords': ['文化', '乐山', '峨眉山', '佛教', '美食', '4天', '5天'],
        'answer': '🎭 文化之旅（4-5天）：\n\n路线：成都 → 乐山 → 峨眉山 → 返回成都\n\n这条路线以文化体验为主，游览乐山大佛和峨眉山，感受佛教文化的博大精深，同时可以品尝地道的乐山美食。\n\n推荐体验：乐山大佛游船、峨眉山金顶日出、品尝钵钵鸡和豆腐脑。'
    },
    'route_plateau': {
        'keywords': ['高原', '稻城', '亚丁', '新都桥', '康定', '7天', '10天', '自然风光'],
        'answer': '🏔️ 高原探秘（7-10天）：\n\n路线：成都 → 康定 → 新都桥 → 稻城亚丁 → 返回成都\n\n这条路线适合喜欢自然风光的游客，沿途可以欣赏到壮丽的高原风光，新都桥的秋色、稻城亚丁的神山圣湖，都令人终身难忘。\n\n⚠️ 注意：高原地区需提前做好高原反应预防。'
    },
    'altitude_sickness': {
        'keywords': ['高原反应', '高反', '红景天', '氧气', '适应', '头痛', '缺氧'],
        'answer': '💊 高原反应预防指南：\n\n1. 提前一周开始服用红景天，增强身体适应能力\n2. 抵达高原后不要剧烈运动，给身体2-3天适应时间\n3. 多喝水，保持身体水分\n4. 避免饮酒和吸烟\n5. 随身携带氧气瓶以备不时之需\n\n如果出现严重高原反应，请及时就医或下撤到低海拔地区。'
    },
    'clothing': {
        'keywords': ['穿什么', '衣服', '衣物', '装备', '羽绒服', '外套', '鞋子', '防晒'],
        'answer': '👕 衣物准备指南：\n\n高原地区昼夜温差大，无论何时前往都需携带保暖衣物。\n\n夏季：轻薄外套和雨具\n冬季：羽绒服、手套、围巾等防寒用品\n\n必备物品：\n- 登山鞋或舒适的运动鞋\n- 防晒霜和太阳镜（紫外线强）\n- 雨具（山区天气多变）'
    },
    'food': {
        'keywords': ['美食', '吃什么', '小吃', '火锅', '麻辣', '川菜', '成都美食', '乐山美食'],
        'answer': '🍜 四川美食指南：\n\n四川美食以麻辣鲜香闻名，推荐尝试：\n\n火锅：麻辣鲜香，回味无穷\n串串香：街头小吃之王\n钵钵鸡：乐山特色美食\n担担面：传统小吃\n夫妻肺片：经典凉菜\n\n⚠️ 四川美食以麻辣为主，肠胃敏感者建议适量食用，可以要求"微辣"或"不辣"。'
    },
    'tips': {
        'keywords': ['注意事项', '贴士', '建议', '准备', '预订', '门票', '酒店', '身份证'],
        'answer': '📌 实用旅行贴士：\n\n1. 部分景区海拔较高，紫外线强，需做好防晒措施\n2. 尊重当地少数民族的风俗习惯\n3. 提前预订景区门票和酒店，特别是旅游旺季\n4. 随身携带身份证等有效证件\n5. 四川美食以麻辣为主，肠胃敏感者建议适量食用\n6. 高原地区建议携带充电宝，低温会影响手机电池'
    },
    'about': {
        'keywords': ['四川', '成都', '天府之国', '介绍', '特色', '历史', '文化'],
        'answer': '🏮 关于四川：\n\n四川，简称"川"或"蜀"，省会成都，被誉为"天府之国"。\n\n四川旅游资源丰富，拥有九寨沟、黄龙、峨眉山、乐山大佛等世界自然和文化遗产。\n\n四川美食文化博大精深，川菜是中国四大菜系之一，以麻辣鲜香著称。\n\n四川还是大熊猫的故乡，成都大熊猫繁育研究基地是游客必去的景点。'
    },
    'attractions': {
        'keywords': ['景点', '推荐', '好玩', '哪里', '旅游', '景区', '必去'],
        'answer': '🏞️ 四川著名景点推荐：\n\n世界遗产：\n- 九寨沟：人间仙境，彩林倒映\n- 黄龙：钙化池奇观\n- 峨眉山：佛教名山，云海佛光\n- 乐山大佛：世界最大石刻造像\n\n其他推荐：\n- 都江堰：古代水利工程\n- 稻城亚丁：最后的香格里拉\n- 四姑娘山：东方阿尔卑斯\n- 青城山：道教名山\n\n您可以告诉我您的兴趣和时间，我为您推荐最适合的路线。'
    }
}

def find_best_match(question):
    max_score = 0
    best_answer = None
    
    for key, item in tourism_knowledge.items():
        score = 0
        for keyword in item['keywords']:
            if keyword in question:
                score += 1
        
        if score > max_score:
            max_score = score
            best_answer = item['answer']
    
    return best_answer

def generate_response(question):
    question = question.strip()
    
    if not question:
        return '请问有什么可以帮您的？关于四川旅游的问题都可以问我哦！'
    
    best_answer = find_best_match(question)
    
    if best_answer:
        return best_answer
    
    return f'抱歉，我暂时无法回答关于"{question}"的问题。您可以问我关于四川旅游的其他问题，比如最佳旅游时间、交通指南、旅游路线等。'

@ai_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        question = str(data.get('question', '')).strip()
        history = data.get('history', [])

        if not question:
            return jsonify({
                'success': False,
                'message': '问题不能为空'
            }), 400

        # 调用统一 AI Service（基于 openai SDK，支持多轮）
        answer, code = ai_ask(question, history=history)

        if answer:
            return jsonify({
                'success': True,
                'answer': answer,
                # 兼容旧前端字段
                'response': answer,
                'source': 'llm',
                'model': code
            })

        # 调用失败：按错误码映射到友好提示，不泄漏内部堆栈 / API Key
        friendly, status_code = _map_error_code(code)
        # 未配置 / SDK 缺失等情况，仍尝试用本地 FAQ 兜底，保证有回答
        if code in ('not_configured', 'sdk_missing', 'client_error'):
            fallback = generate_response(question)
            return jsonify({
                'success': True,
                'answer': fallback,
                'response': fallback,
                'source': 'local',
                'model': None,
                'notice': friendly
            })

        # 其余错误（api_error / timeout / empty_answer）直接返回友好提示
        return jsonify({
            'success': False,
            'message': friendly,
            'error_code': code
        }), status_code

    except Exception:
        # 兜底：避免任何未捕获异常把堆栈返回给前端
        return jsonify({
            'success': False,
            'message': '服务器内部错误，请稍后重试'
        }), 500


def _map_error_code(code):
    """把 ai_service 的错误码映射成对用户友好的提示 + HTTP 状态码。"""
    mapping = {
        'empty_question': ('问题不能为空', 400),
        'not_configured': ('AI 服务未配置，已使用本地知识库回答', 200),
        'sdk_missing': ('未安装 openai SDK，已使用本地知识库回答', 200),
        'client_error': ('AI 客户端初始化失败，已使用本地知识库回答', 200),
        'timeout': ('AI 回答超时，请稍后重试', 504),
        'api_error': ('AI 服务暂时不可用，请稍后重试', 502),
        'empty_answer': ('AI 未返回有效回答，请稍后重试', 502),
    }
    return mapping.get(code, ('AI 服务异常，请稍后重试', 502))

@ai_bp.route('/status', methods=['GET'])
def get_status():
    config = get_llm_config()
    return jsonify({
        'success': True,
        'configured': config is not None,
        'model': config['model'] if config else None
    })

@ai_bp.route('/faq', methods=['GET'])
def get_faq():
    faqs = []
    for key, item in tourism_knowledge.items():
        faqs.append({
            'category': key,
            'keywords': item['keywords'][:3],
            'sample': item['answer'][:50] + '...'
        })
    return jsonify({
        'success': True,
        'data': faqs
    })
