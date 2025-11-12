from webproject.models import Question
from django.db.models import Q

class QuestionManager():

    def get_hot_questions(self):
        return Question.objects.all().order_by('-likes')

    def get_new_questions(self):
        return Question.objects.all().order_by('-created_at')
    
    def get_tagged_questions(self, tag):
        if not tag:
            questions = Question.objects.all()
        else:
            questions = Question.objects.all().filter(Q(tags__title = tag))
        
        return questions.order_by("-created_at")
    
    def get_question_by_id(self, id):
        return Question.objects.get(id = id)