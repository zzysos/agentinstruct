import openai
from langchain.prompts import ChatPromptTemplate
from langchain.utilities import WikipediaAPIWrapper
from langchain.utilities import MetaphorSearchAPIWrapper
import os
from langchain.document_loaders import WebBaseLoader
from langchain.chat_models import ChatOpenAI
# def get_links(search_metadata):
#     links = []
#     for result in search_metadata:
#         links.append(result["url"])
#     return links
#
# os.environ["METAPHOR_API_KEY"] = "8bdc2664-0f69-4f2b-ab9c-4ea0f027d199"
# search=MetaphorSearchAPIWrapper()
# search_metadata=search.results(query='IMDB Movie Reviews dataset',num_results=5)
# print(search_metadata)

template_string = """把由三个反引号分隔的文本\
翻译成一种{style}风格。\
文本: ```{text}```
"""
prompt_template = ChatPromptTemplate.from_template(template_string)
customer_style = """正式普通话 \
用一个平静、尊敬的语气
"""

customer_email = """
嗯呐，我现在可是火冒三丈，我那个搅拌机盖子竟然飞了出去，把我厨房的墙壁都溅上了果汁！
更糟糕的是，保修条款可不包括清理我厨房的费用。
伙计，赶紧给我过来！
"""

# 使用提示模版
# customer_messages = prompt_template.format_messages(
#                     style=customer_style,
#                     text=customer_email)
# open_ai_key='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'
#
# chat=ChatOpenAI(openai_api_key=open_ai_key)
# print(chat(customer_messages))
original_string = "This is a New Instructions example11 1111."

# 找到子字符串的位置
# substring = "New Instructions"
# index = original_string.find(substring)
#
# # 如果找到了，截取后面的字符串
# if index != -1:
#     result = original_string[index + len(substring):]
#     print(result)
# else:
#     print("Subtring not found.")

multiline_string = """This is line 1.
This is line 2.
This is line 3.
"""

# 指定文件路径
file_path='../instructions/myinstructions/boolQ_instr.txt'
#
# # 将多行字符串写入文件
# with open(file_path, "w") as file:
#     file.write(multiline_string)

with open(file_path, "r") as file:
    ttx=file.read()

print(ttx)