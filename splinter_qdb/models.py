from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    UnicodeText,
)
from sqlalchemy.orm import relationship

from splinter.models import Base, User
from splinter.models import TZDateTime, now


class Quote(Base):
    __tablename__ = 'quotes'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    timestamp = Column(TZDateTime, nullable=False, index=True, default=now)
    poster_user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    comment = Column(UnicodeText, nullable=False)
    content = Column(UnicodeText, nullable=False)

    poster = relationship(User,
        backref='quotes_posted')
