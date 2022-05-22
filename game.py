import sys

import game_board
import pygame

pygame.init()
pygame.display.init()

import particles
import discord_bot
import UITools
from threading import Thread
from sys import exit


class GameManager:
    def __init__(self):
        infos = pygame.display.Info()
        self.screen_width, self.screen_height = infos.current_w, infos.current_h - 100
        self.token = ""
        self.chat_id = ""
        self._active_board = None
        self.token = self.get_form_file("TOKEN.txt")
        self.chat_id = self.get_form_file("CHAT_ID.txt")
        self._is_lobby = True
        self.is_bot_started = False
        self.error_text = None
        self.winner_player = None
        self.fps = 30
        self._is_error_with_start_bot = False

        # BOARD SETTINGS
        self.board_widht, self.board_height = min((self.screen_width * 4) // 5 - 10, self.screen_height - 10), \
                                              min((self.screen_width * 4) // 5 - 10, self.screen_height - 10)
        self.board_x, self.board_y = 5 + (self.screen_width * 1) // 5, 5

        # PYGAME SETTINGS
        self.screen = pygame.display.set_mode((self.board_widht + self.board_x, self.board_height + self.board_y))

        self.lobby()

    @property
    def is_error_with_start_bot(self):
        return self._is_error_with_start_bot

    @is_error_with_start_bot.setter
    def is_error_with_start_bot(self, b: bool):
        self._is_error_with_start_bot = b

    @property
    def board_ui_group(self):
        return self.board_ui

    @property
    def is_lobby(self):
        return self._is_lobby

    @is_lobby.setter
    def is_lobby(self, b: bool):
        self._is_lobby = b

    def run_bot(self):
        if not self.chat_id.isdigit():
            self.create_error_text("The chat ID must be a number")
            return
        if self.is_error_with_start_bot:
            self.create_error_text("Restarting bot")
            self.ds_bot.set_chat_id(self.chat_id)
            return
        if self.is_bot_started:
            self.create_error_text("The bot is already running")
        else:
            self.create_error_text("Starting bot")
            self.ds_bot = discord_bot.CustomClient(self, self.chat_id)
            self.thread = Thread(target=self._run_bot)
            self.thread.start()

    def _run_bot(self):
        self.is_bot_started = True
        try:
            self.ds_bot.run(self.token)
        except:
            self.create_error_text("Error when starting the bot. I advise you to close and open the application.")
            self.bot_is_not_started()

    def find_player(self, id):
        for sprite in self.active_board.sprites():
            if type(sprite) is game_board.Player:
                if sprite.id == id:
                    return sprite
        return None

    @staticmethod
    def get_form_file(file):
        try:
            file = open(file, "r")
        except:
            return ""
        text = "".join(list(file))
        file.close()
        return text

    @staticmethod
    def set_to_file(file, text):
        file = open(file, "w")
        file.truncate(0)
        file.write(text)
        file.close()

    def get_token_from_file(self):
        pass

    @property
    def active_board(self):
        return self._active_board

    def bot_is_not_started(self):
        self.is_bot_started = False

    def set_token(self, token):
        if self.token != token:
            self.token = token
            self.set_to_file("TOKEN.txt", str(self.token))

    def set_chat_id(self, chat_id):
        if self.chat_id != chat_id:
            self.chat_id = chat_id
            self.set_to_file("CHAT_ID.txt", str(self.chat_id))

    def lobby(self):
        self.winner_player = None
        self.ui_group = UITools.UIGroup()
        bot_start_button = UITools.Button(self.ui_group, 10, 190, self.board_x // 2, 50, "<start bot>",
                                          font=pygame.font.SysFont("monospace", 25), text_y=10)
        bot_start_button.press = self.run_bot
        start_button = UITools.Button(self.ui_group, 10, 260, self.board_x // 2, 50, "<start game>",
                                      font=pygame.font.SysFont("monospace", 25), text_y=10)
        start_button.press = self.start_game
        self.main_cycle()

    def log_text(self):
        players_names = [i.name for i in self.active_board.alive_players if type(i) is game_board.Player]
        text = " Alive players:\n"
        i = 0
        for p in players_names:
            i += 1
            text += p[:10] + "\n"
            if i == 10:
                text += "..."
                break
        return str(text)

    def create_error_text(self, text):
        if self.error_text is not None:
            self.error_text.kill()
        font = pygame.font.SysFont("monospace", 20)
        x = self.screen_width // 10
        self.error_text = UITools.PopupText(self.ui_group, (x, x), (self.screen_height, self.screen_height - 50),
                                            self.screen_width, 50, str(text), kill_timer=5,
                                            text_color="#ebf208", font=font, fps=self.fps)

    def game(self):
        self.ui_group = UITools.UIGroup()
        end_game_button = UITools.Button(self.ui_group, 10, self.board_height + self.board_y - 70, 140, 50, "end game",
                                         font=pygame.font.SysFont("monospace", 25), text_y=10)
        end_game_button.press_funch = self.end_game
        self.main_cycle()

    def main_cycle(self):
        clock = pygame.time.Clock()
        fps = self.fps
        self.screen.fill("#000000")

        text_surf = pygame.font.SysFont("monospace", 20).render("== Space game ==", 1, "#ffffff")
        self.screen.blit(text_surf, (10, 10))

        # SET BOARDS ANS PARTICLE SYSTEM
        random_cell_event_timer = (3, 6) if self.is_lobby else (1, 5)
        particle_system = particles.ParitcleSystem(fps=fps)
        ground = game_board.Board((self.board_widht, self.board_height), (10, 10), fps=fps,
                                  random_cell_event_timer=random_cell_event_timer)
        board = game_board.Board((self.board_widht, self.board_height), (10, 10), fps=fps,
                                 floor_board=ground, harmless_cells=self.is_lobby,
                                 random_cell_event_timer=random_cell_event_timer)
        # particle_system=particle_system,
        self.board_ui = UITools.UIGroup()
        if not self.is_lobby:
            board.spawn_players(self.active_board.alive_players)
        self._active_board = board
        game_board.random_cells(board, ground, n=20, harmless=self.is_lobby)

        if self.is_lobby:
            token_input_filed = UITools.InputField(self.ui_group, 10, 50, self.board_x - 30, 50, see_simbols=10,
                                                   ampty_text="bot token", text=self.token)
            chat_id_input_filed = UITools.InputField(self.ui_group, 10, 120, self.board_x - 30, 50,
                                                     ampty_text="chat id",
                                                     text=self.chat_id)
        else:
            log_text = UITools.Text(self.ui_group, 10, 50, self.board_widht // 2, self.board_height - 150, "",
                                    text_color="#ffffff",
                                    text_step_y=17)
        now_is_lobby = self.is_lobby

        self.create_error_text("Hello")

        while self.is_lobby == now_is_lobby:
            clock.tick(fps)
            self.screen.fill("#000000")
            # EVENTS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                self.ui_group.event(event)
                self.board_ui.event(event)
                board.event(event, no_zone=now_is_lobby)

            # BOARDS
            boards_screen = pygame.surface.Surface((self.board_widht, self.board_height))
            boards_screen.fill("#000000")
            ground.draw_flor(boards_screen)
            particle_system.update()
            board.update()
            ground.update()
            try:
                ground.draw(boards_screen)
                particle_system.draw(boards_screen)
                board.draw(boards_screen)
            except:
                pass

            self.board_ui.update()
            self.board_ui.draw(boards_screen)

            self.screen.blit(boards_screen, (self.board_x, self.board_y))

            # UI
            self.ui_group.update()
            try:
                self.ui_group.draw(self.screen)
            except:
                pass

            ###
            if now_is_lobby:
                self.set_token(token_input_filed.input_text)
                self.set_chat_id(chat_id_input_filed.input_text)
            else:
                log_text.text = self.log_text()
                if len(self.active_board.alive_players) == 1 and self.winner_player is None:
                    self.winner_player = self.active_board.alive_players[0]
                    font = pygame.font.SysFont("monospace", 30)
                    x = self.screen_width // 10
                    self.error_text = UITools.PopupText(self.ui_group, (x, x),
                                                        (0, 30),
                                                        self.screen_width, 50, str(f"{self.winner_player.name} won!"),
                                                        text_color="#f2f82b", font=font)

            # END
            pygame.display.flip()
        if self.is_lobby:
            self.lobby()
        else:
            self.game()

    def start_game(self):
        if len(self.active_board.alive_players) <= 1:
            self.create_error_text("You need at least 2 players to start.")
            return
        print("start game")
        self.is_lobby = False

    def end_game(self):
        print("end game")
        self.is_lobby = True


if __name__ == "__main__":
    GameManager()
