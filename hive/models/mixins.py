import uuid
from datetime import datetime

from sqlalchemy import CHAR, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID

from hive.database import db


def now():
    return datetime.utcnow()


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Base(db.Model):
    __abstract__ = True

    id = db.Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))


class TimeMixin(Base):
    __abstract__ = True
    created = db.Column(db.DateTime, default=db.func.current_timestamp())


class UserTimeMixin(TimeMixin):
    __abstract__ = True
    last_seen = db.Column(db.DateTime, default=db.func.current_timestamp(),
                          onupdate=db.func.current_timestamp())
