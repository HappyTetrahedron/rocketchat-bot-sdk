import asyncio

class RocketchatMessage:

    def __init__(self, bot, data):
        self._bot = bot
        self.data = data


    def reply(self, reply_text):
        """
        Quickly send a message in the same channel as this message.
        :param reply_text: String containing the text you want to reply with
        """
        tmid = self.data.get('tmid', None)
        asyncio.get_event_loop().create_task(
            self._bot.realtime.send_message(reply_text, self.data['rid'], thread_id=tmid)
        )


    def is_by_me(self):
        return self.data["u"]["_id"] == self._bot.user["_id"]

    def is_new(self):
        if self.data.get('tcount', 0) > 0:
            # Thread count update - they're not new
            return False
        if self.data.get('reactions'):
            # Reaction added to message - they're not new
            return False
        return True