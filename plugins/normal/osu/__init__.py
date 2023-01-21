import time

from .osuApiV2 import AsyncApiClient as osu_api_v2_client

import alicebot
from alicebot import Plugin
from alicebot.log import logger

async def osu_api_check(_bot: alicebot.Bot):
    api_id = _bot.config.osu["api_client_id"]
    api_secret = _bot.config.osu["api_client_secret"]

    if not _bot.global_state.__contains__("osu_api_client"):
        _bot.global_state["osu_api_client"] = {
            "client": osu_api_v2_client(),
            "init": False,
            "start_at": time.time()
        }

    client_dict = _bot.global_state["osu_api_client"]
    client_dict["client"]: osu_api_v2_client
    client_dict["init"]: bool
    client_dict["start_at"]: int

    if not client_dict["init"]:
        await client_dict["client"].initialization(client_id=api_id, client_secret=api_secret)
        client_dict["init"] = True

    if time.time() - client_dict["start_at"] >= 86400 - 400:
        await client_dict["client"].initialization(client_id=api_id, client_secret=api_secret)


class OsuDerankerCheck(Plugin):
    priority = 50
    block = True

    @logger.catch
    async def rule(self) -> bool:
        return (
            self.event.adapter.name == "cqhttp"
            and self.event.type == "message"
            and str(self.event.message).lower().startswith("deranker")
        )

    async def handle(self) -> None:
        logger.log("EVENT_HANDLE", f"Event will be handled by <{self.__class__.__name__}>. Priority {self.priority}.")
        await self._handle()
        logger.log("EVENT_HANDLE", f"Event finished.")

    @logger.catch
    async def _handle(self) -> None:
        await osu_api_check(self.bot)

        username = str(self.event.message)[8:] \
            .strip() \
            .replace('&#91;', '[') \
            .replace('&#93;', ']') \
            .replace('&#44;', ',') \
            .replace('&amp;', '&')

        client: osu_api_v2_client = self.bot.global_state["osu_api_client"]["client"]

        user_best = await client.get_user_best(username)

        if not user_best:
            await self.event.reply("检查一下用户名是否正确")
            return

        first_pp = user_best[0]['pp']
        last_pp = user_best[-1]['pp']

        point = first_pp / (first_pp - last_pp)

        message_to_reply = \
            f"用户名: {username}\n" \
            f"您的第一个bp: {first_pp}pp\n" \
            f"您的最后一个bp: {last_pp}pp\n" \
            f"bp差为{round(first_pp - last_pp, 3)}pp\n" \
            f"derank指数为{round(point, 2)}\n"

        if point < 0:
            message_to_reply += "好家伙你把我都搞坏了"
        elif 0 <= point < 1:
            message_to_reply += "您，是不是把pp系统搞坏了"
        elif 1 <= point < 1.5:
            message_to_reply += "您"
        elif 1.5 <= point < 2:
            message_to_reply += "挺de的，建议多刷pp获得与自己实力相符的pp"
        elif 2 <= point < 2.5:
            message_to_reply += "有点de，来点pp"
        elif 2.5 <= point < 3.5:
            message_to_reply += "我的评价是，正常人"
        elif 3.5 <= point < 4.3:
            message_to_reply += "有点刷多了，练点实力"
        elif 4.3 <= point < 5:
            message_to_reply += "这边建议去mp被六位数暴打"
        elif 5 <= point < 6:
            message_to_reply += "没救了"
        elif point > 6:
            message_to_reply += "remake吧"

        await self.event.reply(message_to_reply)
