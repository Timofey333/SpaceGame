import game_board
import pygame

pygame.init()
pygame.display.init()

import particles
import discord_bot
import UITools
from threading import Thread


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

        # BOARD SETTINGS
        self.board_widht, self.board_height = min((self.screen_width * 4) // 5 - 10, self.screen_height - 10), \
                                              min((self.screen_width * 4) // 5 - 10, self.screen_height - 10)
        self.board_x, self.board_y = 5 + (self.screen_width * 1) // 5, 5

        # PYGAME SETTINGS
        self.screen = pygame.display.set_mode((self.board_widht + self.board_x, self.board_height + self.board_y))

        self.lobby()

    @property
    def is_lobby(self):
        return self._is_lobby

    @is_lobby.setter
    def is_lobby(self, b: bool):
        self._is_lobby = b

    def run_bot(self):
        if not self.is_bot_started:
            self.ds_bot = discord_bot.CustomClient(self, self.chat_id)
            th = Thread(target=self._run_bot)
            th.start()

    def _run_bot(self):
        try:
            self.is_bot_started = True
            self.ds_bot.run(self.token)
        except:
            print("None")

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

    def set_token(self, token):
        if self.token != token:
            self.token = token
            self.set_to_file("TOKEN.txt", str(self.token))

    def set_chat_id(self, chat_id):
        if self.chat_id != chat_id:
            self.chat_id = chat_id
            self.set_to_file("CHAT_ID.txt", str(self.chat_id))

    def lobby(self):
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

    def game(self):
        self.ui_group = UITools.UIGroup()
        end_game_button = UITools.Button(self.ui_group, 10, self.board_height + self.board_y - 70, 140, 50, "end game",
                                         font=pygame.font.SysFont("monospace", 25), text_y=10)
        end_game_button.press_funch = self.end_game
        self.main_cycle()

    def main_cycle(self):
        clock = pygame.time.Clock()
        fps = 30
        self.screen.fill("#000000")

        text_surf = pygame.font.SysFont("monospace", 20).render("== Space game ==", 1, "#ffffff")
        self.screen.blit(text_surf, (10, 10))

        # SET BOARDS ANS PARTICLE SYSTEM
        particle_system = particles.ParitcleSystem(fps=fps)
        ground = game_board.Board((self.board_widht, self.board_height), (10, 10), fps=fps,
                                  particle_system=particle_system)
        board = game_board.Board((self.board_widht, self.board_height), (10, 10), fps=fps,
                                 particle_system=particle_system,
                                 floor_board=ground)
        if not self.is_lobby:
            board.spawn_players(self.active_board.alive_players)
        self._active_board = board
        game_board.random_cells(board, ground, n=20)

        if self.is_lobby:
            token_input_filed = UITools.InputField(self.ui_group, 10, 50, self.board_x - 30, 50, see_simbols=10,
                                                   ampty_text="bot token", text=self.token)
            chat_id_input_filed = UITools.InputField(self.ui_group, 10, 120, self.board_x - 30, 50,
                                                     ampty_text="chat id",
                                                     text=self.chat_id)
        else:
            log_text = UITools.Text(self.ui_group, 10, 50, self.board_widht // 2, self.board_height - 150, "", text_color="#ffffff",
                                    text_step_y=17)
        now_is_lobby = self.is_lobby
        while self.is_lobby == now_is_lobby:
            clock.tick(fps)
            # EVENTS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                self.ui_group.event(event)
                board.event(event, no_zone=now_is_lobby)

            # BOARDS
            boards_screen = pygame.surface.Surface((self.board_widht, self.board_height))
            ground.draw_flor(boards_screen)
            particle_system.update()
            board.update()
            ground.update()
            ground.draw(boards_screen)
            particle_system.draw(boards_screen)
            board.draw(boards_screen)

            # UI
            self.ui_group.update()
            self.ui_group.draw(self.screen)

            ###
            if now_is_lobby:
                self.set_token(token_input_filed.input_text)
                self.set_chat_id(chat_id_input_filed.input_text)
            else:
                log_text.text = self.log_text()

            # END
            self.screen.blit(boards_screen, (self.board_x, self.board_y))
            pygame.display.flip()
        if self.is_lobby:
            self.lobby()
        else:
            self.game()

    def start_game(self):
        print("start game")
        self.is_lobby = False

    def end_game(self):
        print("end game")
        self.is_lobby = True


if __name__ == "__main__":
    GameManager()
