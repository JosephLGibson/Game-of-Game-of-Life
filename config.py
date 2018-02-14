Dead = 0
Square = 1
Hex = 2


class Menu:
    """Change these values to change how the main menu looks."""
    
    def __init__(self):
        self.ButtonSize = 50
        self.ButtonBorder = 4
        self.Width = 1000
        self.Height = 650
        self.Colour = {"Border": (255, 255, 255),
                       "Text": (255, 255, 255),
                       "Hover": (0, 255, 100),
                       "Background": (120, 120, 120)}


class Sim:
    """Change these values to change how the game looks in Simulator mode."""
    
    def __init__(self):
        self.Width = 50  # C 50 How many squares wide the board is
        self.Height = 30  # C 30 Ditto but with height
        self.Size = 20  # C 20 The size of the sides of each square (in pixels)
        self.Edge = 2  # C Size / 15 The gap between each cell
        self.Wrap = False  # Whether the board wraps around on itself
        self.Cushion = 10  # C 10 How far the board extends beyond the visible amount
        self.PreviewSize = 0
        
        self.NoOfButtons = 0
        self.ButtonSize = 50
        self.HighlightSize = 5
        self.NoOfNotches = 9
        self.NotchLength = self.ButtonSize / 5
        self.StartOfSlider = 2 * self.NotchLength
        self.EndOfSlider = self.Height * self.Size - self.HighlightSize - self.NotchLength
        self.SpaceBetweenNotches = (self.EndOfSlider - self.StartOfSlider) / (self.NoOfNotches - 1)
        self.ButtonStart = self.Size * self.Width
        self.SliderY = self.Size * self.Width + self.Edge / 2 + self.ButtonSize / 2
        
        self.GPS = 10  # C 10 How many Generations Per Seconds
        self.TopGPS = 100  # The GPS at the top of the slider.
        self.BottomGPS = 0.5  # The GPS at the bottom of slider.
        self.GPSIsLimited = True
        self.Paused = True
        self.OneTurn = False
        self.CanBePaused = True
        self.CanChangeGPSLimit = True
        self.CanGoForward = True
        self.Colour = {"Alive": (0, 0, 0),
                       "Dead": (255, 255, 255),
                       "Highlighter": (0, 255, 100),
                       "Background": (120, 120, 120),
                       "Text": (180, 180, 180),
                       "Unselected": (160, 160, 160)}


class Game:
    """Change these values to change how the game looks in 2-Player mode."""
    
    def __init__(self):
        self.Width = 25  # C 50 How many squares wide the board is
        self.Height = 15  # C 30 Ditto but with height
        self.Size = 35  # C 20 The size of the sides of each square (in pixels)
        self.Edge = 2  # C 2 The gap between each cell
        self.Wrap = True
        self.Cushion = 0
        self.NoOfPlayers = 2  # C How many players there are - 2 or 4
        self.PlayerNames = ["Joe", "Adam"]  # C Player's names
        self.PreviewSize = self.Size // 2
        self.Colour = {"Alive": (0, 0, 0),
                       "Player1": (0, 255, 100),
                       "Player2": (0, 100, 255),
                       "Player3": (100, 255, 0),
                       "Player4": (100, 0, 255),
                       "Dead": (255, 255, 255),
                       "Highlighter": (0, 255, 100),
                       "Background": (120, 120, 120),
                       "Text": (180, 180, 180), }


class Help:
    def __init__(self):
        self.GapSize = 5
        self.TextSize = 17
        self.TitleSize = int(self.TextSize * 1.5)
        self.TextColour = (255, 255, 255)
        self.Background = (120, 120, 120)
        self.Width = 1000
        self.Height = 500
        self.Text = [["Simulator", """
Controls are as follows:
LEFT CLICK to make a Board "alive".
RIGHT CLICK to Kill a cell.
Press SPACE to pause/unpause the game.
Press RIGHT Arrow to move forward a turn when paused.
Press ENTER to clear the board.
Presets (Press the corresponding number to place one):
    1 - Glider
    2 - Small Exploder
    3 - Exploder
    4 - Light Weight Space Ship
    5 - Tumbler
    6 - Gosper Glider Gun
    7 - Pentadecathlon
    8 - r-Pentomino
Press ESC to exit to the main menu."""], ["Game", "\nComing soon..."]]
