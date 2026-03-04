from examples.rentagent_vn.callbacks import (
    progress_callback,
    result_callback,
    streaming_url_callback,
)
from examples.rentagent_vn.context import RentAgentContext
from examples.rentagent_vn.prompts import SYSTEM_PROMPT
from examples.rentagent_vn.runner import BackgroundScrapeRunner
from examples.rentagent_vn.tinyfish.client import TinyFishClient
from examples.rentagent_vn.toolsx import contact_landlord, research_area, search_rentals
from langclaw import Langclaw

app = Langclaw(system_prompt=SYSTEM_PROMPT, context_schema=RentAgentContext)
app.register_tools([search_rentals, contact_landlord, research_area])

tinyfish_client = TinyFishClient(timeout=5000)


@app.on_startup
async def _open_tinyfish() -> None:
    await tinyfish_client.open()


@app.on_shutdown
async def _close_tinyfish() -> None:
    await tinyfish_client.close()


scrape_runner = BackgroundScrapeRunner(
    app=app,
    result_callback=result_callback,
    streaming_url_callback=streaming_url_callback,
    progress_callback=progress_callback,
    tinyfish_client=tinyfish_client,
)

app.set_context_defaults(
    scrape_runner=scrape_runner,
    rental_urls=["https://www.facebook.com/groups/1930421007111976/"],
)

if __name__ == "__main__":
    app.run()
