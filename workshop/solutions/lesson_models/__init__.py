"""Small, inspectable models used by the facilitator's reference bots."""

from collections import Counter, defaultdict
from functools import lru_cache
from math import exp, log, sqrt

from rpsdk import Move

MOVES = tuple(Move)
COUNTER = {Move.ROCK: Move.PAPER, Move.PAPER: Move.SCISSORS, Move.SCISSORS: Move.ROCK}
UNIFORM = (1 / 3, 1 / 3, 1 / 3)


def payoff(action, opposing):
    return int(action.beats(opposing)) - int(opposing.beats(action))


def best_response(q):
    """An action distribution, uniform over all maximum-payoff actions."""
    values = [sum(p * payoff(action, opposing) for p, opposing in zip(q, MOVES)) for action in MOVES]
    best = max(values)
    tied = [abs(value - best) < 1e-12 for value in values]
    return tuple(int(tie) / sum(tied) for tie in tied)


def frequencies(history):
    counts = Counter(history)
    total = len(history) + 3
    return tuple((counts[move] + 1) / total for move in MOVES)


def one_hot(move):
    return tuple(float(action == move) for action in MOVES)


class ContextCounts:
    """Update each observed successor once; back off when a row is sparse."""

    def __init__(self, order=2):
        self.order = order
        self.rows = [defaultdict(Counter) for _ in range(order + 1)]
        self.seen = 0

    def observe(self, history):
        # setup normally creates a new model. This also handles a shorter replay.
        if len(history) < self.seen:
            self.__init__(self.order)
        for index in range(self.seen, len(history)):
            for order in range(min(self.order, index) + 1):
                context = tuple(history[index - order:index])
                self.rows[order][context][history[index]] += 1
        self.seen = len(history)

    def predict(self, history, order=None, support=3):
        limit = min(self.order if order is None else order, len(history))
        for size in range(limit, -1, -1):
            context = tuple(history[-size:]) if size else ()
            row = self.rows[size].get(context, {})
            count = sum(row.values())
            if size == 0 or count >= support:
                return tuple((row.get(move, 0) + 1) / (count + 3) for move in MOVES)
        return UNIFORM


class Portfolio:
    """Eight policies, scored on proposals stored before the answer arrived."""

    def __init__(self, horizon=501):
        self.model = ContextCounts(2)
        self.logs = [0.0] * 8
        self.eta = sqrt(2 * log(8) / horizon)
        self.pending = None
        self.pending_index = None

    def probabilities(self, mine, theirs):
        if self.pending is not None and len(theirs) > self.pending_index:
            opposing = theirs[self.pending_index]
            for index, proposal in enumerate(self.pending):
                gain = sum(p * payoff(action, opposing) for p, action in zip(proposal, MOVES))
                self.logs[index] += self.eta * gain
            self.pending = None
        self.model.observe(theirs)
        proposals = [
            UNIFORM,
            best_response(frequencies(theirs)),
            best_response(frequencies(theirs[-30:])),
            best_response(self.model.predict(theirs, order=1)),
            best_response(self.model.predict(theirs, order=2)),
            one_hot(COUNTER[mine[-1]]) if mine else UNIFORM,
            one_hot(COUNTER[COUNTER[mine[-1]]]) if mine else UNIFORM,
            one_hot(COUNTER[mine[-2]]) if len(mine) >= 2 else UNIFORM,
        ]
        maximum = max(self.logs)
        weights = [exp(value - maximum) for value in self.logs]
        total = sum(weights)
        mixture = tuple(sum(w * p[action] for w, p in zip(weights, proposals)) / total for action in range(3))
        self.pending = proposals
        self.pending_index = len(theirs)
        return mixture


class TerminalController:
    """Fixed known q: maximize expected terminal match points, not net throws."""

    def __init__(self, q):
        if len(q) != 3 or min(q) < 0 or abs(sum(q) - 1) > 1e-9:
            raise ValueError("q must be a probability distribution over R, P, S")
        self.q = tuple(q)
        # A per-instance cache can be released with this controller at setup.
        self.value = lru_cache(maxsize=None)(self._value)

    def values(self, remaining, difference):
        if remaining < 1:
            raise ValueError("A decision needs at least one remaining throw")
        return tuple(sum(p * self.value(remaining - 1, difference + payoff(action, opposing))
                         for p, opposing in zip(self.q, MOVES)) for action in MOVES)

    def _value(self, remaining, difference):
        if difference > remaining:
            return 1.0
        if difference < -remaining:
            return 0.0
        if remaining == 0:
            return 0.5
        return max(self.values(remaining, difference))

    def choose(self, remaining, difference):
        values = self.values(remaining, difference)
        return MOVES[max(range(3), key=values.__getitem__)]
