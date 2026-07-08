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
WINDOW = '░'
TREE= '♣'

# Set of tiles the player is allowed to walk on
WALKABLE = {FLOOR, DOOR}


class Game:
    def __init__(self):
        """Set up the game state by load the map, placeing the player, and initialising flags."""
        # this is level 1, outside the building in the CBD for example. Just simple street with few trees for now
        # may come back and redesign this level, but TODO: is make a few more levels (at least 5)
        raw_map = [
            "████████████████████████████████████████",
            "█░░██░░██░░██░░██░░██░░██░░██░░██░░██░██",
            "████████████████████████████████████████",
            "█·♣··································♣·█",
            "█······································█",
            "█······································█",
            "█·♣··································♣·█",
            "█···████████████████▒███████████████···█",
            "█···█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█···█",
            "█···█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█···█",
            "█···████████████████████████████████···█",
            "█······································█",
            "█······································█",
            "████████████████████████████████████████",
        ]
        self.map = [list(row) for row in raw_map]
        # Player starts on the road, approaching from the west
        self.player_row = 4
        self.player_col = 2
        self.running = True
        self.level_complete = False

    def render(self, stdscr):
        """Draw the map and player to the terminal."""
        stdscr.clear()
        max_rows, max_cols = stdscr.getmaxyx()

        for row_index, row in enumerate(self.map):
            if row_index >= max_rows:
                break
            for col_index, tile in enumerate(row):
                if col_index >= max_cols - 1:
                    break
                try:
                    if row_index == self.player_row and col_index == self.player_col:
                        stdscr.addstr(row_index, col_index, PLAYER)
                    else:
                        stdscr.addstr(row_index, col_index, tile)
                except curses.error:
                    pass

        # Controls hint below the map
        status_row = len(self.map) + 1
        if status_row < max_rows:
            try:
                stdscr.addstr(status_row, 0, "WASD or Arrow Keys to move | Q to quit")
            except curses.error:
                pass

        stdscr.refresh()

    def handle_input(self, stdscr):
        """Wait for a keypress and return a (row, col) direction tuple."""
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
        """Move the player if the target tile is walkable, and trigger door transitions"""
        new_row = self.player_row + direction[0]
        new_col = self.player_col + direction[1]

        target_tile = self.map[new_row][new_col]

        # Wall borders mean we never go out of bounds
        if target_tile in WALKABLE:
            self.player_row = new_row
            self.player_col = new_col

            # Stepping on a door triggers the next level
            if target_tile == DOOR:
                self.level_complete = True
                self.running = False


def main(stdscr):
    """Initialise curses settings and run the game loop."""
    # Hide cursor
    curses.curs_set(0)
    # stdscr.keypad to enable arrow key detection
    stdscr.keypad(True)

    game = Game()

    while game.running:
        game.render(stdscr)
        direction = game.handle_input(stdscr)
        game.update(direction)

    # Show transition message when a level is completed
    if game.level_complete:
        stdscr.clear()
        stdscr.addstr(5, 10, "Entering the building...")
        stdscr.addstr(7, 10, "Level 2 coming soon. Press any key to exit.")
        stdscr.refresh()
        stdscr.getch()


# Enable Unicode support before curses takes over the terminal
if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
