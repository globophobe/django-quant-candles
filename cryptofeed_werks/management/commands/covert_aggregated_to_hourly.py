from cryptofeed_werks.management.base import BaseAggregatedTradeDataCommand
from cryptofeed_werks.storage import convert_minute_aggregated_to_hourly


class Command(BaseAggregatedTradeDataCommand):
    help = (
        "Convert trade data aggregated by minute to hourly, to reduce file operations."
    )

    def handle(self, *args, **options) -> None:
        kwargs = super().handle(*args, **options)
        if kwargs:
            convert_minute_aggregated_to_hourly(**kwargs)