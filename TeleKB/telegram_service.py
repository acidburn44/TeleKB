from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, PeerChannel
import asyncio
import threading
from typing import List, Optional
from .config import Config

class TelegramService:
    def __init__(self):
        # We start looking immediately? No, wait for connect.
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.thread.start()
        
        # Create client inside the loop context if possible, or just attach later?
        # Telethon client usually prefers being created in the loop.
        # So we should create it inside the loop.
        self.client = None
        
        # Future to wait for client creation
        self._client_ready = threading.Event()
        asyncio.run_coroutine_threadsafe(self._init_client(), self.loop)
        
        self.is_connected = False

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _init_client(self):
        self.client = TelegramClient('telekb_session', Config.API_ID, Config.API_HASH, loop=self.loop)
        self._client_ready.set()

    def _wait_client(self):
        self._client_ready.wait()
        return self.client

    async def _connect_coro(self, phone_callback, code_callback, password_callback):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            if phone_callback:
                try:
                    await self.client.start(
                        phone=phone_callback,
                        code_callback=code_callback,
                        password=password_callback
                    )
                except Exception as e:
                    print(f"Login failed: {e}")
                    return False
            else:
                return False
        self.is_connected = True
        return True

    def connect(self, phone_callback=None, code_callback=None, password_callback=None):
        self._wait_client()
        future = asyncio.run_coroutine_threadsafe(
            self._connect_coro(phone_callback, code_callback, password_callback), 
            self.loop
        )
        return future.result()

    async def _get_subscribed_channels_coro(self, include_groups):
        if not self.is_connected:
             await self.client.connect()
             if await self.client.is_user_authorized():
                 self.is_connected = True
        
        if not self.is_connected:
            return []

        dialogs = await self.client.get_dialogs()
        results = []
        for d in dialogs:
            entity = d.entity
            if isinstance(entity, Channel):
                if entity.megagroup:
                     if include_groups:
                         results.append(entity)
                else:
                     results.append(entity)
            elif isinstance(entity, Chat):
                if include_groups:
                    results.append(entity)
        return results

    def get_subscribed_channels(self, include_groups=False):
        self._wait_client()
        future = asyncio.run_coroutine_threadsafe(
            self._get_subscribed_channels_coro(include_groups), 
            self.loop
        )
        return future.result()

    async def _fetch_messages_coro(self, channel_id, min_id, limit):
        if not self.is_connected:
             await self.client.connect()
             if await self.client.is_user_authorized():
                 self.is_connected = True

        if not self.is_connected:
            return []
             
        try:
            entity = await self.client.get_entity(PeerChannel(channel_id))
        except Exception as e:
            print(f"Entity error {channel_id}: {e}")
            return []

        messages = []
        async for msg in self.client.iter_messages(entity, min_id=min_id, limit=limit, reverse=True): 
            if msg.message: 
                messages.append(msg)
        return messages

    def fetch_messages(self, channel_id, min_id=0, limit=None):
        self._wait_client()
        future = asyncio.run_coroutine_threadsafe(
            self._fetch_messages_coro(channel_id, min_id, limit), 
            self.loop
        )
        return future.result()

    async def _get_latest_id_coro(self, channel_id):
        if not self.is_connected:
             await self.client.connect()
             if await self.client.is_user_authorized():
                 self.is_connected = True

        if not self.is_connected:
            return 0

        try:
            entity = await self.client.get_entity(PeerChannel(channel_id))
            msgs = await self.client.get_messages(entity, limit=1)
            if msgs:
                return msgs[0].id
            return 0
        except Exception as e:
            print(f"Latest ID error {channel_id}: {e}")
            return 0

    def get_latest_message_id(self, channel_id):
        self._wait_client()
        future = asyncio.run_coroutine_threadsafe(
            self._get_latest_id_coro(channel_id), 
            self.loop
        )
        return future.result()

    async def _download_media_coro(self, message, output_path):
        if not self.is_connected:
             await self.client.connect()
             if await self.client.is_user_authorized():
                 self.is_connected = True

        if not self.is_connected:
            return None

        try:
            path = await self.client.download_media(message, file=output_path)
            return path
        except Exception as e:
            print(f"Download media error: {e}")
            return None

    def download_media(self, message, output_path):
        self._wait_client()
        future = asyncio.run_coroutine_threadsafe(
            self._download_media_coro(message, output_path), 
            self.loop
        )
        return future.result()

