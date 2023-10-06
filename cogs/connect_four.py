import discord
from discord.ext import commands
from assets.enums import C4PlaceResults


# Each game is represented by a class instance to allow multiple games at once.
class C4Game:
    def __init__(self, p1, p2):
        self.players = [p1, p2]

        # Emojis for different pieces of the board
        self.empty = ":blue_square:"
        self.p1piece = ":red_circle:"
        self.p2piece = ":yellow_circle:"

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

        # Next player's turn
        if self.turn == 0:
            self.turn = 1
        elif self.turn == 1:
            self.turn = 0

        return C4PlaceResults.SUCCESSFUL

    async def ctx_send_board(self, ctx):
        embed = discord.Embed(title=f"{self.players[0].display_name} and {self.players[1].display_name}'s game:")

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

        embed.description = f"""🔴 ― {self.players[0].display_name}
🟡 ― {self.players[1].display_name}
Game:
{board}"""


class ConnectFour(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["c4", "connect_4", "connectfour", "connect4"])
    async def connect_four(self, ctx, member: discord.Member):
        game = C4Game(ctx.author, member)

        while True:
            # Send the board and then ask for player input
            await game.ctx_send_board(ctx)

            # TODO: player input ill do ce first

    @connect_four.error
    async def c4_error(self, ctx, error):
        # Bad Argument: the {member} parameter could not be converted
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please send j.c4 \"@Member\", where @Member is the member you want to play against.")


async def setup(bot):
    await bot.add_cog(ConnectFour(bot))
