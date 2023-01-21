import re

from alicebot import Plugin
from alicebot.log import logger
from alicebot.adapter import cqhttp

class HelpInfo(Plugin):
    priority = 50
    block = True

    @logger.catch
    async def rule(self) -> bool:
        return (
            self.event.adapter.name == "cqhttp"
            and self.event.type == "message"
            and str(self.event.message) in ["help", "!help", "！help"]
            # and self.event.group_id not in []  # 排除指定群
            # and self.event.group_id in []  # 指定群
            # and type(self.event) != cqhttp.event.GroupMessageEvent
        )

    async def handle(self) -> None:
        logger.log("EVENT_HANDLE", f"Event will be handled by <{self.__class__.__name__}>. Priority {self.priority}.")
        await self._handle()
        logger.log("EVENT_HANDLE", f"Event finished.")

    @logger.catch
    async def _handle(self) -> None:
        await self.event.reply(
            "frz把这个bot接入了猫猫和消防栓，在此之上应群友要求写了几个没啥用的简单功能\n\n"
            "为保持bot共存共生，为几个群单独写了过滤器，过滤掉几个群的消息或只单独为几个群开放\n"
            "有任何修改群过滤器的需求或者简单急需的小功能可以先考虑找frz\n\n"
            "猫猫的help: 发送!help即可\n"
            "消防栓的help: https://xfs.b11p.com/\n"
            "自己写的几个小功能: https://www.showdoc.com.cn/frz/9693003536618739\n\n"
            "osu网页资源集合: https://frzz.rth1.one/\n"
            "请使用对应服务的指令测试对应服务是否还活着("
        )
