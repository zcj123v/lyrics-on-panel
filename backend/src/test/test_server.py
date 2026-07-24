import json
import asyncio
import sys

BASE = "ws://localhost:23560"


def websocket_client():
    import websockets

    return websockets


async def check_healthcheck():
    async with websocket_client().connect(f"{BASE}/healthcheck") as ws:
        resp = await ws.recv()
        data = json.loads(resp)
        print("healthcheck:", data)


async def check_poll():
    async with websocket_client().connect(f"{BASE}/poll") as ws:
        await ws.send('{}')
        resp = await ws.recv()
        data = json.loads(resp)
        print("poll:", data)


async def check_control_ypm():
    '''
    YesPlayMusic的PlaybackStatus控制存在问题。正常情况下，发送两次play信号, 歌曲仍应处于播放状态；但Yesplaymusic会暂停播放。pause同理。
    '''
    async with websocket_client().connect(f"{BASE}/control") as ws:
        await ws.send('{"action": "play", "player": "org.mpris.MediaPlayer2.yesplaymusic"}')
        await asyncio.sleep(5)
        await ws.send('{"action": "pause", "player": "org.mpris.MediaPlayer2.yesplaymusic"}')


async def check_control_spotify():
    async with websocket_client().connect(f"{BASE}/control") as ws:
        await ws.send('{"action": "play", "player": "org.mpris.MediaPlayer2.spotify"}')
        await asyncio.sleep(5)
        await ws.send('{"action": "pause", "player": "org.mpris.MediaPlayer2.spotify"}')


def main(arguments=None):
    arguments = sys.argv[1:] if arguments is None else arguments
    asyncio.run(check_healthcheck())
    asyncio.run(check_poll())
    if "--with-controls" in arguments:
        asyncio.run(check_control_ypm())
        asyncio.run(check_control_spotify())


if __name__ == "__main__":
    main()

        
