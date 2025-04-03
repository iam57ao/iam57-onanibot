from typing import Annotated

from jmcomic import MissingAlbumPhotoException
from nonebot import get_plugin_config, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.exception import AdapterException
from nonebot.params import CommandArg

from iam57_onanibot.configs.jm_config import JMConfig
from iam57_onanibot.services.jm_service import JMService


async def is_jm_enable_group(event: GroupMessageEvent):
    jm_config = get_plugin_config(JMConfig)
    return str(event.group_id) in jm_config.jm_enable_groups


jm_cmd = on_command("jm", rule=is_jm_enable_group)
jm_service = JMService()


@jm_cmd.handle()
async def _(
    bot: Bot, jm_id: Annotated[Message, CommandArg()], event: GroupMessageEvent
):
    jm_id = jm_id.extract_plain_text()
    if not jm_id.isdigit():
        await jm_cmd.finish("参数错误，请输入JM后的纯数字ID!")
    try:
        comic = jm_service.get_comic_detail(jm_id)
    except MissingAlbumPhotoException:
        await jm_cmd.finish(
            "请求的本子不存在!\n"
            "原因可能为:\n"
            "1. ID有误，检查你的本子ID\n"
            "2. 该漫画只对登录用户可见"
        )
    comic_file_path = str(jm_service.get_pdf_file_path(comic))
    if not jm_service.is_comic_exists(comic):
        await jm_cmd.send(f"正在开始下载并转换为PDF:\n{comic.name}")
        comic_file_path = jm_service.download_comic_and_get_pdf_file_path(comic)
    try:
        await jm_cmd.send(f"正在发送:\n{comic.name}")
        await bot.call_api(
            "upload_group_file",
            group_id=event.group_id,
            file=comic_file_path,
            name=f"{comic.id}.pdf",
        )
    except AdapterException:
        await jm_cmd.finish("发送时出现错误!")
