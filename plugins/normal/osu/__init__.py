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
            await self.event.reply("?????????????????????????????????")
            return

        first_pp = user_best[0]['pp']
        last_pp = user_best[-1]['pp']

        point = first_pp / (first_pp - last_pp)

        message_to_reply = \
            f"?????????: {username}\n" \
            f"???????????????bp: {first_pp}pp\n" \
            f"??????????????????bp: {last_pp}pp\n" \
            f"bp??????{round(first_pp - last_pp, 3)}pp\n" \
            f"derank?????????{round(point, 2)}\n"

        if point < 0:
            message_to_reply += "??????????????????????????????"
        elif 0 <= point < 1:
            message_to_reply += "??????????????????pp???????????????"
        elif 1 <= point < 1.5:
            message_to_reply += "???"
        elif 1.5 <= point < 2:
            message_to_reply += "???de??????????????????pp??????????????????????????????pp"
        elif 2 <= point < 2.5:
            message_to_reply += "??????de?????????pp"
        elif 2.5 <= point < 3.5:
            message_to_reply += "???????????????????????????"
        elif 3.5 <= point < 4.3:
            message_to_reply += "??????????????????????????????"
        elif 4.3 <= point < 5:
            message_to_reply += "???????????????mp??????????????????"
        elif 5 <= point < 6:
            message_to_reply += "?????????"
        elif point > 6:
            message_to_reply += "remake???"

        await self.event.reply(message_to_reply)
