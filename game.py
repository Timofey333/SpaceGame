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
        self.lobby = True
        self.is_bot_started = False
        self.main()

    @property
    def is_lobby(self):
        return self.lobby

    @is_lobby.setter
    def is_lobby(self, b: bool):
        self.lobby = b

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

    def start_game(self):
        print("start game")
        self.is_lobby = False

    def main(self):
        #PARAMETERS
        board_widht, board_height = min((self.screen_width * 4) // 5 - 10, self.screen_height - 10), \
                                    min((self.screen_width * 4) // 5 - 10, self.screen_height - 10)
        board_x, board_y = 5 + (self.screen_width * 1) // 5, 5

        #PYGAME SETTINGS
        screen = pygame.display.set_mode((board_widht + board_x, board_height + board_y))
        # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        clock = pygame.time.Clock()
        fps = 30
        screen.fill("#000000")

        # SET BOARDS ANS PARTICLE SYSTEM
        particle_system = particles.ParitcleSystem(fps=fps)
        ground = game_board.Board((board_widht, board_height), (10, 10), fps=fps, particle_system=particle_system)
        board = game_board.Board((board_widht, board_height), (10, 10), fps=fps, particle_system=particle_system,
                                 floor_board=ground)
        self._active_board = board
        game_board.random_cells(board, ground, n=20)

        # SET UI
        ui_group = UITools.UIGroup()
        token_input_filed = UITools.InputField(ui_group, 10, 50, board_x - 30, 50, see_simbols=10,
                                               ampty_text="bot token", text=self.token)
        chat_id_input_filed = UITools.InputField(ui_group, 10, 120, board_x - 30, 50, ampty_text="chat id",
                                                 text=self.chat_id)
        bot_start_button = UITools.Button(ui_group, 10, 190, board_x // 2, 50, "<start bot>",
                                          font=pygame.font.SysFont("monospace", 25), text_y=10)
        bot_start_button.press = self.run_bot
        start_button = UITools.Button(ui_group, 10, 260, board_x // 2, 50, "<start game>",
                                      font=pygame.font.SysFont("monospace", 25), text_y=10)
        start_button.press = self.start_game

        text_surf = pygame.font.SysFont("monospace", 20).render("== Space game ==", 1, "#ffffff")
        screen.blit(text_surf, (10, 10))

        while self.is_lobby:
            clock.tick(fps)
            #EVENTS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                ui_group.event(event)

            # BOARDS
            boards_screen = pygame.surface.Surface((board_widht, board_height))
            ground.draw_flor(boards_screen)
            particle_system.update()
            board.update()
            ground.update()
            ground.draw(boards_screen)
            particle_system.draw(boards_screen)
            board.draw(boards_screen)

            # UI
            ui_group.update()
            ui_group.draw(screen)

            ###
            self.set_token(token_input_filed.input_text)
            self.set_chat_id(chat_id_input_filed.input_text)

            #END
            screen.blit(boards_screen, (board_x, board_y))
            pygame.display.flip()
        self.game(board_widht, board_height, board_x, board_y, screen, fps)

    def end_game(self):
        print("end game")
        self.is_lobby = False

    def game(self, board_widht, board_height, board_x, board_y, screen, fps):
        clock = pygame.time.Clock()
        screen.fill("#000000")

        # SET BOARDS ANS PARTICLE SYSTEM
        particle_system = particles.ParitcleSystem(fps=fps)
        ground = game_board.Board((board_widht, board_height), (10, 10), fps=fps, particle_system=particle_system)
        board = game_board.Board((board_widht, board_height), (10, 10), fps=fps, particle_system=particle_system,
                                 floor_board=ground)
        board.spawn_players(self.active_board.alive_players)
        self._active_board = board
        game_board.random_cells(board, ground, n=20)

        # SET UI
        ui_group = UITools.UIGroup()
        end_game_button = UITools.Button(ui_group, 10,  board_height + board_y - 70, 140, 50, "end game",
                                          font=pygame.font.SysFont("monospace", 25), text_y=10)
        end_game_button.press_funch = self.end_game
        text_surf = pygame.font.SysFont("monospace", 20).render("== Space game ==", 1, "#ffffff")
        screen.blit(text_surf, (10, 10))

        while not self.is_lobby:
            clock.tick(fps)
            # EVENTS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                ui_group.event(event)

            # BOARDS
            boards_screen = pygame.surface.Surface((board_widht, board_height))
            ground.draw_flor(boards_screen)
            particle_system.update()
            board.update()
            ground.update()
            ground.draw(boards_screen)
            particle_system.draw(boards_screen)
            board.draw(boards_screen)

            # UI
            ui_group.update()
            ui_group.draw(screen)

            ###

            # END
            screen.blit(boards_screen, (board_x, board_y))
            pygame.display.flip()


if __name__ == "__main__":
    GameManager()
