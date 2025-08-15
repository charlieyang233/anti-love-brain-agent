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
    description = ("海王模拟器工具：在用户明确要求模拟海王对战/恋爱游戏/模拟海王套路/练习反pua/练习海王话术/挑战海王游戏/海王模拟对战时使用，需要模拟AI海王和用户进行对战。")
    args_schema: Type[BaseModel] = SeakingInput

    def _run(self, user_text: str, persona: str = "ENTJ-高阶PUA", prev_score: int = 50, 
             is_first_seaking: bool = True, challenge_type: str = "海王对战", 
             gender: str = "男", user_gender: str = "女") -> str:
        """海王模拟对战模式 - 直接调用LLM生成回复"""
        
        print(f"=== SeakingTool._run 被调用 ===")
        print(f"输入参数: user_text={user_text}, persona={persona}, is_first_seaking={is_first_seaking}")
        
        try:
            # 构建增强的prompt
            enhanced_prompt = self._build_enhanced_prompt(
                user_text, persona, prev_score, is_first_seaking, 
                challenge_type, gender, user_gender
            )
            
            print(f"SeakingTool输入参数: persona={persona}, challenge_type={challenge_type}")
            print(f"SeakingTool生成的prompt: {enhanced_prompt}")
            
            # 如果是首次对话，直接返回预定义格式，不调用LLM
            if is_first_seaking:
                dialogue = self._generate_first_dialogue(persona, challenge_type, gender)
                commentary = self._generate_first_commentary(challenge_type)
                objective = self._generate_challenge_objective(challenge_type)
                
                return f"""【海王】{persona}说：{dialogue}

【拽姐旁白】点评：{commentary} + 当前得分：0分

【挑战目标】{objective}

【你】可选回应建议：
1. (高冷)哦，是吗？
2. (好奇)哪里让你觉得有意思？
3. (自信)那是当然。"""
            else:
                # 非首次对话，调用LLM
                llm_instance = llm(temperature=0)  # 降低温度确保格式一致性
                response = llm_instance.invoke(enhanced_prompt)
                
                print(f"SeakingTool LLM响应: {response.content}")
                
                return response.content.strip()
        except Exception as e:
            # 降级处理：返回简单的对战回复
            return f"海王断网了，还在骑马赶来的路上...🚬"

    def _build_enhanced_prompt(self, user_text: str, persona: str, prev_score: int, 
                              is_first_seaking: bool, challenge_type: str, 
                              gender: str, user_gender: str) -> str:
        """构建增强的prompt"""
        
        # 基础prompt模板
        base_prompt = SEAKING_EXECUTION_PROMPT.format(
            persona=persona,
            seaking_guide=SEAKING_INNER_GUIDE
        )
        
        # 添加首次对话的特殊处理
        if is_first_seaking:
            first_dialogue_prompt = f"""
你是一个海王模拟器，现在开始{challenge_type}挑战！

【挑战设定】
- 海王人设：{persona}
- 海王性别：{gender}
- 用户性别：{user_gender}
- 挑战类型：{challenge_type}
- 胜利条件：用户得分超过100分

【首次对话要求】
请严格按照以下格式输出，一个字都不能改：

【海王】{persona}说：{self._generate_first_dialogue(persona, challenge_type, gender)}

【拽姐旁白】点评：{self._generate_first_commentary(challenge_type)} + 当前得分：0分

【挑战目标】{self._generate_challenge_objective(challenge_type)}

【你】可选回应建议：
1. (高冷)哦，是吗？
2. (好奇)哪里让你觉得有意思？
3. (自信)那是当然。

输出要求：
1. 必须严格按照上述格式
2. 每段必须以【】开头
3. 不能添加任何其他内容
4. 不能改变格式结构
5. 绝对不能改变人设名称"{persona}"
"""
            return first_dialogue_prompt
        else:
            # 非首次对话，使用原有格式但增强内容
            enhanced_prompt = f"""
{base_prompt}

【当前状态】
- 海王人设：{persona}
- 当前得分：{prev_score}分
- 挑战类型：{challenge_type}
- 海王性别：{gender}
- 用户性别：{user_gender}

用户输入：{user_text}

请严格按照三段式格式输出，并确保得分计算准确。
"""
            return enhanced_prompt

    def _generate_first_dialogue(self, persona: str, challenge_type: str, gender: str) -> str:
        """生成首次对话的海王台词"""
        dialogues = {
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
        
        print(f"查找persona: {persona}, challenge_type: {challenge_type}")
        
        # 根据persona和challenge_type选择台词
        if challenge_type in dialogues:
            # 直接匹配完整的persona字符串
            if persona in dialogues[challenge_type]:
                print(f"找到完全匹配: {persona}")
                return dialogues[challenge_type][persona]
            
            # 如果完整匹配失败，尝试部分匹配
            for persona_key, dialogue in dialogues[challenge_type].items():
                if persona_key in persona:
                    print(f"找到部分匹配: {persona_key} in {persona}")
                    return dialogue
            
            # 如果还是没有匹配到，打印调试信息
            print(f"未找到匹配的persona: {persona}, challenge_type: {challenge_type}")
            print(f"可用的persona: {list(dialogues[challenge_type].keys())}")
        
        # 默认台词
        return "我觉得你很有趣，想和你多聊聊。"

    def _generate_first_commentary(self, challenge_type: str) -> str:
        """生成首次对话的拽姐点评"""
        commentaries = {
            "海王对战": "海王开始试探了，注意他的套路！",
            "茶艺大师": "绿茶味很浓，小心她的心机！",
            "通讯录之巅": "彩虹海王上线，保持清醒！"
        }
        return commentaries.get(challenge_type, "海王开始行动了，保持警惕！")

    def _generate_challenge_objective(self, challenge_type: str) -> str:
        """生成挑战目标"""
        objectives = {
            "海王对战": "识别并应对海王的操控套路，保持理性判断",
            "茶艺大师": "识破绿茶的心机手段，不被表面温柔迷惑",
            "通讯录之巅": "在彩虹世界中保持清醒，不被情感操控"
        }
        return objectives.get(challenge_type, "保持理性，不被情感操控")

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
