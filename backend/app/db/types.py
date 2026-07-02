import uuid

from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.

    SQLite stores UUID as string.
    PostgreSQL can later be upgraded to native UUID with minimal model changes.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID

            return dialect.type_descriptor(UUID(as_uuid=True))

        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        if dialect.name == "postgresql":
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(str(value))

        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(str(value)))

        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        if isinstance(value, uuid.UUID):
            return value

        return uuid.UUID(str(value))