from django.contrib import admin
from .models import UserProfile, Classroom, Enrollment, Test, Question, TestSubmission, Answer

admin.site.register(UserProfile)
admin.site.register(Classroom)
admin.site.register(Enrollment)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(TestSubmission)
admin.site.register(Answer)
