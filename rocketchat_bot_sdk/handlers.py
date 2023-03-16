import re
from abc import ABC
from abc import abstractmethod

class AbstractHandler(ABC):

    @abstractmethod
    def matches(self, bot, message) -> bool:
        """Should return true if this handler feels responsible for handling `message`, false otherwise
        :param message: dict containing a RocketChat message
        :return Whether or not this handler wants to handle `message`"""
        pass

    @abstractmethod
    def handle(self, bot, message):
        """Handles a message received by `bot`
        :param bot: RocketchatBot
        :param message: dict containing a RocketChat message"""
        pass


class CommandHandler(AbstractHandler):
    """A handler that responds to commands of the form `$command`"""
    def __init__(self, command, callback_function):
        """
        :param command: The command this handler should respond to (not including the preceding slash)
        :param callback_function: The function to call when a matching message is received.
        The callback function is passed the RocketchatBot and message dict as arguments
        """
        self.command = command
        self.callback_function = callback_function

    def matches(self, bot, message) -> bool:
        if message["msg"].startswith("${}".format(self.command)):
            return True

        return False

    def handle(self, bot, message):
        self.callback_function(bot, message)


class RegexHandler(AbstractHandler):
    """A handler that responds to messages matching a RegExp"""
    def __init__(self, regex, callback_function):
        """
        :param regex: A regular expression that matches the message texts this handler should respond to.
        :param callback_function: The function to call when a matching message is received.
        The callback function is passed the RocketchatBot and message dict as arguments
        """
        self.regex = re.compile(regex)
        self.callback_function = callback_function

    def matches(self, bot, message) -> bool:
        if message["msg"]:
            if self.regex.search(message["msg"]):
                return True
        return False

    def handle(self, bot, message):
        self.callback_function(bot, message)


class MessageHandler(AbstractHandler):
    """A handler that responds to all messages"""
    def __init__(self, callback_function):
        """
        :param callback_function: The function to call when a matching message is received.
        The callback function is passed the BeekeeperChatBot and beekeeper_sdk.conversations.ConversationMessage as arguments
        """
        self.callback_function = callback_function

    def matches(self, bot, message) -> bool:
        return True

    def handle(self, bot, message):
        self.callback_function(bot, message)


class MentionHandler(AbstractHandler):
    """A handler that responds to all messages mentioning the bot (or any specified users)"""
    ROOM_MENTIONS = ["all", "here"]
    def __init__(self, callback_function, mention_user = None, mention_users=None):
        """
        :param callback_function: The function to call when a matching message is received.
        :param mention_user: Username of the user whose mentions shall call this handler. If not specified, use the bot's own username.
        :param mention_users: List of usernames of the users whose mentions shall call this handler. Supersedes `mention_user` if provided.
        The callback function is passed the RocketchatBot and message dict as arguments
        """
        self.callback_function = callback_function
        self.mention_users = mention_users or ([mention_user] if mention_user else None)

    def matches(self, bot, message) -> bool:
        mus = self.mention_users
        if not mus:
            mus = [bot.user["username"]]
        for mention in message.get("mentions", []):
            if mention.get("username") in mus:
                return True
            if mention.get("username") in self.ROOM_MENTIONS:
                return True
        return False

    def handle(self, bot, message):
        self.callback_function(bot, message)