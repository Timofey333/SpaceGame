import discord
from threading import Thread
from game import GameManager

# REACTIONS
JOIN_REACTION = "🎟"
UP_REACTION = "⬆"
DOWN_REACTION = "⬇"
LEFT_REACTION = "➡"
RIGHT_REACTION = "⬅"
DESTROID_REACTION = "💀"


class CustomClient(discord.Client):
    def __init__(self, game_manager: GameManager, bot_settings_role: str, channel_id: int):
        super().__init__()
        self._game_manager = game_manager
        self.bot_settings_role = bot_settings_role
        self.channel_id = channel_id
        self.reactions = [UP_REACTION, DOWN_REACTION,
                          LEFT_REACTION, RIGHT_REACTION,
                          DESTROID_REACTION]
        self.mes = None

    @property
    def game_manager(self) -> GameManager:
        return self._game_manager

    @game_manager.setter
    def game_manager(self, new_game_manager):
        self._game_manager = new_game_manager

    async def on_ready(self):
        print(f"{self.user} has connected to Ds")

    def set_colot_reactions(self):
        pass

    async def on_message(self, message):
        if message.channel.id != self.channel_id:
            return
        is_admin = len(list(filter(lambda r: r.name == self.bot_settings_role,
                                   message.author.roles))) == 1
        if not is_admin:
            return
        if message.content == "$start":
            print("Start game")
            self.mes = await message.channel.send("=== Space Game ===")
            await self.mes.clear_reactions()
            await self.mes.add_reaction(JOIN_REACTION)
            for i in self.reactions:
                await self.mes.add_reaction(i)

    async def on_reaction_add(self, reaction, user):
        if user == self.user:
            return
        if reaction.message.channel.id != self.channel_id:
            return
        if reaction.message != self.mes:
            return
        print(str(reaction), user)
        await reaction.remove(user)
        board = self._game_manager.active_board
        if str(reaction) == JOIN_REACTION:
            Player(board, user.id, name=user.name)
            return
        player: Player = self._game_manager.board.find_player(user.id)
        if player is None:
            return
        d = {UP_REACTION: player.down,
             DOWN_REACTION: player.up,
             RIGHT_REACTION: player.left,
             LEFT_REACTION: player.right}
        if d.get(str(reaction), None) is not None:
            d.get(str(reaction))()
        if str(reaction) == DESTROID_REACTION:
            player.destroid("Self - destroid.")