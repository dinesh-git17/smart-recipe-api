import logging
import colorlog


class EmojiFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        emoji_map = {
            "DEBUG": "🐛",
            "INFO": "💡",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🔥",
        }
        record.emoji = emoji_map.get(record.levelname, "")
        return super().format(record)


log_colors = {
    "DEBUG": "bold_blue",
    "INFO": "bold_green",
    "WARNING": "bold_yellow",
    "ERROR": "bold_red",
    "CRITICAL": "bold_magenta",
}

log_format = "%(log_color)s%(asctime)s %(emoji)s %(levelname)s:%(reset)s %(message)s"

formatter = EmojiFormatter(
    log_format, datefmt="%Y-%m-%d %H:%M:%S", log_colors=log_colors
)

logger = logging.getLogger("smart_recipe_api")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
