import json
import os
import random
from datetime import datetime
from pathlib import Path

import boto3
import discord
from discord.ext import commands


class Study(commands.Cog):
    """학습 질문 및 피드백 시스템"""

    def __init__(self, bot):
        self.bot = bot
        self.active_questions = {}  # 활성 질문 추적

        # AWS Bedrock 클라이언트 초기화
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        # JSON 파일에서 질문 데이터베이스 로드
        self.question_bank = self.load_questions()

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


async def setup(bot):
    await bot.add_cog(Study(bot))
