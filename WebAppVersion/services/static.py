""" Services to traverse web page and collect static content. """
import enum
import time
import logging
import dataclasses
from typing import Generator, Set, Optional
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from .static import FailedToDownloadFileException


@dataclasses.dataclass
class StaticFile:
    """ Represents static file from web page. """
    path: str
    content: str = dataclasses.field(repr=False)
    content_type: str = None


class StaticFilesTraversalService:
    HTTP_429_TOO_MANY_REQUESTS = 429

    class RetryPolicy(enum.IntEnum):
        """ Available retry policies. """
        EXPONENTIAL = 1

    def __init__(
        self,
        base_url: str,
        request_delay: float = 1.0,
        max_retries: int = 3,
        retry_delay: float = 3.0,
        retry_policy: RetryPolicy = RetryPolicy.EXPONENTIAL,
    ):
        """
        Make instance of StaticFilesTraversalService.

        :param base_url: Base URL of the web page.
        :param request_delay: Delay between requests in seconds.
        :param max_retries: Maximum number of retries.
        :param retry_delay: Retry delay in seconds.
        :param retry_policy: Retry policy.
        """
        self.base_url = base_url

        parsed_base_url = urlparse(base_url)
        self.base_netloc = parsed_base_url.netloc

        self.request_delay = request_delay

        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_policy = retry_policy

        self.session = requests.Session()

    def _get_retry_delay(self, retry_number: int) -> float:
        """
        Get delay in seconds between retry attempts.

        :param retry_number: Number of current retry attempt.
        :return: Delay in seconds.
        """
        if self.retry_policy == self.RetryPolicy.EXPONENTIAL:
            return self.retry_delay ** retry_number
        else:
            raise NotImplementedError("Passed retry policy is not implemented")

    def _download(self, url: str) -> (str, str):
        """
        Download resource from URL.

        :param url: URL to download.
        :return: Downloaded resource and its content type.
        """
        logging.info(f"⌛ Downloading resource {url}")

        try:
            response = self.session.get(url, stream=True)

            retry_number = 1
            while response.status_code == self.HTTP_429_TOO_MANY_REQUESTS and retry_number <= self.max_retries:
                delay = self._get_retry_delay(retry_number)
                logging.info(f"❌ Got HTTP 429 Too Many Requests. Retrying in {delay} seconds.")
                time.sleep(delay)
                response = requests.get(url, stream=True)
                retry_number += 1

            response.raise_for_status()
        except Exception as ex:
            logging.info(f"❌ Failed to download resource {url}: {ex}")
            raise FailedToDownloadFileException() from ex

        logging.info(f"✅ Resource downloaded {url}")

        return response.content, response.headers["Content-Type"]

    def _find_page_links(self, page_link: str, html: str) -> Set[str]:
        """
        Find all links from «a» tags in HTML page.

        :param page_link: Link pointing to HTML page.
        :param html: HTML page.
        :return: Set of links.
        """
        try:
            parsed_html = BeautifulSoup(html, "html.parser")
        except Exception as ex:
            logging.error(f"❌ Error during parsing html {ex}")
            return set()

        links = set()

        a_tags = parsed_html.find_all("a")
        for a_tag in a_tags:
            href = a_tag.get("href")
            links.add(href)

        return self._validate_urls(page_link, links)

    def _find_static_files_links(self, page_link: str, html: str) -> Set[str]:
        """
        Find links to static files.

        :param page_link: Link pointing to HTML page.
        :param html: HTML page.
        :return: Set of links to static files.
        """
        try:
            parsed_html = BeautifulSoup(html, "html.parser")
        except Exception as ex:
            logging.error(f"Error during parsing html {ex}")
            return set()

        static_urls = set()

        for css in parsed_html.find_all("link", rel="stylesheet"):
            if css.get("href"):
                static_urls.add(css["href"])

        for script in parsed_html.find_all("script"):
            if script.get("src"):
                static_urls.add(script["src"])

        for img in parsed_html.find_all("img"):
            if img.get("src"):
                static_urls.add(img["src"])

        return self._validate_urls(page_link, static_urls)

    def _validate_url(self, page_link: str, url: str) -> Optional[str]:
        """
        Validate single URL.

        :param page_link: Base URL of the web page.
        :param url: URL to validate.
        :return: Validated URL.
        """
        if not url:
            return None

        url = urljoin(page_link, url)
        try:
            parsed_url = urlparse(url)
        except Exception:
            return None

        if parsed_url.netloc != self.base_netloc:
            return None

        return url

    def _validate_urls(self, page_link: str, urls: Set[str]) -> Set[str]:
        """
        Validate set of URLs.

        :param page_link: Base URL of the web page.
        :param urls: URLs to validate.
        :return: Set of validated URLs.
        """
        validated_urls = set()
        for url in urls:
            url = self._validate_url(page_link, url)
            if not url:
                continue
            validated_urls.add(url)
        return validated_urls

    def traverse(
        self,
        max_depth: Optional[int] = 1,
    ) -> Generator[StaticFile, None, None]:
        """
        Traverse the web page and collect static content.

        :param max_depth: Max depth of traversal.
        :return: Generator of static files.
        """
        visited_page_links = set()

        visited_static_files_links = set()

        queue = [(self.base_url, 1)]
        while queue:
            page_link, depth = queue.pop(0)
            if max_depth and depth > max_depth:
                continue

            if page_link in visited_page_links:
                continue
            visited_page_links.add(page_link)

            try:
                html, content_type = self._download(page_link)
            except FailedToDownloadFileException:
                continue
            if "text/html" not in content_type:
                continue

            queue.extend(
                (_link, depth + 1) for _link in self._find_page_links(page_link, html)
            )

            static_file_links = self._find_static_files_links(page_link, html)
            for static_file_link in static_file_links:
                if static_file_link in visited_static_files_links:
                    continue
                visited_static_files_links.add(static_file_link)

                try:
                    file, content_type = self._download(static_file_link)
                except FailedToDownloadFileException:
                    continue

                yield StaticFile(static_file_link, file, content_type)

            if self.retry_delay:
                time.sleep(self.request_delay)