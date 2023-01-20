import os

from alicebot import Bot
from alicebot.log import logger
from sys import stdout

# 打开后，在热重载时，log_configure函数做出的更改会部分失效
bot = Bot(hot_reload=False)

@bot.bot_run_hook
async def run_hook(_bot: Bot) -> None:
    async def log_configure() -> None:
        # 重定义控制台输出
        logger.remove()
        logger.add(
            stdout,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <bold><level>{level}</level></bold> | "
                   "<fg 100,100,100>{name}:{function}</fg 100,100,100> | {message}"
        )

        # 添加日志等级
        logger.level("QQ_MESSAGE", no=20, color="<fg #e6cdba>")
        logger.level("QQ_NOTICE", no=20, color="<fg #e6cdba>")
        logger.level("QQ_NOTIFY", no=20, color="<fg #e6cdba>")
        logger.level("QQ_REQUEST", no=20, color="<fg #e6cdba>")
        logger.level("QQ_META_EVENT", no=20, color="<fg #e6cdba>")
        logger.level("EVENT_HANDLE", no=20, color="<fg #bbbbbb>")

        # 关闭原有bot类日志
        logger.disable("alicebot.bot")

        # 查看配置文件，是否日志保存到本地
        if _bot.config.bot.log.save:
            if not os.path.isdir("log"):
                os.mkdir("log")
            if not os.path.isdir("log/normal"):
                os.mkdir("log/normal")
            if not os.path.isdir("log/error"):
                os.mkdir("log/error")

            logger.add(
                "log/normal/bot_run_{time}.log",
                rotation="1 week",
                retention="3 months",
                compression="zip",
                enqueue=True,
                level='INFO',
                colorize=False,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
            )

            logger.add(
                "log/error/error_{time}.log",
                rotation="30 MB",
                retention="3 months",
                compression="zip",
                enqueue=True,
                level="WARNING",
                colorize=False,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
            )

    await log_configure()
    logger.success("Bot running. アトリは、高性能ですから!")

@bot.bot_exit_hook
async def exit_hook(_bot: Bot) -> None:
    logger.warning("Bot exiting...")

if __name__ == "__main__":
    bot.run()
