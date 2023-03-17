import re
from abc import ABC
from abc import abstractmethod

class AbstractHandler(ABC):

    @abstractmethod
    def matches(self, bot, message) -> bool:
        """Should return true if this handler feels responsible for handling `message`, false otherwise
        :param message: RocketchatMessage object
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
        The callback function is passed the RocketchatBot and RocketchatMessage as arguments
        """
        self.command = command
        self.callback_function = callback_function

    def matches(self, bot, message) -> bool:
        if message.is_by_me() or not message.is_new():
            return False
        if message.data["msg"].startswith("${}".format(self.command)):
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
        The callback function is passed the RocketchatBot and RocketchatMessage as arguments
        """
        self.regex = re.compile(regex)
        self.callback_function = callback_function

    def matches(self, bot, message) -> bool:
        if message.is_by_me() or not message.is_new():
            return False
        if message.data["msg"]:
            if self.regex.search(message.data["msg"]):
                return True
        return False

    def handle(self, bot, message):
        self.callback_function(bot, message)


class MessageHandler(AbstractHandler):
    """A handler that responds to all messages"""
    def __init__(self, callback_function):
        """
        :param callback_function: The function to call when a matching message is received.
        The callback function is passed the RocketchatBot and RocketchatMessage as arguments
        """
        self.callback_function = callback_function

    def matches(self, bot, message) -> bool:
        if message.is_by_me() or not message.is_new():
            return False
        return True

    def handle(self, bot, message):
        self.callback_function(bot, message)


class MentionHandler(AbstractHandler):
    """A handler that responds to all messages mentioning the bot (or any specified users)"""
    ROOM_MENTIONS = ["all", "here"]
    def __init__(self, callback_function, mention_user=None, mention_users=None):
        """
        :param callback_function: The function to call when a matching message is received.
        :param mention_user: Username of the user whose mentions shall call this handler. If not specified, use the bot's own username.
        :param mention_users: List of usernames of the users whose mentions shall call this handler. Supersedes `mention_user` if provided.
        The callback function is passed the RocketchatBot and RocketchatMessage as arguments
        """
        self.callback_function = callback_function
        self.mention_users = mention_users or ([mention_user] if mention_user else None)

    def matches(self, bot, message) -> bool:
        if message.is_by_me() or not message.is_new():
            return False
        mus = self.mention_users
        if not mus:
            mus = [bot.user["username"]]
        for mention in message.data.get("mentions", []):
            if mention.get("username") in mus:
                return True
            if mention.get("username") in self.ROOM_MENTIONS:
                return True
        return False

    def handle(self, bot, message):
        self.callback_function(bot, message)

class ReactionHandler(AbstractHandler):
    """A handler that responds to all messages adding reactions to the bot's own messages"""
    def __init__(self, callback_function, reactions=None):
        """
        :param callback_function: The function to call when a matching message is received.
        :param reactions: List of specific reactions to filter for. If left out, all reactions will trigger the handler.
        The callback function is passed the RocketchatBot and RocketchatMessage as arguments
        """
        self.callback_function = callback_function
        self.filter_reactions = reactions

    def matches(self, bot, message) -> bool:
        if not message.is_by_me():
            return False

        reactions = message.data.get("reactions")
        if not reactions:
            return False

        if self.filter_reactions:
            for reaction in reactions.keys():
                if reaction in self.filter_reactions:
                    return True
            return False

        return True

    def handle(self, bot, message):
        self.callback_function(bot, message)