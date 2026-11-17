"""A refused logo skips that club; TFF not answering stops the run without failing it."""

from pathlib import Path

import httpx

from tlelo.site.logos import fetch_logos

PAGE = '<img id="x_dtKulupBilgisi_ad" src="https://www.tff.org/logo/{}.png">'


class FakeClient:
    cache_dir = Path("cache")

    def __init__(self):
        self.asked = []

    def fetch(self, url, key):
        team = int(url.rsplit("=", 1)[1])
        self.asked.append(team)
        if team == 2:
            request = httpx.Request("GET", url)
            raise httpx.HTTPStatusError("404", request=request, response=httpx.Response(404))
        if team == 4:
            raise RuntimeError("giving up")
        return PAGE.format(team)

    def fetch_bytes(self, url, key):
        return b""


def test_fetch_logos_skips_refused_clubs_and_stops_when_tff_gives_up():
    client = FakeClient()
    got = fetch_logos(client, [1, 2, 3, 4, 5])
    assert sorted(got) == [1, 3]
    assert got[1] == Path("cache/logos/1.png")
    assert client.asked == [1, 2, 3, 4]  # 5 waits for the next run
