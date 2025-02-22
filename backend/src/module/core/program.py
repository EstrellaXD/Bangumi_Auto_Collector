import asyncio
import logging

from module.conf import VERSION, settings
from module.update import (
    cache_image,
    data_migration,
    first_run,
    from_30_to_31,
    start_up,
)

# from .sub_thread import RenameTask, RSSTask
from .aiocore import AsyncDownload, AsyncRenamer, AsyncRSS
from .status import ProgramStatus

logger = logging.getLogger(__name__)

figlet = r"""
                _        ____                                    _
     /\        | |      |  _ \                                  (_)
    /  \  _   _| |_ ___ | |_) | __ _ _ __   __ _ _   _ _ __ ___  _
   / /\ \| | | | __/ _ \|  _ < / _` | '_ \ / _` | | | | '_ ` _ \| |
  / ____ \ |_| | || (_) | |_) | (_| | | | | (_| | |_| | | | | | | |
 /_/    \_\__,_|\__\___/|____/ \__,_|_| |_|\__, |\__,_|_| |_| |_|_|
                                            __/ |
                                           |___/
"""


class Program:
    def __init__(self):
        self.program_status = ProgramStatus()
        self.renamer = AsyncRenamer()
        self.rss = AsyncRSS()
        self.download = AsyncDownload()

    @staticmethod
    def __start_info():
        for line in figlet.splitlines():
            logger.info(line.strip("\n"))
        logger.info(
            f"Version {VERSION}  Author: EstrellaXD Twitter: https://twitter.com/Estrella_Pan"
        )
        logger.info("GitHub: https://github.com/EstrellaXD/Auto_Bangumi/")
        logger.info("Starting AutoBangumi...")

    async def startup(self):
        self.__start_info()
        if not self.program_status.database:
            first_run()
            logger.info("[Core] No db file exists, create database file.")
            return {"status": "First run detected."}
        if self.program_status.legacy_data:
            logger.info(
                "[Core] Legacy data detected, starting data migration, please wait patiently."
            )
            await data_migration()
        elif self.program_status.version_update:
            # Update database
            await from_30_to_31()
            logger.info("[Core] Database updated.")
        if not self.program_status.img_cache:
            logger.info("[Core] No image cache exists, create image cache.")
            await cache_image()
        await self.start()

    async def start(self):
        settings.load()
        await self.download.run()
        if self.program_status.enable_rss:
            await self.rss.run()
        if self.program_status.enable_renamer:
            await self.renamer.run()
        logger.info("Program running.")
        return True

    async def stop(self):
        if self.program_status.is_running:
            await self.download.stop()
            await self.rss.stop()
            await self.renamer.stop()
            return True

    async def restart(self) -> bool:
        await self.stop()
        await self.start()
        return True

    def update_database(self):
        if not self.program_status.version_update:
            return {"status": "No update found."}
        else:
            start_up()
            return {"status": "Database updated."}
