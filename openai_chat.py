import openai
from   openai import OpenAI
from   openai import AsyncOpenAI
import asyncio

# OpenAI APIから応答を取得する関数 ログなし（非同期版）
async def chat_req(client, user_msg, role):
    messages = [
        {"role": "system", "content": role},
        {"role": "user", "content": user_msg}
    ]
    # await を使って coroutine の実行結果を取得
    completion = await client.chat.completions.create(
        model="gemma2:latest",
        messages=messages,
    )
    return completion.choices[0].message.content

