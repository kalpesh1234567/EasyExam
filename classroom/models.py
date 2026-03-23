from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({'Teacher' if self.is_teacher else 'Student'})"


class Classroom(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classrooms')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=6, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    class Meta:
        unique_together = (('room', 'student'),)

    room = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} in {self.room.name}"


class Test(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='tests')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def is_ongoing(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    @property
    def total_marks(self):
        return sum(q.max_score for q in self.questions.all())


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    reference_answer = models.TextField()
    max_score = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text[:60]


class TestSubmission(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    ml_total = models.FloatField(default=0)
    teacher_total = models.FloatField(null=True, blank=True)
    is_reviewed = models.BooleanField(default=False)

    class Meta:
        unique_together = (('test', 'student'),)

    def __str__(self):
        return f"{self.student.username} - {self.test.name}"

    @property
    def final_score(self):
        return self.teacher_total if self.teacher_total is not None else self.ml_total

    @property
    def percentage(self):
        total = self.test.total_marks
        if total == 0:
            return 0
        return round((self.final_score / total) * 100, 1)

    @property
    def grade(self):
        p = self.percentage
        if p >= 90: return 'A+'
        if p >= 80: return 'A'
        if p >= 70: return 'B'
        if p >= 60: return 'C'
        if p >= 50: return 'D'
        return 'F'


class Answer(models.Model):
    submission = models.ForeignKey(TestSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    ml_score = models.FloatField(default=0)
    teacher_score = models.FloatField(null=True, blank=True)
    similarity_score = models.FloatField(default=0)
    keyword_score = models.FloatField(default=0)

    def __str__(self):
        return f"Answer by {self.submission.student.username} for Q{self.question.id}"

    @property
    def final_score(self):
        return self.teacher_score if self.teacher_score is not None else self.ml_score
