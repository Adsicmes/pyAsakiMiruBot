import re

from alicebot import Plugin
from alicebot.log import logger
from alicebot.adapter import cqhttp


class MessageDetail(Plugin):
    priority = 0
    block = False

    async def rule(self) -> bool:
        return True

    @logger.catch
    async def handle(self) -> None:
        event = self.event
        message_type = type(event)

        match message_type:
            case cqhttp.event.GroupMessageEvent:
                """群聊消息"""
                logger.log("QQ_MESSAGE",
                           f"{message_type} Group {event.group_id} - {event.sender.nickname}({event.user_id}) - "
                           f"msg_id[{event.message_id}]: {event.raw_message}")

            case cqhttp.event.PrivateMessageEvent:
                """私聊消息"""
                logger.log("QQ_MESSAGE",
                           f"{message_type} {event.sender.nickname}({event.user_id}) - msg_id[{event.message_id}]: "
                           f"{event.raw_message}")

            case cqhttp.event.GroupUploadNoticeEvent:
                """群文件上传"""
                logger.log("QQ_NOTICE",
                           f"{message_type} Group {event.group_id} - QQ {event.user_id} - file_id[{event.file.id}]: "
                           f"{event.file.name} ({event.file.size})")

            case cqhttp.event.GroupAdminNoticeEvent:
                """群管理员变动"""
                logger.log("QQ_NOTICE",
                           f"{message_type} Group {event.group_id} - "
                           f"QQ {event.user_id} is {event.sub_type} to be Admin for the group.")

            case cqhttp.event.GroupDecreaseNoticeEvent:
                """群成员减少"""
                logger.log("QQ_NOTICE",
                           f"{message_type} Group {event.group_id} - QQ {event.user_id} - "
                           f"type '{event.sub_type}' - operator {event.operator_id}")

            case cqhttp.event.GroupIncreaseNoticeEvent:
                """群成员增加"""
                logger.log("QQ_NOTICE",
                           f"{message_type} Group {event.group_id} - QQ {event.user_id} - "
                           f"type '{event.sub_type}' - operator {event.operator_id}")

            case cqhttp.event.GroupBanNoticeEvent:
                """群禁言"""
                logger.log("QQ_NOTICE",
                           f"{message_type} Group {event.group_id} - "
                           f"{event.operator_id} {event.sub_type} {event.user_id} for {event.duration}s")

            case cqhttp.event.FriendAddNoticeEvent:
                """好友添加"""
                logger.log("QQ_NOTICE",
                           f"{message_type} {event.user_id} is added to be a friend")

            case cqhttp.event.GroupRecallNoticeEvent:
                """群消息撤回"""
                logger.log("QQ_NOTICE",
                           f"{message_type} Group {event.group_id} - "
                           f"{event.operator_id} withdraw {event.user_id}'s message. id[{event.message_id}]")

            case cqhttp.event.FriendRecallNoticeEvent:
                """好友消息撤回"""
                logger.log("QQ_NOTICE",
                           f"{message_type} {event.user_id} withdraw a message. id[{event.message_id}]")

            case cqhttp.event.PokeNotifyEvent:
                """戳一戳"""
                pass

            case cqhttp.event.GroupLuckyKingNotifyEvent:
                """群红包运气王"""
                pass

            case cqhttp.event.GroupHonorNotifyEvent:
                """群成员荣誉变更"""
                pass

            case cqhttp.event.FriendRequestEvent:
                """加好友请求"""
                logger.log("QQ_REQUEST",
                           f"{message_type} {event.user_id} want to add a friend. Flag: {event.flag}. Comment: {event.comment}")

            case cqhttp.event.GroupRequestEvent:
                """加群请求／邀请"""
                logger.log("QQ_REQUEST",
                           f"{message_type} Group {event.group_id} - Flag: {event.flag} - Type {event.sub_type}"
                           f"{event.user_id} apply to be one of the group. Comment: {event.comment}")

            case cqhttp.event.LifecycleMetaEvent:
                """生命周期"""
                pass

            case cqhttp.event.HeartbeatMetaEvent:
                """心跳"""
                if event.status.online and event.status.good:
                    pass
                else:
                    logger.warning(f"{message_type} Heartbeat is abnormal. Interval{event.interval}. "
                                   f"Good: {event.status.good}. Online: {event.status.online}")

