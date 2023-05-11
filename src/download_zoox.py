import logging
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Create a logger
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.INFO)
# Create a console handler
handler = logging.StreamHandler()
# Set the logging format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(handler)


class ZooxDownloader:
    def __init__(
        self,
        archive_path,
    ):
        self.archive_path = archive_path

    def _parse_bshtml(self, bs_html):
        parsed_fields = {}
        parsed_fields["title"] = bs_html.h1.text.strip()
        parsed_fields["company"] = "zoox"
        return parsed_fields

    def _get_bshtml(self, url, id, archive_path, redownload):
        in_cache = f"{id}.html" in os.listdir(archive_path)
        if in_cache and not redownload:
            logger.info(f"Cache Hit on {id}, using local file")
            with open(os.path.join(archive_path, f"{id}.html"), "r") as file:
                html = file.read()
            page = BeautifulSoup(html, features="html.parser")
        else:
            logger.info(f"Downloading {id} from {url}")
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            page = BeautifulSoup(
                driver.page_source, features="html.parser"
            )  # fetch HTML source code after rendering

            tags_to_remove = [
                "script",
                "img",
                "style",
                "link",
                "svg",
                "meta",
                "iframe",
                "button",
                "input",
                "label",
            ]
            for tag in tags_to_remove:
                for e in page(tag):
                    e.extract()

            html = page.prettify()
            with open(f"{os.path.join(archive_path,str(id))}.html", "w") as file:
                file.write(html)
        return page

    def download_and_parse(self, url, id, archive_path, redownload):
        page = self._get_bshtml(url, id, archive_path, redownload)
        return self._parse_bshtml(page)
