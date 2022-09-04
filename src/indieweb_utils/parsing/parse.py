import mf2py
import requests
from bs4 import BeautifulSoup


class RequestError(Exception):
    pass


def _get_soup_from_request(url: str, headers: dict = {}):
    try:
        contents = requests.get(url, timeout=10, headers=headers).text
    except requests.exceptions.RequestException:
        raise RequestError("Request to retrieve URL did not return a valid response.")

    return BeautifulSoup(contents, "html.parser")


def get_parsed_mf2_data(parsed_mf2: mf2py.Parser, html: str = "", url: str = ""):
    if parsed_mf2:
        return parsed_mf2
    elif html:
        return mf2py.parse(doc=html)
    elif url:
        return mf2py.parse(url=url)

    raise RequestError("No soup, url, or HTML document provided.")


def get_soup(html: str = "", soup: BeautifulSoup = {}, url: str = "", headers: dict = {}):
    if html:
        return BeautifulSoup(html, "html.parser")

    if soup:
        return soup

    if url:
        return _get_soup_from_request(url, headers=headers)

    raise RequestError("No soup, url, or HTML document provided.")
