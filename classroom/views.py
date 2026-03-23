import json
import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import (
    Classroom, Enrollment, Test, Question,
    TestSubmission, Answer, UserProfile
)
from .forms import SignUpForm, ClassroomForm, JoinClassroomForm, TestForm, QuestionForm
from .nlp_engine import evaluate_answer, evaluate_submission


# ─────────────────────────── Helpers ───────────────────────────

def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile

def is_teacher(user):
    try:
        return user.userprofile.is_teacher
    except Exception:
        return False

def generate_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Classroom.objects.filter(code=code).exists():
            return code


# ─────────────────────────── Public Views ───────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'classroom/home.html')


def student_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            profile = UserProfile.objects.create(
                user=user,
                is_teacher=False
            )
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Student account created successfully.')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'classroom/student_signup.html', {'form': form})

def teacher_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            profile = UserProfile.objects.create(
                user=user,
                is_teacher=True
            )
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Teacher account created successfully.')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'classroom/teacher_signup.html', {'form': form})


# ─────────────────────────── Dashboard ───────────────────────────

@login_required
def dashboard(request):
    profile = get_or_create_profile(request.user)
    if profile.is_teacher:
        classrooms = Classroom.objects.filter(owner=request.user).prefetch_related('tests', 'enrollments')
        return render(request, 'classroom/teacher_dashboard.html', {
            'classrooms': classrooms,
            'total_students': sum(c.enrollments.count() for c in classrooms),
            'total_tests': sum(c.tests.count() for c in classrooms),
        })
    else:
        enrollments = Enrollment.objects.filter(student=request.user).select_related('room')
        classrooms = [e.room for e in enrollments]
        # Get all submissions
        submissions = TestSubmission.objects.filter(student=request.user).select_related('test')
        return render(request, 'classroom/student_dashboard.html', {
            'classrooms': classrooms,
            'submissions': submissions,
        })


# ─────────────────────────── Teacher Views ───────────────────────────

@login_required
def create_classroom(request):
    if not is_teacher(request.user):
        messages.error(request, 'Only teachers can create classrooms.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.owner = request.user
            classroom.code = generate_code()
            classroom.save()
            messages.success(request, f'Classroom "{classroom.name}" created! Code: {classroom.code}')
            return redirect('view_classroom', pk=classroom.pk)
    else:
        form = ClassroomForm()
    return render(request, 'classroom/create_classroom.html', {'form': form})


@login_required
def view_classroom(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if classroom.owner != request.user and not Enrollment.objects.filter(room=classroom, student=request.user).exists():
        messages.error(request, 'You do not have access to this classroom.')
        return redirect('dashboard')
    tests = classroom.tests.all()
    students = classroom.enrollments.select_related('student')
    return render(request, 'classroom/view_classroom.html', {
        'classroom': classroom,
        'tests': tests,
        'students': students,
        'is_owner': classroom.owner == request.user,
    })


@login_required
def create_test(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.classroom = classroom
            test.save()
            messages.success(request, f'Test "{test.name}" created! Now add questions.')
            return redirect('add_question', pk=test.pk)
    else:
        form = TestForm()
    return render(request, 'classroom/create_test.html', {'form': form, 'classroom': classroom})


@login_required
def view_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    profile = get_or_create_profile(request.user)
    questions = test.questions.all()

    if profile.is_teacher:
        submission_count = test.submissions.count()
        return render(request, 'classroom/teacher_test_view.html', {
            'test': test,
            'questions': questions,
            'submission_count': submission_count,
        })
    else:
        # Check enrollment
        if not Enrollment.objects.filter(room=test.classroom, student=request.user).exists():
            messages.error(request, 'You are not enrolled in this classroom.')
            return redirect('dashboard')
        # Check if already submitted
        existing = TestSubmission.objects.filter(test=test, student=request.user).first()
        return render(request, 'classroom/student_test_view.html', {
            'test': test,
            'questions': questions,
            'existing_submission': existing,
        })


@login_required
def add_question(request, pk):
    test = get_object_or_404(Test, pk=pk, classroom__owner=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.test = test
            q.order = test.questions.count() + 1
            q.save()
            if 'add_another' in request.POST:
                messages.success(request, 'Question added! Add another.')
                return redirect('add_question', pk=test.pk)
            messages.success(request, 'Question added!')
            return redirect('view_test', pk=test.pk)
    else:
        form = QuestionForm()
    return render(request, 'classroom/add_question.html', {
        'form': form,
        'test': test,
        'questions': test.questions.all(),
    })


@login_required
def students_work(request, pk):
    test = get_object_or_404(Test, pk=pk, classroom__owner=request.user)
    submissions = test.submissions.select_related('student').prefetch_related('answers__question')
    return render(request, 'classroom/students_work.html', {
        'test': test,
        'submissions': submissions,
    })


@login_required
def review_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk, question__test__classroom__owner=request.user)
    result = evaluate_answer(answer.answer_text, answer.question.reference_answer, answer.question.max_score)
    return render(request, 'classroom/review_answer.html', {
        'answer': answer,
        'result': result,
    })


@login_required
@require_POST
def update_score(request, pk):
    answer = get_object_or_404(Answer, pk=pk, question__test__classroom__owner=request.user)
    try:
        score = float(request.POST.get('score', answer.ml_score))
        score = max(0, min(score, answer.question.max_score))
        answer.teacher_score = score
        answer.save()
        # Update submission totals
        sub = answer.submission
        sub.teacher_total = sum(
            (a.teacher_score if a.teacher_score is not None else a.ml_score)
            for a in sub.answers.all()
        )
        sub.is_reviewed = all(a.teacher_score is not None for a in sub.answers.all())
        sub.save()
        messages.success(request, 'Score updated.')
    except ValueError:
        messages.error(request, 'Invalid score.')
    return redirect('students_work', pk=answer.submission.test.pk)


# ─────────────────────────── Student Views ───────────────────────────

@login_required
def join_classroom(request):
    if is_teacher(request.user):
        messages.error(request, 'Teachers cannot join classrooms.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = JoinClassroomForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].upper()
            try:
                classroom = Classroom.objects.get(code=code)
                _, created = Enrollment.objects.get_or_create(room=classroom, student=request.user)
                if created:
                    messages.success(request, f'Joined "{classroom.name}" successfully!')
                else:
                    messages.info(request, f'You are already enrolled in "{classroom.name}".')
                return redirect('view_classroom', pk=classroom.pk)
            except Classroom.DoesNotExist:
                messages.error(request, 'Invalid classroom code.')
    else:
        form = JoinClassroomForm()
    return render(request, 'classroom/join_classroom.html', {'form': form})


@login_required
def attend_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if not Enrollment.objects.filter(room=test.classroom, student=request.user).exists():
        messages.error(request, 'You are not enrolled in this classroom.')
        return redirect('dashboard')
    if TestSubmission.objects.filter(test=test, student=request.user).exists():
        messages.info(request, 'You have already submitted this test.')
        return redirect('test_result', pk=test.pk)
    questions = test.questions.all()
    return render(request, 'classroom/attend_test.html', {'test': test, 'questions': questions})


@login_required
@require_POST
def submit_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if TestSubmission.objects.filter(test=test, student=request.user).exists():
        messages.warning(request, 'You already submitted this test.')
        return redirect('test_result', pk=test.pk)

    submission = TestSubmission.objects.create(test=test, student=request.user)
    questions = test.questions.all()
    total_ml = 0

    for question in questions:
        student_answer = request.POST.get(f'answer_{question.pk}', '').strip()
        result = evaluate_answer(student_answer, question.reference_answer, question.max_score)
        answer = Answer.objects.create(
            submission=submission,
            question=question,
            answer_text=student_answer,
            ml_score=result['score'],
            similarity_score=result['similarity'],
            keyword_score=result['keyword_coverage'],
        )
        total_ml += result['score']

    submission.ml_total = round(total_ml, 2)
    submission.save()
    messages.success(request, 'Test submitted successfully!')
    return redirect('test_result', pk=test.pk)


@login_required
def test_result(request, pk):
    test = get_object_or_404(Test, pk=pk)
    submission = get_object_or_404(TestSubmission, test=test, student=request.user)
    answers = submission.answers.select_related('question').all()
    detailed = []
    for answer in answers:
        result = evaluate_answer(answer.answer_text, answer.question.reference_answer, answer.question.max_score)
        detailed.append({'answer': answer, 'result': result})
    return render(request, 'classroom/test_result.html', {
        'test': test,
        'submission': submission,
        'detailed': detailed,
    })


# ─────────────────────────── API Views ───────────────────────────

@csrf_exempt
def evaluate_answer_api(request):
    """REST API endpoint to evaluate a single answer."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        student_answer = data.get('student_answer', '')
        reference_answer = data.get('reference_answer', '')
        max_score = int(data.get('max_score', 10))
        result = evaluate_answer(student_answer, reference_answer, max_score)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
