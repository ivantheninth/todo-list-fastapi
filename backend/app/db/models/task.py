# ths file defines the Task db model for the app
#table of contents:
#Task db model
# db column
# __repr__ method

from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, ForeignKey # Import SQLAlchemy column types
from sqlalchemy.orm import Mapped, mapped_column, relationship #import ORM typing and column mapping tools

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.user import User

# Task model represents the "tasks" table
class Task(Base):
    __tablename__ = "tasks" # name of db table

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # unique ID for each task
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="tasks")

    title: Mapped[str] = mapped_column(String, nullable=False) #Required task title
    note: Mapped[str | None] = mapped_column(String, nullable=True) #Optional task note. It could be empty/null
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)# Task status. It is not completed by default

# Returns a readable representation of the Task object for debugging
    def __repr__(self):
        return f"task(id={self.id}, title={self.title}, note={self.note}, completed={self.completed})"