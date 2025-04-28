
import shutil
import random
import curses


class HangmanGame():
    def __init__(self):
        self.tree = r"""
             ooOOOoo
         oOOoOoOooOo oOoo
        oOOoOOOOOoOOooooOOoO
        oooOOOOOO oOo oOOooOOOo
            OOooO  /o o oOOoooO
            \\\//  /oooOO
                \\\////
                ||/\
                ||\/
                ||||
        ......//|||\....
        """
        self.word = random.choice([
            "apple", "banana", "orange", "giraffe", "bicycle", "elephant", "mountain", "python", 
            "rainbow", "sandwich", "adventure", "butterfly", "galaxy", "dolphin", "sunflower", 
            "treasure", "volcano", "diamond", "chocolate", "notebook", "computer", "mermaid", 
            "penguin", "monster", "jungle", "firework", "cucumber", "sunshine", "waterfall", 
            "popcorn", "mystery", "airplane", "backpack", "koala", "hedgehog", "unicorn", 
            "marshmallow", "blizzard", "snowflake", "pumpkin", "cinnamon", "pillow", "necklace", 
            "lantern", "watermelon", "skyscraper", "adventure", "playground", "dragonfly", 
            "telescope", "parachute", "moonlight", "kangaroo", "lighthouse", "stardust", 
            "seahorse", "chocolate", "grapefruit", "raspberry", "thunderstorm", "raindrop", 
            "chocolate", "pomegranate", "sapphire", "buttercup", "meadow", "honeybee", "starfish", 
            "whisper", "sapphire", "cinnamon", "snowman", "mermaid", "lavender", "sunbeam", 
            "blossom", "chandelier", "lighthouse", "mushroom", "raindrop", "skylight", 
            "jellyfish", "snapdragon", "crocodile", "seahorse", "lighthouse", "blackberry", 
            "hummingbird", "waterfall", "dragon", "stardust", "treasure", "bumblebee", 
            "stargazer", "raindrop", "twilight", "raspberry", "whirlwind", "sunshine", "carousel"
        ])
        self.progress = ['_' for _ in range(len(self.word))]
        self.wrong_guesses = []
        self.running = True

    def ensure_term_size(self):
        width, height = shutil.get_terminal_size()
        if height < 15:
            input(f'\033[2J \033[HTerminal not tall enough ({height} -> 15). Adjust and hit enter.')
            self.ensure_term_size()
        elif width < 35:
            input(f'\033[2J \033[HTerminal not wide enough ({width} -> 35). Adjust and hit enter.')
            self.ensure_term_size()

    def wither_tree(self):
        # Adjust probability based on the length of the word
        word_length = len(self.word)
        base_prob = 0.2  # Base probability for withering
        scaling_factor = max(1, word_length / 10)  # Normalize longer words
        prob = base_prob / scaling_factor  # Adjusted probability
        
        new_chars = []
        indices_to_wither = []
        
        # Iterate over the tree characters
        for i, char in enumerate(self.tree):
            r = random.random()
            if char in ['O', 'o'] and r < prob:
                # Mark this index for guaranteed withering
                indices_to_wither.append(i)
                new_chars.append(' ' if char == 'o' else ('\\' if r < prob / 2 else '/'))
            else:
                new_chars.append(char)

        # Guarantee at least one character is withered
        if not indices_to_wither:
            # Find all witherable characters and randomly pick one to wither
            witherable_indices = [i for i, char in enumerate(self.tree) if char in ['O', 'o']]
            if witherable_indices:
                index_to_wither = random.choice(witherable_indices)
                indices_to_wither.append(index_to_wither)
                new_chars[index_to_wither] = (
                    ' ' if self.tree[index_to_wither] == 'o' else random.choice(['\\', '/'])
                )
        
        self.tree = ''.join(new_chars)
        if not set(new_chars) & {'O', 'o'}:
            self.running = False

    def get_guess(self):
        
        selected_index = 0
        guess = None

        while not guess:
            # print('\033[2J \033[H')
            # print('\r')
            for idx, char in enumerate(self.progress):
                if idx == selected_index:
                    print('\033[32m', end='')
                print(char, end='\033[0m')
            
            stdscr = curses.initscr()
            key = stdscr.getch()
            if key == 260:
                if selected_index > 0:
                    selected_index -= 1
            elif key == 261:
                if selected_index < len(self.word):
                    selected_index += 1
            elif 32 <= key <= 126:
                if chr(key).isalpha():
                    guess = chr(key)
            curses.endwin()
                 
                 
                 
                 
        correct = False
        for i, char in enumerate(self.word):
            if char == guess:
                correct = True
                self.progress[i] = guess
        
        if not correct and guess not in self.wrong_guesses:
            self.wrong_guesses.append(guess)
            self.wither_tree()
            
        elif '_' not in self.progress:
            self.running = False
        
        print('\n\n')
        
        
    # def display(self):
        
    #     print('\033[2J \033[H')
        
    #     self.ensure_term_size()
    #     print(self.tree)
        
    #     print('\033[31m')
    #     print(' '. join(self.wrong_guesses))
    #     print('\033[0m')
        
    def loop(self):
        print('\033[?25l')
        while self.running:
            # self.display()
            self.get_guess()
        print('\033[?25h')
        

        



game = HangmanGame()
print(game.tree)

# game.loop()




#     try:
#         while True:
#             key = stdscr.getch()  # Capture key press

#             if key == -1:  # No key was pressed, continue
#                 continue

#             if key == 27:  # Escape key to break the loop
#                 break

#             # Print the key name on the screen
#             stdscr.addstr(0, 0, f"Key pressed: {curses.keyname(key)}\n")
#             stdscr.refresh()  # Refresh to show the updated screen

#     finally:
#         # Clean up curses settings
#         curses.endwin()




