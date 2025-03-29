from typing import Annotated

from httpx import AsyncClient
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg

english_to_kana_cmd = on_command("kana")


@english_to_kana_cmd.handle()
async def _(english_text: Annotated[Message, CommandArg()]):
    english_text = english_text.extract_plain_text()

    url = "https://www.sljfaq.org/cgi/e2k.cgi"
    params = {"o": "json", "word": english_text, "lang": "ja"}

    async with AsyncClient(
        headers={
            "User-Agent": "Mobile Safari/537.36 Edg/134.0.0.0",
        }
    ) as client:
        resp = await client.get(url=url, params=params)

    json_data: dict = resp.json()
    kana_words = json_data.get("words", [])

    if not kana_words:
        await english_to_kana_cmd.finish("没有可转换的英文单词!")

    japanese_kana_text = " ".join(word["j_pron_only"] for word in kana_words)

    await english_to_kana_cmd.finish(japanese_kana_text)
