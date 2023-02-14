from datetime import datetime
from typing import Callable

from django.db import models
from pandas import DataFrame

from quant_candles.models import TradeDataSummary


class BaseController:
    def __init__(
        self,
        symbol: models.Model,
        timestamp_from: datetime,
        timestamp_to: datetime,
        on_data_frame: Callable,
        retry: bool = False,
        verbose: bool = True,
    ):
        self.symbol = symbol
        self.timestamp_from = timestamp_from
        self.timestamp_to = timestamp_to
        self.on_data_frame = on_data_frame
        self.retry = retry
        self.verbose = verbose

    @property
    def log_format(self) -> str:
        """Log format."""
        symbol = str(self.symbol)
        return f"{symbol}: {{timestamp}}"

    @property
    def columns(self) -> list:
        """Columns."""
        return [
            "uid",
            "timestamp",
            "nanoseconds",
            "price",
            "volume",
            "notional",
            "tickRule",
            "index",
        ]

    def main(self):
        """Main."""
        raise NotImplementedError

    def get_candles(
        self, timestamp_from: datetime, timestamp_to: datetime
    ) -> DataFrame:
        """Get candles."""
        raise NotImplementedError

    def delete_trade_data_summary(
        self, timestamp_from: datetime, timestamp_to: datetime
    ) -> None:
        """Delete trade data summary."""
        trade_data_summary = TradeDataSummary.objects.filter(
            symbol=self.symbol,
            date__gte=timestamp_from.date(),
            date__lte=timestamp_to.date(),
        )
        trade_data_summary.delete()
