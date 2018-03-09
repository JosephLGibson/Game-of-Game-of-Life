import set_up
import pygame
import random
import preset
import copy


class Cell:
    def __init__(self, a, b, current_state, next_state, board, player):
        """a,b are the coordinates of the cell the instance represents with respect to the board."""
        self.CurrentState = current_state
        self.NextState = next_state
        self.CurrentPlayer = 0
        self.NextPlayer = player
        self.BoardPos = (a, b)
        self.Coordinates = ((self.BoardPos[0] - board.Cushion) * board.Size + board.CellGap / 2,
                            (self.BoardPos[1] - board.Cushion) * board.Size + board.CellGap / 2)
    
    def kill(self):
        self.NextState = set_up.Dead
        self.NextPlayer = 0
    
    def birth(self, state, player):
        self.NextState = state
        self.NextPlayer = player
    
    def check_fate(self, board):
        """Checks whether the cell will be dead or alive at the end of this turn,
            and if so what type it will be"""
        total = [0, 0, 0, 0]
        player = [0, 0, 0, 0, 0]
        a, b = self.BoardPos
        al = a - 1  # a left (neighbour)
        ar = a + 1  # a right
        bu = b - 1  # b up
        bd = b + 1  # b down
        if board.Wrap and a == board.Width - 1:
            ar = 0
        if board.Wrap and b == board.Height - 1:
            bd = 0
        total[board.Cell[al][b].CurrentState] += 1
        player[board.Cell[al][b].CurrentPlayer] += 1
        
        total[board.Cell[a][bu].CurrentState] += 1
        player[board.Cell[a][bu].CurrentPlayer] += 1
        
        total[board.Cell[ar][b].CurrentState] += 1
        player[board.Cell[ar][b].CurrentPlayer] += 1
        
        total[board.Cell[a][bd].CurrentState] += 1
        player[board.Cell[a][bd].CurrentPlayer] += 1
        
        total[board.Cell[al][bu].CurrentState] += 1
        player[board.Cell[al][bu].CurrentPlayer] += 1
        
        total[board.Cell[ar][bu].CurrentState] += 1
        player[board.Cell[ar][bu].CurrentPlayer] += 1
        
        total[board.Cell[al][bd].CurrentState] += 1
        player[board.Cell[al][bd].CurrentPlayer] += 1
        
        total[board.Cell[ar][bd].CurrentState] += 1
        player[board.Cell[ar][bd].CurrentPlayer] += 1
        
        new_state = self.CurrentState
        new_player = self.CurrentPlayer
        birth = False
        death = False
        if self.CurrentState == set_up.Dead:
            if total[set_up.Dead] == 5:  # if 5 dead cells; ie. if 3 alive cells
                birth = True
        elif self.CurrentState == set_up.Square:
            if total[set_up.Dead] not in (5, 6):
                death = True
        if birth:
            del total[0]
            new_state = total.index(max(total)) + 1
            del player[0]
            if sum(player) == 0:
                new_player = 0
            else:
                new_player = player.index(max(player)) + 1
        
        if death:
            new_state = set_up.Dead
            new_player = 0
        
        return new_state, new_player
    
    def draw(self, screen, size, board):
        x, y = self.Coordinates
        x += board.Size // 2
        y += board.Size // 2
        pygame.draw.rect(screen, board.Colour["Dead"], (x - size / 2, y - size / 2, size, size))
        if not self.CurrentState == set_up.Dead:
            if self.CurrentPlayer == 0:
                self.draw_shape(screen, size, x, y, board.Colour["Alive"])
            else:
                self.draw_shape(screen, size, x, y, board.Colour["Player" + str(self.CurrentPlayer)])
    
    def update(self):
        self.CurrentState = self.NextState
        self.CurrentPlayer = self.NextPlayer


class Square(Cell):
    def draw_shape(self, screen, size, x, y, colour):
        """Draws a type of cell (Type) at the desired cell (a,b)"""
        pygame.draw.rect(screen, colour, (x - size / 2, y - size / 2, size, size))


class Board:
    def __init__(self, state, players=False):
        self.Width = state.Width
        self.Height = state.Height
        self.Size = state.Size
        self.Wrap = state.Wrap
        self.CellGap = state.CellGap
        self.Generations = 0
        self.Cushion = state.Cushion
        self.Colour = state.Colour
        self.PreviewSize = state.PreviewSize
        self.Players = players
        self.Cell = [[Square(a, b, set_up.Square, set_up.Dead, self, 0) for b in range(
            self.Height + (2 * self.Cushion))] for a in range(self.Width + 2 * self.Cushion)]
        pygame.display.set_caption("Game of Life - Generation 0")
    
    def set_up(self, chances):
        if sum(chances) != 0:
            for a in range(self.Width):
                for b in range(self.Height):
                    n = random.randint(1, sum(chances))
                    for c in range(len(chances)):
                        if sum(chances[:c + 1]) > n:
                            if c != 0:
                                if not self.Players:
                                    c = 0
                                self.Cell[a][b].birth(set_up.Square, c)
                            break
    
    def draw(self, screen, preview=False, update_display=True):
        """draws the current board onto the screen then updates the display"""
        if preview:
            size = self.PreviewSize
        else:
            size = self.Size - self.CellGap
        for a in range(self.Cushion, self.Cushion + self.Width):
            for b in range(self.Cushion, self.Cushion + self.Height):
                self.Cell[a][b].draw(screen, size, self)
        if update_display:
            pygame.display.update()
    
    def update(self):
        """Puts the NextState variables in the CurrentState variables"""
        for a in range(self.Width + 2 * self.Cushion):
            for b in range(self.Height + 2 * self.Cushion):
                self.Cell[a][b].update()
    
    def take_turn(self):
        """Changes the NextState variables & updates display caption"""
        pygame.display.set_caption("Game of Life - Generation " + str(self.Generations))
        if self.Wrap:
            cushion = 0
        else:
            cushion = 1
        for a in range(cushion, self.Width + (2 * self.Cushion) - cushion):  # Goes through all cells and kills
            for b in range(cushion, self.Height + (2 * self.Cushion) - cushion):  # those that will die and births
                fate, player = self.Cell[a][b].check_fate(self)  # those that will be born.
                if self.Cell[a][b].CurrentState != fate or self.Cell[a][b].CurrentPlayer != player:
                    if fate == set_up.Dead:
                        self.Cell[a][b].kill()
                    else:
                        if player == 0:
                            self.Cell[a][b].birth(fate, 0)
                        else:
                            self.Cell[a][b].birth(fate, player)
    
    def place_preset(self, screen, preset_no, a, b):
        if self.Wrap:
            shape = preset.get(preset_no, a, b, self)[0]
        else:
            shape, a, b = preset.get(preset_no, a, b, self)
        for c in range(len(shape)):
            for d in range(len(shape[c])):
                if self.Wrap:
                    if a + c >= self.Width:
                        a -= self.Width
                    if b + d >= self.Height:
                        b -= self.Height
                if shape[c][d] == 0:
                    self.Cell[a + c][b + d].kill()
                else:
                    self.Cell[a + c][b + d].birth(shape[c][d], 0)
        self.update()
        self.draw(screen)
    
    def reset(self, state):
        self.__init__(state, players=self.Players)
        self.update()
    
    def show_future(self, screen, actions, player):
        temp_board = copy.deepcopy(self)
        for action in actions:
            if action[2]:
                temp_board.Cell[action[0]][action[1]].kill()
            else:
                temp_board.Cell[action[0]][action[1]].birth(set_up.Square, player)
            temp_board.Cell[action[0]][action[1]].update()
        temp_board.draw(screen, update_display=False)
        temp_board.take_turn()
        temp_board.update()
        temp_board.draw(screen, preview=True)
