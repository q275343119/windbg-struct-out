import json
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv('.env',override=True)

# ✅ 替换为你的 DeepSeek API Key
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# 初始化 DeepSeek 模型（OpenAI 兼容接口）
llm = ChatOpenAI(
    model_name="deepseek-coder",
    openai_api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    temperature=0
)

# ------------------------------
# Prompt 模板
# ------------------------------
PROMPT_TEMPLATE = """
你在 windbg 中运行命令：
{cmd}

会产生如下输出文本：

{output_text}


请你编写一个 Python 函数，函数名为 {func_name}，
函数输入为 text (字符串)，输出为一个 dict，
字段包括：
{fields}

要求：
1. 使用字符串操作或正则提取
2. 如果字段不存在则返回 None
3. 返回值必须是一个 dict
4. 只返回函数代码本身，不要解释

请直接输出函数代码：
"""

prompt = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["cmd", "output_text", "func_name", "fields"]
)

chain = LLMChain(llm=llm, prompt=prompt)

# ------------------------------
# 工具函数
# ------------------------------

def load_cases(json_path="cases.json"):
    """读取 JSON 文件"""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def append_to_command_py(func_code: str, file_path="command.py"):
    """追加写入函数代码到 command.py"""
    with open(file_path, "a", encoding="utf-8") as f:
        f.write("\n\n")
        f.write(func_code)
        f.write("\n")

def clean_code(code: str) -> str:
    """
    去掉前后的 Markdown ```python ``` 代码块
    """
    code = code.strip()
    if code.startswith("```") and code.endswith("```"):
        # 去掉前后 ```
        code = code[3:-3].strip()
        # 如果开头是 ```python，也去掉
        if code.lower().startswith("python"):
            code = code[6:].strip()
    return code

# ------------------------------
# 主执行逻辑
# ------------------------------

def main():
    cases = load_cases("cases.json")
    for case in cases:
        fields_str = ", ".join(case["fields"])
        # 调用 LangChain LLMChain 生成代码
        code = chain.run(
            cmd=case["cmd"],
            output_text=case["output_text"],
            func_name=case["func_name"],
            fields=fields_str
        )

        code_clean = clean_code(code)

        append_to_command_py(code_clean)
        print(f"✅ 已生成函数 {case['func_name']} 并追加到 command.py")

if __name__ == "__main__":
    main()
