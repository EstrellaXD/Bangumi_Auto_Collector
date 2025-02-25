from sqlmodel import Session, SQLModel

from module.models import Bangumi, User
from module.models.rss import RSSItem

from .bangumi import BangumiDatabase
from .engine import engine as e
from .rss import RSSDatabase
from .torrent import TorrentDatabase
from .user import UserDatabase


class Database(Session):
    """
    要提供几个交插的方法
    """

    def __init__(self, engine=e):
        self.engine = engine
        super().__init__(engine)
        self.rss: RSSDatabase = RSSDatabase(self)
        self.torrent: TorrentDatabase = TorrentDatabase(self)
        self.bangumi: BangumiDatabase = BangumiDatabase(self)
        self.user: UserDatabase = UserDatabase(self)

    def bangumi_to_rss(self, bangumi: Bangumi) -> RSSItem | None:
        return self.rss.search_url(bangumi.rss_link)

    def create_table(self):
        SQLModel.metadata.create_all(self.engine)

    def drop_table(self):
        SQLModel.metadata.drop_all(self.engine)

    def migrate(self):
        # Run migration online
        bangumi_data = self.bangumi.search_all()
        user_data = self.exec("SELECT * FROM user").all()
        readd_bangumi = []
        for bangumi in bangumi_data:
            dict_data = bangumi.model_dump()
            del dict_data["id"]
            readd_bangumi.append(Bangumi(**dict_data))
        self.drop_table()
        self.create_table()
        self.commit()
        bangumi_data = self.bangumi.search_all()
        self.bangumi.add_all(readd_bangumi)
        self.add(User(**user_data[0]))
        self.commit()
