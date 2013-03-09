from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    UnicodeText,
)
from sqlalchemy.orm import relationship


from splinter.models import Base, User
from splinter.models import TZDateTime, now


class Love(Base):
    __tablename__ = 'loves'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    timestamp = Column(TZDateTime, nullable=False, index=True, default=now)
    source_user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    target_user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    comment = Column(UnicodeText, nullable=False)

    source = relationship(User,
        foreign_keys=[source_user_id],
        primaryjoin=(source_user_id == User.id),
        backref='loves_expressed')
    target = relationship(User,
        foreign_keys=[target_user_id],
        primaryjoin=(target_user_id == User.id),
        backref='loves_received')
