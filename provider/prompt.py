
electricity_water_prompt = """
根据用户给出的OCR后的内容，识别出是否包含1份或多份的水费或电费的收费通知信息，
1.如果是电费信息，提取并记录以下要素：
-费用类型（Type）: 固定为："电费"
-抄表日期（Date）: 抄表日期或截止日期
-本次读数（Current reading）
-上次读数（Last reading）
-倍比/倍率（Multiplier）：数字
-电费单价（Unit price）
-电费（Electricity fee）：优选电费总计、电费小计或类似描述的字段；
-电费附加费用（Additional fees）: 数字，非文字
-电损/能源处理费/统源服务费（Energy charge）: 数字，非文字
 2.如果是水费信息，提取并记录以下要素：
-费用类型（Type）: 固定为："水费"
-水费抄表日期（Date）: 水费抄表日期或截止日期
-本次读数（Current reading）
-上次读数（Last reading）
-水费（Water fee）: 优选水费总计、水费小计或类似描述的字段；
-排污费/污水处理费（Sewage charge）: 数字，非文字

注意：
-OCR的结果可能有误，比如“水费”识别成“本费”或“水衢”、“能源附加费”识别成“统源附加费”等，你需要结合上下文语义进行综合判断，以抽取准确的关键信息
-只有一个字段也要输出，不要求全部字段都有
-不明确的字段不要输出
-同一张图片，可能同时包含多个水费和电费信息
-碰到用电的峰/平/谷时段或多个电表，合并成用总的电费信息
-垃圾处理费、污水处理费、排污费属于水费的一部分，请放入水费的要素
-Energy charge属于电费的一部分，不要分开输出，请放入电费的要素
-不要输出算式，要将算式计算后在输出
-仅输出JSON数组，不包含其他文字。
"""

delivery_prompt = """
根据用户给出的OCR后的送货单内容，识别出送货单的详细要素，包括：
-订单号(Order number)：订单号
-产品代码(Product code)：产品代码, 4位数字的产品代码，其他长度不是
-产品描述(Product name)：产品描述或名称
-应收金额(Amount due)：应收金额
-数量(Quantity)：数量

注意：
-OCR的结果可能有误，你需要结合上下文语义进行综合判断，以抽取准确的关键信息
-仅输出JSON一维数组，不包含其他文字。
"""

delivery_schema_prompt = """
根据用户给出的OCR后的送货单内容，识别出送货单的详细要素，要素的json schema：
[
"name": "送货单",
"description": "固定为送货单"
"properties": {
      "订单号": {
        "type": "string",
        "description": "订单号"
      },
      "产品代码": {
        "type": "string",
        "description": "产品代码，是提取长度为4的代码"
      },
      "数量": {
        "type": "string",
        "description": "数量"
      },
      "应收金额": {
        "type": "string",
        "description": "应收金额"
      }
}]

注意：
-OCR的结果可能有误，你需要结合上下文语义进行综合判断，以抽取准确的关键信息
-仅按json schema输出JSON一维数组，不包含其他文字。
"""
# 基础prompt
base_prompt = delivery_schema_prompt

# 根据不同的每个LLM的习性，额外增加定制化的prompt
gemini_prompt = """
"""
moonshot_prompt = base_prompt + """
-检查输出字符串，要求符合json格式
"""