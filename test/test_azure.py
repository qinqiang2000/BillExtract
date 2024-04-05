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
[print]
南京百事可乐饮料有限公司送货单
2022-12-30
订单号
开单时间
K1144044
装车单号
793434
12-S1
2022-12-30
区号
TZR9 分销客户:
送货时间
发票类型
现结/普票
联系人
徐凤华/15295250082
K02492/海陵区润银酒业商行
备注
址
泰州市海陵区兴丰西路7号1幢24、26室
单位
数量
单价
产品描述
金额
单价
整车
实物
应收
备注
产品
代码
(元)
折扣(元)
折扣(元)折扣(元)金额(元)
330ML百事*24
箱
20
46
920
191.36
0
6924882486100
1231
0
728.64
1313
500ML+100ML美橙促销装*24
箱
17
58
986
186.57
0
799.43
6924882496215
0
●
1317
500ML+100ML美青促销装*24
箱
19
58
1102
208.52
0
0
893.48
6924882496611
0.6L美西瓜促销装*24
箱
6924882496550
1320
21
58
1218
230.47
0
0
987.53
6924882496116
1371
500ML+100ML百事促销装*24
箱
253
58
14674
2776.67
0
0
11897.33
6924882446104
1601
2.0L百事*6
箱
150
36
5400
1227.15
0
0
4172.85
6924882446609
1603
2.0L美橙*6
箱
20
36
720
163.62
0
0
556.38
合计:
500箱0瓶
25,020.004,984.36
0.00
0
20,035.64
本期空桶回收
银行卡号
收货详情
本期空瓶回收
驾驶员签字
ORD
收货单位签章
日期
第二联:绿色结算联
第三联:红色 客户
第四联:黄
第一联:白色财务联

[handwritten]
z
随水华
"""
result = LLMAzureOpenAI().generate_text(text, base_prompt, "")
print(result)
exit()
result = """
```json
[
  {
    "Order number": "K1144044",
    "Product code": "1231",
    "Product name": "330ML百事*24",
    "Amount due": "728.64",
    "Quantity": "20"
  },
  {
    "Product code": "1313",
    "Product name": "500ML+100ML美橙促销装*24",
    "Amount due": "799.43",
    "Quantity": "17"
  },
  {
    "Product code": "1317",
    "Product name": "500ML+100ML美青促销装*24",
    "Amount due": "893.48",
    "Quantity": "19"
  },
  {
    "Product code": "1320",
    "Product name": "0.6L美西瓜促销装*24",
    "Amount due": "987.53",
    "Quantity": "21"
  },
  {
    "Product code": "1371",
    "Product name": "500ML+100ML百事促销装*24",
    "Amount due": "11897.33",
    "Quantity": "253"
  },
  {
    "Product code": "1601",
    "Product name": "2.0L百事*6",
    "Amount due": "4172.85",
    "Quantity": "150"
  },
  {
    "Product code": "1603",
    "Product name": "2.0L美橙*6",
    "Amount due": "556.38",
    "Quantity": "20"
  }
]
```
"""

# 取出被```json和```包裹的JSON字符串
# result = result[result.find('['):result.rfind(']') + 1]
# Define the regular expression pattern to match JSON blocks
pattern = r"```json(.*?)```"
# Find all non-overlapping matches of the pattern in the string
matches = re.findall(pattern, result, re.DOTALL)
result = matches[0]
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
