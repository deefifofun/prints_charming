
import sys
import termios
import tty
import os
import random
import asyncio
import time
from threading import Thread

from prints_charming import (
    PStyle,
    PrintsCharming,
    FrameBuilder,
    TableManager,
    BoundCell,
)

snake_styles = {
    'default': PStyle(),
    'snake_head': PStyle(color='orange'),
    'snake_segment': PStyle(color='green', underline=True, overline=True),
    'snake_seg1': PStyle(color='yellow'),
    'snake_seg2': PStyle(color='green'),
    'snake_seg3': PStyle(color='blue'),
    'snake_seg4': PStyle(color='indigo'),
    'snake_seg5': PStyle(color='purple'),
    'snake_seg6': PStyle(color='red'),
    'snake_seg7': PStyle(color='orange'),

    'food': PStyle(color='vgreen', bold=True),
    'border': PStyle(bg_color='blue'),
    'blank': PStyle(bg_color='black'),
    'frame': PStyle(color='white', bold=True),
    'title': PStyle(color='cyan', bold=True),
    'score': PStyle(color='yellow', bold=True),
}


# Snake game implementation
class SnakeGame:
    def __init__(self, prints_charming_instance=None, builder_instance=None, table_manager_instance=None, alt_buffer=True, snake_segment=None, snake_head=None, food_segment=None, body_pattern=None, reverse_pattern=False):
        self.pc = prints_charming_instance or PrintsCharming(styles=snake_styles)
        self.apply_style = self.pc.apply_style
        self.ctl = self.pc.ctl_map
        self.unicode = self.pc.unicode_map
        self.write = self.pc.write
        self.builder = builder_instance or FrameBuilder(pc=self.pc, horiz_char=' ', vert_char=' ', vert_width=2)
        self.table_manager = table_manager_instance or TableManager(pc=self.pc)
        self.alt_buffer = alt_buffer
        self.width = 50
        self.height = 20
        self.snake = [(self.height // 2, self.width // 2)]

        self.snake_segment = (
            self.unicode.get(snake_segment, snake_segment)
            or self.unicode.get('half_block', ' ')
        )

        self.styled_snake_segment = self.apply_style('snake_segment', self.snake_segment)

        if snake_head:
            self.snake_head = self.apply_style('snake_head', snake_head)
        else:
            self.snake_head = self.styled_snake_segment

        self.food_segment = (
            self.apply_style(
                'food',
                self.unicode.get(food_segment, food_segment)
                or self.unicode.get('bitcoin', ' ')
            )
        )

        # Body segment pattern and reversal behavior
        self.use_default_body_style = body_pattern is None  # Use default if no pattern provided
        if not self.use_default_body_style:
            self.body_pattern = [self.apply_style(style_name, self.snake_segment) for style_name in body_pattern]
        self.reverse_pattern = reverse_pattern

        self.direction = 'RIGHT'
        self.food = None
        self.food_needs_update = True  # Initial flag for first food draw

        self.level = 1
        self.level_speeds = [0.15, 0.1, 0.08, 0.05]  # Speeds for each level (lower is faster)
        self.level_thresholds = [5, 15, 30, 50]  # Score thresholds for each level
        self.current_speed = self.level_speeds[0]  # Initial speed for level 1
        self.score = 0
        self.game_over = False

        # BoundCells for snake and food positions
        self.snake_cells = [BoundCell(lambda pos=segment: pos) for segment in self.snake]
        self.food_cell = BoundCell(lambda: self.food)


    
    async def init_game(self):
        if self.alt_buffer:
            self.write('alt_buffer', 'cursor_home', 'hide_cursor')

        # Draw border once at the start of the game
        self.draw_border(self.width, self.height)

        self.place_food()
        await self.init_keyboard_listener()


    def place_food(self):
        while True:
            position = (random.randint(1, self.height - 2), random.randint(1, self.width - 2))
            if position not in self.snake:
                self.food = position
                self.food_needs_update = True
                break

    async def init_keyboard_listener(self):
        # Start the keyboard listener as a background task
        asyncio.create_task(self.keyboard_listener())


    async def keyboard_listener(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        try:
            while not self.game_over:
                key = await asyncio.to_thread(sys.stdin.read, 1)  # Non-blocking read
                if key == self.ctl['meta']:
                    key += await asyncio.to_thread(sys.stdin.read, 2)  # Additional byte read for meta keys
                if key == self.ctl['arrow_up'] and self.direction != 'DOWN':
                    self.direction = 'UP'
                elif key == self.ctl['arrow_down'] and self.direction != 'UP':
                    self.direction = 'DOWN'
                elif key == self.ctl['arrow_right'] and self.direction != 'LEFT':
                    self.direction = 'RIGHT'
                elif key == self.ctl['arrow_left'] and self.direction != 'RIGHT':
                    self.direction = 'LEFT'
                elif key == 'q':
                    self.game_over = True
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


    def increase_level(self):
        #Check if the score meets the next threshold and increase the level if so.
        if self.level < len(self.level_thresholds) and self.score >= self.level_thresholds[self.level - 1]:
            self.level += 1
            self.current_speed = self.level_speeds[self.level - 1]
            print(f"Level Up! Reached Level {self.level}, Speed increased!")


    async def update_snake(self):
        while not self.game_over:
            head = self.snake[0]

            # Determine the new head position based on direction
            if self.direction == 'UP':
                new_head = (head[0] - 1, head[1])
            elif self.direction == 'DOWN':
                new_head = (head[0] + 1, head[1])
            elif self.direction == 'LEFT':
                new_head = (head[0], head[1] - 1)
            elif self.direction == 'RIGHT':
                new_head = (head[0], head[1] + 1)

            # Check for collisions with the wall or self
            if (new_head[0] <= 0 or new_head[0] >= self.height - 1 or
                new_head[1] <= 0 or new_head[1] >= self.width - 1 or
                new_head in self.snake):
                self.game_over = True
                return

            # Insert the new head position
            self.snake.insert(0, new_head)

            # Check if the snake has eaten the food
            if new_head == self.food:
                self.score += 1
                self.place_food()
                self.increase_level()  # Check if a level-up is required

            else:
                # Remove the tail segment if no food is eaten
                tail = self.snake.pop()

                # Clear the position of the last segment
                self.write('cursor_position', ' ', row=tail[0] + 1, col=tail[1] + 1)

            # Brief pause to control the speed of the game
            await asyncio.sleep(self.current_speed)

    
    def draw_border(self, width, height):
        horiz_line = self.pc.apply_style('border', self.builder.horiz_char * width)
        # Top border
        print(horiz_line)
        # Side borders
        for _ in range(height - 2):
            line = self.pc.apply_style('border', self.builder.vert_char)
            line += self.pc.apply_style('default', ' ' * (width - 2))
            line += self.pc.apply_style('border', self.builder.vert_char)
            print(line)
        # Bottom border
        print(horiz_line)


    def get_body_style(self, index):
        # Return the style for the body segment at the given index based on the pattern and reversal settings.
        pattern_length = len(self.body_pattern)

        if self.reverse_pattern:
            # Calculate the index in the pattern considering reversal
            cycle = index // pattern_length  # Number of completed pattern cycles
            position_in_cycle = index % pattern_length

            if cycle % 2 == 0:  # Forward cycle
                return self.body_pattern[position_in_cycle]
            else:  # Reverse cycle
                return self.body_pattern[pattern_length - 1 - position_in_cycle]
        else:
            # Regular repetition from the start
            return self.body_pattern[index % pattern_length]


    async def draw(self):
        while not self.game_over:

            # Draw each body segment with the appropriate style
            for i, segment in enumerate(self.snake[1:]):  # Skip the head (first element)
                if self.use_default_body_style:
                    # Use default snake segment style
                    snake_segment = self.styled_snake_segment
                else:
                    # Use styled segment from body_pattern
                    snake_segment = self.get_body_style(i)

                self.write('cursor_position', snake_segment, row=segment[0] + 1, col=segment[1] + 1)

            # Draw snake head as the last item to ensure it's visible
            head = self.snake[0]
            self.write('cursor_position', self.snake_head, row=head[0] + 1, col=head[1] + 1)

            # Draw food only if it has moved
            if self.food_needs_update:
                self.write('cursor_position', self.food_segment, row=self.food[0]+1, col=self.food[1]+1)
                self.food_needs_update = False

            # Draw score
            self.write('cursor_position', row=self.height+1, col=1)
            self.write(f'Level: {self.level}\n')
            self.write(f'Score: {self.score}\n')
            await asyncio.sleep(0.05)


    async def game_loop(self):
        try:
            await asyncio.gather(self.update_snake(), self.draw())
        except asyncio.CancelledError:
            self.game_over = True
        except KeyboardInterrupt:
            self.game_over = True


    async def run(self):
        await self.init_game()
        await self.game_loop()
        self.end_game()


    def end_game(self):
        # Game over screen
        print("Game Over!")
        print(f"Your score: {self.score}")
        time.sleep(3)
        self.write("clear_screen", "cursor_home", "show_cursor")

        if self.alt_buffer:
            self.write('normal_buffer')




if __name__ == "__main__":
    pc = PrintsCharming(styles=snake_styles)
    pattern = ['snake_seg1', 'snake_seg2', 'snake_seg3', 'snake_seg4', 'snake_seg5', 'snake_seg6', 'snake_seg7']
    game = SnakeGame(prints_charming_instance=pc, snake_head=pc.unicode_map.get('medium_block', ' '), body_pattern=pattern, reverse_pattern=True)
    try:
        asyncio.run(game.run())
    except KeyboardInterrupt:
        game.game_over = True  # Signal to end the game
        print("Exiting game due to KeyboardInterrupt.")


