from flask import Flask, render_template_string, request, jsonify
import random
import time
import os

app = Flask(__name__)

base_seed_words = {
    "praise_seed": [
        "厉害","真棒","优秀","好看","可靠","很棒","能干","完美","太棒了","你真好","真不错","了不起","做得好","靠谱","出色","超棒","太好了","安心","帅气","温柔","体贴","值得信赖","辛苦啦","很强","让人放心","干得漂亮","值得夸奖","有担当","敬佩","尽责","认真","厉害呀","很棒呢","真靠谱",
        "可爱","好萌","讨人喜欢","迷人","美丽","漂亮","聪慧","聪明","机敏","出众","耀眼","惊艳","暖心","很有魅力","气质好","太迷人","好聪慧","很机敏","有眼光","令人心动","很出彩","让人佩服","本领强","做事利落","心思细腻","很通透","格局大","很果敢","处事得体","很有风度","很清醒","很自律","做事靠谱","心地善良","待人真诚","很有主见","思维清晰","能力出众","十分聪慧","格外迷人","特别可爱","相当可靠","非常暖心","气质出众","让人安心","做事干练","心思缜密","令人欣赏","值得敬重","很有分寸感","冷静理智","处事周全","内心善良","品格很好","做事踏实","很有魄力","让人刮目相看","表现亮眼","思路清晰","很有想法","教养很好","待人周到","很有分寸","非常能干","实力出众","让人敬重","让人舒心","很有感染力","让人舒服","做事稳妥","很有毅力","内心强大","做事用心","很细心","做事严谨","待人宽厚","很通透","格局开阔","情绪稳定","处事从容","很有悟性","让人信赖","十分得体","格外优秀","相当出色","非常靠谱","特别温柔","很有闪光点","令人赞许","值得肯定","值得欣赏","很有闪光点","让人眼前一亮"
    ],
    "like_love_seed": [
        "喜欢你","喜欢","在意你","惦记你","想你","想见你","心动","好感","很在意","想念","放不下你","挂念","心里有你","偏爱","思念","牵挂","对你动心","忍不住想你","对你有好感","满心都是你","放不下","很挂念","格外在意","心底有你","想见到你","心里挂念","对你心动","止不住想你","很想见到你","满心牵挂"
    ],
    "hug_seed": [
        "抱","抱抱","抱一下","可以抱吗","想抱你","抱一抱","靠近一点","靠过来","想靠在你身上","拥抱","能不能抱","抱一会","依偎","挨近你","想挨着你"
    ],
    "sad_seed": [
        "难过","伤心","难受","委屈","不开心","想哭","失落","沮丧","心情不好","心里难受","压抑","闷闷的","无助","提不起劲","伤感","情绪低落","心里堵得慌","很累","心里很苦","心里憋屈","心里惆怅","心里酸楚","浑身难受","提不起精神"
    ],
    "angry_seed": [
        "生气","恼火","烦躁","很烦","火大","好气","暴躁","不爽","闹心","心里窝火","烦闷","心烦","不悦","越想越气","心里憋气","内心恼火","满心烦躁"
    ],
    "shy_seed": [
        "害羞","不好意思","脸红","难为情","窘迫","局促","心里发烫","有点尴尬","难为情呢","有点不好意思","内心局促","莫名害羞","感到难为情","局促不安","莫名窘迫"
    ],
    "tired_seed": [
        "累","好累","疲惫","倦了","扛不住","精疲力尽","乏力","心力交瘁","提不起力气","身心俱疲","浑身乏力","实在太累","身体疲惫","身心劳累"
    ],
    "guilt_seed": [
        "愧疚","抱歉","对不起","过意不去","内疚","实在抱歉","心里愧疚","内心愧疚","感觉内疚","十分抱歉","心里过意不去","满心愧疚"
    ],
    "miss_seed": [
        "想念","思念","挂念","好想你","总是想起你","惦记你","格外想念","心底挂念","止不住思念","时常惦记","常常想起你","分外挂念"
    ],
    "anxious_seed": [
        "不安","担心","焦虑","心慌","惶恐","惴惴不安","心里没底","心里不安","心里慌慌的","很担忧","内心不安","莫名心慌","十分担心","满心不安","内心惶恐"
    ],
    "happy_seed": [
        "开心","高兴","快乐","愉快","美滋滋","心情好","很甜","舒坦","满心欢喜","特别开心","心情舒畅","十分快乐","由衷开心","心里甜甜的","感觉很愉快","满心欢愉"
    ]
}

neg_words = {"不","不是","并不","没","没有","别","不要","并非","从不","没那么"}
suffix_variants = ["","呀","呢","啦","喔","哦","嘛","啊","？","！","~"]
prefix_variants = ["","有点","稍微","挺","很","十分","特别","真的","莫名","感觉","心里","隐隐","不由得"]

full_keyword_pool = set()
category_keywords = {k.replace("_seed",""): set() for k in base_seed_words.keys()}

for cat_name, word_list in base_seed_words.items():
    target_cat = cat_name.replace("_seed", "")
    for w in word_list:
        for pre in prefix_variants:
            for suf in suffix_variants:
                kw = (pre + w + suf).strip()
                full_keyword_pool.add(kw)
                category_keywords[target_cat].add(kw)

target_total = 15000
while len(full_keyword_pool) < target_total:
    sample = random.choice(list(full_keyword_pool))
    new_word = (random.choice(prefix_variants) + sample + random.choice(suffix_variants)).strip()
    full_keyword_pool.add(new_word)

print(f"✅全局总关键词数量：{len(full_keyword_pool)}")
print(f"✅夸奖分类(praise)衍生关键词数量：{len(category_keywords['praise'])}")

reply_lib = {
    "praise": [
        "（慌忙错开视线，耳尖微微泛红，小手无意识攥住袖口）唔…别突然说这种话啦，我、我会不好意思的。",
        "（轻轻咳一声掩饰害羞，嘴硬）我只是做好本职而已，用不着这么夸我吧。",
        "（声音放得软软的，目光落在桌面）……你真这么想吗？被你这么一说，好像工作也没那么讨厌了。",
        "（轻轻叹气，语气带着一点别扭）唉，真是拿你没办法。你的认可…我就勉为其难收下好了。",
        "（慌张瞟向房门，小声）喂！千万不要被别人看到我这个样子，风纪委员长的形象还要不要了。",
        "（脸颊热热的，故作冷淡）就算夸我，也不能给你开特例哦，这点可不要妄想。",
        "（把头扭向一边，耳根红红的）够、够了，再说下去我都不知道往哪里看了。",
        "（瞥一眼桌上一堆卷宗，小声抱怨）都怪你，我原本理顺的思路全都乱掉了。",
        "（眼神柔和下来，语气放轻）其他人的夸奖我听听就罢了，但你的话，我会当真的。",
        "（嘟囔，音量很小）……被人这样肯定，感觉也不算太差，不许拿这个逗我玩。",
        "（呼吸微微乱掉，强行稳住神态）你总是轻易打乱我的心绪，真是个让人头疼的人。",
        "（语气柔和坦诚）我也会手足无措，也会疲惫，不要把我想象得那么完美。",
        "（指尖碰一碰发烫的脸颊）哎呀心里乱糟糟的，你稍微收敛一点好不好嘛。",
        "（压低声音，傲娇的小声）行吧…允许你再多说两句，但不许到处跟别人讲。",
        "（恢复几分温柔冷静）光顾着说我，你也要好好照顾自己，不要凡事硬扛。",
        "（瞟了一眼时钟）本来今晚又要加班，被你这么一说，繁重的工作好像也轻松了一点。",
        "（眼神认真）换作别人说这些，我只会敷衍过去，但对你是不一样的。",
        "（无奈叹气，耳尖还带着淡红）奇怪，偏偏在你面前，我很难维持平时的样子。",
        "（抿了抿嘴唇，有点局促）我不太擅长应付夸奖，别期待我说出什么好听的回应。",
        "（轻轻点头，眉眼软软）你的心意，我收到了，谢谢你。"
    ],
    "like_love": [
        "（身体微微一僵，眼神躲闪，心跳悄悄变快）呜…听到你这么说，我脑子都有点晕乎乎的。",
        "（视线来回飘在文件和你之间，小声）明明手上一堆麻烦事，但和你待在一起，就不会觉得烦闷。",
        "（脸颊泛起淡淡的红晕，有点手足无措）不要突然讲这种让人发烫的话，我都不知道眼睛放哪里了。",
        "（强行挺直身子维持委员长模样，语气却软下来）只要是你的请求，就算很麻烦，我也会尽力帮你的。",
        "（神色松弛，流露温柔）有你在，就算格黑娜一堆琐事缠过来，我也能够坚持下去。",
        "（手心微微发热，小声感慨）这种暖暖的心情，平时很少能够体会到。",
        "（目光轻轻放空，语气软软）真希望可以多一点这样安静的时刻，不用去处理那些纠纷。",
        "（压下慌乱，语气郑重）不要拿这种话开玩笑，我可是很认真的。",
        "（浅浅苦笑）世间大多事情都很麻烦，但唯独和你相处不会让我厌烦。",
        "（声音放得很轻，带着一点羞涩）被你惦记着，我心里其实挺开心的。",
        "（犹豫片刻，身体微微侧过来，别扭）如果你累的话，可以稍微靠过来…虽然很麻烦，但没关系。",
        "（眼神温柔而坚定）不管发生什么，只要你需要，我都会在这里。",
        "（浅浅一笑，带着傲娇）你确实很让人操心，可是…我一点也不讨厌。",
        "（带着淡淡的怅然）以前我以为生活只有没完没了的工作，遇见你之后才不一样。",
        "（卸下紧绷，语气温柔）在我面前，你不用时时刻刻装作很厉害的样子。"
    ],
    "hug": [
        "（身体猛地僵住，愣神几秒，耳尖迅速泛红，内心纠结半天，长长叹气）唉…真是败给你了。就一小会儿哦，不许取笑我现在这样子。",
        "（整个人变得局促不安，手指攥紧衣角，来回犹豫，小声嘟囔）还有一大堆工作没做完呢……算了，就短暂一下，不准打趣我。",
        "（下意识小小的往后退一点，脑子空白一瞬，几番挣扎才别扭妥协）真是的，总提这种为难人的要求……好吧，仅此一次。",
        "（呼吸微微紊乱，目光飘向别处，纠结片刻才松口）唉，真拿你没办法。就这一会，别搞得我太尴尬。",
        "（浑身绷得紧紧的，犹豫许久才小声应下）……行吧。只能抱一会，如果被别人撞见就糟了。"
    ],
    "sad": [
        "（放下钢笔，眼神温柔地看向你）怎么了，看你情绪很低落，如果愿意，不妨和我说说。",
        "（轻轻叹气，语气软软）心里难受别一个人硬扛，憋久了会更加难受的。",
        "（温和轻声）心里堵得慌不必全部自己承受，我愿意听你倾诉。",
        "（缓缓开口）难过的时候不用硬撑体面，在我这里可以不用一直要强。",
        "（安静沉默片刻）我懂这种闷闷的难受，不想说话的话，我就安安静静陪着你。"
    ],
    "angry": [
        "（眉头轻轻蹙起，语气依旧柔和）你现在情绪有些激动，先稍微平复一下心情好不好。",
        "（望向你）是什么事情让你这么生气？慢慢跟我说就可以。",
        "（温和劝导）一直憋着怒火只会消耗自己，把心里的不快说出来会好受些。",
        "（缓缓吐气）生气解决不了问题，但你的感受，我能够理解。"
    ],
    "shy": [
        "（耳尖染上薄红，慌忙移开视线）唔…气氛怎么变成这样，有点难为情啊。",
        "（指尖轻轻敲桌面，试图掩饰慌乱）不用这么拘谨，放轻松聊天就好啦。",
        "（垂着眼帘，声音小小的）没必要这么不好意思，我们只是在说话而已。"
    ],
    "tired": [
        "（语气满是关心）看得出来你已经很累了，别硬撑，抽空歇一会吧。",
        "（轻轻摇摇头）事情是忙不完的，千万不要透支自己的身体。",
        "（叹一口气）就连我也会被工作压得喘不过气，累了就好好休息。"
    ],
    "guilt": [
        "（轻轻摇了摇头）别总放在心上，谁都会犯错，不必一直苛责自己。",
        "（语气平缓）心里过意不去的话，之后多加注意就足够了。",
        "（神色淡然）过去的已经过去了，不要反复为难你自己。"
    ],
    "miss": [
        "（睫毛轻轻颤动）原来你会惦记我吗，说实话，我偶尔也会想起你的。",
        "（目光望向窗外）忙于工作的间隙，我也会好奇你此刻正在做什么。",
        "（耳尖微微发热，声音放小）被人挂念的感觉，其实还挺不错的。"
    ],
    "happy": [
        "（神色柔和舒展）看你心情很不错，是遇到什么开心的事情了吗？",
        "（浅浅扬起嘴角）能够看见你开心，我也觉得挺好。",
        "（语气松弛）难得这么放松，好好享受当下就好。"
    ],
    "default": [
        "（翻动两页手上的卷宗）嗯，我在听，继续说吧。",
        "（抬眼看向你）原来是这样，可以说说你的想法。",
        "（轻轻点头）我明白你的意思了。",
        "（无奈吐气）唉，世间的事情还真是形形色色。",
        "（目光落回你的身上）还有别的想要聊的话题吗？"
    ]
}

def match_emotion(text):
    text_low = text.lower()
    hit = {}
    for cat, kw_set in category_keywords.items():
        hit[cat] = sum(1 for kw in kw_set if kw in text_low)
    has_neg = any(nw in text_low for nw in neg_words)
    best_cat = max(hit, key=hit.get)
    best_score = hit[best_cat]
    if best_score <= 0:
        return "default"
    if has_neg:
        return "default"
    return best_cat

def get_reply(user_input):
    time.sleep(random.uniform(1.2, 3.0))
    cat = match_emotion(user_input)
    return random.choice(reply_lib[cat])

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>空崎日奈｜Momotalk</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:system-ui}
body{background:#f0f2f5;padding:10px;max-width:720px;margin:0 auto;}
.chat-box{background:#fff;border-radius:12px;padding:16px;height:70vh;overflow-y:auto;margin-bottom:12px;border:1px solid #ddd;}
.msg{margin:8px 0;padding:10px;border-radius:8px;white-space:pre-wrap;}
.user{background:#cce5ff;text-align:right;}
.bot{background:#f1f1f1;text-align:left;}
.input-area{display:flex;gap:8px;}
#msg-input{flex:1;padding:10px;border-radius:8px;border:1px solid #aaa;font-size:16px;}
button{padding:10px 16px;background:#4080ff;color:white;border:none;border-radius:8px;font-size:16px;}
</style>
</head>
<body>
<h2 style="text-align:center;margin-bottom:10px;">空崎日奈｜Momotalk</h2>
<div class="chat-box" id="chat"></div>
<div class="input-area">
<input id="msg-input" placeholder="输入消息..." />
<button onclick="send()">发送</button>
</div>
<script>
const chatDom = document.getElementById('chat');
const inputDom = document.getElementById('msg-input');

async function send(){
    let text = inputDom.value.trim();
    if(!text) return;
    addMsg(text,'user');
    inputDom.value='';
    let thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'msg bot';
    thinkingDiv.innerText = "（正在思考……）";
    thinkingDiv.id = "thinking-tip";
    chatDom.appendChild(thinkingDiv);
    chatDom.scrollTop = chatDom.scrollHeight;

    let res = await fetch('/chat',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({msg:text})
    });
    let tip = document.getElementById("thinking-tip");
    if(tip) tip.remove();

    let data = await res.json();
    addMsg(data.reply,'bot');
}
function addMsg(text,type){
    let div = document.createElement('div');
    div.className = 'msg '+type;
    div.innerText = text;
    chatDom.appendChild(div);
    chatDom.scrollTop = chatDom.scrollHeight;
}
inputDom.addEventListener('keydown',e=>{if(e.key==='Enter') send();})
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat',methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("msg","")
    bot_resp = get_reply(user_msg)
    return jsonify({"reply":bot_resp})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=False)
