import logging
import textdistance
import time

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

        if len(self.store.questions) > 0 and self.store.current_question < len(self.store.questions):
            logger.debug(
                f"Message {self.message_content.lower()} | Answer {self.store.current_answer().lower()} |" 
                f"{textdistance.levenshtein.normalized_distance(self.message_content.lower(), self.store.current_answer().lower()) }"
            )
            
            if textdistance.levenshtein.normalized_distance(self.message_content.lower(), self.store.current_answer().lower()) <= 0.25:
                await send_text_to_room(self.client, self.room.room_id, "Correct ! Answer is {}".format(self.store.current_answer()))
                player = self.room.user_name(self.event.sender)
                if player in self.store.scores:
                    self.store.scores[player] += 1
                else:
                    self.store.scores[player] = 1
                await send_text_to_room(self.client, self.room.room_id, "{} now has {} points".format(player, self.store.scores[player]))
                await self.start_next_question()
            elif textdistance.levenshtein.normalized_distance(self.message_content.lower(), self.store.current_answer().lower()) <= 0.4:
                await send_text_to_room(self.client, self.room.room_id, "So close ! But answer is not {}".format(self.message_content))
            else:
                for wrong in self.store.current_wrong_answers(): 
                    if textdistance.levenshtein.normalized_distance(self.message_content.lower(), wrong) <= 0.25:
                        await send_text_to_room(self.client, self.room.room_id, "Nope! Answer is not {}".format(self.message_content))
                        self.store.fails += 1
                        if self.store.fails > 2:
                            await send_text_to_room(self.client, self.room.room_id, "Morron! Answer was {}".format(self.store.current_answer()))
                            await self.start_next_question()


    async def start_next_question(self):
        await send_text_to_room(self.client, self.room.room_id, self.store.run_next_questions())