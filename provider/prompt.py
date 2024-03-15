
# 基础prompt
base_prompt = """
根据用户给出的OCR后的内容，识别出是否包含1份或多份的水费或电费的收费通知信息，
1.如果包含电费信息，提取并记录以下要素：
-费用类型（Type）: 固定为："电费"
-抄表日期（Date）: 抄表日期或截止日期
-本次读数（Current reading）
-上次读数（Last reading）
-倍比（Multiplier）：自然数，默认为：1
-用量（Usage）: 数字，优先直接提取；如没有，则按此算式计算:(本地读数或止度 - 上次读数或起度) * 倍比
-电费单价（Unit price）
-电费总金额（Total amount）
-电费附加费用（Additional fees）: 数字，非文字
 2.如果包含水费信息，提取并记录以下要素：
-费用类型（Type）: 固定为："水费"
-水费抄表日期（Date）: 水费抄表日期或截止日期
-本次读数（Current reading）
-上次读数（Last reading）
-用量（Usage）
-水费总价（Total amount）

注意：
-同一张图片，可能同时包含多个水费和电费信息
-仅输出JSON数组，不包含其他文字。
"""

# 根据不同的每个LLM的习性，额外增加定制化的prompt
gemini_prompt = """
"""