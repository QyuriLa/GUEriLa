import random
import discord
import twelve_janggi as jg
from discord.ext import commands

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player1 = None
        self.player2 = None

    @commands.command(name="십이장기", aliases=["장기", "12"])
    async def twelve_janggi(self, ctx):
        """십이장기"""

        READY_EMOJIS = ['💜', '💚', '🇷']

        async def ready():
            ready_msg = await ctx.send(
                f"선공: {READY_EMOJIS[0]} / 후공: {READY_EMOJIS[1]} / 랜덤: {READY_EMOJIS[2]}"
                )
            for emoji in READY_EMOJIS:
                await ready_msg.add_reaction(emoji)
                curr_reaction = [[], [], []]

            @self.bot.listen()
            async def on_reaction_remove(reaction, user):
                if reaction.message.id != ready_msg.id:
                    return
                for i in range(3):
                    if reaction.emoji == READY_EMOJIS[i]:
                        curr_reaction[i].remove(user)

            while True:
                reaction, user = await self.bot.wait_for('reaction_add')
                if user.bot:
                    continue
                for i in range(3):
                    if reaction.emoji == READY_EMOJIS[i]:
                        curr_reaction[i].append(user)

                if len(curr_reaction[0]) == 1 and len(curr_reaction[1]) == 1:
                    if curr_reaction[0] == curr_reaction[1]:
                        continue
                    self.player1 = curr_reaction[0][0]
                    self.player2 = curr_reaction[1][0]
                    return
                if len(curr_reaction[2]) == 2:
                    if curr_reaction[2][0] == curr_reaction[2][1]:
                        continue
                    random.shuffle(curr_reaction[2])
                    self.player1, self.player2 = curr_reaction[2]
                    return
            self.bot.remove_listener(on_reaction_remove)
        
        async def game():
            await ctx.send(
                f"{self.player1.display_name}, {self.player2.display_name}"
                )
            await ctx.send("게임을 시작하지")
        
        await ready()
        await game()
        

def setup(bot):
    bot.add_cog(Games(bot))
    