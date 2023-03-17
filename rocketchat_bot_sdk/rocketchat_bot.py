import base64
import asyncio

from threading import Thread

from rocketchat_API.rocketchat import RocketChat as RocketChatApi
from .rocketchat_async import RocketChat as RocketChatRealtime
from .rocketchat_async.dispatcher import Dispatcher
from .rocketchat_message import RocketchatMessage

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

    async def run_forever(self):
        """Start this chat bot
        The chat bot will start listening for incoming chat messages
        """
        self.user = self.api.me().json()

        await self.realtime.start(self._ws_url, username=self._user, password=self._password, token=self._token)
        await self.realtime.subscribe_to_channel_messages("__my_messages__", self._on_message)
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

    def _on_message(self, channel_id, sender_id, msg_id, message):
        if self._verbosity >= 1:
            print(f"Message received by {sender_id} in channel {channel_id}: {message['msg']}")
        message_obj = RocketchatMessage(self, message)
        for handler in self._handlers:
            if handler.matches(self, message_obj):
                handler.handle(self, message_obj)
    
    @staticmethod
    def _format_ws_url(api_url):
        ws_url = api_url.replace("http://", "ws://").replace("https://", "wss://")
        if ws_url[-1] == '/':
            return ws_url + "websocket"
        return ws_url + "/websocket"
