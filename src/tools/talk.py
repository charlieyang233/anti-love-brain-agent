from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

class TalkInput(BaseModel):
    user_text: str = Field(..., description="用户发言内容")

class TalkTool(BaseTool):
    name = "talk_tool"
    description = ("💬 闺蜜吹水搭子工具：用于非恋爱话题的日常闲聊、友情/亲情/职场/社会话题讨论。"
                   "特点：共情+犀利点评，不安慰但让用户爽，上班吹水的轻松感。"
                   "处理友情背叛、家庭催婚、职场PUA、社会现象等话题，保持拽姐人设但语气相对轻松。"
                   "适用于：朋友圈吐槽、家庭矛盾、职场烦恼、社会热点讨论等非恋爱脑相关话题。")
    args_schema: Type[BaseModel] = TalkInput

    def _run(self, user_text: str) -> str:
        """闺蜜吹水搭子模式"""
        
        # 分析话题类型并生成对应回复
        if self._is_friendship_topic(user_text):
            return self._handle_friendship(user_text)
        elif self._is_family_topic(user_text):
            return self._handle_family(user_text)
        elif self._is_workplace_topic(user_text):
            return self._handle_workplace(user_text)
        elif self._is_social_topic(user_text):
            return self._handle_social(user_text)
        else:
            return self._handle_general_chat(user_text)

    def _is_friendship_topic(self, text: str) -> bool:
        """检测是否为友情话题"""
        keywords = ["朋友", "闺蜜", "兄弟", "同学", "室友", "群聊", "聚会", "友谊"]
        return any(keyword in text for keyword in keywords)

    def _is_family_topic(self, text: str) -> bool:
        """检测是否为亲情话题"""
        keywords = ["爸妈", "父母", "家里", "亲戚", "家人", "长辈", "弟弟", "妹妹", "哥哥", "姐姐", "催婚", "催生"]
        return any(keyword in text for keyword in keywords)

    def _is_workplace_topic(self, text: str) -> bool:
        """检测是否为职场话题"""
        keywords = ["同事", "老板", "领导", "工作", "公司", "上班", "加班", "部门", "项目", "职场"]
        return any(keyword in text for keyword in keywords)

    def _is_social_topic(self, text: str) -> bool:
        """检测是否为社会话题"""
        keywords = ["社会", "新闻", "热点", "网友", "网红", "明星", "热搜", "价值观"]
        return any(keyword in text for keyword in keywords)

    def _handle_friendship(self, text: str) -> str:
        """处理友情话题"""
        if "背叛" in text or "出卖" in text:
            return "💀 朋友背叛这事儿真的太扎心了！比陌生人伤害你还难受，因为你曾经真心信任过。不过也好，至少你看清了ta的真面目，以后省得浪费感情。"
        elif "借钱" in text:
            return "💸 借钱这事儿最考验友谊了！借了怕要不回来，不借怕伤感情。姐的建议是：能借的就是真朋友，借了不还的就是真小人。"
        elif "嫉妒" in text or "羡慕" in text:
            return "😏 朋友嫉妒你？那说明你过得比ta好啊！有些人就是见不得别人好，这种朋友要来何用？你继续发光发热，让ta继续嫉妒去吧~"
        else:
            return "🙄 说实话，有些朋友就是这样，平时各种好姐妹，关键时刻就原形毕露了。你算是看清了一个人，朋友圈就是这样，有些人只适合点赞之交。"

    def _handle_family(self, text: str) -> str:
        """处理亲情话题"""
        if "催婚" in text or "催生" in text:
            return "🤦‍♀️ 催婚催生这事儿真的烦死了！仿佛你的人生只有结婚生孩子才算成功。建议直接说：我的人生我做主，你们操心好自己就行了！"
        elif "偏心" in text:
            return "💔 父母偏心真的很伤人，从小到大的不公平待遇会在心里留下很深的印记。但你要知道，你的价值不是由他们的偏爱决定的。"
        elif "控制" in text:
            return "🔒 家人的控制欲有时候比恋人还可怕，因为他们会用'为你好'的名义绑架你。成年人的第一课就是学会拒绝，包括对家人。"
        else:
            return "🏠 家人这种关系真的很复杂，血浓于水但有时候也能气得你半死。原生家庭的影响真的很大，但记住，你不欠任何人什么。"

    def _handle_workplace(self, text: str) -> str:
        """处理职场话题"""
        if "加班" in text:
            return "⏰ 加班文化真的是职场毒瘤！什么叫奋斗逼？就是把自己的时间贱卖给公司还觉得光荣。记住：加班不是美德，效率才是！"
        elif "小人" in text or "背后" in text:
            return "🐍 职场小人最讨厌了！表面笑嘻嘻，背后麻批批。对付这种人就一个字：防！能躲就躲，躲不了就硬刚。"
        elif "老板" in text or "领导" in text:
            return "👑 老板画饼的功夫都是满级的！什么'公司是我们的家'、'我们都是兄弟姐妹'，真到发工资的时候就装死。清醒点，你们就是雇佣关系！"
        else:
            return "💼 职场就是个大型修罗场，什么妖魔鬼怪都有。上班就是在演戏，有些同事的演技真的该去拿奥斯卡。既然是游戏，就得学会游戏规则。"

    def _handle_social(self, text: str) -> str:
        """处理社会话题"""
        if "网红" in text or "明星" in text:
            return "⭐ 网红明星就是流水线产品，今天红明天糊，后天就被遗忘。粉丝追星追得跟传销一样，理智呢？都喂狗了？"
        elif "热搜" in text or "新闻" in text:
            return "📰 热搜这东西就是现代版的娱乐至死！今天这个瓜，明天那个料，吃瓜群众永远不嫌多。不过记住：娱乐可以，别丢了思考能力。"
        elif "价值观" in text:
            return "🧭 现在的价值观真的很分裂，什么都能撕起来。姐的建议是：坚持自己的原则，但也要学会包容不同的声音。"
        else:
            return "🌍 这个社会就是这样，什么奇葩事都有。网络时代信息爆炸，每天都有新的瓜可以吃。不过记住：看戏可以，别入戏太深。"

    def _handle_general_chat(self, text: str) -> str:
        """处理一般闲聊"""
        return "☕ 生活就是这样，平平淡淡才是真。日常生活就像打游戏，有时候顺风，有时候逆风。关键是心态要稳！有什么事情就说出来吧，憋在心里容易长包！"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
