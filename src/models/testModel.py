from ..config import db
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import UUID, String
from sqlalchemy_serializer import SerializerMixin
import uuid

class TestModel(db.Model, SerializerMixin):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text_test: Mapped[str]= mapped_column(String(50),nullable=False)
