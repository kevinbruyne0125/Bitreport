import numpy as np
from app.database.models import Level, db
from app.ta.helpers import indicator
from app.ta.levels.checker import is_level
from app.ta.levels.fuzzy_level import FuzzyLevel
from app.ta.charting.base import Universe


class Levels(object):
    def __init__(self, universe: Universe) -> None:
        self.pair = universe.pair
        self.timeframe = universe.timeframe
        self.close = universe.close
        self.time = universe.time
        assert self.close.size == self.time.size, f'{self.close.size} != {self.time.size}'

    @indicator('levels', ['levels'])
    def __call__(self) -> dict:
        # TODO: do not create levels with each request...
        # Look for new levels
        self._find_levels(self.close, self.time)

        # Select best levels
        levels = {
            'levels': self._score_levels(self.close),
            'info': []
        }
        return levels

    def _save_levels(self, levels: list) -> None:
        for x in levels:
            params = dict(
                pair=self.pair,
                timeframe=self.timeframe,
                strength=x.strength,
                type=x.type,
                value=float(x.value)
            )
            lvl = Level.query.filter_by(**params).first()
            if not lvl:
                params.update(first_occurrence=x.time)
                db.session.add(Level(**params))

        db.session.commit()

    def _find_levels(self, close: np.ndarray, time: np.ndarray) -> None:
        """
        Searches for new levels in the given time series.
        New, unique levels are saved to database.

        Parameters
        ----------
        close - time series of price values
        """
        lvls = []
        for i, x in enumerate(close):
            lvl = is_level(i, x, close, time[i])
            if lvl is not None:
                lvls.append(lvl)

        if lvls:
            self._save_levels(lvls)

    def _score_levels(self, close: np.ndarray, r: float = 0.03) -> list:
        """
        Looks for levels in the given range (r% margin). Then, each
        level is converted to fuzzy level. Next we find number of
        neighbors of each level. Finally we select best support and
        resistance.

        Parameters
        ----------
        close: price values
        r - float from (0,1), additional margin for level search

        Returns
        -------
        list
        """
        # Take levels between prices
        price_max = float(np.max(close))
        price_min = float(np.min(close))

        lvls = Level.query. \
            filter_by(pair=self.pair). \
            filter(Level.value >= (1 - r) * price_min). \
            filter(Level.value <= (1 + r) * price_max). \
            order_by(Level.value).distinct(Level.value, Level.type).all()

        # Create FuzzyLevels
        last_price = close[-1]
        lvls = [FuzzyLevel(lvl, last_price) for lvl in lvls]
        lvls = [lvl.update(lvls) for lvl in lvls]

        resistance = [x for x in lvls if x.dist >= 0]
        support = [x for x in lvls if x.dist <= 0]

        output = []
        if resistance:
            resistance.sort(key=lambda x: x.score)
            resistance = list(filter(lambda x: x.score == resistance[-1].score, resistance))
            resistance.sort(key=lambda x: x.dist)
            if resistance:
                output.append(resistance[0])

        if support:
            support.sort(key=lambda x: x.score)
            check = lambda x: x.score == support[-1].score
            if output:
                res_value = output[0].lvl.value
                check = lambda x: (x.score == support[-1].score) and (abs(x.lvl.value / res_value - 1) > 0.04)

            support = list(filter(check, support))
            support.sort(key=lambda x: x.dist, reverse=True)
            if support:
                output.append(support[0])

        return [x.json() for x in output]

    @staticmethod
    def _fib_levels(close: np.ndarray, top: float, bottom: float) -> list:
        top_index = np.where(close == top)[0][-1]
        bottom_index = np.where(close == bottom)[0][-1]

        height = top - bottom
        fib_lvls = (0.00, .236, .382, .500, .618, 1.00)

        if top_index < bottom_index:
            levels = [bottom + x * height for x in fib_lvls]
        else:
            levels = [bottom - x * height for x in fib_lvls]

        return list(levels)