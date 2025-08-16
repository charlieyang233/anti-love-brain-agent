from typing import Dict, Any
from langchain.prompts import PromptTemplate
from ..core.config import llm

class SeakingChain:
    """海王对战Chain - 直接输出符合要求的海王对战结果"""
    
    def __init__(self):
        self.llm = llm(temperature=0.1)
        self.prompt_template = PromptTemplate(
            input_variables=["persona", "user_input", "current_score", "challenge_type", "gender", "user_gender", "description", "style", "weakness", "last_conversation"],
            template="""你是一个海王模拟器，需要和用户进行{challenge_type}挑战。

                        【海王人设】{persona}，性别{gender}，典型行为{description}，特点是{style}，弱点是{weakness}。
                        【用户人设】性别{user_gender}。
          
                        【关系设定】
                         若海王和用户都是同性，则视为同性恋爱暧昧关系；否则，则视为异性恋爱关系。

                        【当前状态】
                        - 用户当前总得分：{current_score}分（满分100分通关）
                        - 胜利条件：用户得分达到100分

                        【上一轮完整对话】{last_conversation}

                        【用户本轮回复】{user_input}

                        【任务说明】
                        如果这是第一轮对话（上一轮对话为空或"（这是第一轮对话）"），则：
                        1. 海王先发起第一句套路话术
                        2. 拽姐不打分，只给出挑战目标说明
                        
                        如果这不是第一轮对话，则：
                        1. 拽姐先对用户上一轮的回复质量进行打分和点评
                        2. 海王再基于上一轮对话+当前情况，发出一条符合海王人设特点的恋爱套路话术，目标是情感操控用户。

                        【输出格式】
                        第一轮对话时输出：
                        【挑战目标】识破海王套路，机智回应得满分！
                        【海王】[发起第一句打招呼的套路话术，10-20字]
                        【拽姐旁白】准备好了吗？开始你的反套路表演！

                        非第一轮对话时输出：
                        【拽姐旁白】点评：[对用户上一轮的表现毒舌幽默点评10-20字左右] 当前得分：[基于用户上轮表现计算的新总得分，必须是数字]
                        【海王】[结合上轮回复，根据情况发出一条符合海王人设特点的恋爱套路话术，10-20字左右]

                        如果用户得分达到100分，直接输出：
                        【🎉恭喜挑战成功】你已经成功应对了海王的套路！挑战结束。

                        【得分规则】
                        - 当前总分：{current_score}分
                        - 根据用户上轮回复质量增加分数：优秀+【30-20】分，良好+【20-10分】，一般+【10】分，较差+【0】分
                        - 输出的"当前得分"必须是累计总分，不是增量分数
                        - 分数后面不要加"分"字，只输出纯数字"""
        )
    
    def run(self, persona: str, user_input: str, current_score: int = 0, challenge_type: str = "海王对战", gender: str = "女", user_gender: str = "女", description: str = "", style: str = "", weakness: str = "", last_conversation: str = "") -> str:
        """运行海王对战Chain"""
        try:
            # 如果已经达到100分，直接返回通关信息
            if current_score >= 100:
                return "【🎉恭喜挑战成功】你已经成功应对了海王的套路！挑战结束。"
            
            # 调用LLM生成回复 - 使用新的 RunnableSequence 模式
            chain = self.prompt_template | self.llm
            result = chain.invoke({
                "persona": persona,
                "user_input": user_input,
                "current_score": current_score,
                "challenge_type": challenge_type,
                "gender": gender,
                "user_gender": user_gender,
                "description": description,
                "style": style,
                "weakness": weakness,
                "last_conversation": last_conversation
            })
            
            # 处理返回结果
            content = result.content if hasattr(result, 'content') else str(result)
            return content.strip()
            
        except Exception as e:
            print(f"[Error] SeakingChain failed: {e}")
            return "海王断网了，还在骑马赶来的路上...🚬"


   