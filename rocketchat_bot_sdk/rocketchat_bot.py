import base64
import asyncio

from rocketchat_API.rocketchat import RocketChat as RocketChatApi
from .rocketchat_async import RocketChat as RocketChatRealtime
from .rocketchat_async.dispatcher import Dispatcher

class RocketchatBot:
    def __init__(self, server_url, username=None, password=None, api_token=None, user_id=None, verbosity=0):
        super().__init__()
        self._verbosity = verbosity
        self._user = username
        self._password = password
        self._token = api_token
        self._ws_url = self._format_ws_url(server_url)

        self.api = RocketChatApi(user=username, password=password, auth_token=api_token, user_id=user_id, server_url=server_url)
        self.realtime = RocketChatRealtime()
        self.realtime._dispatcher = Dispatcher(verbose=self._verbosity >= 2)
        self.user = None
        self._handlers = []
        self._loop = None
        self._subscriptions = {} 
        self._channel_subscription = ""

    def run_forever(self):
        """Start this chat bot
        The chat bot will start listening for incoming chat messages on a separate thread.
        """
        self.user = self.api.me().json()

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.create_task(self._start())
        self._loop.run_forever()
    
    async def _start(self):
        await self.realtime.start(self._ws_url, username=self._user, password=self._password, token=self._token)
        for channel_id, channel_type in await self.realtime.get_channels():
            sub = await self.realtime.subscribe_to_channel_messages(channel_id, self._on_message)
            self._subscriptions[sub] = channel_id

        chan_sub = await self.realtime.subscribe_to_channel_changes(self._on_channel_change)
        self._channel_subscription = chan_sub
        await self.realtime.run_forever()

    def add_handler(self, handler):
        """Add a handler to this bot which can handle messages received by it
        :param handler: A handler object (has to implement AbstractHandler)"""
        if handler not in self._handlers:
            self._handlers.append(handler)

    def remove_handler(self, handler):
        """Remove a handler from this bot
        :param handler: A handler object"""
        if handler in self._handlers:
            self._handlers.remove(handler)

    def stop(self):
        """Stop this chat bot (blocking)
        """
        self._loop.create_task(self._unsubscribe_all())
        self._loop.stop()
    
    async def _unsubscribe_all(self):
        for sub in self._subscriptions.keys():
            await self.realtime.unsubscribe(sub)
        self._subscriptions = {}
        await self.realtime.unsubscribe(self._channel_subscription)
        self._channel_subscription = ""

    def _on_message(self, channel_id, sender_id, msg_id, message):
        if sender_id == self.user["_id"]:
            return
        if self._verbosity >= 1:
            print(f"Message received by {sender_id} in channel {channel_id}: {message['msg']}")
        for handler in self._handlers:
            if handler.matches(self, message):
                handler.handle(self, message)
    
    def _on_channel_change(self, channel_id, channel_type):
        if channel_id not in self._subscriptions.values():
            print("New channel {}".format(channel_id))
            self._loop.create_task(self._add_subscription(channel_id))
    
    async def _add_subscription(self, channel_id):
        print("Subscribing channel {}".format(channel_id))
        sub_id = await self.realtime.subscribe_to_channel_messages(channel_id, self._on_message)
        self._subscriptions[sub_id] = channel_id

    @staticmethod
    def _format_ws_url(api_url):
        ws_url = api_url.replace("http://", "ws://").replace("https://", "wss://")
        if ws_url[-1] == '/':
            return ws_url + "websocket"
        return ws_url + "/websocket"
