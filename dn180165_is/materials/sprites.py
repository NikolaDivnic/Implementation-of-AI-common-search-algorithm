import pygame
import os
import config


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, row, col, file_name, transparent_color=None):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (col * config.TILE_SIZE, row * config.TILE_SIZE)
        self.row = row
        self.col = col


class Agent(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Agent, self).__init__(row, col, file_name, config.DARK_GREEN)

    def move_towards(self, row, col):
        row = row - self.row
        col = col - self.col
        self.rect.x += col
        self.rect.y += row

    def place_to(self, row, col):
        self.row = row
        self.col = col
        self.rect.x = col * config.TILE_SIZE
        self.rect.y = row * config.TILE_SIZE

    # game_map - list of lists of elements of type Tile
    # goal - (row, col)
    # return value - list of elements of type Tile
    def get_agent_path(self, game_map, goal):
        pass


class Aki(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        visina = len(game_map)
        sirina = len(game_map[0])

        row = self.row
        col = self.col

        smer = ""
        mat = []
        for i in range(visina):
            r = []
            for j in range(sirina):
                r.append(False)
            mat.append(r)

        while True:
            mat[row][col] = True
            if row == goal[0] and col == goal[1]:
                break
            tek = 1001
            if row > 0:
                if tek > game_map[row -1][col].cost() and mat[row-1][col] == False:
                    smer = "gore"
                    tek = game_map[row -1][col].cost()

            if col < sirina-1:
                if tek > game_map[row][col+1].cost() and mat[row][col+1] == False:
                    smer = "desno"
                    tek = game_map[row][col+1].cost()

            if row < visina-1:
                if tek > game_map[row+1][col].cost() and mat[row+1][col] == False:
                    smer = "dole"
                    tek = game_map[row+1][col].cost()

            if col > 0:
                if tek > game_map[row][col-1].cost() and mat[row][col-1] == False:
                    smer = "levo"
                    tek = game_map[row][col-1].cost()

            if smer == "dole":
                row+=1
            if smer == "gore":
                row-=1
            if smer == "levo":
                col-=1
            if smer == "desno":
                col+=1

            path.append(game_map[row][col])
        return path






def odrediCenu(smer, row, col, game_map):
    cena = 0
    br = 0
    visina = len(game_map)
    sirina = len(game_map[0])
    if smer == "dole":
        if col >0:
            cena += game_map[row][col-1].cost()
            br +=1
        if col < sirina - 1:
            cena += game_map[row][col + 1].cost()
            br += 1
        if row < visina-1:
            cena += game_map[row+1][col].cost()
            br += 1
    if smer == "gore":
        if col > 0:
            cena += game_map[row][col-1].cost()
            br += 1
        if col < sirina - 1:
            cena += game_map[row][col + 1].cost()
            br += 1
        if row > 0:
            br += 1
            cena += game_map[row-1][col].cost()
    if smer == "levo":
        if col >0:
            br += 1
            cena += game_map[row][col-1].cost()
        if row >0:
            br += 1
            cena += game_map[row-1][col].cost()
        if row < visina-1:
            br += 1
            cena += game_map[row+1][col].cost()
    if smer == "desno":
        if row >0:
            br += 1
            cena += game_map[row-1][col].cost()
        if row < visina-1:
            br += 1
            cena += game_map[row+1][col].cost()
        if col < sirina - 1:
            br += 1
            cena += game_map[row][col + 1].cost()
    return cena/br

class ElementJocke:
    def __init__(self, row, col, cena, path):
        self.row = row
        self.col = col
        self.cena = cena
        self.path = path
class Jocke(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        visina = len(game_map)
        sirina = len(game_map[0])

        row = self.row
        col = self.col

        red = []

        if row > 0:
            p11 = path.copy()
            p11.append(game_map[row-1][col])
            red.append(ElementJocke(row - 1, col, odrediCenu("gore", row - 1, col, game_map), p11))

        if col < sirina - 1:
            p12 = path.copy()
            p12.append(game_map[row][col+1])
            red.append(ElementJocke(row, col+1, odrediCenu("desno", row, col + 1, game_map), p12))

        if row < visina - 1:
            p13 = path.copy()
            p13.append(game_map[row + 1][col])
            red.append(ElementJocke(row + 1, col, odrediCenu("dole", row + 1, col, game_map), p13))

        if col > 0:
            p14 = path.copy()
            p14.append(game_map[row][col-1])
            red.append(ElementJocke(row, col-1, odrediCenu("levo", row, col - 1, game_map), p14))
        red.sort(key=lambda s: s.cena)

        while True:

            while len(red):
                red2 = []
                pom = red.pop(0)
                row = pom.row
                col = pom.col
                path = pom.path
                if row == goal[0] and col == goal[1]:
                    return path
                if row > 0:
                    p1 = path.copy()
                    usao = False
                    for i in range(len(p1)):
                        if p1[i] == game_map[row - 1][col]:
                            usao = True
                    if not usao:
                        p1.append(game_map[row - 1][col])
                        red2.append(ElementJocke(row - 1, col, odrediCenu("gore", row - 1, col, game_map), p1))

                if col < sirina - 1:
                    p2 = path.copy()
                    usao = False
                    for i in range(len(p2)):
                        if p2[i] == game_map[row][col + 1]:
                            usao = True
                    if not usao:
                        p2.append(game_map[row][col + 1])
                        red2.append(ElementJocke(row, col + 1, odrediCenu("desno", row, col + 1, game_map), p2))

                if row < visina - 1:
                    p3 = path.copy()
                    usao = False
                    for i in range(len(p3)):
                        if p3[i] == game_map[row + 1][col]:
                            usao = True
                    if not usao:
                        p3.append(game_map[row + 1][col])
                        red2.append(ElementJocke(row + 1, col, odrediCenu("dole", row + 1, col, game_map), p3))

                if col > 0:
                    p4 = path.copy()
                    usao = False
                    for i in range(len(p4)):
                        if p4[i] == game_map[row][col - 1]:
                            usao = True
                    if not usao:
                        p4.append(game_map[row][col - 1])
                        red2.append(ElementJocke(row, col - 1, odrediCenu("levo", row, col - 1, game_map), p4))
                red2.sort(key=lambda s: s.cena)
                red.extend(red2)

class ElementDraza:
    def __init__(self, row, col, cena, path):
        self.row = row
        self.col = col
        self.cena = cena
        self.path = path

class Draza(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        visina = len(game_map)
        sirina = len(game_map[0])

        row = self.row
        col = self.col

        red = []

        if row > 0:
            p11 = path.copy()
            p11.append(game_map[row - 1][col])
            red.append(ElementDraza(row - 1, col, game_map[row-1][col].cost(), p11))

        if col < sirina - 1:
            p12 = path.copy()
            p12.append(game_map[row][col + 1])
            red.append(ElementDraza(row, col + 1, game_map[row][col+1].cost(), p12))

        if row < visina - 1:
            p13 = path.copy()
            p13.append(game_map[row + 1][col])
            red.append(ElementDraza(row + 1, col, game_map[row+1][col].cost(), p13))

        if col > 0:
            p14 = path.copy()
            p14.append(game_map[row][col - 1])
            red.append(ElementDraza(row, col - 1, game_map[row][col-1].cost(), p14))
        red.sort(key=lambda s: s.cena)


        while len(red):
            pom = red.pop(0)
            row = pom.row
            col = pom.col
            path = pom.path
            cena = pom.cena
            if row == goal[0] and col == goal[1]:
                return path
            if row > 0:
                p1 = path.copy()
                usao = False
                for i in range(len(p1)):
                    if p1[i] == game_map[row - 1][col]:
                        usao = True
                if not usao:
                    p1.append(game_map[row - 1][col])
                    red.append(ElementDraza(row - 1, col, game_map[row-1][col].cost() + cena, p1))

            if col < sirina - 1:
                p2 = path.copy()
                usao = False
                for i in range(len(p2)):
                    if p2[i] == game_map[row][col + 1]:
                        usao = True
                if not usao:
                    p2.append(game_map[row][col + 1])
                    red.append(ElementDraza(row, col + 1, game_map[row][col+1].cost() + cena, p2))

            if row < visina - 1:
                p3 = path.copy()
                usao = False
                for i in range(len(p3)):
                    if p3[i] == game_map[row + 1][col]:
                        usao = True
                if not usao:
                    p3.append(game_map[row + 1][col])
                    red.append(ElementDraza(row + 1, col, game_map[row+1][col].cost() + cena, p3))

            if col > 0:
                p4 = path.copy()
                usao = False
                for i in range(len(p4)):
                    if p4[i] == game_map[row][col - 1]:
                        usao = True
                if not usao:
                    p4.append(game_map[row][col - 1])
                    red.append(ElementDraza(row, col - 1, game_map[row][col-1].cost() + cena, p4))

            red.sort(key=lambda s: (s.cena, len(s.path)))



class ElementBole:
    def __init__(self, row, col, cena, path, heuristika):
        self.row = row
        self.col = col
        self.cena = cena
        self.path = path
        self.heuristika = heuristika

class Bole(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        visina = len(game_map)
        sirina = len(game_map[0])

        row = self.row
        col = self.col

        red = []
        mat =[]

        for i in range(visina):
            r = []
            for j in range(sirina):
                r.append((abs(goal[0] - i) + abs(goal[1] - j)))
            mat.append(r)


        if row > 0:
            p11 = path.copy()
            p11.append(game_map[row - 1][col])
            red.append(ElementBole(row - 1, col, game_map[row-1][col].cost(), p11, mat[row-1][col]))

        if col < sirina - 1:
            p12 = path.copy()
            p12.append(game_map[row][col + 1])
            red.append(ElementBole(row, col + 1, game_map[row][col+1].cost(), p12, mat[row][col+1]))

        if row < visina - 1:
            p13 = path.copy()
            p13.append(game_map[row + 1][col])
            red.append(ElementBole(row + 1, col, game_map[row+1][col].cost(), p13, mat[row+1][col]))

        if col > 0:
            p14 = path.copy()
            p14.append(game_map[row][col - 1])
            red.append(ElementBole(row, col - 1, game_map[row][col-1].cost(), p14, mat[row][col-1]))
        red.sort(key=lambda s: (s.cena+ s.heuristika))


        while len(red):
            pom = red.pop(0)
            row = pom.row
            col = pom.col
            path = pom.path
            cena = pom.cena
            if row == goal[0] and col == goal[1]:
                return path
            if row > 0:
                p1 = path.copy()
                usao = False
                for i in range(len(p1)):
                    if p1[i] == game_map[row - 1][col]:
                        usao = True
                if not usao:
                    p1.append(game_map[row - 1][col])
                    red.append(ElementBole(row - 1, col, game_map[row-1][col].cost() + cena, p1, mat[row-1][col]))

            if col < sirina - 1:
                p2 = path.copy()
                usao = False
                for i in range(len(p2)):
                    if p2[i] == game_map[row][col + 1]:
                        usao = True
                if not usao:
                    p2.append(game_map[row][col + 1])
                    red.append(ElementBole(row, col + 1, game_map[row][col+1].cost() + cena, p2, mat[row][col+1]))

            if row < visina - 1:
                p3 = path.copy()
                usao = False
                for i in range(len(p3)):
                    if p3[i] == game_map[row + 1][col]:
                        usao = True
                if not usao:
                    p3.append(game_map[row + 1][col])
                    red.append(ElementBole(row + 1, col, game_map[row+1][col].cost() + cena, p3, mat[row+1][col]))

            if col > 0:
                p4 = path.copy()
                usao = False
                for i in range(len(p4)):
                    if p4[i] == game_map[row][col - 1]:
                        usao = True
                if not usao:
                    p4.append(game_map[row][col - 1])
                    red.append(ElementBole(row, col - 1, game_map[row][col-1].cost() + cena, p4, mat[row][col-1]))

            red.sort(key=lambda s: (s.cena + s.heuristika))




class Tile(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Tile, self).__init__(row, col, file_name)

    def position(self):
        return self.row, self.col

    def cost(self):
        pass

    def kind(self):
        pass


class Stone(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'stone.png')

    def cost(self):
        return 1000

    def kind(self):
        return 's'


class Water(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'water.png')

    def cost(self):
        return 500

    def kind(self):
        return 'w'


class Road(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'road.png')

    def cost(self):
        return 2

    def kind(self):
        return 'r'


class Grass(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'grass.png')

    def cost(self):
        return 3

    def kind(self):
        return 'g'


class Mud(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'mud.png')

    def cost(self):
        return 5

    def kind(self):
        return 'm'


class Dune(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'dune.png')

    def cost(self):
        return 7

    def kind(self):
        return 's'


class Goal(BaseSprite):
    def __init__(self, row, col):
        super().__init__(row, col, 'x.png', config.DARK_GREEN)


class Trail(BaseSprite):
    def __init__(self, row, col, num):
        super().__init__(row, col, 'trail.png', config.DARK_GREEN)
        self.num = num

    def draw(self, screen):
        text = config.GAME_FONT.render(f'{self.num}', True, config.WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
