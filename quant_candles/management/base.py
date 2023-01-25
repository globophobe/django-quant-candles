import logging
from typing import Optional

from django.core.management.base import BaseCommand, CommandParser
from django.db.models import QuerySet

from quant_candles.constants import Exchange
from quant_candles.lib import parse_period_from_to
from quant_candles.models import Candle, Symbol

logger = logging.getLogger(__name__)


class BaseTimeFrameCommand(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments."""
        parser.add_argument("--date-to", type=str, default=None)
        parser.add_argument("--time-to", type=str, default=None)
        parser.add_argument("--date-from", type=str, default=None)
        parser.add_argument("--time-from", type=str, default=None)


class BaseTradeDataCommand(BaseTimeFrameCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments."""
        super().add_arguments(parser)
        parser.add_argument("exchange", type=Exchange, choices=Exchange.values)
        parser.add_argument("symbol")
        parser.add_argument("--aggregate", type=bool, default=False)
        parser.add_argument("--filter", type=int, default=0)

    @classmethod
    def get_symbol_display(
        cls,
        exchange: str,
        symbol: str,
        should_aggregate_trades: bool,
        significant_trade_filter: int,
    ) -> str:
        """Get symbol display."""
        parts = [exchange, symbol]
        if should_aggregate_trades:
            parts += ["aggregated", str(significant_trade_filter)]
        else:
            parts.append("raw")
        return " ".join(parts)

    def handle(self, *args, **options) -> Optional[dict]:
        exchange = options["exchange"]
        symbol = options["symbol"]
        should_aggregate_trades = options["aggregate"]
        significant_trade_filter = options["filter"]
        try:
            symbol = Symbol.objects.get(
                exchange=exchange,
                api_symbol=symbol,
                should_aggregate_trades=should_aggregate_trades,
                significant_trade_filter=significant_trade_filter,
            )
        except Symbol.DoesNotExist:
            s = self.get_symbol_display(
                exchange, symbol, should_aggregate_trades, significant_trade_filter
            )
            logger.warn(f"{s} not registered")
        else:
            timestamp_from, timestamp_to = parse_period_from_to(
                date_from=options["date_from"],
                time_from=options["time_from"],
                date_to=options["date_to"],
                time_to=options["time_to"],
            )
            return {
                "symbol": symbol,
                "timestamp_from": timestamp_from,
                "timestamp_to": timestamp_to,
            }


class BaseCandleCommand(BaseTimeFrameCommand):
    def get_queryset(self) -> QuerySet:
        """Get queryset."""
        raise NotImplementedError

    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments."""
        super().add_arguments(parser)
        queryset = self.get_queryset()
        parser.add_argument(
            "name",
            type=str,
            choices=queryset.values_list("code_name", flat=True),
        )
        parser.add_argument("--retry", action="store_true")

    def handle(self, *args, **options) -> None:
        """Run command."""
        name = options["name"]
        try:
            candle = Candle.objects.get(code_name=name)
        except Candle.DoesNotExist:
            logger.warn(f"{name} not registered")
        else:
            timestamp_from, timestamp_to = parse_period_from_to(
                date_from=options["date_from"],
                time_from=options["time_from"],
                date_to=options["date_to"],
                time_to=options["time_to"],
            )
            return {
                "candle": candle,
                "timestamp_from": timestamp_from,
                "timestamp_to": timestamp_to,
                "retry": options["retry"],
            }
