import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import boto3
import discord
from discord.ext import commands, tasks
import discord.utils


class Study(commands.Cog):
    """학습 질문 및 피드백 시스템"""

    def __init__(self, bot):
        self.bot = bot
        self.active_questions = {}  # 활성 질문 추적
        self.start_date = datetime(2025, 7, 20)  # 시작 날짜 (오늘)
        self.allowed_channel_id = int(os.getenv("ALLOWED_CHANNEL_ID", "0")) if os.getenv("ALLOWED_CHANNEL_ID") else None

        # AWS Bedrock 클라이언트 초기화
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        # JSON 파일에서 질문 데이터베이스 로드
        self.question_bank = self.load_questions()
        
        # 스케줄러 시작
        self.daily_question.start()

    def load_questions(self):
        """JSON 파일에서 질문 데이터 로드"""
        try:
            # 현재 파일의 디렉토리 기준으로 경로 설정
            current_dir = Path(__file__).parent.parent
            json_path = current_dir / "data" / "questions.json"

            with open(json_path, "r", encoding="utf-8") as f:
                questions = json.load(f)

            print(f"✅ {json_path}에서 질문 데이터를 로드했습니다.")

            # 통계 출력
            total = 0
            for main_cat in questions.values():
                for sub_cat in main_cat.values():
                    total += len(sub_cat)
            print(f"📊 총 {total}개의 질문이 로드되었습니다.")

            return questions

        except FileNotFoundError:
            print(f"❌ 질문 파일을 찾을 수 없습니다: {json_path}")
            return self.get_default_questions()
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            return self.get_default_questions()
        except Exception as e:
            print(f"❌ 질문 로드 중 오류: {e}")
            return self.get_default_questions()

    def get_default_questions(self):
        """기본 질문 데이터 (폴백용)"""
        return {
            "backend": {
                "database": ["데이터베이스 인덱스의 장단점은?"],
                "api": ["REST API의 특징은?"],
                "architecture": ["마이크로서비스의 장점은?"],
            },
            "frontend": {
                "react": ["React Hooks의 규칙은?"],
                "performance": ["웹 성능 최적화 방법은?"],
                "state": ["상태 관리가 필요한 이유는?"],
            },
        }

    def get_random_question(self, category=None):
        """랜덤 질문 선택"""
        # 사용 가능한 카테고리 목록
        available_categories = list(self.question_bank.keys())

        if category and category in available_categories:
            main_category = self.question_bank[category]
        else:
            # 랜덤 카테고리 선택
            category = random.choice(available_categories)
            main_category = self.question_bank[category]

        # 서브 카테고리 선택
        sub_category = random.choice(list(main_category.keys()))
        questions = main_category[sub_category]

        return {
            "category": category,
            "sub_category": sub_category,
            "question": random.choice(questions),
        }
    
    def get_question_by_index(self, index, category_type):
        """인덱스 기반으로 질문 선택 (스케줄러용)"""
        if category_type not in ["backend", "frontend", "general"]:
            return None
            
        main_category = self.question_bank.get(category_type, {})
        if not main_category:
            return None
            
        # 모든 질문을 하나의 리스트로 평탄화
        all_questions = []
        for sub_category, questions in main_category.items():
            for question in questions:
                all_questions.append({
                    "category": category_type,
                    "sub_category": sub_category,
                    "question": question
                })
        
        if not all_questions:
            return None
            
        # 인덱스가 전체 길이를 초과하면 다시 처음부터
        actual_index = index % len(all_questions)
        return all_questions[actual_index]

    async def generate_feedback(self, question, answer):
        """Bedrock을 사용해 답변에 대한 피드백 생성"""
        prompt = f"""당신은 친절한 개발 멘토입니다. 다음 질문과 답변을 보고 피드백을 작성해주세요.

질문: {question}
답변: {answer}

피드백 형식:
1. 먼저 답변 평가를 이모지로 표시 (✅ 좋은 답변 / ⚠️ 부분적으로 맞음 / ❌ 다시 생각해보세요)
2. 핵심 포인트 설명 (2-3줄)
3. 실무 팁 추가 (구체적인 수치나 도구 포함)
4. 추가 학습 가이드 제시

친근하고 격려하는 톤으로 작성해주세요."""

        try:
            # Claude 3 Sonnet 모델 사용
            body = json.dumps(
                {
                    "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                    "max_tokens_to_sample": 500,
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            )

            response = self.bedrock_runtime.invoke_model(
                body=body,
                modelId="anthropic.claude-instant-v1",
                accept="application/json",
                contentType="application/json",
            )

            response_body = json.loads(response.get("body").read())
            return response_body.get("completion", "피드백을 생성할 수 없습니다.")

        except Exception as e:
            print(f"Bedrock 오류: {e}")
            # 폴백 피드백
            return self.generate_fallback_feedback(answer)

    def generate_fallback_feedback(self, answer):
        """Bedrock 사용 불가시 기본 피드백"""
        if len(answer) < 20:
            return "❌ 답변이 너무 짧아요! 좀 더 자세히 설명해보세요."
        elif len(answer) > 200:
            return (
                "✅ 자세한 답변 감사합니다! 실무에서도 이런 깊이 있는 이해가 중요해요."
            )
        else:
            return "⚠️ 괜찮은 시도예요! 실무 예시를 추가하면 더 좋을 것 같아요."

    @commands.command(name="question", aliases=["문제", "q"])
    async def ask_question(self, ctx, category: str = None):
        """학습 질문 던지기"""
        # 사용 가능한 카테고리 목록
        available_categories = list(self.question_bank.keys())

        # 카테고리 검증
        if category and category not in available_categories:
            categories_str = ", ".join([f"'{cat}'" for cat in available_categories])
            await ctx.send(f"❌ 카테고리는 {categories_str} 중에서 선택해주세요.")
            return

        # 질문 생성
        q_data = self.get_random_question(category)

        # 카테고리별 색상 설정
        color_map = {
            "backend": discord.Color.orange(),
            "frontend": discord.Color.blue(),
            "general": discord.Color.green(),
        }

        # 임베드 생성
        embed = discord.Embed(
            title=f"🔥 오늘의 {q_data['category'].upper()} 질문",
            description=f"**Q. {q_data['question']}**",
            color=color_map.get(q_data["category"], discord.Color.purple()),
        )

        embed.add_field(
            name="📝 답변 방법",
            value="아래에 자동으로 생성되는 **스레드**에서 답변해주세요!",
            inline=False,
        )

        embed.set_footer(
            text=f"카테고리: {q_data['sub_category']} | 답변 후 자동으로 피드백을 받을 수 있습니다"
        )

        # 질문 메시지 전송
        question_msg = await ctx.send(embed=embed)

        # 자동으로 스레드 생성
        try:
            thread = await question_msg.create_thread(
                name=f"💬 {q_data['category']} 질문 토론",
                auto_archive_duration=1440,  # 24시간 후 자동 보관
            )

            # 스레드에 안내 메시지
            await thread.send(
                f"**이 스레드에서 답변해주세요!**\n"
                f"질문: {q_data['question']}\n\n"
                f"답변을 작성하시면 AI가 피드백을 제공합니다. 💡"
            )

            # 활성 질문으로 저장 (스레드 ID 포함)
            self.active_questions[question_msg.id] = {
                "question": q_data["question"],
                "category": q_data["category"],
                "sub_category": q_data["sub_category"],
                "asked_at": datetime.now(),
                "author_id": ctx.author.id,
                "thread_id": thread.id,
                "answered": False,
            }
        except discord.errors.Forbidden:
            # 스레드 생성 권한이 없는 경우
            # 활성 질문으로 저장 (스레드 없이)
            self.active_questions[question_msg.id] = {
                "question": q_data["question"],
                "category": q_data["category"],
                "sub_category": q_data["sub_category"],
                "asked_at": datetime.now(),
                "author_id": ctx.author.id,
                "answered": False,
            }

    @commands.Cog.listener()
    async def on_message(self, message):
        """스레드에서의 답변 감지 및 자동 피드백"""
        # 봇 메시지 무시
        if message.author.bot:
            return

        # 스레드에서의 메시지만 처리
        if isinstance(message.channel, discord.Thread):
            # 스레드 ID로 활성 질문 찾기
            thread_id = message.channel.id
            for q_id, q_info in self.active_questions.items():
                if q_info.get("thread_id") == thread_id:
                    # 스레드에서의 첫 답변만 처리
                    if not q_info.get("answered", False):
                        await self.process_answer(message, q_id, q_info)
                    return

    async def process_answer(self, message, question_id, q_info):
        """답변 처리 및 피드백 생성"""
        # 이미 답변된 질문인지 확인
        if q_info.get("answered", False):
            return

        # 답변 처리 중으로 표시
        self.active_questions[question_id]["answered"] = True

        # 피드백 생성 중 메시지
        thinking_msg = await message.reply("🤔 답변을 분석하고 있습니다...")

        try:
            # 피드백 생성
            feedback = await self.generate_feedback(q_info["question"], message.content)

            # 피드백 임베드 생성
            embed = discord.Embed(
                title="📝 피드백",
                description=feedback,
                color=discord.Color.green(),
            )

            embed.add_field(
                name="💡 다음 단계",
                value="더 많은 질문을 원하시면 `!question` 명령어를 사용하세요!",
                inline=False,
            )

            # 피드백 전송
            await thinking_msg.edit(content=None, embed=embed)

            # 답변 완료된 질문 제거
            del self.active_questions[question_id]

        except Exception as e:
            await thinking_msg.edit(
                content=f"❌ 피드백 생성 중 오류가 발생했습니다: {str(e)}"
            )

    @commands.command(name="mystats", aliases=["내점수", "stats"])
    async def show_stats(self, ctx):
        """학습 통계 보기 (향후 구현)"""
        embed = discord.Embed(
            title="📊 학습 통계",
            description="통계 기능은 곧 추가될 예정입니다!",
            color=discord.Color.purple(),
        )

        embed.add_field(
            name="🎯 목표",
            value="매일 1문제씩, 3개월이면 90문제!",
            inline=False,
        )

        await ctx.send(embed=embed)
    
    @commands.command(name="scheduler_status", aliases=["스케줄러"])
    async def scheduler_status(self, ctx):
        """스케줄러 상태 확인"""
        days_passed = (datetime.now().date() - self.start_date.date()).days
        
        embed = discord.Embed(
            title="⏰ 스케줄러 상태",
            description=f"매일 오전 10시에 자동으로 질문이 게시됩니다.",
            color=discord.Color.blue(),
        )
        
        embed.add_field(
            name="📅 현재 상태",
            value=f"- 시작일: {self.start_date.date()}\n"
                  f"- 경과일: Day {days_passed + 1}\n"
                  f"- 오늘의 인덱스: {days_passed}\n"
                  f"- 오늘 게시될 카테고리: Backend, Frontend, General (3개 모두)",
            inline=False,
        )
        
        embed.add_field(
            name="🔄 스케줄러 상태",
            value=f"실행 중: {'✅' if self.daily_question.is_running() else '❌'}",
            inline=False,
        )
        
        embed.add_field(
            name="📊 질문 게시 정보",
            value=f"- 매일 3개의 질문 게시 (Backend, Frontend, General)\n"
                  f"- 각 카테고리는 순차적으로 진행\n"
                  f"- 모든 질문을 다 돌면 처음부터 다시 시작",
            inline=False,
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="post_daily", aliases=["일일질문"])
    @commands.has_permissions(administrator=True)
    async def post_daily_question(self, ctx):
        """수동으로 일일 질문 게시 (관리자 전용)"""
        await self.daily_question()
        await ctx.send("✅ 일일 질문이 게시되었습니다!")
    
    @tasks.loop(hours=24)
    async def daily_question(self):
        """매일 오전 10시에 질문 자동 게시"""
        if not self.allowed_channel_id:
            print("❌ ALLOWED_CHANNEL_ID가 설정되지 않아 스케줄러를 실행할 수 없습니다.")
            return
            
        channel = self.bot.get_channel(self.allowed_channel_id)
        if not channel:
            print(f"❌ 채널 {self.allowed_channel_id}를 찾을 수 없습니다.")
            return
        
        # 시작일로부터 경과한 일수 계산
        days_passed = (datetime.now().date() - self.start_date.date()).days
        
        # 세 가지 카테고리 모두 처리
        categories = ["backend", "frontend", "general"]
        
        for category_type in categories:
            # 각 카테고리별로 인덱스 계산
            category_index = days_passed
            
            # 인덱스 기반으로 질문 가져오기
            q_data = self.get_question_by_index(category_index, category_type)
            
            if not q_data:
                print(f"❌ {category_type} 카테고리에서 질문을 가져올 수 없습니다.")
                continue
            
            # 카테고리별 색상 설정
            color_map = {
                "backend": discord.Color.orange(),
                "frontend": discord.Color.blue(),
                "general": discord.Color.green(),
            }
            
            # 카테고리별 이모지
            emoji_map = {
                "backend": "🔧",
                "frontend": "🎨",
                "general": "💡",
            }
            
            # 임베드 생성
            embed = discord.Embed(
                title=f"{emoji_map.get(category_type, '🌅')} 오늘의 {q_data['category'].upper()} 질문 (Day {days_passed + 1})",
                description=f"**Q. {q_data['question']}**",
                color=color_map.get(q_data["category"], discord.Color.purple()),
            )
            
            embed.add_field(
                name="📝 답변 방법",
                value="아래에 자동으로 생성되는 **스레드**에서 답변해주세요!",
                inline=False,
            )
            
            embed.set_footer(
                text=f"카테고리: {q_data['sub_category']} | 인덱스: {category_index} | 답변 후 자동으로 피드백을 받을 수 있습니다"
            )
            
            # 질문 메시지 전송
            question_msg = await channel.send(embed=embed)
            
            # 자동으로 스레드 생성
            try:
                thread = await question_msg.create_thread(
                    name=f"💬 Day {days_passed + 1} - {q_data['category']} 질문",
                    auto_archive_duration=1440,  # 24시간 후 자동 보관
                )
                
                # 스레드에 안내 메시지
                await thread.send(
                    f"**📅 Day {days_passed + 1} 질문입니다!**\n"
                    f"질문: {q_data['question']}\n\n"
                    f"답변을 작성하시면 AI가 피드백을 제공합니다. 💡"
                )
                
                # 활성 질문으로 저장
                self.active_questions[question_msg.id] = {
                    "question": q_data["question"],
                    "category": q_data["category"],
                    "sub_category": q_data["sub_category"],
                    "asked_at": datetime.now(),
                    "author_id": self.bot.user.id,  # 봇이 질문한 것으로 표시
                    "thread_id": thread.id,
                    "answered": False,
                    "scheduled": True,  # 스케줄러로 생성된 질문 표시
                }
                
                print(f"✅ Day {days_passed + 1} {category_type} 질문이 게시되었습니다.")
                
            except discord.errors.Forbidden:
                print("❌ 스레드 생성 권한이 없습니다.")
            except Exception as e:
                print(f"❌ 스케줄러 오류: {e}")
            
            # 질문 간 약간의 딜레이 (스팸 방지)
            await discord.utils.sleep_until(datetime.now() + timedelta(seconds=2))
    
    @daily_question.before_loop
    async def before_daily_question(self):
        """스케줄러 시작 전 봇이 준비될 때까지 대기"""
        await self.bot.wait_until_ready()
        
        # 다음 10시까지 대기
        now = datetime.now()
        next_run = now.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # 만약 현재 시간이 10시를 지났다면 다음날 10시로 설정
        if now.hour >= 10:
            next_run += timedelta(days=1)
            
        wait_seconds = (next_run - now).total_seconds()
        print(f"⏰ 스케줄러가 {next_run}에 시작됩니다. ({wait_seconds:.0f}초 대기)")
        
        # 대기
        await discord.utils.sleep_until(next_run)
    
    def cog_unload(self):
        """Cog이 언로드될 때 스케줄러 중지"""
        self.daily_question.cancel()


async def setup(bot):
    await bot.add_cog(Study(bot))
