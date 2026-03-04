from dataclasses import dataclass

from examples.rentagent_vn.runner import BackgroundScrapeRunner
from langclaw import LangclawContext


@dataclass(kw_only=True)
class RentAgentContext(LangclawContext):
    scrape_runner: BackgroundScrapeRunner
    rental_urls: list[str]
