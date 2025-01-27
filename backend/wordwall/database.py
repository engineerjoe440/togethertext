################################################################################
"""
WordWall - Simple, Self-Hosted Collaborative Word Cloud Generator.

(c) 2025 | Stanley Solutions | Joe Stanley
License: MIT
"""
################################################################################

from pathlib import Path
from uuid import uuid4

from pydbantic import Database, DataBaseModel, PrimaryKey


async def connect_database(
    database_path: str,
    testing: bool = False,
) -> Database:
    """Connect to the Database and Manage any Automatic Migrations Needed."""
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    return await Database.create(
        f'sqlite:///{database_path}.db',
        tables=[WordResponse],
        testing=testing,
    )

class WordResponse(DataBaseModel):
    """Single Word Response from a Participant."""
    id: str = PrimaryKey(default=lambda: str(uuid4()))
    wall_hash: str
    player_id: str
    word: str
