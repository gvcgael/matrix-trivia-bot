import logging

from nio import AsyncClient, MatrixRoom, RoomMessageText

from matrix_trivia_bot.chat_functions import send_text_to_room
from matrix_trivia_bot.config import Config
from matrix_trivia_bot.storage import Storage

logger = logging.getLogger(__name__)


class Message:
    def __init__(
        self,
        client: AsyncClient,
        store: Storage,
        config: Config,
        message_content: str,
        room: MatrixRoom,
        event: RoomMessageText,
    ):
        """Initialize a new Message

        Args:
            client: nio client used to interact with matrix.

            store: Bot storage.

            config: Bot configuration parameters.

            message_content: The body of the message.

            room: The room the event came from.

            event: The event defining the message.
        """
        self.client = client
        self.store = store
        self.config = config
        self.message_content = message_content
        self.room = room
        self.event = event

    async def process(self) -> None:
        """Process and possibly respond to the message"""

        if len(self.store.questions) > 0:
            logger.debug(
                f"Message {self.message_content.lower()} | Answer {self.store.current_answer().lower()}"
                f"{self.message_content.lower() == self.store.current_answer().lower()}"
            )
            if self.message_content.lower() == self.store.current_answer().lower():
                await send_text_to_room(self.client, self.room.room_id, "Correct ! Answer is {}".format(self.store.current_answer()))
                player = self.room.user_name(self.event.sender)
                if player in self.store.scores:
                    self.store.scores[player] += 1
                else:
                    self.store.scores[player] = 1
                await send_text_to_room(self.client, self.room.room_id, "{} now has {} points".format(player, self.store.scores[player]))
                await self.start_next_question()
            elif self.message_content.lower() in self.store.current_wrong_answers():
                await send_text_to_room(self.client, self.room.room_id, "Nope! Answer is not {}".format(self.message_content))
                self.store.fails += 1
                if self.store.fails > 5:
                    await send_text_to_room(self.client, self.room.room_id, "Morron! Answer was {}".format(self.store.current_answer()))
                    await self.start_next_question()


    async def start_next_question(self):
        self.store.fails = 0
        self.store.current_question += 1
        if self.store.current_question >= len(self.store.questions):
            await send_text_to_room(self.client, self.room.room_id, "Quizz ended ! Clap clap for the victorious ! {}".format(self.store.champion()))
            self.store.scores = {}
        else:
            await send_text_to_room(self.client, self.room.room_id, """Question {} : {} 
 - {}""".format(
                                                                    self.store.current_question+1, 
                                                                    self.store.current_question_text(), 
                                                                    "\n - ".join(self.store.current_answers())))
