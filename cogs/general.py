import discord
from discord.ext import commands


class General(commands.Cog):
    """일반적인 명령어들을 담은 Cog"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='server', aliases=['서버'])
    async def server_info(self, ctx):
        """현재 서버의 정보를 표시합니다"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"📊 {guild.name} 서버 정보",
            color=discord.Color.blue()
        )
        
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="서버 ID", value=guild.id, inline=True)
        embed.add_field(name="소유자", value=guild.owner.mention, inline=True)
        embed.add_field(name="멤버 수", value=guild.member_count, inline=True)
        embed.add_field(name="채널 수", value=len(guild.channels), inline=True)
        embed.add_field(name="역할 수", value=len(guild.roles), inline=True)
        embed.add_field(name="생성일", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='user', aliases=['유저', '사용자'])
    async def user_info(self, ctx, member: discord.Member = None):
        """사용자 정보를 표시합니다"""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"👤 {member.display_name} 정보",
            color=member.color
        )
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="사용자명", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="닉네임", value=member.nick or "없음", inline=True)
        embed.add_field(name="계정 생성일", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="서버 가입일", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="최고 역할", value=member.top_role.mention, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clear', aliases=['청소', '삭제'])
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int = 5):
        """메시지를 삭제합니다 (관리자 권한 필요)"""
        if amount < 1 or amount > 100:
            await ctx.send("❌ 1~100 사이의 숫자를 입력해주세요.")
            return
        
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 for the command message
        await ctx.send(f"✅ {len(deleted) - 1}개의 메시지를 삭제했습니다.", delete_after=3)
    
    @clear_messages.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ 이 명령어를 사용하려면 메시지 관리 권한이 필요합니다.")


async def setup(bot):
    await bot.add_cog(General(bot))