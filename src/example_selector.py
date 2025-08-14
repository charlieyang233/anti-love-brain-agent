#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能示例选择器 - 为恋爱脑识别器提供动态few-shot示例
"""
import re
from typing import List, Dict, Tuple
from .prompt_config import RISK_SIGNALS

class ExampleSelector:
    """基于相似度的示例选择器"""
    
    def __init__(self, max_examples: int = 2):
        """
        初始化示例选择器
        
        Args:
            max_examples: 每次最多选择的示例数量
        """
        self.max_examples = max_examples
        self.risk_signals = RISK_SIGNALS
    
    def _calculate_similarity(self, user_input: str, example: str) -> float:
        """
        计算用户输入与示例的相似度
        
        Args:
            user_input: 用户输入文本
            example: 示例文本
            
        Returns:
            相似度分数 (0-1)
        """
        # 高权重关键词匹配 - 根据新的严重程度标准重新设计
        high_weight_keywords = {
            # 轻度关键词 (0-39): 早期预警信号，不影响日常生活
            '理想化': 0.9, '完美': 0.8, '真命天子': 0.9, '王子': 0.8,
            '焦虑': 0.8, '担心': 0.7, '紧张': 0.7, '不安': 0.8,
            '迎合': 0.8, '顺从': 0.7, '听话': 0.7, '配合': 0.6,
            '改变': 0.7, '习惯': 0.6, '调整': 0.6, '适应': 0.6,
            '消息': 0.8, '回复': 0.7, '秒回': 0.8, '已读': 0.7,
            
            # 中度关键词 (40-69): 心理依赖、小额财产、社交限制
            '礼物': 0.8, '买单': 0.8, '付费': 0.8, '花钱': 0.7,
            '隐瞒': 0.9, '撒谎': 0.9, '编造': 0.8, '欺骗': 0.8,
            '价值观': 0.9, '信念': 0.9, '原则': 0.8, '底线': 0.8,
            '检查': 0.8, '查看': 0.8, '监视': 0.9, '窥视': 0.8,
            '依赖': 0.9, '离不开': 0.9, '没有': 0.8, '失控': 0.8,
            '疏远': 0.8, '冷淡': 0.7, '减少': 0.7, '避免': 0.7,
            
            # 重度关键词 (70-89): 大额财产、社交隔离、实质控制
            '借钱': 0.9, '转账': 0.9, '贷款': 0.9, '万': 0.9,
            '工作': 0.8, '辞职': 0.9, '学业': 0.8, '放弃': 0.9,
            '朋友': 0.7, '家人': 0.8, '联系': 0.8, '断绝': 0.9,
            '跟踪': 0.9, '偷看': 0.8, '监控': 0.9, '定位': 0.9,
            '签署': 0.8, '合同': 0.8, '文件': 0.7, '协议': 0.8,
            '洗钱': 0.9, '违法': 0.9, '犯罪': 0.9, '帮助': 0.6,
            '操控': 0.9, '控制': 0.9, '勒索': 0.9, '威胁': 0.9,
            
            # 危险关键词 (90-100): 生命安全、人身自由、严重心理危害
            '自杀': 1.0, '自残': 1.0, '自伤': 1.0, '想死': 1.0,
            '打': 0.9, '暴力': 1.0, '掐': 0.9, '推': 0.8,
            '威胁': 1.0, '伤害': 0.9, '报复': 0.9, '恐吓': 0.9,
            '照片': 0.9, '视频': 0.9, '裸聊': 1.0, '私密': 0.9,
            '未成年': 1.0, '15岁': 1.0, '16岁': 1.0, '17岁': 0.9,
            '软禁': 1.0, '限制': 0.9, '夺走': 0.9, '抢走': 0.9,
            '传销': 1.0, '诈骗': 1.0, '犯罪': 0.9, '违法': 0.9,
            '强迫': 1.0, '逼迫': 1.0, '不安全': 0.9, '无套': 0.9
        }
        
        # 短语匹配（更高权重）- 重新设计关键短语
        phrase_matches = {
            # 轻度短语
            '过度理想化': 1.3, '红旗行为': 1.2, '过度焦虑': 1.2,
            '社交圈缩小': 1.2, '自我价值绑定': 1.3, '过度迎合': 1.2,
            
            # 中度短语  
            '金钱不对等': 1.4, '隐瞒关系': 1.4, '改变价值观': 1.4,
            '频繁检查': 1.3, '情绪依赖': 1.3, '牺牲需求': 1.3,
            '疏远亲友': 1.4, '要求下疏远': 1.4,
            
            # 重度短语
            '大额转账': 1.5, '网恋转账': 1.5, '放弃工作': 1.5,
            '脱离支持': 1.5, '跟踪监控': 1.5, '签署文件': 1.4,
            '违法行为': 1.5, '精神操控': 1.5, '情绪勒索': 1.4,
            
            # 危险短语
            '自杀倾向': 1.8, '自残行为': 1.8, '肢体暴力': 1.8,
            '威胁伤害': 1.8, '私密照片': 1.7, '裸聊威胁': 1.8,
            '未成年恋爱': 1.8, '限制自由': 1.7, '软禁跟踪': 1.7,
            '传销诈骗': 1.8, '强迫性行为': 1.8, '暴力犯罪': 1.8
        }
        
        score = 0.0
        
        # 短语匹配检查 - 优先级最高
        for phrase, weight in phrase_matches.items():
            if phrase in user_input and phrase in example:
                score += weight
        
        # 单词匹配检查
        user_words = set(re.findall(r'[\u4e00-\u9fff]+', user_input))
        example_words = set(re.findall(r'[\u4e00-\u9fff]+', example))
        
        common_words = user_words & example_words
        for word in common_words:
            if word in high_weight_keywords:
                score += high_weight_keywords[word]
            else:
                score += 0.15  # 降低普通匹配分数
        
        # 数字匹配（金额相关）- 增强权重
        user_numbers = re.findall(r'\d+', user_input)
        example_numbers = re.findall(r'\d+', example)
        if user_numbers and example_numbers:
            # 检查是否涉及大额金钱
            for num in user_numbers + example_numbers:
                if int(num) >= 10000:  # 万元级别
                    score += 0.8
                elif int(num) >= 1000:  # 千元级别
                    score += 0.6
                else:
                    score += 0.3
        
        # 危险信号特殊检测
        danger_signals = ['自杀', '自残', '自伤', '想死', '暴力', '打', '威胁', '裸聊', '私密照片', 
                         '未成年', '15岁', '16岁', '17岁', '软禁', '限制自由', '传销', '诈骗']
        danger_count = sum(1 for signal in danger_signals if signal in user_input and signal in example)
        if danger_count > 0:
            score += danger_count * 1.5  # 危险信号高权重
        
        # 重度信号检测
        severe_signals = ['大额', '万', '转账', '借钱', '辞职', '放弃工作', '断绝联系', '脱离', '跟踪', '监控']
        severe_count = sum(1 for signal in severe_signals if signal in user_input and signal in example)
        if severe_count > 0:
            score += severe_count * 1.2
        
        # 语句结构相似性
        if ('？' in user_input and '？' in example) or ('，' in user_input and '，' in example):
            score += 0.2
            
        # 情感色彩匹配
        negative_emotions = ['焦虑', '担心', '害怕', '痛苦', '绝望', '崩溃', '失控']
        emotion_match = sum(1 for emotion in negative_emotions if emotion in user_input and emotion in example)
        if emotion_match > 0:
            score += emotion_match * 0.4
            
        return min(score, 3.0)  # 提高最大分数限制
    
    def select_examples(self, user_input: str) -> List[Dict]:
        """
        为用户输入选择最相关的few-shot示例
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            选中的示例列表，包含级别和示例文本
        """
        all_examples = []
        
        # 收集所有示例并计算相似度
        for level, data in self.risk_signals.items():
            for example in data["典型表述"]:
                similarity = self._calculate_similarity(user_input, example)
                all_examples.append({
                    "level": level,
                    "example": example,
                    "similarity": similarity,
                    "signals": data["信号"]
                })
        
        # 按相似度排序并选择top examples
        all_examples.sort(key=lambda x: x["similarity"], reverse=True)
        
        # 确保不同级别的多样性
        selected = []
        used_levels = set()
        
        for example in all_examples:
            if len(selected) >= self.max_examples:
                break
                
            # 优先选择不同级别的示例
            if example["level"] not in used_levels or len(selected) < self.max_examples // 2:
                selected.append(example)
                used_levels.add(example["level"])
        
        return selected[:self.max_examples]
    
    def generate_dynamic_prompt(self, user_input: str, context_summary: str = "") -> str:
        """
        生成包含动态选择示例的prompt
        
        Args:
            user_input: 用户输入
            context_summary: 上下文摘要
            
        Returns:
            优化后的prompt字符串
        """
        selected_examples = self.select_examples(user_input)
        
        # 构建动态few-shot部分
        examples_text = ""
        if selected_examples:
            examples_text = "\n## 相关参考示例\n"
            for example in selected_examples:
                level_map = {"轻度": "0-39", "中度": "40-69", "重度": "70-89", "危险": "90-100"}
                examples_text += f"**{example['level']}({level_map[example['level']]}):** \"{example['example']}\"\n"
        
        prompt = f"""你是"恋爱脑程度识别器"。仔细分析用户的恋爱脑程度，严格按照标准评分，只输出JSON格式。

## 评分标准
- **轻度(0-39):** 情绪焦虑、过度解读对方行为
- **中度(40-69):** 经济付出、隐瞒关系、改变习惯  
- **重度(70-89):** 大额转账、重大人生决定、自伤想法
- **危险(90-100):** 暴力威胁、违法行为、控制人身自由
{examples_text}
## 输出格式
{{"index":0-100,"level":"轻|中|重|危","signals":["具体风险信号"],"switch_to_help":true|false}}

switch_to_help规则：轻度/中度=false，重度/危险=true

用户发言：{user_input}
上下文提要：{context_summary}"""
        
        return prompt

# 使用示例
if __name__ == "__main__":
    selector = ExampleSelector(max_examples=2)
    
    test_inputs = [
        "他今天没回我消息，是不是不爱我了？",
        "我每个月给他2000生活费",
        "网恋三个月他要我转账5万",
        "他不让我和朋友联系"
    ]
    
    for user_input in test_inputs:
        print(f"\n用户输入: {user_input}")
        examples = selector.select_examples(user_input)
        print("选中的示例:")
        for ex in examples:
            print(f"  {ex['level']}: {ex['example']} (相似度: {ex['similarity']:.2f})")
        
        print("\n生成的prompt:")
        print(selector.generate_dynamic_prompt(user_input)[:200] + "...")
