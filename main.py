# Asynchronous Clutch.co scraper.
# Collects Ukrainian web development companies from paginated listings,
# validates provider entries, and exports structured data to Excel.

import nodriver as nd
import asyncio
import re
import pandas as pd
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, TimeRemainingColumn
from web_util import select_until_appear, select_all_until_appear

console = Console()


def ask_pages() -> int:
    """Ask user for number of pages to parse; ensures input is a positive integer."""

    while True:
        value = Prompt.ask("[cyan]Pages to parse[/]")
        if value.isdigit() and int(value) > 0:
            return int(value)
        console.print("[bold red]Please enter a valid number[/]")


async def get_providers(page: nd.Tab, pages_to_parse: int) -> list[str]:
    """Gathers all provider links from entered amount of pages."""

    all_provider_links = []
    with Progress(SpinnerColumn(spinner_name='simpleDots', style='blue'),
                  TextColumn('{task.description} [dim magenta]({task.completed}/{task.total})'),
                  BarColumn(),
                  TimeRemainingColumn()
                  ) as progress:
        pages_gathered = progress.add_task('Pages gathered', total=pages_to_parse)
        for page_num in range(pages_to_parse + 1):
            if page_num == 1:
                continue  # page 1 is copy of page 2, so page 1 must be skipped explicitly

            await page.get(f'https://clutch.co/ua/web-developers?page={page_num}')

            if '<title>404 - Not Found</title>' in await page.get_content():
                break  # stop when pagination exceeds available page
            providers = await select_all_until_appear(page, '.provider-row')
            progress.update(pages_gathered, advance=1)
            providers_validated = progress.add_task('Providers validated', total=len(providers))
            for nv_provider in providers:
                link_pr = await provider_validation(nv_provider)
                if link_pr is None:
                    progress.update(providers_validated, advance=1)
                    continue
                all_provider_links.append(link_pr)
                progress.update(providers_validated, advance=1)
            progress.remove_task(providers_validated)
        progress.remove_task(pages_gathered)

    return all_provider_links


async def provider_validation(provider: nd.Element) -> str | None:
    """Checks if provider is not featured, and returns its link."""

    # Skip promoted providers to avoid biased listings
    if "featured" in await provider.get_html():
        return None
    link_el = await provider.query_selector('a.directory_profile')
    link = 'https://clutch.co' + link_el.attributes[link_el.attributes.index('href') + 1]
    return str(link)


async def city_get(page: nd.Tab) -> list[str]:
    """Extract Ukrainian city locations from provider profile."""
    cities_el = await select_until_appear(page, '#profile-locations > ul')
    cities = []
    li_els = await cities_el.query_selector_all('li')
    for i in li_els:
        city = i.text_all
        if "Ukraine" in city:
            cities.append((city.split(',')[0]).strip())
    return cities


async def provider_parsing(page: nd.Tab, link: str) -> dict:
    """Parse provider profile page into structured fields."""
    await page.get(str(link))
    link_el = await select_until_appear(page, '.website-link__item')
    name_el = await select_until_appear(page, 'head > title')
    hour_rate_el = await select_until_appear(page,
                                             '#summary_section > ul > li:nth-child(2) > div > span.profile-summary__detail-title')
    min_project_size_el = await select_until_appear(page,
                                                    '#summary_section > ul > li:nth-child(1) > div > span.profile-summary__detail-title')
    rating_for_cost_el = await select_until_appear(page,
                                                   '#metrics_section > div.profile-metrics__item.profile-metrics__item--rating > span.profile-metrics__value.profile-metrics__value--rating')
    num_of_reviews_el = await select_until_appear(page,
                                                  '#reviews-sg-accordion > div > section > div.profile-insights > button')

    name = name_el.text.split(' Reviews')[0]
    website = \
        ((link_el.attributes[link_el.attributes.index('data-link') + 1]).split('provider_website=')[1]).split('&')[0]
    cities = await city_get(page)
    hour_rate = hour_rate_el.text_all.replace(' ', '')
    min_project_size = min_project_size_el.text_all
    rating_for_cost = (rating_for_cost_el.text_all.replace('\n', '')).replace(' ', '')
    num_of_reviews = re.sub(r'\D', '', num_of_reviews_el.text)
    return {'name': name,
            'website': website,
            'cities': cities,
            'hour rate': hour_rate,
            'min project size': min_project_size,
            'rating for cost': rating_for_cost,
            'number of reviews': num_of_reviews}


async def main():
    browser = await nd.start()
    page = await browser.get('https://google.com')

    providers_data = []
    unique_keys = set()

    pages_to_parse = ask_pages()
    provider_links = await get_providers(page, pages_to_parse)

    with Progress(SpinnerColumn(spinner_name='simpleDots', style='blue'),
                  TextColumn('{task.description} [dim magenta]({task.completed}/{task.total})'),
                  BarColumn(),
                  TimeRemainingColumn()
                  ) as progress:
        providers_processed = progress.add_task('Providers processed', total=len(provider_links))
        for provider in provider_links:
            parsed_data = await provider_parsing(page, provider)
            if parsed_data['name'].lower() not in unique_keys:
                unique_keys.add(parsed_data['name'].lower())
                providers_data.append(parsed_data)
            progress.update(providers_processed, advance=1)

    df = pd.DataFrame(providers_data)
    df.to_excel('results.xlsx')


asyncio.run(main())
