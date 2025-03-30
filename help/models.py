# from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Question(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='question', on_delete=models.CASCADE)
    answer_id = models.CharField(max_length=8)
    answer = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.question.title

class ReportQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    details = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question.title

class ReportAnswer(models.Model):
    answer = models.ForeignKey(Answer, related_name='answer', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer')
    details = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.answer.question.title
