from jmcomic import MissingAlbumPhotoException
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.params import CommandArg
from typing import Annotated

from ..utils.jm import download_comic, get_comic_file_path

jm_cmd = on_command("jm")


@jm_cmd.handle()
async def _(bot: Bot,
            jm_id: Annotated[Message, CommandArg()],
            event: GroupMessageEvent):
    jm_id = jm_id.extract_plain_text()
    if not jm_id.isdigit():
        await jm_cmd.finish("参数错误，请输入纯数字!")
    try:
        await jm_cmd.send("正在下载...")
        comic = download_comic(jm_id)
    except MissingAlbumPhotoException:
        await jm_cmd.finish(
            "请求的本子不存在！\n"
            "原因可能为:\n"
            "1. id有误，检查你的本子id\n"
            "2. 该漫画只对登录用户可见"
        )
    comic_file_path = get_comic_file_path(comic)
    print(comic_file_path)
    await bot.call_api("upload_group_file",
                       group_id=event.group_id,
                       file=comic_file_path,
                       name=f"{comic.title}.pdf")
