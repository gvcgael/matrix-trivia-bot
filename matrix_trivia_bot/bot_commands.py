from nio import AsyncClient, MatrixRoom, RoomMessageText

from matrix_trivia_bot.chat_functions import react_to_event, send_text_to_room
from matrix_trivia_bot.config import Config
from matrix_trivia_bot.storage import Storage
import aiohttp
import logging
import re
logger = logging.getLogger(__name__)

class Command:
    def __init__(
        self,
        client: AsyncClient,
        store: Storage,
        config: Config,
        command: str,
        room: MatrixRoom,
        event: RoomMessageText,
    ):
        """A command made by a user.

        Args:
            client: The client to communicate to matrix with.

            store: Bot storage.

            config: Bot configuration parameters.

            command: The command and arguments.

            room: The room the command was sent in.

            event: The event describing the command.
        """
        self.client = client
        self.store = store
        self.config = config
        self.command = command.split()[1]
        self.room = room
        self.event = event
        self.args = command.split()[2:]

    async def process(self):
        """Process the command"""
        logger.debug(
            f"{self.command}"
        )
        if self.command.startswith("start"):
            await self._startquizz()
        elif self.command.startswith("help"):
            await self._show_help()
        else:
            await self._unknown_command()

    async def _startquizz(self):
        """Echo back the command's arguments"""

        if self.store.current_question < len(self.store.questions):
            await send_text_to_room(self.client, self.room.room_id, "A quizz is already running")
        else:
            nb_questions = 3
            difficulty = "easy"
            for arg in self.args:
                questions = re.match(r'([0-9]{1,2})q', arg)
                difficulties = ["easy", "medium", "hard"]
                if questions:
                    nb_questions = int(questions.group(1))
                elif arg in difficulties:
                    difficulty = arg
            

            async with aiohttp.ClientSession() as session:
                async with session.get('https://opentdb.com/api.php?amount={nb_questions}&category=9&difficulty={difficulty}&type=multiple'.format(
                        nb_questions=nb_questions, 
                        difficulty=difficulty)) as response:

                    data = await response.json()
                    self.store.questions = data["results"]
                    await send_text_to_room(self.client, self.room.room_id, "Quizz started ! {} {} questions".format(nb_questions, difficulty))
                    self.store.current_question = 0
                    await send_text_to_room(self.client, self.room.room_id, """Question {} : {} 
 - {}""".format(
                            self.store.current_question+1, 
                            self.store.current_question_text(), 
                            "\n - ".join(self.store.current_answers())))


    async def _show_help(self):
        """Show the help text"""
        if not self.args:
            text = (
                "Hello, I am a bot made with matrix-nio! Use `help commands` to view "
                "available commands."
            )
            await send_text_to_room(self.client, self.room.room_id, text)
            return

        topic = self.args[0]
        if topic == "rules":
            text = "These are the rules!"
        elif topic == "commands":
            text = "Available commands: ..."
        else:
            text = "Unknown help topic!"
        await send_text_to_room(self.client, self.room.room_id, text)

    async def _unknown_command(self):
        await send_text_to_room(
            self.client,
            self.room.room_id,
            f"Unknown command '{self.command}'. Try the 'help' command for more information.",
        )
