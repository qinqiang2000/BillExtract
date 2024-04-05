import os
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    create_engine, Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker


def get_sqlite_url() -> str:
    # 使用 SQLite：//<nohostname>/<path>
    # 其中<path>是你的SQLite数据库文件的路径，这里我们使用相对路径example.db
    return "sqlite:///data.db"


# 使用SQLite引擎
ENGINE = create_engine(get_sqlite_url())
SessionClass = sessionmaker(bind=ENGINE)

Base = declarative_base()


@contextmanager
def get_session():
    """Provide a transactional scope around a series of operations."""
    session = SessionClass()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class TimestampedModel(Base):
    """An abstract base model that includes the timestamp fields."""
    __abstract__ = True

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        comment="The time the record was created (UTC).",
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="The time the record was last updated (UTC).",
    )

    uuid = Column(
        String,  # 修改为 String 以兼容 SQLite
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        doc="Unique identifier for this model.",
    )


class Example(TimestampedModel):
    """A representation of an example.

    Examples consist of content together with the expected output.

    The output is a JSON object that is expected to be extracted from the content.

    The JSON object should be valid according to the schema of the associated extractor.

    The JSON object is defined by the schema of the associated extractor, so
    it's perfectly fine for a given example to represent the extraction
    of multiple instances of some object from the content since
    the JSON schema can represent a list of objects.
    """

    __tablename__ = "examples"

    content = Column(
        Text,
        nullable=False,
        comment="The input portion of the example.",
    )
    output = Column(
        Text,
        comment="The output associated with the example.",
    )
    extractor_id = Column(
        String,
        ForeignKey("extractors.uuid", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key referencing the associated extractor.",
    )

    def __repr__(self) -> str:
        return f"<Example(uuid={self.uuid}, content={self.content[:20]}>"


class Extractor(TimestampedModel):
    __tablename__ = "extractors"

    name = Column(
        String(100),
        nullable=False,
        server_default="",
        comment="The name of the extractor.",
    )
    owner_id = Column(
        String,  # 修改为 String 以兼容 SQLite
        nullable=True,
        comment="Owner uuid.",
    )
    schema = Column(
        Text,  # 修改为 Text 以存储 JSON 结构，因为 SQLite 不支持 JSONB
        nullable=True,
        comment="JSON Schema that describes what content will be extracted from the document",
    )
    description = Column(
        String(100),
        nullable=True,
        server_default="",
        comment="Surfaced via UI to the users.",
    )
    instruction = Column(
        Text, nullable=False, comment="The prompt to the language model."
    )

    examples = relationship("Example", backref="extractor")

    share_uuid = Column(
        String,  # 修改为 String 以兼容 SQLite
        nullable=True,
        comment="The uuid of the shareable link.",
    )

    selected = Column(
        Boolean,
        default=False,
        comment="Indicates whether the extractor is selected.",
    )

    def __repr__(self) -> str:
        return f"<Extractor(id={self.uuid}, description={self.description})>"


def validate_extractor_owner(
        session: Session, extractor_id: String, user_id: String
) -> Extractor:
    """Validate the extractor id."""
    extractor = (
        session.query(Extractor).filter_by(uuid=extractor_id, owner_id=user_id).first()
    )
    return extractor is not None
