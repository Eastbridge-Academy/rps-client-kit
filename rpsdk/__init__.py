"""Shared primitives exposed to bots during execution."""

from __future__ import annotations

from enum import Enum


class Move(str, Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"

    @classmethod
    def from_value(cls, value: str | Move) -> Move:
        if isinstance(value, Move):
            return value
        normalized = value.lower()
        try:
            return Move(normalized)
        except ValueError as exc:  # pragma: no cover - defensive path
            raise ValueError(f"Invalid move: {value!r}") from exc

    def beats(self, other: Move) -> bool:
        return (
            (self is Move.ROCK and other is Move.SCISSORS)
            or (self is Move.SCISSORS and other is Move.PAPER)
            or (self is Move.PAPER and other is Move.ROCK)
        )

    def to_payload(self) -> str:
        return self.value


ALL_MOVES: tuple[Move, ...] = (Move.ROCK, Move.PAPER, Move.SCISSORS)
