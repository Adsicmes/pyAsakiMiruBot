from alicebot import Plugin
from alicebot.log import logger
from alicebot.adapter import cqhttp

class Ping(Plugin):
    priority = 50
    block = True

    @logger.catch
    async def rule(self) -> bool:
        return (
            self.event.adapter.name == "cqhttp"
            and self.event.type == "message"
            and str(self.event.message).lower() in ["ping"]
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
        await self.event.reply("meow~")
