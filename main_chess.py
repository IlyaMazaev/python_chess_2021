from copy import deepcopy
import pygame
import os
import sys


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.board = [[0] * width for _ in range(height)]

        # значения по умолчанию
        self.left = 0
        self.top = 0
        self.cell_size = 70

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
        # расстановка фигур:
        # пешки:
        for i in range(8):
            self.board[1][i] = Pawn(1, i, self.board, False)  # чёрная пешка
            self.board[6][i] = Pawn(6, i, self.board, True)  # белая пешка
        # ладьи:
        self.board[0][0] = Rook(0, 0, self.board, False)
        self.board[0][7] = Rook(0, 7, self.board, False)
        self.board[7][0] = Rook(7, 0, self.board, True)
        self.board[7][7] = Rook(7, 7, self.board, True)
        # кони:
        self.board[0][1] = Knight(0, 1, self.board, False)
        self.board[0][6] = Knight(0, 6, self.board, False)
        self.board[7][1] = Knight(7, 1, self.board, True)
        self.board[7][6] = Knight(7, 6, self.board, True)
        # слоны:
        self.board[0][2] = Bishop(0, 2, self.board, False)
        self.board[0][5] = Bishop(0, 5, self.board, False)
        self.board[7][2] = Bishop(7, 2, self.board, True)
        self.board[7][5] = Bishop(7, 5, self.board, True)
        # ферзи:
        self.board[0][3] = Queen(0, 3, self.board, False)
        self.board[7][3] = Queen(7, 3, self.board, True)
        # короли:
        self.board[0][4] = King(0, 4, self.board, False)
        self.board[7][4] = King(7, 4, self.board, True)

        self.step = True  # True означает белый цвет хода
        self.eaten_pieces = []  # листок, который хранит съеденные фигуры
        self.board_history = []  # для записи истории ходов(для ctrl+z)

    # отрисовка доски
    def render(self, input_screen):
        input_screen.fill((0, 0, 0))  # очистка экрана
        pieces_sprites = pygame.sprite.Group()
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
                if bool(self.board[i][j]) is not False:  # если в клетке фигура
                    self.board[i][j].render(pieces_sprites)  # создание спрайта фигуры
        pieces_sprites.draw(input_screen)  # отрисовка группы спрайтов фигур на поле
        # отрисовка съеденных фигур на поле
        if len(self.eaten_pieces) > 0:  # если есть съеденные фигура
            dead_pieces_sprites = pygame.sprite.Group()  # создаю группу спрайтов
            rendered_eaten_white, rendered_eaten_black = 0, 0  # количество отрисованных каждого цвета
            for piece in self.eaten_pieces:
                if piece.color:  # если фигура белая рисую выше
                    piece.render(dead_pieces_sprites, 25, 30, 560, 30 * rendered_eaten_white + 10)
                    rendered_eaten_white += 1
                else:  # если фигура чёрная рисую ниже
                    piece.render(dead_pieces_sprites, 25, 30, 595, 30 * rendered_eaten_black + 10)
                    rendered_eaten_black += 1
            dead_pieces_sprites.draw(input_screen)

    def is_cell_under_attack(self, y, x, color):
        '''
        for i in range(8):
            for j in range(8):
                if self.board[i][j].is_it_possible_step(y, x, self.board) and self.board[i][j].get_color() is not color:
                    return True
        '''
        if color and y > 1:
            if x > 0:
                if isinstance(self.board[y - 1][x - 1], Pawn):
                    if self.board[y - 1][x - 1].get_color() is not color:
                        return True
            if x < 7:
                if isinstance(self.board[y - 1][x + 1], Pawn):
                    if self.board[y - 1][x + 1].get_color() is not color:
                        return True
        if not color and y < 7:
            if x > 0:
                if isinstance(self.board[y + 1][x - 1], Pawn):
                    if self.board[y + 1][x - 1].get_color() is not color:
                        return True
            if x < 7:
                if isinstance(self.board[y + 1][x + 1], Pawn):
                    if self.board[y + 1][x + 1].get_color() is not color:
                        return True

    def on_click(self, y, x, screen_of_click):  # обработчик действий на поле
        print('стартовые координаты:', y, x)
        if bool(self.board[y][x]):  # если нажатие произошло на фигуру
            if self.step == self.board[y][x].color:  # можно ходить только в свой ход(проверка на цвет фигуры = хода)
                # board_before_step = deepcopy(self)  # копия доски до хода
                self.render(screen_of_click)  # отривоска самой доски и фигур
                steps_field = self.board[y][x].possible_steps_field(self.board)  # получение всех возможный ходов фигуры
                # для того, чтобы нельзя было подставить короля под атаку
                if isinstance(self.board[y][x], King):  # если ходим королём
                    for i in range(8):  # перебираем клетки
                        for j in range(8):
                            if self.is_cell_under_attack(i, j, self.board[y][x].get_color()):
                                # если клетка под атакой противника, убираем её из возможных ходов короля
                                steps_field[i][j] = 0

                # проверка на возможность рокировки:
                # для белой стороны
                if (y, x) == (7, 4) and isinstance(self.board[y][x], King) and isinstance(self.board[7][7], Rook):
                    # если король стоит на месте хода и ладья на своем
                    if self.board[7][5] == 0 and self.board[7][6] == 0:  # если между ними нет других фигур
                        if not self.board[y][x].was_moved and not self.board[7][7].was_moved:  # если они не ходили
                            steps_field[7][6] = 1  # добавляем возможность хода на 2 клетки для рокировки
                # для чёрной стороны
                elif (y, x) == (0, 4) and isinstance(self.board[y][x], King) and isinstance(self.board[0][7], Rook):
                    # если король стоит на месте хода и ладья на своем
                    if self.board[0][5] == 0 and self.board[0][6] == 0:  # если между ними нет других фигур
                        if not self.board[y][x].was_moved and not self.board[0][7].was_moved:  # если они не ходили
                            steps_field[0][6] = 1  # добавляем возможность хода на 2 клетки для рокировки

                for i in range(8):
                    for j in range(8):
                        if bool(steps_field[i][j]):  # если ход возможен в координату
                            #  отрисовка зелёной окружности
                            pygame.draw.circle(screen_of_click, pygame.Color('Green'),
                                               (self.left + self.cell_size * j + self.cell_size // 2,
                                                self.top + self.cell_size * i + self.cell_size // 2),
                                               self.cell_size // 2 - 20, 3)
                pygame.display.flip()

                # вылавливание второго нажатия на поле для выбора конечной координаты хода
                step_y, step_x = 10, 10  # неправильные значения хода(если вылетит с этим, то проблемма в цикле)
                local_clock = pygame.time.Clock()
                local_running = True
                while local_running:
                    for local_event in pygame.event.get():
                        if local_event.type == pygame.QUIT:
                            pygame.quit()

                        if local_event.type == pygame.MOUSEBUTTONDOWN:
                            if local_event.button == 1:
                                step_y, step_x = board.get_cell(local_event.pos)  # координаты хода
                                local_running = False  # выход из цикла
                    local_clock.tick(30)
                print('координаты хода:', step_y, step_x)

                if step_y != y or step_x != x:  # нельзя сходить в клетку старта
                    if bool(steps_field[step_y][step_x]):  # если ход в координату возможен
                        #  рокировка:
                        if (  # для белой стороны
                                (y, x) == (7, 4)
                                and isinstance(self.board[y][x], King)  # если ход королём в клетку рокировки
                                and (step_y, step_x) == (7, 6)
                        ):
                            self.board[7][5] = self.board[7][7]  # перемещаем ладью
                            self.board[7][5].set_new_position(7, 5)  # обновляем координаты ладьи
                            self.board[7][5].was_moved = 1  # меняем флаг ладьи (т.к она ходила)
                            self.board[y][x].was_moved = 1  # меняем флаг короля (т.к она ходила)
                            self.board[7][7] = 0  # очистка начальной координаты ладьи
                            # если рокировка произошла, то король идёт по основному алгоритму
                        elif (  # для чёрной стороны
                                (y, x) == (0, 4)
                                and isinstance(self.board[y][x], King)  # если ход королём в клетку рокировки
                                and (step_y, step_x) == (0, 6)
                        ):
                            self.board[0][5] = self.board[0][7]  # перемещаем ладью
                            self.board[0][5].set_new_position(0, 5)  # обновляем координаты ладьи
                            self.board[0][5].was_moved = 1   # меняем флаг ладьи (т.к она ходила)
                            self.board[y][x].was_moved = 1  # меняем флаг короля (т.к она ходила)
                            self.board[0][7] = 0  # очистка начальной координаты ладьи
                            # если рокировка произошла, то король идёт по основному алгоритму

                        if bool(self.board[step_y][step_x]):  # если в клетке хода есть фигура, то её нужно сьесть
                            self.board[step_y][step_x].is_alive = False  # фигура знает, что её сьели
                            self.eaten_pieces.append(self.board[step_y][step_x])  # съеденная фигура записана в листок
                        self.board[step_y][step_x] = 0  # очистка клетки шага
                        self.board[step_y][step_x] = self.board[y][x]  # перемещение фигуры в клетку хода
                        if type(self.board[step_y][step_x]) == Pawn:
                            self.board[step_y][step_x].was_moved = 1
                        self.board[y][x].set_new_position(step_y, step_x)  # обновляем координаты самой фигуры
                        self.board[y][x] = 0  # очистка начальной координаты хода
                        '''
                        self.board_history.append(board_before_step)  # записываем доску до хода(для работы ctrl+z)
                        if len(self.board_history) > 3:  # если более 10 записей истории поля:
                            self.board_history.pop(0)  # удаляем самую раннюю
                        '''

                        # превращение пешки
                        for x in range(8):  # перебираем x
                            if isinstance(self.board[0][x], Pawn):  # если в 0 строке есть пешка
                                # то на её месте создаётся ферзь с координатами и цветом пешки
                                self.board[0][x] = Queen(*self.board[0][x].get_pos(), self,
                                                         self.board[0][x].get_color())
                            if isinstance(self.board[7][x], Pawn):  # если в 8 строке есть пешка
                                # то на её месте создаётся ферзь с координатами и цветом пешки
                                self.board[7][x] = Queen(*self.board[7][x].get_pos(), self,
                                                         self.board[7][x].get_color())

                        # проверка на шах:
                        for y in range(8):
                            for x in range(8):
                                if isinstance(self.board[y][x],
                                              King) and self.is_cell_under_attack(y, x, self.board[y][x].get_color()):
                                    # если в клетке стоит король и на него может напасть другая фигура
                                    print('шах')


                        self.step = not self.step  # смена хода
                        print('ход выполнен')


class Piece:
    def __init__(self, y, x, board, color=True):
        self.y, self.x = y, x  # координаты фигуры (y-сверху, x-слева-направо)
        self.color = color  # значение True означает белый цвет фигуры
        self.is_alive = True  # жива ли фигура
        self.was_moved = False  # была ли сдвинута фигура
        self.board = board

    def __hash__(self):
        return hash((str(type(self).__name__), self.x, self.y))

    def __repr__(self):
        return str(type(self).__name__) + ' y:' + str(self.get_y()) + ' x:' + str(self.get_x())

    def get_color(self):
        return self.color

    def set_new_position(self, y, x):
        self.y, self.x = y, x

    def get_y(self):
        return self.y

    def get_x(self):
        return self.x

    def get_pos(self):
        return self.get_y(), self.get_x()

    def get_linear_moves(self):
        board = self.board
        a1 = [[self.y, i] for i in range(self.x + 1, 8)]
        a2 = [[self.y, i] for i in range(0, self.x)][::-1]
        a3 = [[i, self.x] for i in range(self.y + 1, 8)]
        a4 = [[i, self.x] for i in range(0, self.y)][::-1]
        for i in range(len(a1)):
            if type(board[a1[i][0]][a1[i][1]]) != int:
                if board[a1[i][0]][a1[i][1]].get_color() == self.color:
                    a1 = a1[:i]
                else:
                    a1 = a1[:i + 1]
                break
        for i in range(len(a2)):
            if type(board[a2[i][0]][a2[i][1]]) != int:
                if board[a2[i][0]][a2[i][1]].get_color() == self.color:
                    a2 = a2[:i]
                else:
                    a2 = a2[:i + 1]
                break
        for i in range(len(a3)):
            if type(board[a3[i][0]][a3[i][1]]) != int:
                if board[a3[i][0]][a3[i][1]].get_color() == self.color:
                    a3 = a3[:i]
                else:
                    a3 = a3[:i + 1]
                break
        for i in range(len(a4)):
            if type(board[a4[i][0]][a4[i][1]]) != int:
                if board[a4[i][0]][a4[i][1]].get_color() == self.color:
                    a4 = a4[:i]
                else:
                    a4 = a4[:i + 1]
                break
        return a1 + a2 + a3 + a4

    def get_diagonal_moves(self):
        board = self.board
        a1 = []
        curr = [self.y - 1, self.x - 1]
        while curr[0] >= 0 and curr[1] >= 0:
            a1.append(curr.copy())
            curr[0] -= 1
            curr[1] -= 1
        a2 = []
        curr = [self.y + 1, self.x + 1]
        while curr[0] <= 7 and curr[1] <= 7:
            a2.append(curr.copy())
            curr[0] += 1
            curr[1] += 1
        a3 = []
        curr = [self.y - 1, self.x + 1]
        while curr[0] >= 0 and curr[1] <= 7:
            a3.append(curr.copy())
            curr[0] -= 1
            curr[1] += 1
        a4 = []
        curr = [self.y + 1, self.x - 1]
        while curr[0] <= 7 and curr[1] >= 0:
            a4.append(curr.copy())
            curr[0] += 1
            curr[1] -= 1
        for i in range(len(a1)):
            if type(board[a1[i][0]][a1[i][1]]) != int:
                if board[a1[i][0]][a1[i][1]].get_color() == self.color:
                    a1 = a1[:i]
                else:
                    a1 = a1[:i + 1]
                break
        for i in range(len(a2)):
            if type(board[a2[i][0]][a2[i][1]]) != int:
                if board[a2[i][0]][a2[i][1]].get_color() == self.color:
                    a2 = a2[:i]
                else:
                    a2 = a2[:i + 1]
                break
        for i in range(len(a3)):
            if type(board[a3[i][0]][a3[i][1]]) != int:
                if board[a3[i][0]][a3[i][1]].get_color() == self.color:
                    a3 = a3[:i]
                else:
                    a3 = a3[:i + 1]
                break
        for i in range(len(a4)):
            if type(board[a4[i][0]][a4[i][1]]) != int:
                if board[a4[i][0]][a4[i][1]].get_color() == self.color:
                    a4 = a4[:i]
                else:
                    a4 = a4[:i + 1]
                break
        return a1 + a2 + a3 + a4

    def render(self, sprite_group, sprite_size_y=55, sprite_size_x=55, delta_y=0, delta_x=0, image_name='not_defied'):
        fullname = os.path.join('обрезанные шахматы', image_name)  # путь к фаилу с картинкой
        # если файл не существует, то выходим
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        if self.is_alive:  # если фигура жива, то спрайт рисуется на поле
            transformed_image = pygame.transform.scale(image, (sprite_size_y, sprite_size_x))  # подгонка размеров картинки
            sprite = pygame.sprite.Sprite(sprite_group)  # создание спрайта в группе спрайтов
            sprite.image = transformed_image  # картинка спарайтиа
            sprite.rect = sprite.image.get_rect()
            sprite.rect.y = self.get_y() * 70 + delta_y  # y координата спрайта
            sprite.rect.x = self.get_x() * 70 + delta_x  # x координата спрайта
        else:  # если её съели, то спрайт рисуется под полем, в уменьшенном размере
            transformed_image = pygame.transform.scale(image, (sprite_size_y, sprite_size_x))
            sprite = pygame.sprite.Sprite(sprite_group)  # создание спрайта в группе спрайтов
            sprite.image = transformed_image  # картинка спарайтиа
            sprite.rect = sprite.image.get_rect()
            sprite.rect.y = delta_y  # y координата спрайта
            sprite.rect.x = delta_x  # x координата спрайта

    def is_it_possible_step(self, step_y, step_x, board):  # проверка на возможность шага(ввод- конечные координаты)
        return True

    def possible_steps_field(self, board):
        steps_field = []
        for y in range(8):
            line = []
            for x in range(8):
                if self.is_it_possible_step(y, x, board):
                    line.append(1)
                else:
                    line.append(0)
            steps_field.append(line)
        return steps_field


class Pawn(Piece):
    def __init__(self, y, x, board, color=True):
        super().__init__(y, x, board, color=color)

    def render(self, sprite_group, sprite_size_y=55, sprite_size_x=55, delta_y=0, delta_x=0, image_name='not_defined'):
        if delta_y == 0 and delta_x == 0:  # если параметры были изменены извне, то не меняем их
            # отрисовка фигуры
            if self.color:  # если фигура белая
                image_name = 'white_pawn.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 50, 60  # размеры картинки спрайта
                delta_y, delta_x = 5, 10  # тут можно подкрутить расположение спрайта фигуры в клетке
            elif self.color is False:
                image_name = 'black_pawn.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 50, 60   # размеры картинки спрайта
                delta_y, delta_x = 5, 10  # тут можно подкрутить расположение спрайта фигуры в клетке
        else:
            if self.color:  # если пешка белая
                image_name = 'white_pawn.png'  # имя фаила картинки
            elif self.color is False:
                image_name = 'black_pawn.png'  # имя фаила картинки
        # вызов общего кода отрисовки в родительском классе Piece
        super().render(sprite_group, sprite_size_y, sprite_size_x, delta_y, delta_x, image_name)

    def is_it_possible_step(self, step_y, step_x, board):  # проверка на возможность шага(ввод- конечные координаты)
        accepted = []
        f1, f2 = self.x == 0, self.x == 7
        if self.color:
            if type(board[self.y - 1][self.x]) == int:
                accepted.append([self.y - 1, self.x])
            if not self.was_moved and type(board[self.y - 2][self.x]):
                accepted.append([self.y - 2, self.x])
            if not f2 and type(board[self.y - 1][self.x + 1]) != int and board[self.y - 1][self.x + 1].get_color() != self.color:
                accepted.append([self.y - 1, self.x + 1])
            if not f1 and type(board[self.y - 1][self.x - 1]) != int and board[self.y - 1][self.x - 1].get_color() != self.color:
                accepted.append([self.y - 1, self.x - 1])
        else:
            if type(board[self.y + 1][self.x]) == int:
                accepted.append([self.y + 1, self.x])
            if not self.was_moved:
                accepted.append([self.y + 2, self.x])
            if not f2 and type(board[self.y + 1][self.x + 1]) != int and board[self.y + 1][self.x + 1].get_color() != self.color:
                accepted.append([self.y + 1, self.x + 1])
            if not f1 and type(board[self.y + 1][self.x - 1]) != int and board[self.y + 1][self.x - 1].get_color() != self.color:
                accepted.append([self.y + 1, self.x - 1])
        if [step_y, step_x] in accepted:
            return True
        return False


class Rook(Piece):
    def __init__(self, y, x, board, color=True):
        super().__init__(y, x, board, color)

    def render(self, sprite_group, sprite_size_y=55, sprite_size_x=55, delta_y=0, delta_x=0, image_name='not_defined'):
        if delta_y == 0 and delta_x == 0:  # если параметры были изменены извне, то не меняем их
            if self.color:  # если фиугра белая
                image_name = 'white_rook.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 50, 60  # размеры картинки спрайта
                delta_y, delta_x = 5, 10  # тут можно подкрутить расположение спрайта фигуры в клетке
            elif self.color is False:
                image_name = 'black_rook.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 50, 60  # размеры картинки спрайта
                delta_y, delta_x = 5, 10  # тут можно подкрутить расположение спрайта фигуры в клетке
            # вызов общего кода отрисовки в родительском классе Piece
        else:
            if self.color:  # если фигура белая
                image_name = 'white_rook.png'  # имя фаила картинки
            elif self.color is False:
                image_name = 'black_rook.png'  # имя фаила картинки
        super().render(sprite_group, sprite_size_y, sprite_size_x, delta_y, delta_x, image_name)

    def is_it_possible_step(self, step_y, step_x, board):
        accepted = self.get_linear_moves()
        if [step_y, step_x] in accepted:
            return True
        return False


class King(Piece):
    def __init__(self, y, x, board, color=True):
        super().__init__(y, x, board, color)

    def render(self, sprite_group, sprite_size_y=55, sprite_size_x=55, delta_y=0, delta_x=0, image_name='not_defined'):
        if delta_y == 0 and delta_x == 0:  # если параметры были изменены извне, то не меняем их
            if self.color:  # если фигура белая
                image_name = 'white_king.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 50, 60  # размеры картинки спрайта
                delta_y, delta_x = 5, 10  # тут можно подкрутить расположение спрайта фигуры в клетке
            elif self.color is False:
                image_name = 'black_king.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 50, 60  # размеры картинки спрайта
                delta_y, delta_x = 5, 10  # тут можно подкрутить расположение спрайта фигуры в клетке
            # вызов общего кода отрисовки в родительском классе Piece
        else:
            if self.color:  # если фигура белая
                image_name = 'white_king.png'  # имя фаила картинки
            elif self.color is False:
                image_name = 'black_king.png'  # имя фаила картинки
        super().render(sprite_group, sprite_size_y, sprite_size_x, delta_y, delta_x, image_name)

    def is_it_possible_step(self, step_y, step_x, board):
        accepted = []
        f1, f2, f3, f4 = self.y > 0, self.y < 7, self.x > 0, self.x < 7
        if f1:
            accepted.append([self.y - 1, self.x])
            if f3:
                accepted.append([self.y - 1, self.x - 1])
        if f2:
            accepted.append([self.y + 1, self.x])
            if f4:
                accepted.append([self.y + 1, self.x + 1])
        if f3:
            accepted.append([self.y, self.x - 1])
            if f2:
                accepted.append([self.y + 1, self.x - 1])
        if f4:
            accepted.append([self.y, self.x + 1])
            if f1:
                accepted.append([self.y - 1, self.x + 1])
        accepted = [i for i in accepted if type(board[i[0]][i[1]]) == int or board[i[0]][i[1]].get_color() != self.color]
        if [step_y, step_x] in accepted:
            return True
        return False


class Queen(Piece):
    def __init__(self, y, x, board, color=True):
        super().__init__(y, x, board, color)

    def render(self, sprite_group, sprite_size_y=55, sprite_size_x=55, delta_y=0, delta_x=0, image_name='not_defined'):
        if delta_y == 0 and delta_x == 0:  # если параметры были изменены извне, то не меняем их
            if self.color:  # если фигура белая
                image_name = 'white_queen.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 60, 60  # размеры картинки спрайта
                delta_y, delta_x = 5, 5  # тут можно подкрутить расположение спрайта фигуры в клетке
            elif self.color is False:
                image_name = 'black_queen.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 60, 60  # размеры картинки спрайта
                delta_y, delta_x = 5, 5  # тут можно подкрутить расположение спрайта фигуры в клетке
            # вызов общего кода отрисовки в родительском классе Piece
        else:
            if self.color:  # если фигура белая
                image_name = 'white_queen.png'  # имя фаила картинки
            elif self.color is False:
                image_name = 'black_queen.png'  # имя фаила картинки
        super().render(sprite_group, sprite_size_y, sprite_size_x, delta_y, delta_x, image_name)

    def is_it_possible_step(self, step_y, step_x, board):
        accepted = self.get_linear_moves() + self.get_diagonal_moves()
        if [step_y, step_x] in accepted:
            return True
        return False


class Bishop(Piece):
    def __init__(self, y, x, board, color=True):
        super().__init__(y, x, board, color)

    def render(self, sprite_group, sprite_size_y=55, sprite_size_x=55, delta_y=0, delta_x=0, image_name='not_defined'):
        if delta_y == 0 and delta_x == 0:  # если параметры были изменены извне, то не меняем их
            if self.color:  # если фигура белая
                image_name = 'white_bishop.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 50, 60  # размеры картинки спрайта
                delta_y, delta_x = 5, 10  # тут можно подкрутить расположение спрайта фигуры в клетке
            elif self.color is False:
                image_name = 'black_bishop.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 50, 60  # размеры картинки спрайта
                delta_y, delta_x = 5, 10  # тут можно подкрутить расположение спрайта фигуры в клетке
            # вызов общего кода отрисовки в родительском классе Piece
        else:
            if self.color:  # если фигура белая
                image_name = 'white_bishop.png'  # имя фаила картинки
            elif self.color is False:
                image_name = 'black_bishop.png'  # имя фаила картинки
        super().render(sprite_group, sprite_size_y, sprite_size_x, delta_y, delta_x, image_name)

    def is_it_possible_step(self, step_y, step_x, board):
        accepted = self.get_diagonal_moves()
        if [step_y, step_x] in accepted:
            return True
        return False


class Knight(Piece):
    def __init__(self, y, x, board, color=True):
        super().__init__(y, x, board, color)

    def render(self, sprite_group, sprite_size_y=55, sprite_size_x=55, delta_y=0, delta_x=0, image_name='not_defined'):
        if delta_y == 0 and delta_x == 0:  # если параметры были изменены извне, то не меняем их
            if self.color:  # если фигура белая
                image_name = 'white_knight.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 50, 60  # размеры картинки спрайта
                delta_y, delta_x = 5, 10  # тут можно подкрутить расположение спрайта фигуры в клетке
            elif self.color is False:
                image_name = 'black_knight.png'  # имя фаила картинки
                sprite_size_y, sprite_size_x = 50, 60  # размеры картинки спрайта
                delta_y, delta_x = 5, 10  # тут можно подкрутить расположение спрайта фигуры в клетке
            # вызов общего кода отрисовки в родительском классе Piece
        else:
            if self.color:  # если фигура белая
                image_name = 'white_knight.png'  # имя фаила картинки
            elif self.color is False:
                image_name = 'black_knight.png'  # имя фаила картинки
        super().render(sprite_group, sprite_size_y, sprite_size_x, delta_y, delta_x, image_name)

    def is_it_possible_step(self, step_y, step_x, board):
        if abs(step_x - self.x) in [1, 2] and abs(step_y - self.y) in [1, 2] \
                and abs(step_x - self.x) != abs(step_y - self.y):
            if type(board[step_y][step_x]) == int or board[step_y][step_x].get_color() != self.color:
                return True
        return False


board = Chess()

pygame.init()

screen = pygame.display.set_mode((board.cell_size * board.width, board.cell_size * board.height + 70))
# + 70 по высоте - для поля со съедеными фигурами
pygame.display.set_caption('Шахматы')

clock = pygame.time.Clock()
FPS = 30

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                board.on_click(*board.get_cell(event.pos), screen)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:  # новая игра
                board = Chess()  # сздание нового поля
            if event.mod & pygame.KMOD_CTRL:
                if event.key == pygame.K_z:  # ctrl + z
                    if len(board.board_history) > 0:  # если есть записи в истории
                        board = board.board_history.pop()  # достаю последнюю запись в истории
                        # и теперь наша доска является доской до хода

    board.render(screen)

    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
