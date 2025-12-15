from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Text

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(32), default="user")
    password_hash: Mapped[str] = mapped_column(String(255))

class App(Base):
    __tablename__ = "apps"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    developer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    developer = relationship("User")

class Version(Base):
    __tablename__ = "versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    app_id: Mapped[int] = mapped_column(ForeignKey("apps.id"))
    semver: Mapped[str] = mapped_column(String(32))
    platform: Mapped[str] = mapped_column(String(32))  # android/ios/web
    file_url: Mapped[str] = mapped_column(String(512))
    file_sha256: Mapped[str] = mapped_column(String(64))
    release_notes: Mapped[str] = mapped_column(Text)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
