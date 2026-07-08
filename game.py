import curses
import locale

# Tile definitions
# initially start with ASCII but then realized
# I could use Unicode characters to make the game look nicer
WALL = '█'
FLOOR = '·'
PLAYER = '□'
DOOR = '▒'
NPC = '☻'
ITEM = '◆'

# Set of tiles the player is allowed to walk on
WALKABLE = {FLOOR, DOOR}


class Game:
    def __init__(self):
        # Map defined as strings for readability, converted to 2D list so tiles can be modified at runtime
        raw_map = [
            "████████████████████",
            "█······█···········█",
            "█······█···········█",
            "█······█···········█",
            "█······▒···········█",
            "█······█···········█",
            "█······█···········█",
            "████████████▒███████",
            "█··················█",
            "█··················█",
            "█··················█",
            "████████████████████",
        ]
        self.map = [list(row) for row in raw_map]
        self.player_row = 1
        self.player_col = 1
        self.running = True

    def render(self, stdscr):
        # Redraw the entire map each frame
        stdscr.clear()

        for row_index, row in enumerate(self.map):
            for col_index, tile in enumerate(row):
                if row_index == self.player_row and col_index == self.player_col:
                    stdscr.addstr(row_index, col_index, PLAYER)
                else:
                    stdscr.addstr(row_index, col_index, tile)

        # Status bar below the map
        status_row = len(self.map) + 1
        stdscr.addstr(status_row, 0, "WASD or Arrow Keys to move | Q to quit")

        stdscr.refresh()

    def handle_input(self, stdscr):
        # getch() blocks until a key is pressed, returns the key code
        key = stdscr.getch()

        if key in (ord('w'), curses.KEY_UP):
            return (-1, 0)
        elif key in (ord('s'), curses.KEY_DOWN):
            return (1, 0)
        elif key in (ord('a'), curses.KEY_LEFT):
            return (0, -1)
        elif key in (ord('d'), curses.KEY_RIGHT):
            return (0, 1)
        elif key == ord('q'):
            self.running = False

        return (0, 0)

    def update(self, direction):
        new_row = self.player_row + direction[0]
        new_col = self.player_col + direction[1]

        # Wall borders mean we never go out of bounds, so only need the walkable check
        if self.map[new_row][new_col] in WALKABLE:
            self.player_row = new_row
            self.player_col = new_col


def main(stdscr):
    # hide the blinking cursor
    curses.curs_set(0)
    # stdscr.keypad to enable arrow key detection
    stdscr.keypad(True)

    game = Game()

    while game.running:
        game.render(stdscr)
        direction = game.handle_input(stdscr)
        game.update(direction)


# Enable Unicode support before curses takes over the terminal
locale.setlocale(locale.LC_ALL, '')
curses.wrapper(main)
