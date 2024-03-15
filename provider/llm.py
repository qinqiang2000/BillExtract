import json
import os
import time
import re
from enum import Enum
from opencc import OpenCC
from dateutil import parser

from provider.llm_azure import LLMAzureOpenAI
from provider.llm_gemini import LLMGemini
from provider.llm_moonshot import LLMMoonshot
from provider.llm_openai import LLMOpenAI
from provider.llm_rpa_chatgpt import ChatGPTRPA
from provider.prompt import base_prompt


class Channel(Enum):
    MOCK = 1
    RPA = 2
    GPT4 = 3
    GPT35 = 4
    GEMINI_PRO = 5
    AZURE_OPENAI = 6
    MOONSHOT = 7


# 取环境变量LLM_MODEL的值，如果没有，则默认为GPT4
channel = Channel(int(os.getenv("LLM_MODEL", Channel.GPT4.value)))


def switch_channel(new_channel):
    global channel
    channel = Channel(new_channel)


def before_extract(text):
    return text


# 后处理
def after_extract(result):
    try:
        ret = json.loads(result)
    except Exception as e:
        print(f"json.loads出错：{e}")
        return """ {"Doc Type": "json.loads出错"}"""

    # 遍历列表，item如果没有Usage，则通过计算获取
    new_order = ['Type', 'Date', 'Current reading', 'Last reading', 'Usage', 'Unit price', 'Total amount', 'Additional fees']
    for i, item in enumerate(ret):
        if "Usage" not in item:
            # 将item["Current reading"]和item["Last reading"]转换为数字
            item["Current reading"] = float(item["Current reading"])
            item["Last reading"] = float(item["Last reading"])
            # 如果item["Multiplier"]不存在，则默认为1
            item["Multiplier"] = float(item.get("Multiplier", 1))

            item["Usage"] = round((item["Current reading"] - item["Last reading"]) * item["Multiplier"], 1)
            # 调整 Usage在item中的位置，放在Date之后
            ret[i] = {key: item[key] for key in new_order if key in item}

    chs_info = {
        "Type": "费用类型",
        "Date": "抄表日期",
        "Current reading": "本次读数",
        "Last reading": "上次读数",
        "Usage": "用量",
        "Unit price": "单价",
        "Total amount": "总价",
        "Additional fees": "电费附加费用",
    }

    # 将英文key 转换为中文
    for i, item in enumerate(ret):
        transformed_ret = {
            chs_info[key]: value
            for key, value in item.items()
            if key in chs_info  # and value is not None and value != ""
        }

        ret[i] = transformed_ret

    return json.dumps(ret, ensure_ascii=False, indent=4)


# 入口，包括事前、事中、事后处理
def extract_invoice(text, text_id=""):
    # 事前
    ret = before_extract(text)

    # 事中
    ret = extract(ret, text_id)

    # 事后
    return after_extract(ret)


def extract(text, text_id=""):
    if channel == Channel.MOCK:
        # 模拟延时，睡眠1秒
        time.sleep(1)
        return """[
          {
            "Type": "电费",
            "Date": "2024-01",
            "Current reading": "3230.42",
            "Unit price": 1.017,
            "Total price": 35325.19,
            "Additional fees": null
          },
          {
            "Type": "水费",
            "Date": "2024-01",
            "Total price": 889.20
          },
          {
            "Type": "电费",
            "Date": "2024-01",
            "Current reading": "58",
            "Unit price": 1.017,
            "Total price": 394.60,
            "Additional fees": null
          }
        ]
    """

    if channel == Channel.RPA:
        rpa = ChatGPTRPA()
        return rpa.generate_text(text, base_prompt, text_id)

    if channel == channel.GPT35:
        return LLMOpenAI("gpt-3.5-turbo-1106").generate_text(text, base_prompt, text_id)

    if channel == channel.GPT4:
        return LLMOpenAI("gpt-4-1106-preview").generate_text(text, base_prompt, text_id)

    if channel == channel.GEMINI_PRO:
        return LLMGemini("gemini-pro").generate_text(text, base_prompt, text_id)

    if channel == channel.AZURE_OPENAI:
        return LLMAzureOpenAI().generate_text(text, base_prompt, text_id)

    if channel == channel.MOONSHOT:
        return LLMMoonshot("moonshot-v1-8k").generate_text(text, base_prompt, text_id)
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
