from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Unicode,
    UnicodeText,
)
from sqlalchemy.orm import relationship

from splinter.models import Base, User
from splinter.models import Prose, TZDateTime, now


class ComicPage(Base):
    __tablename__ = 'comic_pages'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    timestamp = Column(TZDateTime, nullable=False, index=True, default=now)
    author_user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    file = Column(UnicodeText, nullable=False)
    title = Column(Unicode, nullable=False)
    comment = Column(Prose, nullable=False)

    author = relationship(User, backref='comic_pages')
