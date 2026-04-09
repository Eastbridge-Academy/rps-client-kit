"""Local copy of tournament SDK for participants."""

from __future__ import annotations

from enum import Enum


class Move(str, Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"

    @classmethod
    def from_value(cls, value: str | "Move") -> "Move":
        if isinstance(value, Move):
            return value
        return Move(value.lower())

    def beats(self, other: "Move") -> bool:
        return (
            (self is Move.ROCK and other is Move.SCISSORS)
            or (self is Move.SCISSORS and other is Move.PAPER)
            or (self is Move.PAPER and other is Move.ROCK)
        )
