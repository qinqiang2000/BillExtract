import os
import re

from dotenv import load_dotenv
from openai import AzureOpenAI
import json
from provider.prompt import base_prompt

load_dotenv(override=True)


# 去除 JSON 字符串中的单行注释
def remove_comments(json_str):
    # 使用正则表达式匹配以 // 开头的注释，并去除这些注释
    # 注意：这可能会误删除字符串内部包含 // 的情况
    no_comments = re.sub(r'//.*', '', json_str)
    return no_comments


client = AzureOpenAI(
    api_key=os.environ['AZURE_OPENAI_API_KEY'],
    api_version=os.environ['OPENAI_API_VERSION'],
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT']
    )


class LLMAzureOpenAI:
    def generate_text(self, text, sys_prompt, reqid):
        print("使用模型【Azure OpenAI】", os.environ['OPENAI_DEPLOYMENT_NAME'], reqid)
        try:
            response = client.chat.completions.create(
                model=os.environ['OPENAI_DEPLOYMENT_NAME'],  # model = "deployment_name"
                # response_format={"type": "json_object"},
                temperature=0,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": text}
                ]
            )
        except Exception as e:
            print(f"调用openai出错：{e}")
            return json.dumps({"error": "fail: 调用大模型接口出错"})

        print("total tokens:", response.usage.total_tokens)
        # print(response.choices[0].message.content)

        return response.choices[0].message.content


text = """
吉林万瑞城购物休闲广场
肯德基世纪广场餐厅水、电费付款通知(1月)
抄表日期
2024年1月31日
电表号220652008540
项目
时刻
期初读数
期末读数
倍率
单价
金额
电损费
合计
尖
443.36
497.51
80
1.356133
5874.77
1.02
5992.26
峰
2553.11
2717.15
80
1.143265
15003.30
1.02
15303.36
电费
平
3064.54
3306.47
80
0.788485
15260.65
1.02
15565.87
谷
959.46
1055.73
80
0.433705
3340.22
1.02
3407.03
水费
11550
11694
1
6.85
986.40
/
986.4
合计
41254.92
制表人:杨忠波
万瑞城负责人确认签字:
肯德基负责人确认签字:
备注:因系统四舍五入,请款金额请以发票为准。
"""
# result = LLMAzureOpenAI().generate_text(text, base_prompt, "")
# print(result)
result="""
 [
  {
    "Type": "电费",
    "Date": "2024年1月31日",
    "Current reading": "497.51",
    "Last reading": "443.36",
    "Multiplier": 80,
    "Usage": (497.51 - 443.36) * 80,
    "Unit price": "1.356133",
    "Total amount": "5874.77",
    "Additional fees": "1.02"
  },
  {
    "Type": "电费",
    "Date": "2024年1月31日",
    "Current reading": "2717.15",
    "Last reading": "2553.11",
    "Multiplier": 80,
    "Usage": (2717.15 - 2553.11) * 80,
    "Unit price": "1.143265",
    "Total amount": "15003.30",
    "Additional fees": "1.02"
  },
  {
    "Type": "电费",
    "Date": "2024年1月31日",
    "Current reading": "3306.47",
    "Last reading": "3064.54",
    "Multiplier": 80,
    "Usage": (3306.47 - 3064.54) * 80,
    "Unit price": "0.788485",
    "Total amount": "15260.65",
    "Additional fees": "1.02"
  },
  {
    "Type": "电费",
    "Date": "2024年1月31日",
    "Current reading": "1055.73",
    "Last reading": "959.46",
    "Multiplier": 80,
    "Usage": (1055.73 - 959.46) * 80,
    "Unit price": "0.433705",
    "Total amount": "3340.22",
    "Additional fees": "1.02"
  },
  {
    "Type": "水费",
    "Date": "2024年1月31日",
    "Current reading": "11694",
    "Last reading": "11550",
    "Usage": 11694 - 11550,
    "Total amount": "986.40"
  }
]
"""

# 取出被```json和```包裹的JSON字符串
result = result[result.find('['):result.rfind(']') + 1]
print("json string:", result)

# 去除注释
result = remove_comments(result)
print("clean json string:", result)

# 去除usage产生的可能错误的JSON字符串
result = re.sub(r'^.*?"Usage": .*? - .*(?=\n|$)', '', result, flags=re.MULTILINE)
print("clean Usage:", result)

ret = json.loads(result)
# 遍历列表，item如果没有Usage，则通过计算获取
for item in ret:
    if "Usage" not in item:
        # 将item["Current reading"]和item["Last reading"]转换为数字
        item["Current reading"] = float(item["Current reading"])
        item["Last reading"] = float(item["Last reading"])
        # 如果item["Multiplier"]不存在，则默认为1
        item["Multiplier"] = float(item.get("Multiplier", 1))

        item["Usage"] = round((item["Current reading"] - item["Last reading"]) * item["Multiplier"], 1)

# 使用集合去除重复项
unique_items = set(json.dumps(item, sort_keys=True) for item in ret)
# 将去重后的JSON字符串转换回字典
unique_ret = [json.loads(item) for item in unique_items]

print(unique_ret)
