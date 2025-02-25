import pytest

from module.database import Database
from module.rss import RSSEngine, RSSManager, RSSRefresh

from .test_database import engine as e


@pytest.mark.asyncio
async def test_rss_engine():
    engine = RSSEngine(e)
    manager = RSSManager(e)
    rss_link = "https://mikanani.me/RSS/Bangumi?bangumiId=2353&subgroupid=552"

    res = await manager.add_rss(rss_link, aggregate=False)
    assert res

    with Database(e) as db:
        result = db.rss.search_active()

    assert result[1].name == "Mikan Project - 无职转生～到了异世界就拿出真本事～"

    new_torrents = await RSSRefresh(result[1]).pull_rss()

    torrent = new_torrents[0]
    assert (
        torrent.name
        == "[Lilith-Raws] 无职转生，到了异世界就拿出真本事 / Mushoku Tensei - 11 [Baha][WEB-DL][1080p][AVC AAC][CHT][MP4]"
    )
