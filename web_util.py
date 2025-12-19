import nodriver as nd
import asyncio


async def select_until_appear(
    page: nd.Tab,
    selector: str,
    max_attempts: int = 100,
    poll_interval: float = 0.1
) -> nd.Element | None:
    for _ in range(max_attempts):
        try:
            el = await page.select(selector)
            if el is not None:
                return el
        except Exception:
            pass
        await asyncio.sleep(poll_interval)

    return None


async def select_all_until_appear(
    page: nd.Tab,
    selector: str,
    max_attempts: int = 100,
    poll_interval: float = 0.1
) -> list[nd.Element]:
    for _ in range(max_attempts):
        try:
            els = await page.select_all(selector)
            if els:
                return els
        except Exception:
            pass

        await asyncio.sleep(poll_interval)

    return []
