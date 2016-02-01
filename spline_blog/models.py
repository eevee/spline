from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Unicode,
    UnicodeText,
)
from spline.models import Base, TZDateTime, now


class BlogPost(Base):
    __tablename__ = 'blog'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    timestamp = Column(TZDateTime, nullable=False, index=True, default=now)
    title = Column(Unicode, nullable=False)
    content = Column(UnicodeText, nullable=False)

    # TODO author?

    # TODO split this stuff off.
    #attachment = Column(Unicode, nullable=True)
