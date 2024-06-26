import json
from dotenv import load_dotenv
from openai import OpenAI
from provider.prompt import base_prompt


load_dotenv(override=True)
client = OpenAI()


class LLMOpenAI:
    def __init__(self, model):
        self.model = model

    def generate_text(self, text, sys_prompt, reqid):
        print("使用模型API：", self.model, reqid)
        try:
            stream = client.chat.completions.create(
                model=self.model,
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

        ret = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                ret += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="")

        return ret


text = text = """
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
result = LLMOpenAI("gpt-4-turbo-preview").generate_text(text, base_prompt, "")
print(result)