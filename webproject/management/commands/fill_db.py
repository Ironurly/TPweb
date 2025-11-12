import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker

from webproject.models import UserProfile, Question, Comment, Tag, QuestionLikes, CommentLikes

class Command(BaseCommand):
    help = "Заполнение БД тестовыми данными"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Базовое количество для генерации данных')

    def handle(self, *args, **options):
        count = options.get('count')
        fake = Faker('ru_RU')

        # Расчет количества объектов
        num_users = count
        num_tags = count 
        num_questions = count * 10
        num_comments = count * 100

        self.stdout.write(f"Начинаем генерацию данных с базовым count={count}...")

        users = []
        for i in range(num_users):
            user, created = User.objects.get_or_create(
                username=f"user_{i}",
                defaults={
                    'email': fake.email(),
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            if created:
                user.set_password("123456")
                user.save()

            user_profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'avatar': None,
                    'bio': fake.text(max_nb_chars=2000),
                }
            )
            users.append(user)
        
        self.stdout.write(self.style.SUCCESS(f"Создано пользователей: {len(users)}"))

        tags = []
        seen_tags = set()

        while len(tags) < num_tags:
            tag_name = fake.word() + "_" + fake.word()
            if tag_name in seen_tags:
                continue
            tag, created = Tag.objects.get_or_create(title=tag_name)
            if created:
                tags.append(tag)
                seen_tags.add(tag_name)
        
        self.stdout.write(self.style.SUCCESS(f"Создано тегов: {len(tags)}"))

        questions = []
        for i in range(num_questions):
            question = Question.objects.create(
                title=fake.sentence()[:250],
                body=fake.text(max_nb_chars=3000),
                author_id=random.choice(users),
                likes=0,
                answers=0,
                is_active=True
            )
            
            question_tags = random.sample(tags, random.randint(1, 5))
            question.tags.set(question_tags)
            questions.append(question)

        self.stdout.write(self.style.SUCCESS(f"Создано вопросов: {len(questions)}"))

        comments = []
        for i in range(num_comments):
            question = random.choice(questions)
            comment = Comment.objects.create(
                title=fake.sentence()[:250],
                body=fake.text(max_nb_chars=2000),
                author_id=random.choice(users),
                question_id=question,
                likes=0,
                is_correct=fake.boolean(chance_of_getting_true=15),
                is_active=True
            )
            comments.append(comment)

        self.stdout.write(self.style.SUCCESS(f"Создано комментариев: {len(comments)}"))

        question_likes_created = 0
        for question in questions:
            likers = random.sample(users, random.randint(0, min(20, len(users))))
            for liker in likers:
                try:
                    QuestionLikes.objects.create(
                        question_id=question,
                        user_id=liker,
                        status=random.choice([True, False, None])
                    )
                    question_likes_created += 1
                except:
                    pass

        self.stdout.write(self.style.SUCCESS(f"Создано лайков вопросов: {question_likes_created}"))

        comment_likes_created = 0
        for comment in comments:
            likers = random.sample(users, random.randint(0, min(15, len(users))))
            for liker in likers:
                try:
                    CommentLikes.objects.create(
                        comment_id=comment,
                        user_id=liker,
                        status=random.choice([True, False, None])
                    )
                    comment_likes_created += 1
                except:
                    pass

        self.stdout.write(self.style.SUCCESS(f"Создано лайков комментариев: {comment_likes_created}"))

        self.stdout.write("Обновление счетчиков...")
        
        for question in questions:
            likes_count = QuestionLikes.objects.filter(
                question_id=question, 
                status=True
            ).count()
            dislikes_count = QuestionLikes.objects.filter(
                question_id=question, 
                status=False
            ).count()
            question.likes = likes_count - dislikes_count
            question.save()

        for comment in comments:
            likes_count = CommentLikes.objects.filter(
                comment_id=comment, 
                status=True
            ).count()
            dislikes_count = CommentLikes.objects.filter(
                comment_id=comment, 
                status=False
            ).count()
            comment.likes = likes_count - dislikes_count
            comment.save()
        
        for question in questions:
            answers_count = Comment.objects.filter(
                question_id=question, 
                is_active=True
            ).count()
            question.answers = answers_count
            question.save()

        self.stdout.write(self.style.SUCCESS("Все данные успешно сгенерированы!"))
        self.stdout.write(self.style.SUCCESS(f"Итоговая статистика:"))
        self.stdout.write(self.style.SUCCESS(f"Пользователи: {User.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Теги: {Tag.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Вопросы: {Question.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Комментарии: {Comment.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Лайки вопросов: {QuestionLikes.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Лайки комментариев: {CommentLikes.objects.count()}"))