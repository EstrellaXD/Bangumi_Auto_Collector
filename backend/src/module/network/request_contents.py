import logging
import xml.etree.ElementTree
from typing import Any

from httpx import Response

from module.models import Torrent

from .request_url import RequestURL
from .site import rss_parser

logger = logging.getLogger(__name__)


class RequestContent(RequestURL):
    # 对错误包裹, 所有网络的错误到这里就结束了
    async def get_torrents(
        self,
        _url: str,
        limit: int = 0,
        retry: int = 3,
    ) -> list[Torrent]:
        feeds = await self.get_xml(_url, retry)
        if feeds:
            torrent_titles, torrent_urls, torrent_homepage = rss_parser(feeds)
            torrents: list[Torrent] = []
            for _title, torrent_url, homepage in zip(
                torrent_titles, torrent_urls, torrent_homepage
            ):
                torrents.append(
                    Torrent(name=_title, url=torrent_url, homepage=homepage)
                )
            return torrents if limit == 0 else torrents[:limit]
        else:
            logger.error(f"[Network] Torrents list is empty: {_url}")
            return []

    async def get_xml(
        self, _url: str, retry: int = 3
    ) -> xml.etree.ElementTree.Element | None:
        try:
            req = await self.get_url(_url, retry)
            if req:
                return xml.etree.ElementTree.fromstring(req.text)
        except xml.etree.ElementTree.ParseError:
            logger.warning(
                f"[Network] Cannot parser {_url}, please check the url is right"
            )
        except Exception as e:
            logger.error(f"[Network] Cannot get xml from {_url}: {e}")
        return None

    # API JSON
    async def get_json(self, _url: str) -> dict[str, Any]:
        try:
            req = await self.get_url(_url)
            if req:
                return req.json()
        except Exception as e:
            logger.error(f"[Network] Cannot get json from {_url}: {e}")
        return {}

    async def post_data(
        self, _url: str, data: dict[str, str], files: dict[str, bytes]
    ) -> Response:
        try:
            req = await self.post_url(_url, data, files)
            return req
        except Exception as e:
            logger.error(f"[Network] Cannot post data to {_url}: {e}")
        return Response(status_code=400)

    async def get_html(self, _url: str) -> str:
        try:
            req = await self.get_url(_url)
            if req:
                return req.text
        except Exception as e:
            logger.error(f"[Network] Cannot get html from {_url}: {e}")
        return ""

    async def get_content(self, _url: str) -> bytes:
        try:
            req = await self.get_url(_url)
            if req:
                return req.content
        except Exception as e:
            logger.error(f"[Network] Cannot get content from {_url}: {e}")
        return b""

    async def check_connection(self, _url: str) -> bool:
        return await self.check_url(_url)

    async def get_rss_title(self, _url: str) -> str | None:
        # 有一说一,不该在这里,放在 rss_parser 里面
        soup = await self.get_xml(_url)
        if soup:
            title = soup.find("./channel/title")
            logger.debug(
                f"XML structure: {xml.etree.ElementTree.tostring(title, encoding='unicode')}"
            )
            if title is not None:
                return title.text
