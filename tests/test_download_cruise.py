import os
import sys

import pytest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, path)

from src.download_cruise import CruiseDownloader  # noqa: E402

# @pytest.fixture
# def tmp_path():
#     return os.path.join(os.path.dirname(__file__), "tmp")


class TestDownloadCruise:
    def test_parse_bshtml_cruise(self, cruise_bs, tmp_path):
        """Test download_cruise"""
        downloader = CruiseDownloader(archive_path=tmp_path)
        parsed_fields = downloader._parse_bshtml(cruise_bs)
        assert parsed_fields["company"] == "cruise"
        assert (
            parsed_fields["title"] == "Senior Systems Engineer, Data Logging & Offload"
        )
        assert True

    @pytest.mark.networked
    def test_download_bshtml_cruise(self, tmp_path):
        cruise_path = os.path.join(tmp_path, "cruise")
        if os.path.exists(cruise_path):
            os.rmdir(cruise_path)
        os.mkdir(cruise_path)
        downloader = CruiseDownloader(archive_path=tmp_path)
        parsed_fields = downloader.download_and_parse(
            "https://getcruise.com/careers/jobs/2449571/", 1, cruise_path, False
        )
        assert parsed_fields["company"] == "cruise"
        assert (
            parsed_fields["title"] == "Senior Systems Engineer, Data Logging & Offload"
        )
