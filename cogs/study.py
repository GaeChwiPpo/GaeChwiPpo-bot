import json
import os
import random
from datetime import datetime

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

        # 질문 데이터베이스
        self.question_bank = {
            "backend": {
                "database": [
                    "데이터베이스 커넥션 풀이 왜 필요한가요? 실무에서 어떻게 설정하시나요?",
                    "인덱스를 추가했는데 오히려 성능이 느려졌습니다. 가능한 원인은?",
                    "트랜잭션 격리 레벨 중 READ COMMITTED와 REPEATABLE READ의 차이점은?",
                    "데이터베이스 샤딩과 레플리케이션의 차이점을 설명해주세요.",
                    "N+1 쿼리 문제란 무엇이고 어떻게 해결하나요?",
                ],
                "api": [
                    "API 응답 시간이 5초 걸립니다. 어떤 순서로 체크하시겠습니까?",
                    "REST API와 GraphQL의 장단점을 비교해주세요.",
                    "API 버전 관리 전략에는 어떤 것들이 있나요?",
                    "Rate Limiting은 왜 필요하고 어떻게 구현하나요?",
                    "JWT vs Session 기반 인증의 차이점은?",
                ],
                "architecture": [
                    "마이크로서비스 vs 모놀리식, 언제 무엇을 선택하나요?",
                    "이벤트 드리븐 아키텍처의 장단점은?",
                    "CQRS 패턴은 언제 사용하면 좋을까요?",
                    "서킷 브레이커 패턴을 설명하고 언제 사용하나요?",
                    "캐시 전략 중 Cache-Aside vs Write-Through의 차이는?",
                ],
            },
            "frontend": {
                "react": [
                    "React 렌더링이 느립니다. 어떻게 최적화하나요?",
                    "useState vs useReducer, 언제 무엇을 사용하나요?",
                    "React.memo와 useMemo의 차이점은?",
                    "Virtual DOM이 실제로 성능에 도움이 되나요?",
                    "useEffect의 dependency array를 빈 배열로 두면 어떤 일이 생기나요?",
                ],
                "performance": [
                    "번들 사이즈가 3MB입니다. 줄이는 방법은?",
                    "첫 화면 로딩이 느립니다. 개선 방법은?",
                    "이미지 최적화 방법들을 설명해주세요.",
                    "Code Splitting은 어떻게 구현하나요?",
                    "Web Vitals 중 LCP를 개선하는 방법은?",
                ],
                "state": [
                    "Redux vs Zustand vs Jotai, 각각 언제 사용하나요?",
                    "Props Drilling 문제를 해결하는 방법들은?",
                    "상태 정규화(normalization)는 왜 필요한가요?",
                    "Optimistic Update는 어떻게 구현하나요?",
                    "전역 상태 vs 로컬 상태를 구분하는 기준은?",
                ],
            },
        }

    def get_random_question(self, category=None):
        """랜덤 질문 선택"""
        if category and category in ["backend", "frontend"]:
            main_category = self.question_bank[category]
        else:
            # 랜덤 카테고리 선택
            category = random.choice(["backend", "frontend"])
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
        # 카테고리 검증
        if category and category not in ["backend", "frontend", None]:
            await ctx.send("❌ 카테고리는 'backend' 또는 'frontend'만 가능합니다.")
            return

        # 질문 생성
        q_data = self.get_random_question(category)

        # 임베드 생성
        embed = discord.Embed(
            title=f"🔥 오늘의 {q_data['category'].upper()} 질문",
            description=f"**Q. {q_data['question']}**",
            color=(
                discord.Color.orange()
                if q_data["category"] == "backend"
                else discord.Color.blue()
            ),
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
