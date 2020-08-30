import random
import discord
from .twelve_janggi import classes as jg
from discord.ext import commands

READY_EMOJIS = ['💜', '💚', '🇷']
ACTION_EMOJIS = [
    '🇶', '🇼', '🇪', '🇷',
    '🇦', '🇸', '🇩', '🇫',
    '🇿', '🇽', '🇨', '🇻',
    '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣'
    ]
ACTION_KWDS = [
    'q', 'w', 'e', 'r',
    'a', 's', 'd', 'f',
    'z', 'x', 'c', 'v',
    '1', '2', '3', '4', '5', '6'
    ]
JG_EMOJIS = {
    jg.General: ['🟪⬆️🟪⬅️✝️➡️🟪⬇️🟪', '🟩⬆️🟩⬅️❇️➡️🟩⬇️🟩'],
    jg.Premier: ['↖️🟪↗️🟪♓🟪↙️🟪↘️', '↖️🟩↗️🟩❎🟩↙️🟩↘️'],
    jg.King: ['↖️⬆️↗️⬅️☸️➡️↙️⬇️↘️', '↖️⬆️↗️⬅️✳️➡️↙️⬇️↘️'],
    jg.Man: ['🟪🟪🟪🟪♌➡️🟪🟪🟪', '🟩🟩🟩⬅️✅🟩🟩🟩🟩'],
    jg.Lord: ['🟪⬆️↗️⬅️☪️➡️🟪⬇️↘️', '↖️⬆️🟩⬅️🈯➡️↙️⬇️🟩'],
    0: '⬜'*9
    }

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player1 = None
        self.player2 = None

    @commands.command(name="십이장기", aliases=["장기", "12"])
    async def twelve_janggi(self, ctx):
        """십이장기"""

        async def ready():
            # 메시지 전송 및 반응 추가
            ready_msg = await ctx.send(
                f"선공: {READY_EMOJIS[0]} / 후공: {READY_EMOJIS[1]} / "
                f"랜덤: {READY_EMOJIS[2]}"
                )
                
            for emoji in READY_EMOJIS:
                await ready_msg.add_reaction(emoji)

            curr_reaction = [[], [], []]

            @self.listener(name='jg_ready')
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

                # 반응 현황이 적절하면 게임 시작을 위해 return
                if len(curr_reaction[0]) == 1 and len(curr_reaction[1]) == 1:
                    if curr_reaction[0] == curr_reaction[1]:
                        continue
                    self.player1 = curr_reaction[0][0]
                    self.player2 = curr_reaction[1][0]
                    self.bot.remove_listener(on_reaction_remove,
                                             name='jg_ready')
                    return
                if len(curr_reaction[2]) == 2:
                    if curr_reaction[2][0] == curr_reaction[2][1]:
                        continue
                    random.shuffle(curr_reaction[2])
                    self.player1, self.player2 = curr_reaction[2]
                    self.bot.remove_listener(on_reaction_remove,
                                             name='jg_ready')
                    return
        
        async def play():
            await ctx.send(
                f"{self.player1.display_name}, {self.player2.display_name}"
                )
            await ctx.send("게임을 시작하지")

            game = jg.Game()
            curr_player = self.player1

            curr_reaction = []
            @self.listener(name='jg_reaction_add')
            async def on_reaction_add(reaction, user):
                if user != curr_player or reaction.message.id != game_msg.id:
                    return
                curr_reaction.append(reaction.emoji)
                if len(curr_reaction) != 2:
                    return

                # 턴 진행 시도
                try:
                    (x, y) = [ACTION_EMOJIS.index(i) for i in curr_reaction]
                    for from_to in [(x, y), (y, x)]:
                        game.turn(from_to)
                except:
                    return
                    
                # 유저 반응 삭제
                for reaction_ in [i for i in game_msg.reactions if not i.me]:
                    await reaction_.remove(curr_player)
            
            @self.listener(name='jg_reaction_remove')
            async def on_reaction_remove(reaction, user):
                if user != curr_player or reaction.message.id != game_msg.id:
                    return
                curr_reaction.remove(reaction.emoji)
            
            turn_fail_msg = None
            @self.listener(name='jg_message')
            async def on_message(message):
                if (message.author != curr_player
                        or message.channel != ctx.channel
                        or len(message.content) != 2
                        or not message.content.isalnum()):
                    return
                (x, y) = [ACTION_KWDS.index(i)
                            for i in message.content.lower()]
                for from_to in [(x, y), (y, x)]:
                    try:
                        game.turn(from_to)
                    except ValueError:
                        pass
                if not turn_fail_msg:
                    turn_fail_msg = await ctx.send("유효하지 않은 입력")
                


                await message.delete()
                await end_turn()
            '''
            임베드 전송
            임베드 메시지에 반응 추가
            채팅 혹은 반응 추가를 대기: 채팅 및 유저 반응을 삭제
            만약 입력이 무효하면 안내 메시지 전송
             아니면 턴 진행
            만약 이겼으면 안내 메시지 전송 및 게임 종료
             아니면 turn.for_red 토글하고 continue
            '''
            def make_embed():
                # 이모지 덱 생성
                emoji_deck = []
                for i in range(0, 9, 3):
                    emoji_deck.append('⬛'.join(JG_EMOJIS[key][i:i+3]
                                               for key in game.table.deck))
                # 임베드 생성
                [curr_player, curr_color] \
                    = [self.player1, 0xaa8ed6] if game.red_turn \
                    else [self.player2, 0x78b159]
                self.embed = discord.Embed(title='잡힌 말', color=curr_color,
                                      description='\n'.join(emoji_deck))
                self.embed.set_author(name=curr_player.nick + '차례',
                                 icon_url=str(curr_player.avatar_url))

                # 이모지 보드 생성 및 임베드에 추가
                for i in range(3):
                    emoji_board = []
                    for j in range(3):
                        emoji_board.append(
                            '⬛'.join(JG_EMOJIS[key][j*3:(j+1)*3]
                                     for key in game.table.board[i*4:(i+1)*4])
                            )
                    self.embed.add_field(
                        name='말판' if i == 0 else ' ',
                        value='\n'.join(emoji_board), inline=False
                        )
                #TODO: self.embed.set_footer()로 타이머 표시, 10초마다 갱신

            async def end_turn():
                if not game.finished:
                    make_embed()
                else:
                    winner = self.player1 if game.red_won else self.player2
                    cause = "왕을 잡았습니다!" if game.killed_king \
                        else "왕이 적진에서 한 턴을 버텼습니다!"
                    self.embed = discord.Embed(
                        title=f'{winner.nick}의 승리!', color=0xffffff,
                        description=cause
                        )
                    self.embed.set_author(name='십이장기')
                    self.embed.set_thumbnail(url=str(winner.avatar_url))
                    for func, name in [
                            (on_reaction_add, 'jg_reaction_add'),
                            (on_reaction_remove, 'jg_reaction_remove'),
                            (on_message, 'jg_message')
                            ]:
                        self.bot.remove_listener(func, name=name)
                # 임베드 메시지 수정
                await game_msg.edit(embed=make_embed())

            # 최초 임베드 메시지 전송 및 반응 추가
            game_msg = await ctx.send(embed=make_embed())
            for emoji in ACTION_EMOJIS[:12+len(game.table.deck)]:
                await game_msg.add_reaction(emoji)

        await ready()
        await play()
    
    @commands.command(name="설정", parent=twelve_janggi)
    async def setting_twelve_janggi(self, ctx):
        pass

def setup(bot):
    bot.add_cog(Games(bot))
    