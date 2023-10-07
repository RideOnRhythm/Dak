# Connect Four v1.0

import math
from copy import deepcopy
import random
import discord
from discord.ext import commands
import numpy as np
from scipy.signal import convolve2d
from assets.enums import C4PlaceResults
from assets.enums import C4GameResults


# This class replaces a Discord member with the .mention and .display_name attributes
class DummyAI:
    def __init__(self, level):
        self.mention = f"AI (Level {level})"
        self.display_name = f"AI (Level {level})"


# Each game is represented by a class instance to allow multiple games at once.
class C4Game:
    def __init__(self, p1, p2):
        self.players = [p1, p2]

        # Emojis for different pieces of the board
        self.empty = ":blue_square:"
        self.p1piece = ":red_circle:"
        self.p2piece = ":yellow_circle:"
        self.embed_color = discord.Color.random()

        self.turn = 0

        # Initialize game board
        self.COLUMNS = 7
        self.ROWS = 6
        self.game_board = [[0 for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]
        # Game board is indexed like self.game_board[row][col]
        # 0 is the bottom row, 5 is the top row

    async def place(self, input_col):
        # Adjusted for indexes starting at 0
        input_col = input_col - 1

        # Simulates the gravity needed when usually playing Connect Four.
        # Each column's row is checked from bottom to top for an empty square,
        # and the piece is placed in that square
        for i in range(self.ROWS):
            if self.game_board[i][input_col] == 0:
                # 1 is added to self.turn because 1 represents player 1, and 2 represents player 2
                self.game_board[i][input_col] = self.turn + 1
                break
        else:
            # No available space left for the piece
            return C4PlaceResults.NO_SPACE

    async def check_result(self, board=None, turn=None):
        if board is None:
            board = self.game_board
        if turn is None:
            turn = self.turn

        # idk how this works but it's super cool!
        horizontal_kernel = np.array([[1, 1, 1, 1]])
        vertical_kernel = np.transpose(horizontal_kernel)
        diag1_kernel = np.eye(4, dtype=np.uint8)
        diag2_kernel = np.fliplr(diag1_kernel)
        detection_kernels = [horizontal_kernel, vertical_kernel, diag1_kernel, diag2_kernel]

        for kernel in detection_kernels:
            if (convolve2d(np.array(board) == turn + 1, kernel, mode="valid") == 4).any():
                return C4GameResults.WIN

        # all(top_row) can be done here as the game is a draw when
        # all pieces in the top row are full
        if all(self.game_board[-1]):
            return C4GameResults.DRAW

    async def swap_players(self):
        # Next player's turn
        if self.turn == 0:
            self.turn = 1
        elif self.turn == 1:
            self.turn = 0

    async def ctx_send_board(self, ctx, color_guide=False):
        embed = discord.Embed(
            title=f"{self.players[0].display_name} and {self.players[1].display_name}'s game:",
            color=self.embed_color
        )

        board = ""
        # Representing the game board in an embed
        # The game board is reversed to display it top to bottom instead of bottom to top
        for row in reversed(self.game_board):
            for col in row:
                if col == 0:
                    board += self.empty
                elif col == 1:
                    board += self.p1piece
                elif col == 2:
                    board += self.p2piece
            # Newline for next row in the board
            board += "\n"

        embed.description = ""
        if color_guide:
            embed.description = f"""🔴 ― {self.players[0].mention}
🟡 ― {self.players[1].mention}
"""
        embed.description += f"{self.players[self.turn].mention}'s turn"
        embed.add_field(name="Game", value=board)

        await ctx.send(self.players[self.turn].mention, embed=embed)

    async def game_over(self, bot, ctx, result):
        embed = discord.Embed(
            title=f"{self.players[0].display_name} and {self.players[1].display_name}'s game:",
            color=self.embed_color
        )

        board = ""
        # Representing the game board in an embed
        # The game board is reversed to display it top to bottom instead of bottom to top
        for row in reversed(self.game_board):
            for col in row:
                if col == 0:
                    board += self.empty
                elif col == 1:
                    board += self.p1piece
                elif col == 2:
                    board += self.p2piece
            # Newline for next row in the board
            board += "\n"

        coin_amount = random.randint(100, 300)
        if result == C4GameResults.WIN:
            await bot.database.add_member_coins(self.players[self.turn], coin_amount)

            embed.description = (f"**{self.players[self.turn].mention} has won! {coin_amount}** "
                                 f":coin: has been added to their balance.")
        elif result == C4GameResults.DRAW:
            embed.description = f"The game has ended in a draw."
        elif result == C4GameResults.FORFEIT:
            await bot.database.add_member_coins(self.players[self.turn], coin_amount)

            # 1 - self.turn gives the opposite of the turn
            embed.description = (f"**{self.players[1 - self.turn].mention} has won** because of "
                                 f"{self.players[self.turn].mention}'s forfeit. **{coin_amount}** "
                                 f":coin: has been added to their balance.")

        embed.add_field(name="Game", value=board)
        await ctx.send(self.players[self.turn].mention, embed=embed)


async def evaluate_window(window, piece):
    score = 0
    opp_piece = 1
    if piece == 1:
        opp_piece = 2

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score


class C4GameAI(C4Game):
    def __init__(self, p1, p2, level):
        super().__init__(p1, p2)
        self.level = level
        self.game_board = np.zeros((self.ROWS, self.COLUMNS))
        self.last_played_col = None

    async def ctx_send_board(self, ctx, color_guide=False):
        embed = discord.Embed(
            title=f"{self.players[0].display_name} and {self.players[1].display_name}'s game:",
            color=self.embed_color
        )

        board = ""
        for row in reversed(self.game_board):
            for col in row:
                if col == 0:
                    board += self.empty
                elif col == 1:
                    board += self.p1piece
                elif col == 2:
                    board += self.p2piece
            board += "\n"

        embed.description = ""
        if color_guide:
            embed.description = f"""🔴 ― {self.players[0].mention}
🟡 ― {self.players[1].mention}
"""
        if self.last_played_col is None:
            embed.description += f"{self.players[self.turn].mention}'s turn"
        else:
             embed.description += f"The AI placed its piece on column **{self.last_played_col}**."
        embed.add_field(name="Game", value=board)

        await ctx.send(self.players[self.turn].mention, embed=embed)

    def is_valid_location(self, board, col):
        return board[self.ROWS - 1][col] == 0

    def get_next_open_row(self, board, col):
        for r in range(self.ROWS):
            if board[r][col] == 0:
                return r

    async def place(self, input_col):
        input_col = input_col - 1
        for i in range(self.ROWS):
            if self.game_board[i][input_col] == 0:
                self.game_board[i][input_col] = self.turn + 1
                return

    async def in_place(self, board, input_col, piece):
        for i in range(self.ROWS):
            if board[i][input_col] == 0:
                board[i][input_col] = piece
                return

    async def possible_columns(self, board):
        cols = []

        for i in range(self.COLUMNS):
            if board[-1][i] == 0:
                cols.append(i)

        return cols

    async def is_terminal(self, board):
        result = await self.check_result(turn=0, board=board)
        result2 = await self.check_result(turn=1, board=board)
        return result == C4GameResults.WIN or result2 == C4GameResults.WIN or result == C4GameResults.DRAW

    async def winning_move(self, board, piece):
        # Check horizontal locations for win
        for c in range(self.COLUMNS - 3):
            for r in range(self.ROWS):
                if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][
                        c + 3] == piece:
                    return True

        # Check vertical locations for win
        for c in range(self.COLUMNS):
            for r in range(self.ROWS - 3):
                if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][
                        c] == piece:
                    return True

        # Check positively sloped diagonals
        for c in range(self.COLUMNS - 3):
            for r in range(self.ROWS - 3):
                if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and \
                        board[r + 3][c + 3] == piece:
                    return True

        # Check negatively sloped diagonals
        for c in range(self.COLUMNS - 3):
            for r in range(3, self.ROWS):
                if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and \
                        board[r - 3][c + 3] == piece:
                    return True

    async def heuristic(self, board, piece):
        # Keith Galli's scoring function

        score = 0

        # Score center column
        center_array = [int(i) for i in list(board[:, self.COLUMNS // 2])]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Score Horizontal
        for r in range(self.ROWS):
            row_array = [int(i) for i in list(board[r, :])]
            for c in range(self.COLUMNS - 3):
                window = row_array[c:c + 4]
                score += await evaluate_window(window, piece)

        # Score Vertical
        for c in range(self.COLUMNS):
            col_array = [int(i) for i in list(board[:, c])]
            for r in range(self.ROWS - 3):
                window = col_array[r:r + 4]
                score += await evaluate_window(window, piece)

        # Score positive sloped diagonal
        for r in range(self.ROWS - 3):
            for c in range(self.COLUMNS - 3):
                window = [board[r + i][c + i] for i in range(4)]
                score += await evaluate_window(window, piece)

        for r in range(self.ROWS - 3):
            for c in range(self.COLUMNS - 3):
                window = [board[r + 3 - i][c + i] for i in range(4)]
                score += await evaluate_window(window, piece)

        return score

    async def minimax(self, board, depth, alpha, beta, max_player):
        # Minimax algorithm
        # This algorithm recursively generates the game tree
        # and chooses the best path based on a scoring function.

        valid_cols = await self.possible_columns(board)
        is_terminal = await self.is_terminal(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if await self.winning_move(board, 2):
                    return None, math.inf
                elif await self.winning_move(board, 1):
                    return None, -math.inf
            else:
                return None, await self.heuristic(board, 2)
        if max_player:
            value = -math.inf
            column = random.choice(valid_cols)
            for col in valid_cols:
                b_copy = board.copy()
                await self.in_place(b_copy, col, 2)
                new_score = (await self.minimax(b_copy, depth - 1, alpha, beta, False))[1]

                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break

            return column, value
        else:
            value = math.inf
            column = random.choice(valid_cols)
            for col in valid_cols:
                b_copy = board.copy()
                await self.in_place(b_copy, col, 1)
                new_score = (await self.minimax(b_copy, depth - 1, alpha, beta, True))[1]

                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break

            return column, value

    async def game_over(self, bot, ctx, result):
        embed = discord.Embed(
            title=f"{self.players[0].display_name} and {self.players[1].display_name}'s game:",
            color=self.embed_color
        )

        board = ""
        # Representing the game board in an embed
        # The game board is reversed to display it top to bottom instead of bottom to top
        for row in reversed(self.game_board):
            for col in row:
                if col == 0:
                    board += self.empty
                elif col == 1:
                    board += self.p1piece
                elif col == 2:
                    board += self.p2piece
            # Newline for next row in the board
            board += "\n"

        coin_amount = random.randint(100, 300)
        coin_amount *= self.level / 5
        if result == C4GameResults.WIN:
            # Only add coins if the player won
            if self.turn == 0:
                await bot.database.add_member_coins(self.players[self.turn], coin_amount)

                embed.description = (f"**{self.players[self.turn].mention} has won! {coin_amount}** "
                                     f":coin: has been added to your balance.")
            else:
                embed.description = f"**{self.players[self.turn].mention} has won!**"
        elif result == C4GameResults.DRAW:
            embed.description = f"The game has ended in a draw."
        elif result == C4GameResults.FORFEIT:
            # 1 - self.turn gives the opposite of the turn
            embed.description = (f"**{self.players[1 - self.turn].mention} has won** because of "
                                 f"{self.players[self.turn].mention}'s forfeit.")

        embed.add_field(name="Game", value=board)
        await ctx.send(self.players[0].mention, embed=embed)

    async def ai_place(self):
        b_copy = deepcopy(self.game_board)
        col, _ = await self.minimax(b_copy, self.level, -math.inf, math.inf, True)
        self.last_played_col = col + 1

        await self.place(col + 1)


class ConnectFour(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["c4", "connect_4", "connectfour", "connect4"])
    async def connect_four(self, ctx, member: discord.Member):
        game = C4Game(ctx.author, member)
        color_guide = True

        while True:
            player = game.players[game.turn]

            # Send the board and then ask for player input
            # Only include the color guide for the first turn
            await game.ctx_send_board(ctx, color_guide=color_guide)
            color_guide = False

            while True:
                def check(m):
                    # Message author is the player with the turn, and the channel is right
                    return m.author == player and m.channel == ctx.channel

                player_input = await self.bot.wait_for('message', check=check)
                player_input = player_input.content
                if player_input.isnumeric():
                    # Input is a number, proceed if number is between 1 and 7
                    if 1 <= int(player_input) <= 7:
                        await game.place(int(player_input))
                        break
                elif player_input.lower() in ("forfeit", "ff", "resign", ":handshake:", "�"):
                    await game.game_over(self.bot, ctx, C4GameResults.FORFEIT)
                    return
                else:
                    continue

            result = await game.check_result()
            if result in (C4GameResults.WIN, C4GameResults.DRAW):
                await game.game_over(self.bot, ctx, result)
                return

            await game.swap_players()

    @connect_four.error
    async def c4_error(self, ctx, error):
        # Bad Argument: the {member} parameter could not be converted
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please send j.c4 \"@Member\", where @Member is the member you want to play against.")
        else:
            print(error)

    @commands.command(aliases=[
        "c4ai", "connect_4ai", "connectfourai", "connect4ai",
        "c4_ai", "connect_4_ai", "connectfour_ai", "connect4_ai", "connect_fourai"
    ])
    async def connect_four_ai(self, ctx, level: int):
        game = C4GameAI(ctx.author, DummyAI(level), level)
        color_guide = True

        while True:
            await game.ctx_send_board(ctx, color_guide=color_guide)
            color_guide = False

            while True:
                def check(m):
                    # Message author is the player with the turn, and the channel is right
                    return m.author == ctx.author and m.channel == ctx.channel

                player_input = await self.bot.wait_for('message', check=check)
                player_input = player_input.content
                if player_input.isnumeric():
                    # Input is a number, proceed if number is between 1 and 7
                    if 1 <= int(player_input) <= 7:
                        await game.place(int(player_input))
                        break
                elif player_input.lower() in ("forfeit", "ff", "resign", ":handshake:", "�"):
                    await game.game_over(self.bot, ctx, C4GameResults.FORFEIT)
                    return
                else:
                    continue

            result = await game.check_result()
            if result in (C4GameResults.WIN, C4GameResults.DRAW):
                await game.game_over(self.bot, ctx, result)
                return

            await game.swap_players()

            await game.ai_place()

            result = await game.check_result()
            if result in (C4GameResults.WIN, C4GameResults.DRAW):
                await game.game_over(self.bot, ctx, result)
                return

            await game.swap_players()


async def setup(bot):
    await bot.add_cog(ConnectFour(bot))
