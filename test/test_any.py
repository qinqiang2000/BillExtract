import re

input_string = '''
[
  {
    "Type": "水费",
    "Date": "2023.01.11-2024.02.10",
    "Current reading": 31975,
    "Last reading": 31673,
    "Usage": 302,
    "Total amount": 1057.00
  },
  {
    "Type": "电费",
    "Date": "2024.01.23-2024.02.22",
    "Current reading": 50790,
    "Last reading": 50383,
    "Usage": 407,
    "Multiplier": 400/5,
    "Unit price": 0.7100,
    "Total amount": 23811.13,
    "Additional fees": 32560 * 0.03
  }
]
'''

# 定义一个函数，该函数用于计算表达式并返回结果
def eval_expression(match):
    expression = match.group(2).strip()  # 移除头尾的空白字符，包括换行符
    try:
        # 计算表达式的值
        result = eval(expression)
        # 返回替换字符串，即字段名和计算后的结果
        return f'{match.group(1)}: {result}'
    except Exception as e:
        print(f"Error evaluating expression '{expression}': {e}")
        return match.group(0)  # 发生错误时返回原始匹配字符串

# 使用正则表达式查找并替换表达式
pattern = re.compile(r'("Total amount"|"Additional fees"|"Multiplier"): ([\d\.\s\+\-\*\/]+)', re.MULTILINE)
updated_string = pattern.sub(eval_expression, input_string)

print(updated_string)
