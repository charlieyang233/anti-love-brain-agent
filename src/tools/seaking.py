from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from ..prompts.prompts import SEAKING_INNER_GUIDE
from ..prompts.prompt_config import SEAKING_EXECUTION_PROMPT
from ..core.config import llm

class SeakingInput(BaseModel):
    user_text: str = Field(..., description="用户最近一句回应")
    persona: str = Field("ENTJ-高阶PUA", description="海王人设")
    prev_score: int = Field(50, description="上一轮得分0-100")
    is_first_seaking: bool = Field(True, description="是否首次海王对战")
    challenge_type: str = Field("海王对战", description="挑战类型")
    gender: str = Field("男", description="海王性别")
    user_gender: str = Field("女", description="用户性别")

class SeakingTool(BaseTool):
    name = "seaking_tool"
    description = "海王模拟器工具：模拟AI海王和用户进行对战，用于练习反PUA技能"
    args_schema: Type[BaseModel] = SeakingInput

    # 海王台词库
    DIALOGUES = {
        "海王对战": {
            "ENTJ-霸道总裁型海王": "我的时间很宝贵，如果你不能跟上我的节奏，我建议你重新考虑一下。",
            "ENFP-温柔暖男型海王": "我觉得我们之间有种特别的缘分，你愿意和我一起探索吗？",
            "ISTP-高冷学霸型海王": "你的想法很有趣，但我觉得你还需要提升一下自己的认知水平。",
            "ESFJ-社交达人型海王": "我身边有很多朋友，但我觉得你比较特别，想和你多聊聊。",
            "INTJ-神秘精英型海王": "我很少对人有兴趣，但你让我觉得有点意思。"
        },
        "茶艺大师": {
            "ENFJ-绿茶心机型海王": "哎呀，我觉得你真的很特别呢，不像其他人那么肤浅。",
            "ISFP-白莲花型海王": "我只是想和你做朋友，你不要想太多啦～",
            "ESTJ-女王型海王": "我觉得你很有潜力，但还需要我的指导才能变得更好。",
            "INFP-文艺女神型海王": "你的灵魂很纯净，我想和你分享一些美好的事物。",
            "ENTP-毒舌女王型海王": "你这个人还挺有意思的，虽然有点笨，但我不介意教教你。"
        },
        "通讯录之巅": {
            "ENFP-彩虹暖男型海王": "我觉得我们之间有种特殊的连接，你感觉到了吗？",
            "ISTJ-精英同志型海王": "我的生活很规律，但我觉得你可以成为我的例外。",
            "ESFP-派对王子型海王": "今晚有个很棒的派对，我觉得你应该和我一起去。",
            "INFJ-文艺同志型海王": "你的眼神很深邃，我想了解你内心的世界。",
            "ESTP-运动型海王": "我觉得你的身材不错，要不要一起去健身？"
        }
    }

    # 点评库
    COMMENTARIES = {
        "海王对战": "海王开始试探了，注意他的套路！",
        "茶艺大师": "绿茶味很浓，小心她的心机！",
        "通讯录之巅": "彩虹海王上线，保持清醒！"
    }

    # 挑战目标库
    OBJECTIVES = {
        "海王对战": "识别并应对海王的操控套路，保持理性判断",
        "茶艺大师": "识破绿茶的心机手段，不被表面温柔迷惑",
        "通讯录之巅": "在彩虹世界中保持清醒，不被情感操控"
    }

    def _run(self, user_text: str, persona: str = "ENTJ-高阶PUA", prev_score: int = 50, 
             is_first_seaking: bool = True, challenge_type: str = "海王对战", 
             gender: str = "男", user_gender: str = "女") -> str:
        """海王模拟对战模式"""
        
        try:
            if is_first_seaking:
                return self._generate_first_response(persona, challenge_type)
            else:
                return self._generate_ongoing_response(user_text, persona, prev_score, challenge_type, gender, user_gender)
        except Exception as e:
            print(f"[Error] SeakingTool failed: {e}")
            return "海王断网了，还在骑马赶来的路上...🚬"

    def _generate_first_response(self, persona: str, challenge_type: str) -> str:
        """生成首次对话响应"""
        dialogue = self._get_dialogue(persona, challenge_type)
        commentary = self.COMMENTARIES.get(challenge_type, "海王开始行动了，保持警惕！")
        objective = self.OBJECTIVES.get(challenge_type, "保持理性，不被情感操控")
        
        return f"""【海王】{persona}说：{dialogue}

【拽姐旁白】点评：{commentary} + 当前得分：0分

【挑战目标】{objective}

【你】可选回应建议：
1. (高冷)哦，是吗？
2. (好奇)哪里让你觉得有意思？
3. (自信)那是当然。"""

    def _generate_ongoing_response(self, user_text: str, persona: str, prev_score: int, 
                                  challenge_type: str, gender: str, user_gender: str) -> str:
        """生成持续对话响应"""
        prompt = f"""
{SEAKING_EXECUTION_PROMPT.format(persona=persona, seaking_guide=SEAKING_INNER_GUIDE)}

【当前状态】
- 海王人设：{persona}
- 当前得分：{prev_score}分
- 挑战类型：{challenge_type}
- 海王性别：{gender}
- 用户性别：{user_gender}

用户输入：{user_text}

请严格按照三段式格式输出，并确保得分计算准确。
"""
        
        llm_instance = llm(temperature=0)
        response = llm_instance.invoke(prompt)
        return response.content.strip()

    def _get_dialogue(self, persona: str, challenge_type: str) -> str:
        """获取海王台词"""
        if challenge_type not in self.DIALOGUES:
            return "我觉得你很有趣，想和你多聊聊。"
        
        dialogues = self.DIALOGUES[challenge_type]
        
        # 直接匹配
        if persona in dialogues:
            return dialogues[persona]
        
        # 部分匹配
        for persona_key, dialogue in dialogues.items():
            if persona_key in persona:
                return dialogue
        
        # 默认台词
        return "我觉得你很有趣，想和你多聊聊。"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
