import discord
from game import GameManager
import game_board

# REACTIONS
JOIN_REACTION = "🎟"
UP_REACTION = "⬆"
DOWN_REACTION = "⬇"
LEFT_REACTION = "➡"
RIGHT_REACTION = "⬅"
DESTROID_REACTION = "💀"


class CustomClient(discord.Client):
    def __init__(self, game_manager: GameManager, channel_id: int):
        super().__init__()
        self._game_manager = game_manager
        self.channel_id = channel_id
        self.reactions = [UP_REACTION, DOWN_REACTION,
                          LEFT_REACTION, RIGHT_REACTION,
                          DESTROID_REACTION]
        print("Start game")

    @property
    def game_manager(self) -> GameManager:
        return self._game_manager

    @game_manager.setter
    def game_manager(self, new_game_manager):
        self._game_manager = new_game_manager

    async def on_ready(self):
        print(f"{self.user} has connected to Ds")
        channel = self.get_channel(int(self.channel_id))
        print(*self.get_all_channels())
        self.mes = await channel.send("=== Space Game ===")
        await self.mes.clear_reactions()
        await self.mes.add_reaction(JOIN_REACTION)
        for i in self.reactions:
            await self.mes.add_reaction(i)

    def set_colot_reactions(self):
        pass

    async def on_reaction_add(self, reaction, user):
        if user == self.user:
            return
        if int(reaction.message.channel.id) != int(self.channel_id):
            return
        if reaction.message != self.mes:
            return
        print(str(reaction), user)
        await reaction.remove(user)
        player = self._game_manager.find_player(user.id)
        if str(reaction) == JOIN_REACTION and player is None:
            if user.id in self._game_manager.active_board.destroided_players_id:
                return
            game_board.Player(user.id, None, None, self._game_manager.active_board,
                              particle_system=self.game_manager.active_board.particle_system)
            return

        if player is None:
            return
        if user.id in self._game_manager.active_board.destroided_players_id:
            return
        d = {UP_REACTION: player.down,
             DOWN_REACTION: player.up,
             RIGHT_REACTION: player.left,
             LEFT_REACTION: player.right}
        if d.get(str(reaction), None) is not None:
            d.get(str(reaction))()
        if str(reaction) == DESTROID_REACTION:
            player.destroid("Self - destroid.")
