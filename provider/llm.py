import json
import os
import time
import re
from enum import Enum
from opencc import OpenCC
from dateutil import parser

from provider.llm_azure import LLMAzureOpenAI
from provider.llm_azure_stream import LLMAzureOpenAIStream
from provider.llm_gemini import LLMGemini
from provider.llm_moonshot import LLMMoonshot
from provider.llm_openai import LLMOpenAI
from provider.llm_rpa_chatgpt import ChatGPTRPA
from web.extractor import get_prompt_template


class Channel(Enum):
    MOCK = 1
    RPA = 2
    GPT4 = 4
    GPT35 = 3
    GEMINI_PRO = 5
    AZURE_OPENAI = 6
    MOONSHOT = 7


# 取环境变量LLM_MODEL的值，如果没有，则默认为GPT4
channel = Channel(int(os.getenv("LLM_MODEL", Channel.GPT4.value)))


def switch_channel(new_channel):
    global channel
    channel = Channel(new_channel)


def is_number(value):
    return isinstance(value, (int, float))


def before_extract(text):
    return text


# 定义函数，处理json字符串不合法的情况
def remove_illegal(json_str):
    # 定义一个函数，该函数用于计算表达式并返回结果
    def eval_expression(match):
        expression = match.group(2).strip()  # 移除头尾的空白字符，包括换行符
        try:
            # 计算表达式的值
            result = eval(expression)
            # 将结果格式化为保留两位小数的字符串
            result = f"{result:.2f}"
            # 返回替换字符串，即字段名和计算后的结果
            return f'{match.group(1)}: {result}'
        except Exception as e:
            print(f"Error evaluating expression '{expression}': {e}")
            return match.group(0)  # 发生错误时返回原始匹配字符串

    # 使用正则表达式查找并替换表达式
    pattern = re.compile(r'("Total amount"|"Additional fees"|"Usage"): ([\d\.\s\+\-\*]+)', re.MULTILINE)
    updated_string = pattern.sub(eval_expression, json_str)

    return updated_string


def after_extract_electricity(ret):
    # 遍历列表，item如果没有Usage，则通过计算获取
    new_order = ['Type', 'Date', 'Current reading', 'Last reading', 'Usage', 'Multiplier', 'Unit price', 'Total amount',
                 'Additional fees']
    for i, item in enumerate(ret):
        if "Usage" not in item:
            # 校验是否为空
            if "Current reading" not in item or "Last reading" not in item or "Multiplier" not in item:
                continue

            try:
                # 如果item["Current reading"]和item["Last reading"]不是数字，则跳过
                if not item["Current reading"].replace(".", "").isdigit() \
                        or not item["Last reading"].replace(".", "").isdigit() or not \
                        item["Multiplier"].replace(".", "").isdigit():
                    continue

                # 将item["Current reading"]和item["Last reading"]转换为数字
                item["Current reading"] = float(item["Current reading"])
                item["Last reading"] = float(item["Last reading"])
                # 如果item["Multiplier"]不存在，则默认为1
                item["Multiplier"] = float(item.get("Multiplier", 1))
                item["Usage"] = round((item["Current reading"] - item["Last reading"]) * item["Multiplier"], 1)
            except Exception as e:
                print(f"计算Usage出错：{e}")
                continue

            ret[i] = {key: item[key] for key in new_order if key in item}

    return ret


def get_chs_info():
    chs_info = {
        "Type": "费用类型",
        "Date": "抄表日期",
        "Current reading": "本次读数",
        "Last reading": "上次读数",
        # "Usage": "用量",
        "Multiplier": "倍率",
        "Unit price": "单价",
        "Electricity fee": "电费",
        "Water fee": "水费",
        "Sewage charge": "排污费",
        "Energy charge": "电损",
        "Additional fees": "附加费用",
    }

    chs_info = {
        "Order number": "订单号",
        "Date": "送货时间",
        "Product code": "产品代码",
        "Product name": "产品描述",
        "Amount due": "应收金额",
        "Quantity": "数量",
    }

    return chs_info


# 后处理
def after_extract(result):
    # 提取字符串中的json数组部分
    result = result[result.find('['):result.rfind(']') + 1]
    # 去除 JSON 字符串中的单行注释
    result = re.sub(r'//.*', '', result)
    # 去除usage产生的可能错误的JSON字符串
    result = re.sub(r'^.*?"Usage": .*? - .*(?=\n|$)', '', result, flags=re.MULTILINE)
    # 处理 JSON 字符串中的算术表达式
    result = remove_illegal(result)

    try:
        ret = json.loads(result)
    except Exception as e:
        print(f"json.loads出错：{e}")
        return """ {"Doc Type": "json.loads出错"}"""

    # 将英文key 转换为中文
    # chs_info = get_chs_info()
    # for i, item in enumerate(ret):
    #     transformed_ret = {
    #         chs_info[key]: value
    #         for key, value in item.items()
    #         if key in chs_info  # and value is not None and value != ""
    #     }
    #
    #     ret[i] = transformed_ret

    return json.dumps(ret, ensure_ascii=False, indent=4)


# 入口，包括事前、事中、事后处理
def extract_bill(text, text_id="", socket_io=None):
    # 事前
    ret = before_extract(text)

    # 事中
    ret = extract(ret, text_id, socket_io)

    # 事后
    return after_extract(ret)


def extract(text, text_id="", socket_io=None):
    if channel == Channel.MOCK:
        # 模拟延时，睡眠1秒
        time.sleep(1)
        return """[
            {
                "Type": "电费",
                "Date": "2023/12/25",
                "Current reading": 11727,
                "Last reading": 11403.67,
                "Multiplier": 1,
                "Usage": 323.33,
                "Unit price": 0.008,
                "Total amount": 190.11,
                "Additional fees": 9.05
            }
        ]
    """

    base_prompt = get_prompt_template()
    print("使用prompt template：\n", base_prompt)

    if channel == Channel.RPA:
        rpa = ChatGPTRPA()
        return rpa.generate_text(text, base_prompt, text_id)

    if channel == channel.GPT35:
        return LLMOpenAI("gpt-3.5-turbo-1106", True, socket_io).generate_text(text, base_prompt, text_id)

    if channel == channel.GPT4:
        return LLMOpenAI("gpt-4-turbo-preview", True, socket_io).generate_text(text, base_prompt, text_id)

    if channel == channel.GEMINI_PRO:
        return LLMGemini("gemini-pro").generate_text(text, base_prompt, text_id)

    if channel == channel.AZURE_OPENAI:
        return LLMAzureOpenAIStream(True, socket_io).generate_text(text, base_prompt, text_id)

    if channel == channel.MOONSHOT:
        return LLMMoonshot("moonshot-v1-8k", True, socket_io).generate_text(text, base_prompt, text_id)
    return """ {"Doc Type": "LLM配置错误"}"""


def get_half(text):
    lines = text.splitlines()
    half_line_count = len(lines) // 2
    first_half_lines = lines[:half_line_count]
    second_half_lines = lines[half_line_count::]
    return '\n'.join(first_half_lines), '\n'.join(second_half_lines)


def convert_date(date_str):
    if date_str is None:
        return date_str

    try:
        # 解析日期字符串
        dt = parser.parse(date_str)
        # 格式化为 YYYY-MM-DD
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return date_str


def contain_keywords(text, excludes):
    # 将关键词列表转换为正则表达式
    # 使用 \s* 来匹配关键词中可能存在的空格或换行符
    keywords_pattern = '|'.join([keyword.replace(" ", r"\s*") for keyword in excludes])
    pattern = re.compile(keywords_pattern, re.IGNORECASE)

    ret = pattern.search(text)
    return bool(ret)
