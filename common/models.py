from core.database.config import Base
from sqlalchemy import Column, DateTime, func, Boolean
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Column, Integer, String, Text, BigInteger, Integer, ForeignKey


class BaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=func.now(), nullable=True)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )

    is_deleted = Column(Boolean, default=False, nullable=True)


class User(BaseModel, SerializerMixin):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # hashed password
    is_superuser = Column(Boolean, default=False)  # For admin
    is_active = Column(Boolean, default=False)  # For email verification
    is_parent = Column(Boolean, default=False)  # For parent management
    password_reset_token = Column(String(100), nullable=True, unique=True)

    age = Column(Integer, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    country = Column(String(50), nullable=True)
    pin_code = Column(String(10), nullable=True)
    profile_photo = Column(String(255), nullable=True)

    # Relationship to Children
    children: Mapped[list["Child"]] = relationship(back_populates="parent")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.first_name} {self.last_name})>"


class Child(BaseModel, SerializerMixin):
    __tablename__ = "children"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    additional_info = Column(Text, nullable=True)

    # Relationship to Parent
    parent_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    parent: Mapped["User"] = relationship(back_populates="children")

    def __repr__(self):
        return f"<Child(id={self.id}, name={self.name})>"
