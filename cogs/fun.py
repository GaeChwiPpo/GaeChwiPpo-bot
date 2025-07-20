import discord
from discord.ext import commands
import random


class Fun(commands.Cog):
    """재미있는 명령어들을 담은 Cog"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='dice', aliases=['주사위'])
    async def roll_dice(self, ctx, sides: int = 6):
        """주사위를 굴립니다"""
        if sides < 2:
            await ctx.send("❌ 주사위는 최소 2면 이상이어야 합니다.")
            return
        
        result = random.randint(1, sides)
        await ctx.send(f"🎲 {sides}면 주사위를 굴렸습니다: **{result}**")
    
    @commands.command(name='choose', aliases=['선택', '골라'])
    async def choose(self, ctx, *choices):
        """여러 선택지 중 하나를 무작위로 선택합니다"""
        if len(choices) < 2:
            await ctx.send("❌ 최소 2개 이상의 선택지를 입력해주세요.")
            return
        
        choice = random.choice(choices)
        await ctx.send(f"🤔 제 선택은... **{choice}** 입니다!")
    
    @commands.command(name='8ball', aliases=['질문'])
    async def eight_ball(self, ctx, *, question):
        """마법의 8ball에게 질문합니다"""
        responses = [
            "확실합니다 🟢",
            "절대적으로 그렇습니다 🟢",
            "의심의 여지가 없습니다 🟢",
            "네, 확실합니다 🟢",
            "믿어도 좋습니다 🟢",
            "제가 보기엔 그렇습니다 🟡",
            "아마도요 🟡",
            "좋아 보입니다 🟡",
            "그럴 가능성이 높습니다 🟡",
            "지금은 예측하기 어렵습니다 🟠",
            "다시 한 번 물어보세요 🟠",
            "나중에 다시 물어보세요 🟠",
            "지금은 말하지 않는 게 좋겠습니다 🟠",
            "집중해서 다시 물어보세요 🟠",
            "기대하지 마세요 🔴",
            "아니라고 봅니다 🔴",
            "출처에 따르면 아닙니다 🔴",
            "전망이 좋지 않습니다 🔴",
            "매우 의심스럽습니다 🔴"
        ]
        
        response = random.choice(responses)
        embed = discord.Embed(
            title="🎱 마법의 8ball",
            color=discord.Color.purple()
        )
        embed.add_field(name="질문", value=question, inline=False)
        embed.add_field(name="대답", value=response, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='coin', aliases=['동전'])
    async def flip_coin(self, ctx):
        """동전을 던집니다"""
        result = random.choice(['앞면', '뒷면'])
        coin_emoji = "🪙"
        
        embed = discord.Embed(
            title=f"{coin_emoji} 동전 던지기",
            description=f"결과는... **{result}**입니다!",
            color=discord.Color.gold()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='rps', aliases=['가위바위보'])
    async def rock_paper_scissors(self, ctx, choice: str):
        """가위바위보 게임을 합니다"""
        choices = {
            '가위': '✂️',
            '바위': '🪨', 
            '보': '📄',
            'scissors': '✂️',
            'rock': '🪨',
            'paper': '📄'
        }
        
        if choice.lower() not in choices:
            await ctx.send("❌ 가위, 바위, 보 중에서 선택해주세요.")
            return
        
        user_choice = choice.lower()
        if user_choice in ['scissors', 'rock', 'paper']:
            user_choice = {'scissors': '가위', 'rock': '바위', 'paper': '보'}[user_choice]
        
        bot_choice = random.choice(['가위', '바위', '보'])
        
        # 결과 판정
        if user_choice == bot_choice:
            result = "🤝 비겼습니다!"
            color = discord.Color.yellow()
        elif (user_choice == '가위' and bot_choice == '보') or \
             (user_choice == '바위' and bot_choice == '가위') or \
             (user_choice == '보' and bot_choice == '바위'):
            result = "🎉 당신이 이겼습니다!"
            color = discord.Color.green()
        else:
            result = "😢 제가 이겼습니다!"
            color = discord.Color.red()
        
        embed = discord.Embed(
            title="가위바위보 게임",
            description=result,
            color=color
        )
        embed.add_field(name="당신의 선택", value=f"{choices[user_choice]} {user_choice}", inline=True)
        embed.add_field(name="봇의 선택", value=f"{choices[bot_choice]} {bot_choice}", inline=True)
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))