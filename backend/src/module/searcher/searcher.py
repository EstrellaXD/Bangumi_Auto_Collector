import json
from typing import TypeAlias

from module.conf import settings
from module.models import Bangumi, RSSItem, Torrent
from module.network import RequestContent
from module.rss import RSSAnalyser

from .provider import search_url

SEARCH_KEY = [
    "group_name",
    "title_raw",
    "season_raw",
    "subtitle",
    "source",
    "dpi",
]

BangumiJSON: TypeAlias = str


class SearchTorrent(RequestContent, RSSAnalyser):     
    def get_dense_torrent(self, bangumi: Bangumi) -> Torrent:
        dense_info = self.official_dense_parser(bangumi, None)
        if dense_info:
            return Torrent(name=dense_info.title_web, url=dense_info.torrent_url, homepage=dense_info.homepage)
    
    def search_torrents(self, rss_item: RSSItem) -> list[Torrent]:
        return self.get_torrents(rss_item.url)

    def analyse_keyword(
        self, keywords: list[str], site: str = "mikan", limit: int = 5
    ) -> BangumiJSON:
        rss_item = search_url(site, keywords)
        torrents = self.search_torrents(rss_item)
        # yield for EventSourceResponse (Server Send)
        exist_list = []
        for torrent in torrents:
            if len(exist_list) >= limit:
                break
            bangumi = self.torrent_to_data(torrent=torrent, rss=rss_item)
            if bangumi:
                if site in ["kisssub"]:
                    yield json.dumps(bangumi.dict(), separators=(",", ":"))
                else:
                    special_link = self.special_url(bangumi, site).url
                    if special_link not in exist_list:
                        bangumi.rss_link = special_link
                        exist_list.append(special_link)
                        yield json.dumps(bangumi.dict(), separators=(",", ":"))

    @staticmethod
    def special_url(data: Bangumi, site: str) -> RSSItem:
        keywords = [getattr(data, key) for key in SEARCH_KEY if getattr(data, key)]
        url = search_url(site, keywords)
        return url

    def search_season(self, data: Bangumi, site: str = "mikan") -> list[Torrent]:
        rss_item = self.special_url(data, site)
        torrents = self.search_torrents(rss_item)
        return [torrent for torrent in torrents if data.title_raw in torrent.name]

