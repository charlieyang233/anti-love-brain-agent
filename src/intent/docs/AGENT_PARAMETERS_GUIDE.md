# Agent参数传递详解

## 🎯 **回答您的问题**

**Q: 目前如果是交给Agent来处理的话，意图识别分类器会传递什么样的参数？**

**A: 经过优化后，系统现在为Agent提供结构化的增强参数，包含6大类信息：**

---

## 📦 **完整参数结构**

### **1️⃣ 意图分析 (intent_analysis)**
```json
{
  "routing_path": "reference",        // 路由路径类型
  "confidence": 0.6,                  // 置信度 (0-1)
  "processing_time_ms": 0.22,         // 处理时间
  "rule_triggered": null,             // 触发的具体规则
  "context_aware": false,             // 是否需要上下文
  "bypass_agent": null                // 是否绕过Agent
}
```

### **2️⃣ 内容分析 (content_analysis)**
```json
{
  "matched_keywords": {               // 匹配的关键词详情
    "help_words": ["怎么办"],
    "medium_risk": ["控制"],
    "romance_self": ["男朋友"]
  },
  "keyword_coverage": 1.0,            // 关键词覆盖率
  "text_complexity": "simple",        // 文本复杂度
  "text_length": 14,                  // 文本长度
  "question_marks": 1,                // 问号数量
  "exclamation_marks": 0              // 感叹号数量
}
```

### **3️⃣ 上下文信号 (context_signals)**
```json
{
  "risk_level": "medium",             // 风险等级
  "romance_context": {                // 恋爱上下文
    "subject": "self",                // 主体 (self/other/unknown)
    "behaviors": [],                  // 行为列表
    "emotions": []                    // 情绪列表
  },
  "help_intent": true,                // 是否有求助意图
  "emotion_intensity": 0.1,           // 情绪强度 (0-1)
  "matched_patterns": [               // 匹配的模式
    "medium_risk", "self_romance", "help_seeking"
  ],
  "confidence_factors": {             // 置信度因子
    "risk_detection": 0.7,
    "romance_self": 0.8,
    "help_intent": 0.9
  }
}
```

### **4️⃣ Agent指导 (agent_guidance)**
```json
{
  "suggested_tools": ["talk_tool", "help_tool"],  // 建议工具
  "reasoning": "检测到medium风险等级的复杂情况...",  // 推理说明
  "priority_aspects": [                           // 优先方面
    "风险评估", "情感支持", "自我保护意识"
  ],
  "avoid_aspects": ["直接建议分手"],               // 避免方面
  "response_tone": "caring_cautious",             // 回应语调
  "safety_level": "alert"                        // 安全级别
}
```

### **5️⃣ 记忆上下文 (memory_context)**
```json
{
  "recent_topics": ["工作", "压力"],     // 最近话题
  "user_emotional_state": "negative",   // 用户情绪状态
  "conversation_flow": "seeking_help",   // 对话流程
  "context_continuity": true            // 上下文连续性
}
```

### **6️⃣ 技术元数据 (technical_meta)**
```json
{
  "router_version": "dual_layer_v2_enhanced",  // 路由器版本
  "fallback_reason": null,                     // 兜底原因
  "performance_stats": {                       // 性能统计
    "token_saved": false,                      // 是否节省token
    "routing_efficiency": 0.7,                 // 路由效率
    "optimization_level": "medium"             // 优化级别
  },
  "debug_info": {                             // 调试信息
    "signals": ["risk_detection", "romance_self"]
  }
}
```

---

## 🎭 **两种Agent调用场景**

### **场景1: 参考信号指导 (reference路由)**
- **何时触发**: 检测到复杂情况但有明确信号
- **传递内容**: 完整的6类参数
- **Agent行为**: 参考信号和指导进行智能决策
- **示例**: "我男朋友总是控制我" → 中等风险+恋爱上下文+求助意图

### **场景2: 兜底处理 (fallback路由)**
- **何时触发**: 无明确模式匹配
- **传递内容**: 基础参数+兜底原因
- **Agent行为**: 通用处理逻辑
- **示例**: "感情问题很复杂" → 无明确关键词匹配

---

## 🚀 **Agent如何使用这些参数**

### **风险防护**
```python
# 根据风险等级调整安全措施
risk = params['context_signals']['risk_level']
if risk == 'high':
    enable_emergency_protocols()
elif risk == 'medium':
    enable_caution_mode()
```

### **个性化回应**
```python
# 根据语调建议调整回应风格
tone = params['agent_guidance']['response_tone']
if tone == 'caring_cautious':
    set_empathetic_mode()
elif tone == 'serious_supportive':
    set_professional_mode()
```

### **策略指导**
```python
# 根据优先方面调整回应重点
priorities = params['agent_guidance']['priority_aspects']
if '风险评估' in priorities:
    focus_on_safety_analysis()
if '情感支持' in priorities:
    provide_emotional_support()
```

### **上下文连贯**
```python
# 考虑历史话题保持连贯性
recent_topics = params['memory_context']['recent_topics']
if '工作' in recent_topics and '压力' in recent_topics:
    acknowledge_work_stress_context()
```

---

## 📊 **参数价值总结**

| 参数类别 | 价值 | 应用场景 |
|---------|------|----------|
| **意图分析** | 理解处理复杂度和置信度 | 决定回应确定性 |
| **内容分析** | 精确理解用户关注点 | 定制回应内容 |
| **上下文信号** | 情境感知和风险评估 | 安全防护措施 |
| **Agent指导** | 具体的策略建议 | 回应策略选择 |
| **记忆上下文** | 历史连贯性 | 保持对话自然 |
| **技术元数据** | 性能和调试信息 | 系统优化 |

---

## 🎯 **核心优势**

1. **🔍 精准理解**: 通过关键词匹配和模式识别，准确理解用户意图
2. **🛡️ 安全防护**: 风险等级和安全级别指导，确保用户安全
3. **🎨 个性化**: 语调建议和策略指导，提供个性化回应
4. **🔄 连贯性**: 历史话题和情绪状态，保持对话连贯
5. **⚡ 高效**: 路由效率和优化级别，提升处理效率
6. **🔧 可调试**: 完整的技术元数据，便于系统优化

**💡 总结**: 现在的意图识别分类器不再只是简单的文本传递，而是为Agent提供了一个结构化、全面的"用户画像+处理指南"，让Agent能够更智能、更安全、更个性化地响应用户需求。
