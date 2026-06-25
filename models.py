# ths file defines the Task db model for the app
#table of contents:
#Task db model
# db column
# __repr__ method

from sqlalchemy import String, Integer, Boolean # Import SQLAlchemy column types
from sqlalchemy.orm import Mapped, mapped_column #import ORM typing and column mapping tools

from database import Base

# Task model represents the "tasks" table
class Task(Base):
    __tablename__ = "tasks" # name of db table

    id: Mapped[int] = mapped_column(Integer, primary_key=True) # unique ID for each task
    title: Mapped[str] = mapped_column(String, nullable=False) #Required task title
    note: Mapped[str | None] = mapped_column(String, nullable=True) #Optional task note. It could be empty/null
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False) # Task status. It is not completed by default

# Returns a readable representation of the Task object for debugging
    def __repr__(self):
        return f"task(id={self.id}, title={self.title}, note={self.note}, completed={self.completed})"