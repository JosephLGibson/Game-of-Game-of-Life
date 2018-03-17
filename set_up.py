import pygame
import config
import math as maths
import time
import copy

Font = config.Font
Dead = 0
Square = 1


class Player:
    def __init__(self, number, colour, starting_turns):
        self.Number = number
        self.Colour = colour
        self.NoOfCells = 0
        self.SpareTurns = starting_turns


class Menu:
    """Change these values to change how the main self looks."""
    
    def __init__(self):
        self.ButtonHeight = config.M_ButtonHeight
        self.ButtonWidth = config.M_ButtonWidth
        self.ButtonBorder = config.M_ButtonBorder
        self.ButtonGapSize = config.M_ButtonGapSize
        self.SideGapSize = config.M_SideGapSize
        self.TextSize = config.M_TextSize
        self.TitleGapSize = config.M_TitleGapSize
        self.TitleTextSize = config.M_TitleTextSize
        self.Buttons = ("Simulator", "2-Player Game", "Help", "Quit")
        self.Colour = config.M_Colour
    
    def get_choice(self, screen):
        pygame.display.set_caption("Game of Life - Main Menu")
        pygame.display.set_mode((2 * self.SideGapSize + self.ButtonWidth,
                                 2 * self.TitleGapSize + len(self.Buttons) * (self.ButtonHeight + self.ButtonGapSize)))
        screen.fill(self.Colour["Background"])
        
        buttons = [[screen.get_width() // 2,
                    2 * self.TitleGapSize + a * (self.ButtonHeight + self.ButtonGapSize) + self.TitleTextSize,
                    self.Buttons[a], self.Colour["Text"]] for a in range(len(self.Buttons))]
        for a in range(len(self.Buttons)):
            pygame.draw.rect(screen, self.Colour["Border"], (buttons[a][0] - self.ButtonWidth // 2,
                                                             buttons[a][1] - self.ButtonHeight // 2,
                                                             self.ButtonWidth, self.ButtonHeight))
            pygame.draw.rect(screen, self.Colour["Background"], ((buttons[a][0] - self.ButtonWidth // 2 + self.ButtonBorder,
                                                                  buttons[a][1] - self.ButtonHeight // 2 + self.ButtonBorder,
                                                                  self.ButtonWidth - self.ButtonBorder * 2,
                                                                  self.ButtonHeight - self.ButtonBorder * 2)))
        
        write(screen, screen.get_width() // 2, self.TitleGapSize, "Main Menu", self.Colour["Text"], self.TitleTextSize,
              alignment=("centre", "centre"))
        
        while True:
            if check_quit(pygame.event.get()):
                quit_game()
            x, y = pygame.mouse.get_pos()
            for a in range(len(self.Buttons)):
                buttons[a][3] = self.Colour["Text"]
            if screen.get_width() / 2 - self.ButtonWidth / 2 < x < screen.get_width() / 2 + self.ButtonWidth / 2:
                for a in range(len(self.Buttons)):
                    if buttons[a][1] - self.ButtonHeight / 2 < y < buttons[a][1] + self.ButtonHeight / 2:
                        if pygame.mouse.get_pressed()[0]:
                            return buttons[a][2]
                        buttons[a][3] = self.Colour["Hover"]
            for a in range(len(self.Buttons)):
                write(screen, screen.get_width() // 2, buttons[a][1], buttons[a][2], buttons[a][3], self.TextSize,
                      alignment=("centre", "centre"))
            pygame.display.update()


class Sim:
    """Change these values to change how the game looks and behaves in Simulator mode."""
    
    def __init__(self):
        self.Width = config.S_Width
        self.Height = config.S_Height
        self.Size = config.S_Size
        self.CellGap = config.S_CellGap
        self.Wrap = config.S_Wrap
        self.Cushion = config.S_Cushion
        self.PreviewSize = 0
        self.SetUpChances = config.S_SetUpChances
        
        self.SliderSize = config.S_SliderSize
        self.HighlightSize = config.S_HighlightSize
        self.NoOfNotches = config.S_NoOfNotches
        self.NotchLength = config.S_NotchLength
        self.StartOfSlider = 2 * self.NotchLength
        self.SpeedSize = config.S_SpeedSize
        self.EndOfSlider = self.Height * self.Size - self.HighlightSize - self.NotchLength
        self.SpaceBetweenNotches = (self.EndOfSlider - self.StartOfSlider) / (self.NoOfNotches - 1)
        self.SliderY = self.Size * self.Width + self.CellGap // 2 + self.SliderSize // 2
        self.ButtonStart = self.Size * self.Width
        
        self.GPS = config.S_GPS
        self.TopGPS = config.S_TopGPS
        self.BottomGPS = config.S_BottomGPS
        self.GPSIsLimited = True
        self.Paused = True
        self.OneTurn = False
        self.HeldDown = {"space": True,
                         "right": True,
                         "number": True,
                         "f": True}
        self.Colour = config.S_Colour
    
    def run(self, screen, board):
        pygame.display.set_caption("Game of Life")
        pygame.display.set_mode((board.Size * board.Width + self.SliderSize, board.Size * board.Height))
        screen.fill(self.Colour["Background"])
        self.draw_gps_slider(screen, ((maths.log(self.GPS, 10) + 1) // -3)
                             * (self.EndOfSlider - self.StartOfSlider) + self.EndOfSlider, self.GPSIsLimited, board)
        last_frame = time.time()
        board.update()
        board.draw(screen)
        
        while not self.check_user_input(screen, board):
            board.update()
            if (not self.Paused and (not self.GPSIsLimited or time.time() - last_frame > 1 / self.GPS)) \
                    or (self.Paused and self.OneTurn):
                if self.OneTurn:
                    self.OneTurn = False
                board.take_turn(update_caption=True)
                board.update()
                board.Generations += 1
                board.draw(screen)
                last_frame = time.time()
    
    def check_user_input(self, screen, board):
        """Checks for user input and acts accordingly"""
        
        go_back = check_quit(pygame.event.get())
        x, y = pygame.mouse.get_pos()
        a, b = board.get_square(x, y)
        if pygame.key.get_pressed()[pygame.K_SPACE] and not self.HeldDown["space"]:
            self.Paused = not self.Paused
        if pygame.key.get_pressed()[pygame.K_f] and not self.HeldDown["f"]:
            self.GPSIsLimited = not self.GPSIsLimited
            bottom_gps_log = maths.log(self.BottomGPS, self.TopGPS)
            self.draw_gps_slider(screen, self.EndOfSlider -
                                 ((maths.log(self.GPS, self.TopGPS) - bottom_gps_log) *
                                  (self.EndOfSlider - self.StartOfSlider)) // (1 - bottom_gps_log),
                                 self.GPSIsLimited, board)
        if pygame.key.get_pressed()[pygame.K_RIGHT] and not self.HeldDown["right"]:
            self.OneTurn = True
        else:
            self.OneTurn = False
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            board.reset(self)
            board.draw(screen)
            self.Paused = True
        if pygame.mouse.get_pressed()[0]:
            if board.Size * board.Width + board.CellGap / 2 < x < (
                        board.Size * board.Width) + self.SliderSize + board.CellGap / 2:
                if y < self.StartOfSlider:
                    y = self.StartOfSlider
                elif y > self.EndOfSlider:
                    y = self.EndOfSlider
                    self.GPSIsLimited = True
                self.draw_gps_slider(screen, y, self.GPSIsLimited, board)
                bottom_gps_log = maths.log(self.BottomGPS, self.TopGPS)
                self.GPS = self.TopGPS ** (((1 - bottom_gps_log) * (self.EndOfSlider - y)
                                            / (self.EndOfSlider - self.StartOfSlider)) + bottom_gps_log)
            elif 0 <= a < board.Width + board.Cushion and 0 <= b < board.Height + board.Cushion:
                board.Cell[a][b].birth(Square, 0)
                board.update()
                board.draw(screen)
        if pygame.mouse.get_pressed()[2]:
            board.Cell[a][b].kill()
            board.update()
            board.draw(screen)
        number_pressed = False
        for key in range(pygame.K_1, pygame.K_9):
            if pygame.key.get_pressed()[key]:
                if not self.HeldDown["number"]:
                    board.place_preset(screen, int(pygame.key.name(key)), a, b)
                number_pressed = True
        self.HeldDown["number"] = number_pressed
        for key in (("space", "SPACE"), ("f", "f"), ("right", "RIGHT")):
            self.HeldDown[key[0]] = eval("pygame.key.get_pressed()[pygame.K_%s]" % key[1])
        
        return go_back
    
    def draw_gps_slider(self, screen, y, gps_limit, board):
        """Draws the slider with the y coordinate of the button click
           (How many GPS this corresponds to is not dealt with here.)"""
        if y < self.StartOfSlider:
            y = self.StartOfSlider
        elif y > self.EndOfSlider:
            y = self.EndOfSlider
        pygame.draw.rect(screen, self.Colour["Background"],
                         ((self.ButtonStart, self.StartOfSlider - self.NotchLength),
                          (self.ButtonStart + board.CellGap + self.HighlightSize + self.SliderSize, self.EndOfSlider)))
        pygame.draw.line(screen, self.Colour["Text"], (self.SliderY, self.StartOfSlider), (self.SliderY, self.EndOfSlider))
        for n in range(self.NoOfNotches):
            pygame.draw.line(screen, self.Colour["Text"], (self.SliderY - self.NotchLength // 2,
                                                           self.StartOfSlider + int(n * self.SpaceBetweenNotches)),
                             (self.SliderY + self.NotchLength // 2, self.StartOfSlider + int(n * self.SpaceBetweenNotches)))
        write(screen, (self.Size * self.Width + self.SliderY - self.NotchLength) // 2,
              (self.StartOfSlider + self.EndOfSlider) // 2, "Speed", self.Colour["Text"], self.SpeedSize,
              rotate=90, alignment=("centre", "centre"))
        if gps_limit:
            colour = "Highlighter"
        else:
            colour = "Unselected"
        pygame.draw.polygon(screen, self.Colour[colour], ((self.SliderY + self.NotchLength // 2, y),
                                                          (self.SliderY + self.NotchLength, y - self.NotchLength // 2),
                                                          (self.SliderY + 2 * self.NotchLength, y - self.NotchLength // 2),
                                                          (self.SliderY + 2 * self.NotchLength, y + self.NotchLength // 2),
                                                          (self.SliderY + self.NotchLength, y + self.NotchLength // 2)))
        pygame.display.update()


class Game:
    """Change these values to change how the game looks and behaves in 2-Player mode."""
    
    def __init__(self):
        self.Width = config.G_Width
        self.Height = config.G_Height
        self.Size = config.G_Size
        self.CellGap = config.G_CellGap
        self.Wrap = True
        self.Cushion = 0
        self.Turns = 0
        self.Gens = 0
        self.NoOfPlayers = config.G_NoOfPlayers
        self.PlayerNames = config.G_PlayerNames[:self.NoOfPlayers]
        self.PreviewSize = config.G_PreviewSize
        self.SetUpChances = config.G_SetUpChances[:self.NoOfPlayers + 1]
        self.TextSize = config.G_TextSize
        self.RightColumnSize = config.G_RightColumnSize
        self.ButtonHeight = config.G_ButtonHeight
        self.ButtonBorderSize = config.G_ButtonBorderSize
        self.WinMessageWidth = config.G_WinMessageWidth
        self.WinMessageHeight = config.G_WinMessageHeight
        self.PartImmuneTime = config.G_PartImmuneTime
        self.FullImmuneTime = config.G_FullImmuneTime
        self.Colour = config.G_Colour
        self.CurrentPlayer = 1
        self.IsTurnLimit = config.G_IsTurnLimit
        self.TurnLimit = config.G_TurnLimit
        self.IsGenLimit = config.G_IsGenLimit
        self.GenLimit = config.G_GenLimit
        self.BoardAmountWin = config.G_BoardAmountWin
        self.BoardAmount = config.G_BoardAmount
        self.PlayerAmountWin = config.G_PlayerAmountWin
        self.PlayerAmount = config.G_PlayerAmount
        self.StartingTurns = config.G_StartingTurns
        self.FairerTurns = config.G_FairerTurns
        self.Players = [Player(n, self.Colour["Player" + str(n)], self.StartingTurns) for n in range(1, self.NoOfPlayers + 1)]
    
    def run(self, screen, board):
        board.update()
        board.draw(screen)
        screen = pygame.display.set_mode((board.Size * board.Width + self.RightColumnSize, board.Size * board.Height))
        screen.fill(self.Colour["Background"])
        if self.FairerTurns:
            turns_added = 2
            for p in range(self.NoOfPlayers // 2):
                self.Players[p].SpareTurns -= 1
        else:
            turns_added = 1
        for player in self.Players:
            player.SpareTurns -= turns_added
        while True:
            gen_text = "Generations: " + str(self.Gens)
            if self.IsGenLimit:
                 gen_text += " (%s)" % str(self.GenLimit)
            turn_text = "Turns: " + str(self.Turns)
            if self.IsTurnLimit:
                turn_text += " (%s)" % str(self.TurnLimit)
            if self.BoardAmountWin:
                turn_text += " Cells needed to win: " + str(maths.floor(self.BoardAmount * self.Width * self.Height))
            pygame.display.set_caption("Game of Life - Game - " + gen_text + " " + turn_text)
            player_scores = self.get_player_scores(board)
            for p in range(self.NoOfPlayers):
                self.Players[p].NoOfCells = player_scores[p + 1]
            self.Players[self.CurrentPlayer - 1].SpareTurns += turns_added
            turn = self.take_turn(screen, board, self.CurrentPlayer)
            if turn == "Go Back":
                self.Players[self.CurrentPlayer - 1].SpareTurns -= 1
                return False
            else:
                board.impose_turns(turn, self.CurrentPlayer)
                self.Players[self.CurrentPlayer - 1].SpareTurns -= len(turn[1])
                screen.fill(self.Colour["Background"])
                board.draw(screen)
            if turn[0] is not None:
                self.Gens += 1
            if self.CurrentPlayer == self.NoOfPlayers:
                self.CurrentPlayer = 1
                self.Turns += 1
            else:
                self.CurrentPlayer += 1
            win = self.check_for_wins(board, self.Turns, self.Gens)
            if win is not None:
                if win[0].startswith("T"):
                    win_message = "Turn limit reached.Player " + str(win[1]) + " wins!"
                elif win[0].startswith("G"):
                    win_message = "Generation limit reached.Player " + str(win[1]) + " wins!"
                elif win[0].startswith("S"):
                    win_message = "Player " + str(win[1]) + " got enough points to win!"
                else:
                    win_message = "Player " + str(win[1]) + " got more cells than the other player by enough to win"
                pygame.draw.rect(screen, (self.Colour["Highlighter"]),
                                 ((screen.get_width() - self.WinMessageWidth) // 2 - self.ButtonBorderSize,
                                  (screen.get_height() - self.WinMessageHeight) // 2 - self.ButtonBorderSize,
                                  self.WinMessageWidth + 2 * self.ButtonBorderSize,
                                  self.WinMessageHeight + 2 * self.ButtonBorderSize))
                pygame.draw.rect(screen, (self.Colour["Background"]),
                                 ((screen.get_width() - self.WinMessageWidth) // 2,
                                  (screen.get_height() - self.WinMessageHeight) // 2,
                                  self.WinMessageWidth, self.WinMessageHeight))
                write(screen, screen.get_width() // 2, screen.get_height() // 2, win_message, self.Colour["Text"],
                      self.TextSize, max_len=self.WinMessageWidth, alignment=("centre", "centre"))
                pygame.display.update()
                board_view = False
                while True:
                    if check_quit(pygame.event.get()):
                        if board_view:
                            return True
                        else:
                            board_view = True
                            screen.fill(self.Colour["Background"])
                            board.draw(screen)
                            self.draw_right_column(screen, self.get_player_scores(board), (False, False), (0, 0, 0, 0), 0,
                                                   clickable=False)
                            pygame.display.update()
    
    def take_turn(self, screen, board, player_no):
        turn_chosen = False
        board.draw(screen)
        turn = [None, []]
        held_down = {"mouse0": True, "mouse2": False, "esc": False, "space": True, "f": False, "j": False}
        show_future = True
        show_alive_for = False
        turns_used = [0 for _ in range(self.NoOfPlayers)]
        while not turn_chosen:
            events = pygame.event.get()
            if check_quit(events) and not held_down["esc"]:  # if ESC is pressed
                if len(turn[1]) == 0 and turn[0] is None:
                    return "Go Back"
                else:
                    if turn[0] == len(turn[1]):
                        turn[0] = None
                    else:
                        del turn[1][-1]
                        turns_used[player_no - 1] -= 1
                held_down["esc"] = True
            else:
                held_down["esc"] = False
            x, y = pygame.mouse.get_pos()
            a, b = board.get_square(x, y)
            if 0 <= a < board.Width + board.Cushion and 0 <= b < board.Height + board.Cushion:
                kill = None
                if len(turn[1]) < self.Players[player_no - 1].SpareTurns and not (held_down["mouse0"] or held_down["mouse2"]):
                    if pygame.mouse.get_pressed()[0] and self.check_turn_is_valid(board, turn, player_no, a, b, False):
                        kill = False
                    elif pygame.mouse.get_pressed()[2] and self.check_turn_is_valid(board, turn, player_no, a, b, True):
                        kill = True
                if kill is not None:
                    turn[1].append([a, b, kill])
                    turns_used[player_no - 1] += 1
            if pygame.key.get_pressed()[pygame.K_SPACE] and not held_down["space"]:
                turn_chosen = True
            if pygame.key.get_pressed()[pygame.K_f] and not held_down["f"]:
                show_future = not show_future
                show_alive_for = False
            if pygame.key.get_pressed()[pygame.K_j] and not held_down["j"]:
                show_alive_for = not show_alive_for
                show_future = False
            on_button = [False, False]
            if 2 * self.ButtonBorderSize < screen.get_width() - x < self.RightColumnSize - 2 * self.ButtonBorderSize:
                if 0 < screen.get_height() - y - self.ButtonBorderSize < self.ButtonHeight:
                    if pygame.mouse.get_pressed()[0] and not held_down["mouse0"]:
                        turn_chosen = True
                    on_button[0] = True
                elif 0 > y - screen.get_height() + 3 * self.ButtonBorderSize + self.ButtonHeight > -self.ButtonHeight:
                    if pygame.mouse.get_pressed()[0] and turn[0] is None:
                        turn[0] = len(turn[1])
                    on_button[1] = True
            
            self.draw_right_column(screen, self.get_player_scores(board, turns=turn, player_no=player_no), on_button,
                                   turns_used, not turn[0] is None, update=False)
            if show_alive_for:
                board.show_alive(screen, self.TextSize,self.Colour)
            else:
                board.show_future(screen, turn, player_no, smaller=show_future)
            held_down["mouse0"] = pygame.mouse.get_pressed()[0]
            held_down["mouse2"] = pygame.mouse.get_pressed()[2]
            held_down["space"] = pygame.key.get_pressed()[pygame.K_SPACE]
            held_down["f"] = pygame.key.get_pressed()[pygame.K_f]
            held_down["j"] = pygame.key.get_pressed()[pygame.K_j]
            pygame.display.update()
        return turn
    
    @staticmethod
    def check_turn_is_valid(board, turns, player_no, a, b, kill):
        temp_board = copy.deepcopy(board)
        temp_board.impose_turns(turns, player_no)
        if temp_board.Cell[a][b].CurrentPlayer == player_no:
            return kill
        elif temp_board.Cell[a][b].CurrentState == Dead:
            return not kill
        else:
            if temp_board.Cell[a][b].FullImmune:
                return False
            else:
                return kill
    
    def get_player_scores(self, board, turns=None, player_no=0):
        player_scores = [0 for _ in range(self.NoOfPlayers + 1)]
        if turns is None:
            for a in range(self.Width):
                for b in range(self.Height):
                    player_scores[board.Cell[a][b].CurrentPlayer] += 1
        else:
            temp_board = copy.deepcopy(board)
            temp_board.impose_turns(turns, player_no)
            for a in range(self.Width):
                for b in range(self.Height):
                    player_scores[temp_board.Cell[a][b].CurrentPlayer] += 1
        return player_scores
    
    def draw_right_column(self, screen, player_scores, on_button, turns_used, generated, clickable=None, update=True):
        pygame.draw.rect(screen, self.Colour["Background"], (screen.get_width() - self.RightColumnSize, 0,
                                                             self.RightColumnSize, screen.get_height()))
        
        write(screen, screen.get_width() - self.RightColumnSize // 2, self.ButtonBorderSize,
              self.PlayerNames[self.CurrentPlayer - 1] + "'s turn", self.Colour["Player" + str(self.CurrentPlayer)],
              self.TextSize, max_len=self.RightColumnSize, alignment=("centre", "top"))
        button_centres = [[screen.get_width() - self.RightColumnSize // 2,
                           screen.get_height() - 2 * self.ButtonBorderSize - self.ButtonHeight // 2
                           - a * (self.ButtonHeight + 2 * self.ButtonBorderSize)] for a in range(2)]
        for a in range(2):
            pygame.draw.rect(screen, self.Colour["ButtonBorder"],
                             (button_centres[a][0] - self.RightColumnSize // 2 + self.ButtonBorderSize,
                              button_centres[a][1] - self.ButtonHeight // 2 + self.ButtonBorderSize,
                              self.RightColumnSize - 2 * self.ButtonBorderSize, self.ButtonHeight))
            pygame.draw.rect(screen, self.Colour["Background"],
                             (button_centres[a][0] - self.RightColumnSize // 2 + 2 * self.ButtonBorderSize,
                              button_centres[a][1] - self.ButtonHeight // 2 + 2 * self.ButtonBorderSize,
                              self.RightColumnSize - 4 * self.ButtonBorderSize,
                              self.ButtonHeight - self.ButtonBorderSize - 2))
        if clickable is None:
            button_colours = [self.Colour["Text"] for _ in range(2)]
            if on_button[0]:
                button_colours[0] = self.Colour["Highlighter"]
            if generated:
                button_colours[1] = self.Colour["Unselectable"]
            else:
                if on_button[1]:
                    button_colours[1] = self.Colour["Highlighter"]
        else:
            button_colours = [self.Colour["Unselectable"] for _ in range(2)]
            
        button_text = ("End Turn", "Generate")
        for a in range(2):
            write(screen, button_centres[a][0], button_centres[a][1], button_text[a], button_colours[a], self.TextSize,
                  max_len=self.RightColumnSize, alignment=("centre", "centre"))
        bottom = (screen.get_width() - self.RightColumnSize + self.ButtonBorderSize,
                  button_centres[-1][1] - self.ButtonBorderSize - self.ButtonHeight // 2)
        extra_space = 0
        for n in [self.NoOfPlayers - a - 1 for a in range(self.NoOfPlayers)]:
            col = self.Players[n].Colour
            extra_space += 4 * self.ButtonBorderSize
            extra_space += write(screen, bottom[0], bottom[1] - extra_space,
                                 "Spare Turns: " + str(self.Players[n].SpareTurns - turns_used[n]),
                                 col, int(self.TextSize / 1.5), alignment=("left", "bottom")) + 2 * self.ButtonBorderSize
            extra_space += write(screen, bottom[0], bottom[1] - extra_space, "Cells: " + str(player_scores[n + 1]), col,
                                 int(self.TextSize / 1.5), alignment=("left", "bottom")) + 2 * self.ButtonBorderSize
            extra_space += write(screen, bottom[0], bottom[1] - extra_space, self.PlayerNames[n], col,
                                 int(self.TextSize / 1.2),
                                 max_len=self.RightColumnSize - 2 * self.ButtonBorderSize, alignment=("left", "bottom"))
        if update:
            pygame.display.update()
    
    def check_for_wins(self, board, turns, generations):
        player_scores = self.get_player_scores(board)
        del player_scores[0]
        for a in range(len(player_scores)):
            if self.BoardAmountWin and player_scores[a] > self.Height * self.Width * self.BoardAmount:
                return "Board Amount Passed", a + 1
            for b in range(len(player_scores)):
                if self.IsTurnLimit and turns >= self.TurnLimit:
                    return "Turn Limit Reached", player_scores.index(max(player_scores)) + 1
                if self.IsGenLimit and generations >= self.GenLimit:
                    return "Generation Limit Reached", player_scores.index(max(player_scores)) + 1
                if self.PlayerAmountWin and player_scores[a] * self.PlayerAmount > player_scores[b]:
                    return "Score Difference Passed", a + 1
                

class Help:
    def __init__(self):
        self.SectionGapSize = config.H_SectionGapSize
        self.TextSize = config.H_TextSize
        self.TitleSize = config.H_TitleSize
        self.IndentSize = config.H_IndentSize
        self.SliderWidth = config.H_SliderWidth
        self.SliderGapSize = config.H_SliderGapSize
        self.SliderLength = config.H_SliderLength
        self.Width = config.H_Width
        self.Height = 600  # gets changed in the program depending on space taken up by help
        self.ScrollAmount = config.H_ScrollAmount
        self.Colour = config.H_Colour
        self.Surfaces = self.get_surfaces()
    
    def display(self, screen):
        pygame.display.set_caption("Game of Life - Help")
        pygame.display.set_mode((self.Width, self.Surfaces[0].get_height()))
        screen.fill(self.Colour["Background"])
        self.Height = screen.get_height()
        slider_range = (self.SliderGapSize + self.SliderLength // 2, self.Height - self.SliderGapSize - self.SliderLength // 2)
        slider_centre = slider_range[0]
        help_rect = self.Surfaces[0].get_rect()
        help_rect.topleft = (self.SectionGapSize, self.SectionGapSize)
        screen.blit(self.Surfaces[0], help_rect)
        self.draw(screen, self.Surfaces[1], slider_centre, slider_range)
        slider_last_turn = False
        while True:
            events = pygame.event.get()
            if check_quit(events):
                break
            x, y = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:
                if not slider_last_turn and -2 * self.SliderGapSize - self.SliderWidth < x - self.Width < 0:
                    slider_last_turn = True
                    mouse_start = y
                    if not slider_centre - self.SliderLength / 2 < y < slider_centre + self.SliderLength / 2:
                        slider_centre = y
                if slider_last_turn:
                    if slider_centre + y - mouse_start < slider_range[0]:
                        y = slider_range[0] + mouse_start - slider_centre
                    elif slider_centre + y - mouse_start > slider_range[1]:
                        y = slider_range[1] + mouse_start - slider_centre
                    self.draw(screen, self.Surfaces[1], slider_centre + y - mouse_start, slider_range)
            else:
                if slider_last_turn:
                    slider_last_turn = False
                    slider_centre += y - mouse_start
            if x > (self.Width - self.SliderWidth - self.SectionGapSize) / 2 - self.SliderGapSize:
                for e in events:
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        draw = False
                        if e.button == 4:
                            slider_centre -= self.ScrollAmount
                            slider_centre = max(slider_centre, slider_range[0])
                            draw = True
                        if e.button == 5:
                            slider_centre += self.ScrollAmount
                            slider_centre = min(slider_centre, slider_range[1])
                            draw = True
                        if draw:
                            self.draw(screen, self.Surfaces[1], slider_centre, slider_range)
            
            pygame.display.update()
    
    def draw(self, screen, help_surface, slider_centre, slider_range):
        pygame.draw.rect(screen, self.Colour["Background"],
                         ((self.Width - self.SliderWidth - self.SectionGapSize) // 2 - self.SliderGapSize, 0,
                          self.Width, self.Height))
        pygame.draw.rect(screen, self.Colour["Slider"],
                         (self.Width - self.SliderGapSize - self.SliderWidth, slider_centre - self.SliderLength // 2,
                          self.SliderWidth, self.SliderLength))
        help_rect = help_surface.get_rect()
        text_range = (self.SectionGapSize, help_surface.get_height() - self.Height + 2 * self.SectionGapSize)
        top_y = text_range[0] - (text_range[1] - text_range[0]) * (slider_centre - slider_range[0]) // (slider_range[1]
                                                                                                        - slider_range[0])
        help_rect.topleft = (int((self.Width - self.SliderWidth) // 2) + self.SliderGapSize, top_y)
        screen.blit(help_surface, help_rect)
        pygame.display.update()
    
    def get_surfaces(self):
        text = open("help.txt").read().split("++")
        for section in range(len(text)):
            text[section] = text[section].split("\n")
        help_surfaces = []
        
        for section in text:
            extra = 0
            for _ in range(2):
                help_surface = pygame.Surface(((self.Width - self.SliderWidth)
                                               // 2 - self.SectionGapSize - self.SliderGapSize, extra))
                help_surface.fill(self.Colour["Background"])
                extra = 0
                for line in section:
                    if line.startswith("**"):
                        size = self.TitleSize
                        line = line[2:]
                    else:
                        size = self.TextSize
                    indent = 0
                    while line.startswith("--"):
                        indent += 1
                        line = line[2:]
                    extra += write(help_surface, indent * self.IndentSize, extra, line, self.Colour["Text"], size,
                                   max_len=help_surface.get_width() - indent * self.IndentSize) + self.SectionGapSize
            help_surfaces.append(help_surface)
        return help_surfaces


def write(screen, x, y, text, colour, size, max_len=None, gap=0, font=Font, rotate=0, alignment=("left", "top")):
    """Puts text onto the screen at point x,y. the alignment variable, if used, can take first value \"left\",
    \"centre\" or \"right\" and the second value can be \"top\", \"centre\" or \"bottom\".
    note that these values relate to x and y respectively whatever the rotation, which is in degrees.
    max_len allows you to wrap a line if it becomes too long; the text will be restricted to being that many pixels long,
    and if it gets longer a new line will be started"""
    font_obj = pygame.font.SysFont(font, size)
    if text == "":
        line = 1
        extra_space = size
    else:
        line = 0
        extra_space = 0
    while len(text.split()) > 0:
        line += 1
        msg_surface_obj = pygame.transform.rotate(font_obj.render(text, False, colour), rotate)
        used = len(text.split())
        while max_len is not None and msg_surface_obj.get_width() > max_len:
            used -= 1
            msg_surface_obj = pygame.transform.rotate(font_obj.render(" ".join(text.split()[:used]), False, colour), rotate)
        msg_rect_obj = msg_surface_obj.get_rect()
        a, b = msg_surface_obj.get_size()
        if alignment[0] == "centre":
            new_x = x - a // 2
        elif alignment[0] == "right":
            new_x = x - a
        else:
            new_x = x
        if alignment[1] == "centre":
            new_y = y - b // 2
        elif alignment[1] == "bottom":
            new_y = y - b
        else:
            new_y = y
        msg_rect_obj.topleft = (new_x, new_y)
        screen.blit(msg_surface_obj, msg_rect_obj)
        y += msg_surface_obj.get_height() + gap
        extra_space += msg_surface_obj.get_height() + gap
        text = " ".join(text.split()[used:])
    return extra_space


def check_quit(events):
    for event in events:
        if event.type == pygame.QUIT:
            quit_game()
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            return True
    return False


def quit_game():
    pygame.quit()
    import sys
    sys.exit(0)
