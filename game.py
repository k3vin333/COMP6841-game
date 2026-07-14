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

# Starting meter values that reflect an authorized professional which is the player
# Four meters = higher is better, two which are risk, cia = higher is worse
STARTING_METERS = {
    # actions stay authorized
    "scope": 100,
    # findings documented so far
    "evidence": 0,
    # privacy and professional conduct
    "ethics": 100,
    # operational danger accumulated (higher = worse)
    "risk": 0,
    # client confidence
    "trust": 100,
    # damage caused to target systems (higher = worse)
    "cia": 0
}

# Meters run on a fixed scale so scoring can stay predictable
METER_MIN = 0
METER_MAX = 100

# After reviewing the levels and game design, i think its best to keep levels as a
# constant list of dictionaries, each containing a map and a starting position for the player. 
# That way we can expand game easily to list without change much
LEVELS = [
    {
        # Level 1: outside the building in the CBD - a simple street with trees
        "map": [
            "████████████████████████████████████████",
            "█░░██░░██░░██░░██░░██░░██░░██░░██░░██░██",
            "████████████████████████████████████████",
            "█·♣·♣·♣·♣·♣·♣·♣·♣·♣··♣·♣·♣·♣·♣·♣·♣·♣·♣·█",
            "█······································█",
            "█······································█",
            "█·♣··································♣·█",
            "█···████████████████▒███████████████···█",
            "█···█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█···█",
            "█···█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█···█",
            "█···█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█···█",
            "█···█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█···█",
            "█···████████████████████████████████···█",
            "████████████████████████████████████████",
        ],
        "start": (4, 2),
    },
    {
        # Level 2: the building lobby - front desk (☻) and an inner door deeper in
        "map": [
            "██████████████████████████████",
            "█····························█",
            "█····························█",
            "█·········☻··················█",
            "█····························█",
            "█····························█",
            "█····························█",
            "█····························█",
            "█····························█",
            "█·············▒··············█",
            "██████████████████████████████",
        ],
        "start": (1, 15),
    },
]

# HACKERMAN title banner (block style) shown on the start screen
TITLE_ART = [
    "██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ ███╗   ███╗ █████╗ ███╗   ██╗",
    "██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗████╗ ████║██╔══██╗████╗  ██║",
    "███████║███████║██║     █████╔╝ █████╗  ██████╔╝██╔████╔██║███████║██╔██╗ ██║",
    "██╔══██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══██║██║╚██╗██║",
    "██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║██║ ╚═╝ ██║██║  ██║██║ ╚████║",
    "╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝",
]


class Game:
    def __init__(self):
        """Set up persistent game state (meters, tick), then load the first level."""
        self.running = True
        self.level_complete = False
        # dict() copies so choices mutate this game's meters, not the shared constant
        self.meters = dict(STARTING_METERS)
        # counts every player action - visible evidence of gameplay
        self.tick_count = 0
        # meters and tick persist across levels, only the map + player position swap
        self.current_level = 0
        self.load_level(self.current_level)

    def load_level(self, index):
        """Swap in a level's map and player start. Meters and tick persist across levels."""
        level = LEVELS[index]
        self.current_level = index
        # fresh 2D copy so opening doors/editing tiles never change the LEVELS constant
        self.map = [list(row) for row in level["map"]]
        self.player_row, self.player_col = level["start"]

    def modify_meter(self, name, delta):
        """Apply a change to a meter, clamped to the [0, 100] range."""
        current = self.meters[name]
        # max/min pair clamps: never below MIN, never above MAX
        self.meters[name] = max(METER_MIN, min(METER_MAX, current + delta))

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

        # Action counter below the controls hint
        tick_row = status_row + 1
        if tick_row < max_rows:
            try:
                stdscr.addstr(tick_row, 0, f"TICK: {self.tick_count}")
            except curses.error:
                pass

        # Meters panel below the tick counter
        meter_start_row = status_row + 3
        # enumerate gives each meter its own row so they stack vertically
        for offset, (name, value) in enumerate(self.meters.items()):
            meter_row = meter_start_row + offset
            if meter_row >= max_rows:
                break
            try:
                # upper() and :>3 keep the labels and numbers aligned in a column
                stdscr.addstr(meter_row, 0, f"{name.upper():<10} {value:>3}")
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

            # Level advancement logic: Stepping on a door advances to the next level, or ends the game after the last
            if target_tile == DOOR:
                if self.current_level + 1 < len(LEVELS):
                    self.load_level(self.current_level + 1)
                else:
                    self.level_complete = True
                    self.running = False


def main(stdscr):
    """Initialise curses settings and run the game loop."""
    # Hide cursor
    curses.curs_set(0)
    # stdscr.keypad to enable arrow key detection
    stdscr.keypad(True)

    # Title screen: draw banner then wait for a keypress
    stdscr.clear()
    try:
        stdscr.addstr("\n".join(TITLE_ART) + "\n\nPress any key to begin...")
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()

    game = Game()

    while game.running:
        game.render(stdscr)
        direction = game.handle_input(stdscr)
        game.update(direction)
        # one loop pass = one action processed, so increment the counter
        game.tick_count += 1

    # Show completion message once the final level's door is reached
    if game.level_complete:
        stdscr.clear()
        stdscr.addstr(5, 10, "Assessment complete.")
        stdscr.addstr(7, 10, "Press any key to exit.")
        stdscr.refresh()
        stdscr.getch()


# Enable Unicode support before curses takes over the terminal
if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
