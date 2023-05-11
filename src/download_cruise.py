import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class CruiseDownloader:
    def __init__(
        self,
        archive_path,
        chrome_driver_path="/Users/dbernadett/chromedriver_mac_arm64/chromedriver",
    ):
        self.archive_path = archive_path
        self.chrome_driver_path = chrome_driver_path

    def _parse_bshtml(self, bs_html):
        parsed_fields = {}
        parsed_fields["title"] = bs_html.h4.text.strip()
        parsed_fields["company"] = "cruise"
        return parsed_fields

    def _get_bshtml(self, url, id, archive_path, redownload):
        in_cache = f"{id}.html" in os.listdir(archive_path)
        if in_cache and not redownload:
            with open(os.path.join(archive_path, f"{id}.html"), "r") as file:
                html = file.read()
            page = BeautifulSoup(html, features="html.parser")
        else:
            options = Options()
            # options.headless = True
            options.add_argument("--headless")

            # create a service object to start the chromedriver service
            service = webdriver.chrome.service.Service(self.chrome_driver_path)
            driver = webdriver.Chrome(service=service, options=options)
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
