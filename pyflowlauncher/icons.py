import logging
import os
from pathlib import Path
from typing import Dict, Optional

_logger = logging.getLogger(__name__)

IMAGE_DIR = "Images"
FLOW_PROGRAM_DIRECTORY = os.getenv("FLOW_PROGRAM_DIRECTORY", None)

ENV_EXISTS: bool = FLOW_PROGRAM_DIRECTORY is not None

if not ENV_EXISTS:
    _logger.warning("Unable to find FLOW_PROGRAM_DIRECTORY environment variable. Icons will not be loaded.")


def _get_icon(icon_name: str, file_ext: str = "png") -> Optional[str]:
    if ENV_EXISTS:
        return str(Path(FLOW_PROGRAM_DIRECTORY) / IMAGE_DIR / f"{icon_name}.{file_ext}")  # type: ignore
    return None


ICONS: Dict[str, Optional[str]] = {
    "2566": _get_icon("2566"),
    "admin": _get_icon("admin"),
    "app": _get_icon("app"),
    "app_error": _get_icon("app_error"),
    "app_missing_img": _get_icon("app_missing_img"),
    "baidu": _get_icon("baidu"),
    "bing": _get_icon("bing"),
    "bookmark": _get_icon("bookmark"),
    "browser": _get_icon("Browser"),
    "calculator": _get_icon("calculator"),
    "cancel": _get_icon("cancel"),
    "checkupdate": _get_icon("checkupdate"),
    "close": _get_icon("close"),
    "cmd": _get_icon("cmd"),
    "color": _get_icon("color"),
    "context_menu": _get_icon("context_menu"),
    "controlpanel_small": _get_icon("ControlPanel_Small"),
    "copy": _get_icon("copy"),
    "copylink": _get_icon("copylink"),
    "deletedfolder": _get_icon("deletedfolder"),
    "disable": _get_icon("disable"),
    "down": _get_icon("down"),
    "duckduckgo": _get_icon("duckduckgo"),
    "error": _get_icon("error"),
    "everything_error": _get_icon("everything_error"),
    "excludeindexpath": _get_icon("excludeindexpath"),
    "exe": _get_icon("EXE"),
    "explorer": _get_icon("explorer"),
    "facebook": _get_icon("facebook"),
    "file": _get_icon("file"),
    "find": _get_icon("find"),
    "folder": _get_icon("folder"),
    "gamemode": _get_icon("gamemode"),
    "gist": _get_icon("gist"),
    "github": _get_icon("github"),
    "gmail": _get_icon("gmail"),
    "google": _get_icon("google"),
    "google_drive": _get_icon("google_drive"),
    "google_maps": _get_icon("google_maps"),
    "google_translate": _get_icon("google_translate"),
    "hibernate": _get_icon("hibernate"),
    "history": _get_icon("history"),
    "image": _get_icon("image"),
    "index_error": _get_icon("index_error"),
    "index_error2": _get_icon("index_error2"),
    "indexoption": _get_icon("indexoption"),
    "link": _get_icon("link"),
    "loading": _get_icon("loading"),
    "lock": _get_icon("lock"),
    "logoff": _get_icon("logoff"),
    "manifestsite": _get_icon("manifestsite"),
    "netflix": _get_icon("netflix"),
    "new_message": _get_icon("New Message"),
    "ok": _get_icon("ok"),
    "open": _get_icon("open"),
    "openrecyclebin": _get_icon("openrecyclebin"),
    "pictures": _get_icon("pictures"),
    "pluginsmanager": _get_icon("pluginsmanager"),
    "program": _get_icon("program"),
    "quickaccess": _get_icon("quickaccess"),
    "recyclebin": _get_icon("recyclebin"),
    "removequickaccess": _get_icon("removequickaccess"),
    "request": _get_icon("request"),
    "restart": _get_icon("restart"),
    "restart_advanced": _get_icon("restart_advanced"),
    "robot_error": _get_icon("robot_error"),
    "search": _get_icon("search"),
    "settings": _get_icon("settings"),
    "shell": _get_icon("shell"),
    "shutdown": _get_icon("shutdown"),
    "sleep": _get_icon("sleep"),
    "sourcecode": _get_icon("sourcecode"),
    "stackoverflow": _get_icon("stackoverflow"),
    "twitter": _get_icon("twitter"),
    "up": _get_icon("up"),
    "update": _get_icon("update"),
    "url": _get_icon("url"),
    "user": _get_icon("user"),
    "warning": _get_icon("warning"),
    "web_search": _get_icon("web_search"),
    "wiki": _get_icon("wiki"),
    "windowsindexingoptions": _get_icon("windowsindexingoptions"),
    "windowssettingslight": _get_icon("windowssettings.light"),
    "wizard": _get_icon("wizard"),
    "wolframalpha": _get_icon("wolframalpha"),
    "work": _get_icon("work"),
    "yahoo": _get_icon("yahoo"),
    "youtube": _get_icon("youtube"),
    "youtubemusic": _get_icon("youtubemusic"),
}
