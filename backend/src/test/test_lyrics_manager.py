import json
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch


SRC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_DIR))

from lyrics_manager import LyricsManager


class YesPlayMusicLyricsTest(unittest.TestCase):
    def test_fetches_synced_lyrics_from_api_endpoint(self):
        manager = LyricsManager()
        player_response = {
            "currentTrack": {
                "id": 12345,
                "name": "测试歌曲",
                "artists": [{"id": 67890, "name": "测试歌手"}],
                "album": {"id": 24680, "name": "测试专辑"},
            },
            "playing": True,
        }
        lyric_response = {
            "lrc": {
                "version": 1,
                "lyric": "[00:01.50]第一行\n[00:03.00]第二行",
            }
        }

        with patch.object(
            manager,
            "_http_get",
            side_effect=[
                (200, json.dumps(player_response)),
                (200, json.dumps(lyric_response)),
            ],
        ) as http_get:
            lyrics = manager._fetch_lyrics_ypm("测试歌曲")

        self.assertEqual(
            lyrics,
            [
                {"time_ms": 1_500_000, "lyric": "第一行"},
                {"time_ms": 3_000_000, "lyric": "第二行"},
            ],
        )
        self.assertEqual(
            http_get.call_args_list,
            [
                call("http://localhost:27232/player"),
                call("http://localhost:27232/api/lyric?id=12345"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
