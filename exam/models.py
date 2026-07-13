from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import User


class Section(models.Model):
    """
    Example:
    Django Basics
    Models
    Views
    REST Framework
    Authentication
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Question(models.Model):

    DIFFICULTY = (
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question = models.TextField()

    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY,
        default="easy"
    )

    marks = models.PositiveIntegerField(default=1)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:60]


class Option(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options"
    )

    option_text = models.CharField(max_length=500)

    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text


class Exam(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    sections = models.ManyToManyField(Section)

    total_marks = models.PositiveIntegerField(default=0)

    duration = models.PositiveIntegerField(
        help_text="Duration in Minutes"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class UserExam(models.Model):

    STATUS = (
        ("started", "Started"),
        ("submitted", "Submitted"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )

    score = models.PositiveIntegerField(default=0)

    total_questions = models.PositiveIntegerField(default=0)

    correct_answers = models.PositiveIntegerField(default=0)

    wrong_answers = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="started"
    )

    started_at = models.DateTimeField(auto_now_add=True)

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ("user", "exam")

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"


class UserAnswer(models.Model):

    user_exam = models.ForeignKey(
        UserExam,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    selected_option = models.ForeignKey(
        Option,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_correct = models.BooleanField(default=False)

    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user_exam", "question")

    def __str__(self):
        return f"{self.user_exam.user.username} - {self.question.id}"



