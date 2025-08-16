from typing import Dict, Any
from langchain.prompts import PromptTemplate
from ..core.config import llm

class SeakingChain:
    """海王对战Chain - 直接输出符合要求的海王对战结果"""
    
    def __init__(self):
        self.llm = llm(temperature=0.8)
        self.prompt_template = PromptTemplate(
            input_variables=["persona", "user_input", "current_score", "challenge_type"],
            template="""你是一个海王模拟器，现在进行{challenge_type}挑战。

【海王人设】{persona}

【当前状态】
- 当前得分：{current_score}分
- 胜利条件：用户得分达到100分

【用户输入】{user_input}

请严格按照以下格式输出，不能改变格式：

【海王】{persona}说：[根据人设特点，生成一句符合海王套路的回复]

【拽姐旁白】点评：[分析海王的真实意图，给出战术建议] + 当前得分：[根据用户回应质量计算得分，0-100分]

如果用户得分达到100分，直接输出：
【🎉恭喜挑战成功】你已经成功应对了海王的套路！挑战结束。

注意：
1. 海王回复要符合人设特点，真实自然
2. 拽姐点评要一针见血，指出海王套路
3. 得分计算要合理，好的回应给10-20分，差的回应给0-5分
4. 达到100分时立即结束挑战"""
        )
    
    def run(self, persona: str, user_input: str, current_score: int = 0, challenge_type: str = "海王对战") -> str:
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
                "challenge_type": challenge_type
            })
            
            # 处理返回结果
            content = result.content if hasattr(result, 'content') else str(result)
            return content.strip()
            
        except Exception as e:
            print(f"[Error] SeakingChain failed: {e}")
            return "海王断网了，还在骑马赶来的路上...🚬"


   