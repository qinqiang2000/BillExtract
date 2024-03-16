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
            stream = client.chat.completions.create(
                model=os.environ['OPENAI_DEPLOYMENT_NAME'],  # model = "deployment_name"
                # response_format={"type": "json_object"},
                temperature=0,
                stream=True,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": text}
                ]
            )
        except Exception as e:
            print(f"调用openai出错：{e}")
            return json.dumps({"error": "fail: 调用大模型接口出错"})

        # print("total tokens:", response.usage.total_tokens)
        # print(response.choices[0].message.content)

        ret = ""
        for chunk in stream:
            if len(chunk.choices) == 0:
                continue
            if chunk.choices[0].delta.content is not None:
                ret += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="")

        return ret


text = """
聚龙大厦缴费通知书
缴费单位:杭州肯德基有限公司
建筑面积:3391.88㎡²
内容:
1、1月份水费:743.82元
2、1月份电费:19046.19元
共付金额:19790.01元
请贵公司在此通知书发出后15日内前来大厦物管处缴纳
如有疑问,请与物业公司管理处联系
电话:28918868 28918869
注:物业管理收费说明:总建筑面积3391.88㎡×10元×3个月
水电费收费见《水电缴费明细表》
杭州聚龙物业管理有限公司
聚龙大厦管理处
2024年2月26日
"""
result = LLMAzureOpenAI().generate_text(text, base_prompt, "")
print(result)
result1 = """
 [
  {
    "Type": "电费",
    "Date": "02/03",
    "Current reading": null,
    "Last reading": null,
    "Usage": null,
    "Multiplier": null,
    "Unit price": null,
    "Total amount": 3642.66 + 243.52 + 2453.40 + 1837.44 + 1260.63 + 1007.04 + 313.35 + 144.00 + 457.57 + 10.13 + 22.50 + 39.60 + 171.00 + 2.70,
    "Additional fees": null
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
for i, item in enumerate(ret):
    if "Usage" not in item:
        # 校验是否为空
        if "Current reading" not in item or "Last reading" not in item or "Multiplier" not in item:
            continue

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
