import game_board
import pygame
import particles
import discord_bot
import input_field


class GameManager:
    def __init__(self):
        pygame.init()
        pygame.display.init()
        infos = pygame.display.Info()
        self.screen_width, self.screen_height = infos.current_w, infos.current_h - 100
        self.main()

    def run_bot(self):
        test_id = 972432532589125752
        game_id = 972420298303504414
        token = "token"
        ds_bot = discord_bot.CustomClient(self, "admin", test_id)
        ds_bot.run(token)

    def main(self):
        board_widht, board_height = min((self.screen_width * 4) // 5 - 10, self.screen_height - 10), \
                                    min((self.screen_width * 4) // 5 - 10, self.screen_height - 10)
        board_x, board_y = 5 + (self.screen_width * 1) // 5, 5

        pygame.init()
        screen = pygame.display.set_mode((board_widht + board_x, board_height + board_y))
        # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        clock = pygame.time.Clock()
        fps = 30
        screen.fill("#000000")

        particle_system = particles.ParitcleSystem(fps=fps)

        ground = game_board.Board((board_widht, board_height), (10, 10), fps=fps, particle_system=particle_system)
        board = game_board.Board((board_widht, board_height), (10, 10), fps=fps, particle_system=particle_system, floor_board=ground)

        game_board.random_cells(board, ground, n=20)

        buttons_group = pygame.sprite.Group()
        token_input_filed = input_field.InputField(buttons_group, 10, 50, board_x - 30, 50, see_simbols=10)

        player = game_board.Player(1, 1, board, particle_system=particle_system)

        while True:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                token_input_filed.event(event)

            # BOARDS
            boards_screen = pygame.surface.Surface((board_widht, board_height))
            board.draw_flor(boards_screen)
            ground.draw_flor(boards_screen)
            particle_system.update()
            board.update()
            ground.update()
            ground.draw(boards_screen)
            particle_system.draw(boards_screen)
            board.draw(boards_screen)

            # BUTTONS
            text_surf = pygame.font.SysFont("monospace", 20).render("Bot token:", 1, "#ffffff")
            screen.blit(text_surf, (10, 10))
            buttons_group.update()
            buttons_group.draw(screen)

            screen.blit(boards_screen, (board_x, board_y))
            pygame.display.flip()


if __name__ == "__main__":
    gm = GameManager()