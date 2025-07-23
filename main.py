import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "!")
ALLOWED_CHANNEL_ID = (
    int(os.getenv("ALLOWED_CHANNEL_ID", "0"))
    if os.getenv("ALLOWED_CHANNEL_ID")
    else None
)

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


# Cogs 로드
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded: {filename[:-3]}")
            except Exception as e:
                print(f"❌ Failed to load {filename[:-3]}: {e}")


@bot.event
async def on_ready():
    print(f"✅ {bot.user} 온라인!")
    print(f"📋 서버: {len(bot.guilds)}개")

    if ALLOWED_CHANNEL_ID:
        print(f"🎯 허용된 채널: {ALLOWED_CHANNEL_ID}")
        channel = bot.get_channel(ALLOWED_CHANNEL_ID)
        if channel:
            await channel.send("✅ 봇이 다시 시작되었습니다!")
    else:
        print("📢 모든 채널에서 작동합니다")


@bot.event
async def on_message(message):
    # 봇 메시지 무시
    if message.author.bot:
        return

    # ALLOWED_CHANNEL_ID가 설정된 경우에만 채널 체크
    if ALLOWED_CHANNEL_ID and message.channel.id != ALLOWED_CHANNEL_ID:
        return

    await bot.process_commands(message)


@bot.command(name="ping")
async def ping(ctx):
    """응답 시간 확인"""
    await ctx.send(f"Pong! 🏓 {round(bot.latency * 1000)}ms")


@bot.command(name="hello", aliases=["안녕"])
async def hello(ctx):
    """인사"""
    await ctx.send(f"안녕하세요, {ctx.author.mention}님! 👋")


@bot.command(name="info")
async def info(ctx):
    """봇 정보"""
    embed = discord.Embed(title="봇 정보", color=discord.Color.blue())
    embed.add_field(name="서버", value=len(bot.guilds), inline=True)
    embed.add_field(
        name="지연시간", value=f"{round(bot.latency * 1000)}ms", inline=True
    )
    embed.add_field(name="채널 ID", value=ALLOWED_CHANNEL_ID, inline=True)
    await ctx.send(embed=embed)


# 에러 핸들러
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ 존재하지 않는 명령어입니다.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ 필요한 인자가 누락되었습니다.")
    else:
        await ctx.send(f"❌ 에러가 발생했습니다: {error}")


# 봇 실행
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
