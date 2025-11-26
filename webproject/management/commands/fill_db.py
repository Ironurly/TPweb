import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from django.db.models import Count, Q
from webproject.models import UserProfile, Question, Answer, Tag, QuestionLikes, AnswerLikes

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
        num_answers = count * 100

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
                author=random.choice(users),
                likes=0,
                answers_count=0,
                is_active=True
            )
            
            question_tags = random.sample(tags, random.randint(1, 5))
            question.tags.set(question_tags)
            questions.append(question)

        self.stdout.write(self.style.SUCCESS(f"Создано вопросов: {len(questions)}"))

        answers = []
        for i in range(num_answers):
            question = random.choice(questions)
            answer = Answer.objects.create(
                title=fake.sentence()[:250],
                body=fake.text(max_nb_chars=2000),
                author=random.choice(users),
                question=question,
                likes=0,
                is_correct=fake.boolean(chance_of_getting_true=15),
                is_active=True
            )
            answers.append(answer)

        self.stdout.write(self.style.SUCCESS(f"Создано ответов: {len(answers)}"))

        question_likes_created = 0
        for question in questions:
            likers = random.sample(users, random.randint(0, min(20, len(users))))
            for liker in likers:
                try:
                    QuestionLikes.objects.create(
                        question=question,
                        user=liker,
                        reaction = random.choice([
                            QuestionLikes.LIKE, 
                            QuestionLikes.DISLIKE, 
                        ])
                    )
                    question_likes_created += 1
                except:
                    pass

        self.stdout.write(self.style.SUCCESS(f"Создано лайков вопросов: {question_likes_created}"))

        answer_likes_created = 0
        for answer in answers:
            likers = random.sample(users, random.randint(0, min(15, len(users))))
            for liker in likers:
                try:
                    AnswerLikes.objects.create(
                        answer=answer,
                        user=liker,
                        reaction = random.choice([
                            QuestionLikes.LIKE, 
                            QuestionLikes.DISLIKE, 
                        ])
                    )
                    answer_likes_created += 1
                except:
                    pass

        self.stdout.write(self.style.SUCCESS(f"Создано лайков комментариев: {answer_likes_created}"))

        self.stdout.write("Обновление счетчиков...")
        
        questions_to_update = []
        question_ids = [q.id for q in questions]
        
        question_likes_data = QuestionLikes.objects.filter(
            question_id__in=question_ids
        ).values('question_id').annotate(
            likes=Count('id', filter=Q(reaction=QuestionLikes.LIKE)),
            dislikes=Count('id', filter=Q(reaction=QuestionLikes.DISLIKE))
        )
        
        question_likes_dict = {
            item['question_id']: item['likes'] - item['dislikes'] 
            for item in question_likes_data
        }
        
        for question in questions:
            question.likes = question_likes_dict.get(question.id, 0)
            questions_to_update.append(question)
        
        Question.objects.bulk_update(questions_to_update, ['likes'])
    
        answers_to_update = []
        answer_ids = [a.id for a in answers]
        
        answer_likes_data = AnswerLikes.objects.filter(
            answer_id__in=answer_ids
        ).values('answer_id').annotate(
            likes=Count('id', filter=Q(reaction=AnswerLikes.LIKE)),
            dislikes=Count('id', filter=Q(reaction=AnswerLikes.DISLIKE))
        )
        
        answer_likes_dict = {
            item['answer_id']: item['likes'] - item['dislikes'] 
            for item in answer_likes_data
        }
        
        for answer in answers:
            answer.likes = answer_likes_dict.get(answer.id, 0)
            answers_to_update.append(answer)
        
        Answer.objects.bulk_update(answers_to_update, ['likes'])
        
        questions_for_answers_update = []
        
        answers_count_data = Answer.objects.filter(
            question_id__in=question_ids,
            is_active=True
        ).values('question_id').annotate(count=Count('id'))
        
        answers_count_dict = {
            item['question_id']: item['count'] 
            for item in answers_count_data
        }
        
        for question in questions:
            question.answers_count = answers_count_dict.get(question.id, 0)
            questions_for_answers_update.append(question)
        
        Question.objects.bulk_update(questions_for_answers_update, ['answers_count'])

        self.stdout.write(self.style.SUCCESS("Все данные успешно сгенерированы!"))
        self.stdout.write(self.style.SUCCESS(f"Итоговая статистика:"))
        self.stdout.write(self.style.SUCCESS(f"Пользователи: {User.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Теги: {Tag.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Вопросы: {Question.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Комментарии: {Answer.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Лайки вопросов: {QuestionLikes.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Лайки комментариев: {AnswerLikes.objects.count()}"))