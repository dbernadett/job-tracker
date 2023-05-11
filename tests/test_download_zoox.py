import os
import sys

import pytest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, path)

from src.download_zoox import ZooxDownloader  # noqa: E402


class TestDownloadZoox:
    def test_parse_bshtml_zoox(self, zoox_bs, tmp_path):
        """Test download_zoox"""
        downloader = ZooxDownloader(archive_path=tmp_path)
        parsed_fields = downloader._parse_bshtml(zoox_bs)
        assert parsed_fields["company"] == "zoox"
        assert parsed_fields["title"] == "Software Engineer - Autonomy Metrics"
        assert True

    @pytest.mark.networked
    def test_download_bshtml_zoox(self, zoox_bs, tmp_path):
        downloader = ZooxDownloader(archive_path=tmp_path)
        parsed_fields = downloader.download_and_parse(
            "https://zoox.com/careers/job-opportunity/?job=acaafc9a-486d-4045-80d7-12b09e39330e",
            1,
            tmp_path,
            False,
        )
        assert parsed_fields["company"] == "zoox"
        assert parsed_fields["title"] == "Software Engineer - Autonomy Metrics"
