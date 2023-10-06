import discord
from discord.ext import commands
import numpy as np
from scipy.signal import convolve2d
from assets.enums import C4PlaceResults
from assets.enums import C4GameResults


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
        # Each column's row is checked for bottom to top for an empty square,
        # and the piece is placed in that square
        for i in range(self.ROWS):
            if self.game_board[i][input_col] == 0:
                # 1 is added to self.turn because 1 represents player 1, and 2 represents player 2
                self.game_board[i][input_col] = self.turn + 1
                break
        else:
            # No available space left for the piece
            return C4PlaceResults.NO_SPACE

    async def check_result(self):
        # idk how this works but it's super cool!
        horizontal_kernel = np.array([[1, 1, 1, 1]])
        vertical_kernel = np.transpose(horizontal_kernel)
        diag1_kernel = np.eye(4, dtype=np.uint8)
        diag2_kernel = np.fliplr(diag1_kernel)
        detection_kernels = [horizontal_kernel, vertical_kernel, diag1_kernel, diag2_kernel]

        for kernel in detection_kernels:
            if (convolve2d(np.array(self.game_board) == self.turn + 1, kernel, mode="valid") == 4).any():
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

    async def ctx_send_board(self, ctx):
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

        embed.description = f"""🔴 ― {self.players[0].mention}
🟡 ― {self.players[1].mention}
{self.players[self.turn].mention}'s turn
Game:
{board}"""

        await ctx.send(self.players[self.turn].mention, embed=embed)

    async def game_over(self, ctx, result):
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

        if result == C4GameResults.WIN:
            embed.description = f"""🔴 ― {self.players[0].mention}
🟡 ― {self.players[1].mention}
{self.players[self.turn].mention} has won!
Game:
{board}"""
        elif result == C4GameResults.DRAW:
            embed.description = f"""🔴 ― {self.players[0].mention}
🟡 ― {self.players[1].mention}
The game has ended in a draw.
Game:
{board}"""
        elif result == C4GameResults.FORFEIT:
            # 1 - self.turn gives the opposite of the turn
            embed.description = f"""🔴 ― {self.players[0].mention}
🟡 ― {self.players[1].mention}
{self.players[1 - self.turn].mention} has won because of {self.players[self.turn].mention}'s forfeit.
Game:
{board}"""

        await ctx.send(self.players[self.turn].mention, embed=embed)


class ConnectFour(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["c4", "connect_4", "connectfour", "connect4"])
    async def connect_four(self, ctx, member: discord.Member):
        game = C4Game(ctx.author, member)

        while True:
            player = game.players[game.turn]

            # Send the board and then ask for player input
            await game.ctx_send_board(ctx)

            def check(m):
                # Message author is the player with the turn, and the channel is right
                return m.author == player and m.channel == ctx.channel

            player_input = await self.bot.wait_for('message', check=check)
            player_input = player_input.content
            if player_input.isnumeric():
                # Input is a number, proceed if number is between 1 and 7
                if 1 <= int(player_input) <= 7:
                    await game.place(int(player_input))
            elif player_input.lower() in ("forfeit", "ff", "resign", "you win", "i quit"):
                await game.game_over(ctx, C4GameResults.FORFEIT)
            else:
                continue

            result = await game.check_result()
            if result in (C4GameResults.WIN, C4GameResults.DRAW):
                await game.game_over(ctx, result)
                return

            await game.swap_players()

    @connect_four.error
    async def c4_error(self, ctx, error):
        # Bad Argument: the {member} parameter could not be converted
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please send j.c4 \"@Member\", where @Member is the member you want to play against.")
        else:
            print(error)


async def setup(bot):
    await bot.add_cog(ConnectFour(bot))
