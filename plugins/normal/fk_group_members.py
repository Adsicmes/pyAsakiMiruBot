import asyncio

import datetime
import os.path
import typing

import aiosqlite
import json
import random
import re
import time
from aiosqlite.core import Connection as AioSqliteConnection, Cursor as AioSqliteCursor
from alicebot import Plugin
from alicebot.adapter import cqhttp
from alicebot.adapter.cqhttp.message import CQHTTPMessage, CQHTTPMessageSegment
from alicebot.log import logger

NV_TONG = {
    1: ["「<fucker>」跟「<name>」<location>磨豆腐，弄的房间里到处都是😕，下次能不能收敛点啊！",
        "今天「<fucker>」和「<name>」<location>磨了豆腐哦，还弄的房间里到处都是"],
    2: ["「<fucker>」突然长出来了牛子，今天不能磨了。试试把「<name>」让出去给别人磨吧！",
        "今天长出来牛子的「<fucker>」不能跟「<name>」磨豆腐了，可能她已经跟别人快乐了哦"],
    3: ["「<fucker>」<time>和「<name>」带着波奇酱一起上了天堂",
        "今天是和波奇酱还有「<name>」一起愉悦的日子~爽上天了！"],
    4: ["「<fucker>」狠狠的磨了「<name>」的欢乐豆「<random>」次，「<name>」脱水晕倒了。",
        "「<name>」已经被「<fucker>」磨了「<random>」次磨得脱水晕倒了！！！"],
    5: ["女人像沙子，握得越紧，越容易从指间流逝！「<fucker>」如何才能留住「<name>」呢？把她弄湿!",
        "今天把「<name>」弄湿了，沙子一样的她就不会从「<fucker>」的指尖溜走了"],
    6: ["「<fucker>」和「<name>」磨了一晚上，得到了一份十分珍贵的姬汤，不咸不淡，味道真是好极了",
        "「<fucker>」今天和「<name>」磨出来的姬汤味道不咸不淡，十分美味"],
    7: ["「<fucker>」和「<name>」正在专心磨豆腐，突然被其他群友发现了，太羞耻啦！",
        "今天「<fucker>」和「<name>」磨豆腐呗发现了，呜呜呜好羞耻"],
    8: ["「<name>」正在刷PP，「<fucker>」按下了开关开磨，「<name>」满脸通红的丢了她的BP1",
        "「<fucker>」今天强行跟「<name>」开磨，她满脸通红地丢了她的BP1"],
    9: ["嘿嘿，啊哈哈哈哈，「<name>」的姬汤来喽！",
        "喝了「<name>」的姬汤，「<fucker>」感觉浑身酸爽！"],
    10: ["「<fucker>」和「<name>」再也忍不住了，<location>相拥在一起，互相吮吸对方的舌头，品尝独一无二的香味",
         "今天「<fucker>」和「<name>」<location>忍不住拥在一起品尝对方的舌头."],
    11: ["「<fucker>」把和「<name>」磨好的豆腐汁装到了瓶子里，对「<name>」说:“喝，TNND，你为什么不喝”。",
         "今天「<fucker>」让「<name>」喝两人磨好的豆腐汁，但是「<name>」死活没喝(..."]
}
NAN_TONG = {
    1: ["「<name>」你去哪了啊，电话也不接消息也不回。「<fucker>」一个人戴着项圈迷路了",
        "「<fucker>」一个人带着项圈迷路了，找不到「<name>」，信誉太急猝死了"],
    2: ["「<fucker>」的牛子离家出走了！试试去sb群发送\"磨群友\"吧！",
        "「<fucker>」今天没有牛牛了！试试去sb群磨群友吧！"],
    3: ["「<fucker>」准备了一大堆小玩具，<time>「<name>」一定很色情",
        "「<name>」好涩，小玩具好好玩！今天好累但是好涩啊！"],
    4: ["「<fucker>」<time>与「<name>」展开柏拉图式的爱情",
        "「<fucker>」今天和「<name>」展开了柏拉图式的爱情~异常纯洁！"],
    5: [
        "好想，好想你！如果清风有情，请带去我对你的思念，这一生都为你牵挂；如果白云有意，请带去我对你的爱恋，生生世世都愿和你共缠绵！「<name>」",
        "「<fucker>」今天发病太羞耻了，「<name>」你不会不要他吧！！！"],
    6: ["「<name>」是危险南通，千万别访问！！！！",
        "「<fucker>」今天没经住诱惑，强行访问了「<name>」这个危险南通"]
}
NORMAL = {
    1: ["今天日到了「<name>」，感觉神清气爽！",
        "今天已经日过了「<name>」，现在是贤者时间！！"],
    2: ["<time>，「<name>」一脸坏笑地看着「<fucker>」，<location>扑倒了「<fucker>」",
        "「<fucker>」今天被「<name>」<time><location>扑倒了，并快乐了一番"],
    3: ["「<fucker>」把「<name>」的身体当做健身房进行了一个健的身",
        "「<fucker>」今天在「<name>」的身体里好好健身了一番！"],
    4: ["「<fucker>」为「<name>」送出了祖传的染色体~",
        "「<fucker>」今天为「<name>」送出了祖传的染色体~"],
    5: ["「<name>」为「<fucker>」送出了祖传的染色体~",
        "「<name>」今天为「<fucker>」送出了祖传的染色体~"],
    6: ["「<fucker>」把「<name>」弄得热热的，满身是汗",
         "今天「<name>」满身是汗，「<fucker>」弄的。"],
    7: ["「<name>」成功引诱「<fucker>」中厨了好几次",
         "「<fucker>」今天被「<name>」诱惑，中厨了她好几次"],
    8: ["「<fucker>」因为从下往上不断突进导致「<name>」的意识已经飞到九霄云外了",
         "「<name>」今天被「<fucker>」从下往上不断突进，意识都已经飞走了"],
    9: ["「<fucker>」用手勾起「<name>」的下巴，一脸坏笑的说“让姐姐看看你发育正不正常啊，听话，让我看看”。",
         "「<name>」今天被「<fucker>」查看发育情况了，呜呜呜~"],
    10: ["「<fucker>」弄得「<name>」嘴上的白色汁液一点一点滴落，猫耳兴奋地跳动着",
         "「<name>」今天被「<fucker>」弄的满嘴白色汁液，异常兴奋."]
}
TIME = {
    1: "起床时",
    2: "打胶时",
    3: "玩osu时",
    4: "快要span白猫时",
    5: "刷pp时",
    6: "直播时"
}
LOCATION = {
    1: "在床上",
    2: "在教室里",
    3: "在泳池里",
    4: "在漆黑的小黑屋"
}


# noinspection DuplicatedCode
class FkGroupMembers():
    priority = 50
    block = True
    hook_flag = False

    con_fk_log: AioSqliteConnection
    con_group_classification: AioSqliteConnection
    con_user_fk_stat: AioSqliteConnection

    # :TODO 等待框架作者添加bot退出的异步插件钩子函数  对数据库连接进行断开
    # def __post_init__(self):
    #     if self.hook_flag:
    #         self.bot.bot_exit_hook(self.bot_exit)
    #         self.hook_flag = False
    #
    # def bot_exit(self):
    #     asyncio.run(self._bot_exit(self))
    #
    # @staticmethod
    # @logger.catch()
    # async def _bot_exit(self):
    #     if self.con_fk_log.is_alive():
    #         logger.warning("con_fk_log connection closing...")
    #         await self.con_fk_log.close()
    #     if self.con_group_classification.is_alive():
    #         logger.warning("con_group_classification connection closing...")
    #         await self.con_group_classification.close()
    #     if self.con_user_fk_stat.is_alive():
    #         logger.warning("con_user_fk_stat connection closing...")
    #         await self.con_user_fk_stat.close()

    @logger.catch()
    async def rule(self) -> bool:
        await self._check_db_connection()

        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        if type(self.event) != cqhttp.event.GroupMessageEvent:
            return False

        nv_tong_groups_cursor: AioSqliteCursor = await self.con_group_classification.execute(
            """select group_id from groups where classify is 'NvTong';"""
        )
        nan_tong_groups_cursor: AioSqliteCursor = await self.con_group_classification.execute(
            """select group_id from groups where classify is 'NanTong';"""
        )
        nv_tong_groups = [i[0] for i in (await nv_tong_groups_cursor.fetchall())]
        nan_tong_groups = [i[0] for i in (await nan_tong_groups_cursor.fetchall())]

        if self.event.group_id in nv_tong_groups:
            if str(self.event.message)[:3] in ["磨群友", "搞钕同"]:
                return True
        if self.event.group_id in nan_tong_groups:
            if str(self.event.message)[:3] in ["搞群友", "搞南通"]:
                return True
        if self.event.group_id not in (nv_tong_groups + nan_tong_groups):
            if str(self.event.message)[:3] in ["日群友"]:
                return True

        return False

    async def handle(self) -> None:
        logger.log("EVENT_HANDLE", f"Event will be handled by <{self.__class__.__name__}>. Priority {self.priority}.")
        await self._handle()
        logger.log("EVENT_HANDLE", f"Event finished.")

    @logger.catch()
    async def _check_db_connection(self):
        # 检查建立目录
        if not os.path.isdir("data"):
            os.mkdir("data")
        if not os.path.isdir("data/fk_group_members"):
            os.mkdir("data/fk_group_members")

        # 检查建立全局字段并初始化连接和游标
        if not self.bot.global_state.__contains__("fk_group_members"):
            con_fk_log = await aiosqlite.connect('data/fk_group_members/FkLog.db')
            con_group_classification = await aiosqlite.connect('data/fk_group_members/GroupClassification.db')
            con_user_fk_stat = await aiosqlite.connect('data/fk_group_members/UserFkStat.db')
            self.bot.global_state["fk_group_members"] = {
                "db_connections": {
                    "FkLog": {
                        "con": con_fk_log
                    },
                    "GroupClassification": {
                        "con": con_group_classification
                    },
                    "UserFkStat": {
                        "con": con_user_fk_stat
                    },
                }
            }

        self.con_fk_log: AioSqliteConnection = \
            self.bot.global_state["fk_group_members"]["db_connections"]["FkLog"]["con"]
        self.con_group_classification: AioSqliteConnection = \
            self.bot.global_state["fk_group_members"]["db_connections"]["GroupClassification"]["con"]
        self.con_user_fk_stat: AioSqliteConnection = \
            self.bot.global_state["fk_group_members"]["db_connections"]["UserFkStat"]["con"]

        # 检查表是否存在 创建表
        await self.con_fk_log.execute(f'''
            create table if not exists main.Logs
            (
                id                integer not null
                    constraint Logs_pk
                        primary key autoincrement,
                user_id           integer,
                group_id          integer,
                fk_type           TEXT,
                target            integer,
                fk_text_id        integer,
                fk_time           integer,
                is_specified      integer,
                fk_text_params    TEXT
            );
        ''')
        await self.con_group_classification.execute(f'''
            create table if not exists main.groups
            (
                group_id     integer not null
                    constraint groups_pk
                        primary key,
                classify     TEXT    not null,
                modify_count integer,
                last_modify  integer
            );
        ''')
        await self.con_user_fk_stat.execute(f'''
            create table if not exists main.Status
            (
                id                  integer not null
                    constraint Status_pk
                        primary key autoincrement,
                user_id             integer,
                group_id            integer,
                specified_count     integer,
                be_specified_count     integer,
                fk_count            integer,
                fked_count          integer,
                last_fk_member      integer,
                last_fk_time        integer,
                last_be_fk_member   integer,
                last_be_fk_time     integer
            );
        ''')

    @logger.catch()
    async def _handle(self) -> None:
        """
        :TODO 日群友信息  被日记录  日人记录  周被日排行  月被日排行
        :TODO BUGFIX 三天一日不生效  可以日自己   被日过的人还可以日别人
        具体处理：
        - 先看当天有没有fk过或被fk过
            - fk过了就返回当天fk的那条语句
            - 没fk过首先检查是否存在at
                - 若存在则检查是否三天冷却完毕
                    - 冷却完毕继续at然后记录
                    - 没冷却完毕返回报错
                - 不存在直接roll当天还没有fk和被fk的群友然后记录
        """
        msg_event: cqhttp.event.GroupMessageEvent = self.event

        now_time = time.localtime()
        now_date = time.strptime(f"{now_time.tm_year}-{now_time.tm_mon}-{now_time.tm_mday}",
                                 "%Y-%m-%d")

        # 首先查阅是否已经日过了或者被日过
        query_cur: AioSqliteCursor = await self.con_fk_log.execute(f"""
            select fk_type, fk_text_id, target, fk_text_params from Logs
            where (
                user_id == {msg_event.user_id}
                or target == {msg_event.user_id}
            )
            and group_id == {msg_event.group_id}
            and {time.mktime(now_date)} < fk_time 
            and fk_time < {time.mktime(now_date) + 86400};
        """)

        # 今天日过了
        if result := (await query_cur.fetchone()):
            fk_type, fk_text_id, fk_target, fk_text_params = result

            fker_info = await self.event.adapter.call_api(
                api='get_group_member_info', **{
                    'group_id': msg_event.group_id,
                    'user_id': self.event.user_id
                })

            fked_info = await self.event.adapter.call_api(
                api='get_group_member_info', **{
                    'group_id': msg_event.group_id,
                    'user_id': fk_target
                })

            if fk_mem := re.findall(r"\[CQ:at,qq=[0-9]*\]", msg_event.raw_message):
                if int(fk_mem[0][10:][:-1]) != fked_info['user_id']:
                    print(fked_info['user_id'])
                    await self.event.reply("今天你已经r过别人了！一天一个不准贪！")
                    return

            fk_text_params = json.loads(fk_text_params)

            match fk_type:
                case "NanTong":
                    fk_text = NAN_TONG.get(fk_text_id)[1]
                case "NvTong":
                    fk_text = NV_TONG.get(fk_text_id)[1]
                case _:
                    fk_text = NORMAL.get(fk_text_id)[1]

            fker_name = fker_info['card'] if fker_info['card'] != '' else fker_info['nickname']
            fked_name = fked_info['card'] if fked_info['card'] != '' else fked_info['nickname']
            fk_text = fk_text.replace("<name>", f"{fked_name}") \
                .replace("<location>", str(fk_text_params["location"])) \
                .replace("<time>", str(fk_text_params["time"])) \
                .replace("<random>", str(fk_text_params["random"]))\
                .replace("<fucker>", f"{fker_name}")

            msg_return = CQHTTPMessage()
            msg_return += CQHTTPMessageSegment.text(fk_text)
            msg_return += CQHTTPMessageSegment.image(f"http://q1.qlogo.cn/g?b=qq&nk={fk_target}&s=160")

            await self.event.reply(msg_return)
            return

        # 今天还没日
        # 列表不为空表示要指定fk的人
        if fk_mem := re.findall(r"\[CQ:at,qq=[0-9]*\]", msg_event.raw_message):
            query_cur: AioSqliteCursor = await self.con_fk_log.execute(f"""
                select * from Logs
                where is_specified == 1  -- 指定了fk的人
                and user_id == {msg_event.user_id}
                and {int(time.time())} - fk_time >= {self.bot.config.fk_group_friends['at_limit_time']}; -- 时间超过了指定的限制
                """)

            # 指定日过了 return
            if await query_cur.fetchall():
                await self.event.reply("指定member的冷却时间还没到！别急！")
                return

            fk_mem = fk_mem[0]  # 就取第一个at  别的不要了

            result_roll = await self.roll(int(fk_mem[10:][:-1]))
            if result_roll == -1:  # 指定的人已经...fked了
                fk_target_info: dict = await self.event.adapter.call_api(
                    api="get_group_member_info", **{
                        "group_id": self.event.group_id,
                        "user_id": int(fk_mem[10:][:-1])
                    }
                )
                target_name = fk_target_info['card'] if fk_target_info['card'] != '' else fk_target_info['nickname']
                await self.event.reply(f"今天「{target_name}」已经日过别人或者被日过了哦~")
                return

            fker_info, fk_target_info, fk_text, fk_text_type, fk_text_id, fk_text_params = result_roll

            fk_text = self.fk_text_replace(fk_text, fk_text_params)

            msg_return = CQHTTPMessage()
            msg_return += CQHTTPMessageSegment.text(fk_text)
            msg_return += CQHTTPMessageSegment.image(f"http://q1.qlogo.cn/g?b=qq&nk={fk_target_info['user_id']}&s=160")
            await self.event.reply(msg_return)

            fk_time = int(time.mktime(time.localtime()))
            await self.log_db_save(
                user_id=fker_info['user_id'],
                group_id=self.event.group_id,
                fk_type=fk_text_type,
                target=fk_target_info['user_id'],
                fk_text_id=fk_text_id,
                fk_time=fk_time,
                is_specified=1,
                fk_text_params=json.dumps(fk_text_params)
            )
            await self.user_stat_update(
                fk_user_id=fker_info["user_id"],
                fk_ed_user_id=fk_target_info["user_id"],
                group_id=self.event.group_id,
                fk_time=fk_time,
                update_type="fk_specified"
            )
        # 列表为空表示不指定 随机
        else:
            result_roll = await self.roll()
            fker_info, fk_target_info, fk_text, fk_text_type, fk_text_id, fk_text_params = result_roll
            fk_text = self.fk_text_replace(fk_text, fk_text_params)

            msg_return = CQHTTPMessage()
            msg_return += CQHTTPMessageSegment.text(fk_text)
            msg_return += CQHTTPMessageSegment.image(f"http://q1.qlogo.cn/g?b=qq&nk={fk_target_info['user_id']}&s=160")
            await self.event.reply(msg_return)

            fk_time = int(time.mktime(time.localtime()))
            await self.log_db_save(
                user_id=fker_info['user_id'],
                group_id=self.event.group_id,
                fk_type=fk_text_type,
                target=fk_target_info['user_id'],
                fk_text_id=fk_text_id,
                fk_time=fk_time,
                is_specified=1,
                fk_text_params=json.dumps(fk_text_params)
            )
            await self.user_stat_update(
                fk_user_id=fker_info["user_id"],
                fk_ed_user_id=fk_target_info["user_id"],
                group_id=self.event.group_id,
                fk_time=fk_time,
                update_type="fk_normal"
            )

    @logger.catch()
    async def roll(self, fk_target: int = -1) -> tuple[dict, dict, str, str, int, dict] | int:
        """
        对各种参数进行一个的roll
        在使用roll之前已经指定了发起人

        roll 文本、文本内参数、若没有指定群成员还会roll群成员
        :param fk_target: 指定be fked的人，若不传入则随机从群友内选择
        :return: 正常roll完返回 fker_info: dict
                              fk_target_info: dict
                              fk_text: str
                              fk_text_type: Optional["NanTong", "NvTong", "Normal"]
                              fk_text_id: int
                              fk_text_params: dict
                 异常roll返回报错值 -1: 当天已经指定be fked过了
        """
        # 判断群南钕同类型进行对应语句的筛选

        nv_tong_groups_cursor: AioSqliteCursor = await self.con_group_classification.execute(
            """select group_id from groups where classify is 'NvTong';"""
        )
        nan_tong_groups_cursor: AioSqliteCursor = await self.con_group_classification.execute(
            """select group_id from groups where classify is 'NanTong';"""
        )
        nv_tong_groups = [i[0] for i in (await nv_tong_groups_cursor.fetchall())]
        nan_tong_groups = [i[0] for i in (await nan_tong_groups_cursor.fetchall())]

        if self.event.group_id in nan_tong_groups:
            fk_text_type = NAN_TONG
        elif self.event.group_id in nv_tong_groups:
            fk_text_type = NV_TONG
        else:
            fk_text_type = NORMAL

        fk_text_id: int = random.randint(1, len(fk_text_type))
        fk_text: str = fk_text_type.get(fk_text_id)[0]

        if fk_text_type == NAN_TONG:
            fk_text_type = "NanTong"
        elif fk_text_type == NV_TONG:
            fk_text_type = "NvTong"
        else:
            fk_text_type = "Normal"

        # 查询今天fk的和没fk的   群成员进行排除
        query_cur = await self.con_fk_log.execute(f"""
            select user_id, target from Logs
            where group_id == {self.event.group_id}
            and fk_time >= {int(time.mktime(datetime.date.today().timetuple()))};
        """)

        fk_member_exclude = [self.event.user_id]
        for row in (await query_cur.fetchall()):
            fk_member_exclude.append(row[0])
            fk_member_exclude.append(row[1])

        print(fk_member_exclude)

        # 在排除列表里表示已经fked了，报错返回-1
        if fk_target in fk_member_exclude:
            return -1

        if fk_target == -1:
            all_members_info = await self.event.adapter.call_api(
                api="get_group_member_list", **{
                    "group_id": self.event.group_id
                }
            )
            all_members_list = [member["user_id"] for member in all_members_info]

            for m in fk_member_exclude:
                if m in all_members_list:
                    all_members_list.remove(m)

            fk_target = all_members_list[random.randint(0, len(all_members_list)-1)]

        fk_target_info: dict = await self.event.adapter.call_api(
            api="get_group_member_info", **{
                "group_id": self.event.group_id,
                "user_id": fk_target
            }
        )
        fker_info: dict = await self.event.adapter.call_api(
            api="get_group_member_info", **{
                "group_id": self.event.group_id,
                "user_id": self.event.user_id
            }
        )

        fker_name = fker_info['card'] if fker_info['card'] != '' else fker_info['nickname']
        target_name = fk_target_info['card'] if fk_target_info['card'] != '' else fk_target_info['nickname']
        fk_text_params = {
            "random": random.randint(1, 100),
            "location": LOCATION.get(random.randint(1, len(LOCATION))),
            "time": TIME.get(random.randint(1, len(TIME))),
            "fucker": f"{fker_name}",
            "name": f"{target_name}"
        }

        return fker_info, fk_target_info, fk_text, fk_text_type, fk_text_id, fk_text_params

    @staticmethod
    @logger.catch()
    def fk_text_replace(text_original: str, replace_params: dict) -> str:
        """
        文本参数替换
        :param text_original:
        :param replace_params:
        :return:
        """
        for key, value in replace_params.items():
            text_original = text_original.replace(f"<{key}>",str(value))
        return text_original

    @logger.catch()
    async def log_db_save(self,
                          user_id: int,
                          group_id: int,
                          fk_type: str,
                          target: int,
                          fk_text_id: int,
                          fk_time: int,
                          is_specified: int,
                          fk_text_params: str) -> None:
        await self.con_fk_log.execute(f"""
            insert into Logs
            values (NULL, {user_id}, {group_id}, '{fk_type}', {target}, {fk_text_id}, {fk_time}, {is_specified}, '{fk_text_params}');
        """)

    @logger.catch()
    async def user_status_init(self, fk_user_id, group_id):
        query_cur: AioSqliteCursor = await self.con_user_fk_stat.execute(f"""
            insert into Status values 
            (NULL, {fk_user_id}, {group_id}, 0, 0, 0, 0, -1, -1, -1, -1);
        """)

    @logger.catch()
    async def user_stat_update(
            self,
            fk_user_id: int,
            fk_ed_user_id: int,
            group_id: int,
            fk_time: int,
            update_type: typing.Literal["fk_specified", "fk_normal"]
    ) -> None:
        query_cur = await self.con_user_fk_stat.execute(f"""
            select id, user_id from Status where (
                user_id == {fk_user_id}
                and group_id == {group_id}
            ) or (
                user_id == {fk_ed_user_id}
                and group_id == {group_id}
            );
        """)
        # [(id, userid), (id, userid)]
        result = await query_cur.fetchall()

        # 检查发起方
        is_existed = False
        for i in result:
            if fk_user_id == i[1]:
                is_existed = True
                break
        if not is_existed:
            await self.user_status_init(fk_user_id, group_id)

        # 检查target方
        is_existed = False
        for i in result:
            if fk_ed_user_id == i[1]:
                is_existed = True
                break
        if not is_existed:
            await self.user_status_init(fk_ed_user_id, group_id)

        if update_type == "fk_specified":
            sp = 1
        else:
            sp = 0

        # 执行status更改
        await self.con_user_fk_stat.execute(f"""
                update Status 
                set fk_count = fk_count + 1,
                    specified_count = specified_count + {sp},
                    last_fk_member = {fk_ed_user_id},
                    last_fk_time = {fk_time}
                where (
                    user_id == {fk_user_id}
                    and group_id == {group_id}
                )
        """)

        await self.con_user_fk_stat.execute(f"""
                update Status 
                set fked_count = fk_count + 1,
                    be_specified_count = specified_count + {sp},
                    last_be_fk_member = {fk_user_id},
                    last_be_fk_time = {fk_time}
                where (
                    user_id == {fk_ed_user_id}
                    and group_id == {group_id}
                )
        """)
