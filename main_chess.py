import pygame


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.board = [[0] * width for _ in range(height)]

        # значения по умолчанию
        self.left = 0
        self.top = 0
        self.cell_size = 55

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    #  возвращает координаты клетки в виде кортежа по переданным координатам мыши
    def get_cell(self, mouse_pos):
        for i in range(self.height):
            for j in range(self.width):
                if (
                        self.left + self.cell_size * j < mouse_pos[0] < self.left + self.cell_size * j + self.cell_size
                        and
                        self.top + self.cell_size * i < mouse_pos[1] < self.top + self.cell_size * i + self.cell_size
                ):
                    return i, j
        return None


class Chess(Board):
    def __init__(self):
        super(Chess, self).__init__(8, 8)  # создание доски 8 на 8
        self.step = True  # True означает белый цвет

    # отрисовка доски
    def render(self, input_screen):
        for i in range(self.height):
            for j in range(self.width):
                # отрисовка фоноваго квадрата
                if (i + j) % 2 == 0:  # светлый квадрат
                    pygame.draw.rect(input_screen, pygame.Color('#99958C'),
                                     pygame.Rect(self.left + self.cell_size * j,
                                                 self.top + self.cell_size * i, self.cell_size,
                                                 self.cell_size), 0)
                else:  # тёмный квадрат
                    pygame.draw.rect(input_screen, pygame.Color('#474A51'),
                                     pygame.Rect(self.left + self.cell_size * j,
                                                 self.top + self.cell_size * i, self.cell_size,
                                                 self.cell_size), 0)
                #  отрисовка фигур
                if bool(self.board[i][j]) is not False:
                    self.board[i][j].render()

    def on_click(self, y, x):
        pass


class Piece:
    def __init__(self, y, x, color=True):
        self.y, self.x = y, x  # координаты фигуры (y-сверху, x-слева-направо)
        self.color = color  # значение True означает белый цвет фигуры

    def set_new_position(self, y, x):
        self.y, self.x = y, x

    def get_y(self):
        return self.y

    def get_x(self):
        return self.x

    def get_pos(self):
        return self.get_y(), self.get_x()


class Pawn(Piece):
    def render(self, screen_name):  # отрисовка фигуры
        pass

    def is_it_possible_step(self, step_y, step_x):  # проверка на возможность шага(ввод- конечные координаты)
        return True


board = Chess()

pygame.init()

screen = pygame.display.set_mode((board.cell_size * board.width, board.cell_size * board.height))
pygame.display.set_caption('Шахматы')

clock = pygame.time.Clock()
FPS = 50

running = True
pause = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and pause:
                board.on_click(board.get_cell(event.pos))

    screen.fill((0, 0, 0))
    board.render(screen)

    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
