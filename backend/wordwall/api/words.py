################################################################################
"""
WordWall - Simple, Self-Hosted Collaborative Word Cloud Generator.

(c) 2025 | Stanley Solutions | Joe Stanley
License: MIT
"""
################################################################################

from typing import Awaitable, Union

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from ..database import WordResponse
from ..session import Manager

router = APIRouter(prefix="/words")

manager = Manager()

TEST_WORDS = [{
    "value": 'invent',
    "count": 64,
  },
  {
    "value": 'clever',
    "count": 11,
  },
  {
    "value": 'thought',
    "count": 16,
  },
  {
    "value": 'create',
    "count": 17,
  },
]

async def active_wall(
    func: Awaitable,
    wall_hash: str,
    player_id: str | None = None
) -> list[dict[str, Union[int, str]]]:
    """Handler for the Wall's Activity."""
    if (wall := manager.get_by_hash(wall_hash=wall_hash)):
        if wall.active:
            await func()
        else:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="That WordWall is not presently active."
            )
        return await get_words_for_wall(wall_id=wall.id, player_id=player_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="That WordWall could not be found."
    )

@router.get("/{wall_id}")
async def get_words_for_wall(
    wall_id: str,
    player_id: str | None = None,
):
    """Get all of the Words for a Particular Wall."""
    if 'test' in wall_id.lower():
        # Respond with Test Words
        return TEST_WORDS
    if wall_id.lower() == "all":
        return await WordResponse.all()
    if (wall := manager.get_by_id(wall_id=wall_id)):
        extra_filters = {}
        if player_id:
            extra_filters["player_id"] = player_id
        word_records = await WordResponse.filter(
            wall_hash=wall.hash,
            **extra_filters
        )
        if player_id:
            # Loading for a Player Page
            return word_records
        words = {}
        for record in word_records:
            if not record.word:
                # Null/Empty -- Skip
                continue
            cleaned_word = record.word.strip()
            if cleaned_word not in words:
                words[cleaned_word] = 1 # Record Word
            else:
                words[cleaned_word] += 1 # Increment
        # Pack List of Dictionaries with Appropriate Structure
        return [{'value':w, 'count':cnt} for w, cnt in words.items()]
    logger.error(f"Attempted to load Wall with ID: {wall_id}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="That WordWall could not be found."
    )

@router.get("/{wall_id}/count")
async def get_word_count(wall_id: str) -> int:
    """Count the Total Number of Words for the Wall."""
    if (wall := manager.get_by_id(wall_id=wall_id)):
        return await WordResponse.filter(
            WordResponse.gt('word', ""), # Ensure Not Empty
            wall_hash=wall.hash,
            count_rows=True, # Return as a count
        )

@router.put("/")
async def add_word_to_wall(
    word: WordResponse,
    player_id: str | None = None,
) -> list[dict[str, Union[int, str]]]:
    """Add a new Word to a Specified Wall."""
    if player_id:
        word.player_id = player_id
    word.word = word.word.lower()
    return await active_wall(
        func=word.insert,
        wall_hash=word.wall_hash,
        player_id=word.player_id,
    )

@router.post("/")
async def update_word_on_wall(
    word: WordResponse
) -> list[dict[str, Union[int, str]]]:
    """Update an Existing Word on a Specified Wall."""
    word.word = word.word.lower()
    return await active_wall(
        func=word.update,
        wall_hash=word.wall_hash,
        player_id=word.player_id,
    )

@router.delete("/")
async def remove_word_from_wall(
    word: WordResponse,
) -> list[dict[str, Union[int, str]]]:
    """Remove an Existing Word from a Wall."""
    return await active_wall(
        func=word.delete,
        wall_hash=word.wall_hash,
        player_id=word.player_id,
    )
