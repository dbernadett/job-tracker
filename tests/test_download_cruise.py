import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, path)

from src.download_cruise import CruiseDownloader  # noqa: E402


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
