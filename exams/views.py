import math
import re

from django.shortcuts import render
from django.contrib.auth import get_user, get_user_model
from exams.models import Exam, Test, SPLIT_LEVEL_1
from django.shortcuts import redirect

from datetime import datetime


def parse_for_exam(post_request):
    name = post_request.get('name')
    error_msgs = []
    if not name:
        error_msgs.append('The exam does not have name!')

    time = post_request.get('time')
    if not time:
        error_msgs.append('The exam does not have time!')
    elif not re.search("^([0-1][0-9]:[0-5][0-9]:[0-5][0-9])|(2[0-3]:[0-5][0-9]:[0-5][0-9])|(24:00:00)$", time):
        error_msgs.append('The exam does not have true time format!')

    number_of_questions = post_request.get('number_of_questions')
    if not (number_of_questions and re.search("^[0-9]+$", number_of_questions) and int(number_of_questions)):
        error_msgs.append('The exam is empty!')
        return error_msgs, {'name': name, 'time': time, 'questions': [], 'optional_answers': [], 'correct_answers': []}

    questions: list[str] = []
    optional_answers: list[list[str]] = []
    correct_answers: list[str] = []
    for order_of_question in range(1, int(number_of_questions) + 1):
        question = post_request.get(f'question_{order_of_question}')
        if question:
            questions.append(question)
        else:
            error_msgs.append(f'The question {order_of_question} is empty!')
            questions.append('')

        number_of_options = post_request.get(f'number_of_options_{order_of_question}')
        if number_of_options and number_of_options in ["2", "3", "4", "5"]:
            options = []
            for order_of_option in range(1, int(number_of_options) + 1):
                option = post_request.get(f'option_{order_of_question}_{order_of_option}')
                if option:
                    if option in options:
                        error_msgs.append(
                            f'The option of optional answer {order_of_option} ' + f'of question {order_of_question} is duplicate!')
                    options.append(option)
                else:
                    error_msgs.append(
                        f'The option of optional answer {order_of_option} ' + f'of question {order_of_question} is empty!')
                    options.append('')
            optional_answers.append(options)
        else:
            error_msgs.append(f'Number of optional answer of question {order_of_question} is invalid! (must from 2 to 5)')
            optional_answers.append([])

        correct_answer = post_request.get(f'correct_answer_{order_of_question}')
        if correct_answer:
            correct_answers.append(correct_answer)
        else:
            error_msgs.append(f'The correct answer of question {order_of_question} is empty!')
            correct_answers.append('')

    return error_msgs, {'name': name, 'time': time, 'questions': questions, 'optional_answers': optional_answers,
                        'correct_answers': correct_answers}


# exams/exams
CAN_DO_TYPE = 1
DID_TYPE = 2
CREATED_TYPE = 3


def get_params_of_read_exams__get(get_request):
    direction = get_request.get('direction')
    direction = int(direction) if direction and re.search("^-*[0-9]+$", direction) else 0

    page_number = get_request.get('page')
    page_number = int(page_number) if page_number and re.search("^[0-9]+$", page_number) else 1

    _type = get_request.get('type')
    _type = int(_type) if _type and (re.search("^[0-9]+$", _type) and 1 <= int(_type) <= 3) else CAN_DO_TYPE

    return _type, direction, page_number


def compute_read_exams_context__get(direction, exams, page_number):
    exam_count = len(exams)

    max_exam_quartet_index = math.ceil(exam_count / 4)

    if direction == 1:
        if page_number < max_exam_quartet_index:
            page_number += 1
    elif direction == -1:
        if 1 < page_number:
            page_number -= 1

    User = get_user_model()
    response_exams = []
    range_response_exams = range((page_number - 1) * 4, min(exam_count, page_number * 4))
    for i in range_response_exams:
        author = User.objects.filter(id=exams[i]['created_by_id']).values()[0]
        exams[i]['author'] = f"{author['name']} ({author['code']})"
        response_exams.append(exams[i])

    up_of_range_exam_quartet_index = min(page_number + 2, max_exam_quartet_index)
    down_of_range_exam_quartet_index = max(1, up_of_range_exam_quartet_index - 2)
    range_exam_quartet_index = range(down_of_range_exam_quartet_index, up_of_range_exam_quartet_index + 1)

    return max_exam_quartet_index, page_number, range_exam_quartet_index, response_exams


def read_exams__get(request):
    _type, direction, page_number = get_params_of_read_exams__get(request.GET)

    if request.user.is_authenticated:
        if _type == CREATED_TYPE:
            exams = Exam.objects.filter(created_by=request.user.id).order_by('-id').values()

            count = len(exams)

            max_quartet_index, page_number, range_quartet_index, exams = compute_read_exams_context__get(direction, exams, page_number)

            return render(request, template_name='exams/exams.html', context={
                'number_of_exam': count,
                'exams': exams,
                'type': 3,
                'current_exam_quartet_index': page_number,
                'max_exam_quartet_index': max_quartet_index,
                'range_exam_quartet_index': range_quartet_index,
                'can_create': True,
                'can_set_constraints': True,
                'can_edit': True,
            })

        elif _type == DID_TYPE:
            tests = Test.objects.filter(created_by=request.user.id).order_by('-id').values('exam_id', 'score')
            did_exam_ids = []
            test_scores = []
            for test in tests:
                if test['exam_id'] not in did_exam_ids:
                    did_exam_ids.append(test['exam_id'])
                    test_scores.append(test['score'])

            temp_exams = Exam.objects.filter(id__in=did_exam_ids).order_by('-id').values()

            exams = []
            for i in range(len(did_exam_ids)):
                for exam in temp_exams:
                    if exam['id'] == did_exam_ids[i]:
                        exam['your_score'] = str(test_scores[i])
                        exams.append(exam)
                        break

            count = len(exams)

            max_quartet_index, page_number, range_quartet_index, exams = compute_read_exams_context__get(direction, exams, page_number)

            return render(request, template_name='exams/exams.html', context={
                'number_of_exam': count,
                'exams': exams,
                'type': 2,
                'current_exam_quartet_index': page_number,
                'max_exam_quartet_index': max_quartet_index,
                'range_exam_quartet_index': range_quartet_index,
                'can_view_last_do': True,
                'score': request.GET.get('score'),
                'exam_code_number': request.GET.get('exam_code_number', ''),
            })

        else:  # _type == CAN_DO_TYPE:
            tests = Test.objects.filter(created_by=request.user.id).values_list('exam_id')
            did_exam_ids = [test[0] for test in tests]

            temp_exams = Exam.objects \
                .filter(begin_on__lte=datetime.utcnow(),
                        end_on__gte=datetime.utcnow(),) \
                .exclude(id__in=did_exam_ids) \
                .order_by('-id') \
                .values()
            # .filter(begin_on__lt=datetime.now(timezone.utc), end_on__gt=datetime.now(timezone.utc)) \

            exams = []
            User = get_user_model()
            user_code = User.objects.filter(id=request.user.id).first().code
            for exam in temp_exams:
                if not exam['_user_codes'] or user_code in exam['_user_codes'].split(SPLIT_LEVEL_1):
                    exams.append(exam)

            count = len(exams)

            max_quartet_index, page_number, range_quartet_index, exams = compute_read_exams_context__get(direction, exams, page_number)

            return render(request, template_name='exams/exams.html', context={
                'number_of_exam': count,
                'exams': exams,
                'type': 1,
                'current_exam_quartet_index': page_number,
                'max_exam_quartet_index': max_quartet_index,
                'range_exam_quartet_index': range_quartet_index,
                'can_do': True,
            })
    else:
        exams = Exam.objects \
            .filter(_user_codes="",
                    begin_on__lte=datetime.utcnow(),
                    end_on__gte=datetime.utcnow()) \
            .order_by('-id') \
            .values()

        max_quartet_index, page_number, range_quartet_index, exams = compute_read_exams_context__get(direction, exams, page_number)

        return render(request, template_name='exams/exams.html', context={
            'exams': exams,
            'type': 0,
            'current_exam_quartet_index': page_number,
            'max_exam_quartet_index': max_quartet_index,
            'range_exam_quartet_index': range_quartet_index,
        })


# exams/exam
class Quiz(object):
    index: int
    question: str
    options: list[str]
    correct_answer: str

    @property
    def number_of_options(self):
        return len(self.options)


def compute_create_or_update_exam_quizzes(questions, optional_answers, correct_answers):
    quizzes = []
    for i in range(len(correct_answers)):
        quiz = Quiz()
        quiz.index = i + 1
        quiz.question = questions[i]
        quiz.options = optional_answers[i]
        quiz.correct_answer = correct_answers[i]
        quizzes.append(quiz)

    return quizzes


def parse_for_constraints_of_exam(post_request):
    begin_on = post_request.get('begin_on') or None
    end_on = post_request.get('end_on') or None
    user_codes: list[str] = post_request.get('user_codes').split(',')
    user_codes = [user_code.strip() for user_code in user_codes]
    return {'begin_on': begin_on, 'end_on': end_on, 'user_codes': user_codes}


def create_or_update_exam__get(request):
    exam_id = request.GET.get('exam_id')
    if not exam_id:
        return render(request, template_name='exams/creating_exam.html', context={})

    exam: Exam = Exam.objects.filter(id=exam_id).first()
    if not exam:
        raise ValueError('No exam')

    if exam.created_by != request.user:
        raise ValueError('Error permission')

    mode = request.GET.get('mode')

    if mode == '2':
        return render(request,
                      template_name='exams/setting_constraints_of_exam.html',
                      context={
                          'exam_id': exam.id,
                          'exam_begin_on': exam.begin_on,
                          'exam_end_on': exam.end_on,
                          'exam_user_codes': exam.user_codes,
                      })
    # else
    quizzes = compute_create_or_update_exam_quizzes(exam.questions, exam.optional_answers, exam.correct_answers)
    return render(request,
                  template_name='exams/creating_exam.html',
                  context={
                      'exam_id': exam.id,
                      'exam_name': exam.name,
                      'exam_time': exam.time,
                      'exam_number_of_quizzes': len(quizzes),
                      'quizzes': quizzes,
                  })


def create_exam__post(request):
    error_messages, parsed_result = parse_for_exam(post_request=request.POST)
    if not error_messages:
        Exam.objects.create(
            name=parsed_result['name'],
            time=parsed_result['time'],
            questions=parsed_result['questions'],
            optional_answers=parsed_result['optional_answers'],
            correct_answers=parsed_result['correct_answers'],
            created_by=get_user(request),
        )
        return redirect(to='/exams/exams?type=3&page=1')

    quizzes = compute_create_or_update_exam_quizzes(parsed_result['questions'], parsed_result['optional_answers'],
                                                    parsed_result['correct_answers'])
    return render(request, template_name='exams/creating_exam.html', context={
        'exam_name': parsed_result['name'],
        'exam_time': parsed_result['time'],
        'exam_number_of_quizzes': len(quizzes),
        'quizzes': quizzes,
        'error_messages': error_messages,
    })


def update_exam__post(request, exam_id):
    error_messages, parsed_result = parse_for_exam(post_request=request.POST)

    exam = Exam.objects.filter(id=exam_id).first()
    if not exam:
        raise ValueError('No exam')

    tests = Test.objects.filter(exam_id=exam_id).all()
    mode = request.GET.get('mode')

    if mode == '2':
        parsed_result = parse_for_constraints_of_exam(request.POST)
        Exam.objects.update_constrains(
            exam_id=exam_id,
            begin_on=parsed_result['begin_on'],
            end_on=parsed_result['end_on'],
            user_codes=parsed_result['user_codes'])
        return redirect(to='/exams/exams?type=3&page=1')
    else:
        if tests:
            raise ValueError('Had test')

        if not error_messages:
            Exam.objects.update(
                exam_id=exam_id,
                name=parsed_result['name'],
                time=parsed_result['time'],
                questions=parsed_result['questions'],
                optional_answers=parsed_result['optional_answers'],
                correct_answers=parsed_result['correct_answers']
            )
            return redirect(to='/exams/exams?type=3&page=1')

        quizzes = compute_create_or_update_exam_quizzes(parsed_result['questions'], parsed_result['optional_answers'],
                                                        parsed_result['correct_answers'])
        return render(request, template_name='exams/creating_exam.html', context={
            'exam_id': exam_id,
            'exam_name': parsed_result['name'],
            'exam_time': parsed_result['time'],
            'exam_number_of_quizzes': len(quizzes),
            'quizzes': quizzes,
            'error_messages': error_messages,
        })


def create_or_update_exam__post(request):
    exam_id = request.POST.get('exam_id')
    if not exam_id:
        return create_exam__post(request)

    return update_exam__post(request, exam_id)


# exams/test
class QuizzesOfTest(object):
    index: int
    question: str
    options: list[str]
    answer: str

    @property
    def number_of_options(self):
        return len(self.options)


def parse_for_test_answers(post_request, number_of_quizzes):
    answers: list[str] = []
    for i in range(1, number_of_quizzes + 1):
        answers.append(post_request.get(f'answer_{i}'))
    return answers


def validate_for_read_or_create_test(request, exam_id):
    if not exam_id:
        raise ValueError('No exam_id')

    exam = Exam.objects.filter(id=exam_id).first()
    if not exam:
        raise ValueError('No exam')

    User = get_user_model()
    if not (not exam.user_codes or User.objects.filter(id=request.user.id).first().code in exam.user_codes):
        raise ValueError('Error permission')

    return exam


def compute_read_or_create_test_quizzes(questions, optional_answers, answers=None):
    quizzes = []
    for i in range(len(questions)):
        quiz = QuizzesOfTest()
        quiz.index = i + 1
        quiz.question = questions[i]
        quiz.options = optional_answers[i]
        if answers:
            quiz.answer = answers[i]
        else:
            quiz.answer = ''
        quizzes.append(quiz)

    return quizzes


def read_or_create_test__get(request):
    exam_id = request.GET.get('exam_id')
    exam = validate_for_read_or_create_test(request, exam_id)

    mode = request.GET.get('mode')

    if mode == '2':
        test = Test.objects.filter(exam_id=exam_id).first()
        if not test:
            raise ValueError('No test')

        quizzes = compute_read_or_create_test_quizzes(exam.questions, exam.optional_answers, test.answers)

        return render(request,
                      template_name='exams/viewing_test.html',
                      context={
                          'exam_id': exam.id,
                          'exam_name': exam.name,
                          'exam_code': exam.code,
                          'exam_time': exam.time,
                          'exam_number_of_quizzes': len(quizzes),
                          'quizzes': quizzes,
                          'score': test.score,
                          'exam_code_number': exam.code,
                      })
    # else
    quizzes = compute_read_or_create_test_quizzes(exam.questions, exam.optional_answers)

    return render(request,
                  template_name='exams/doing_exam.html',
                  context={
                      'exam_id': exam.id,
                      'exam_name': exam.name,
                      'exam_code': exam.code,
                      'exam_time': exam.time,
                      'exam_number_of_quizzes': len(quizzes),
                      'quizzes': quizzes,
                  })


def read_or_create_test__post(request):
    exam_id = request.POST.get('exam_id')
    exam = validate_for_read_or_create_test(request, exam_id)

    answers = parse_for_test_answers(request.POST, len(exam.correct_answers))

    test = Test.objects.create(name=exam.name,
                               answers=answers,
                               exam_id=exam_id,
                               created_by=request.user)

    return redirect(f'/exams/exams?type=2&page=1&exam_code_number={exam.code[1:]}&score={test.score}')


# Create your views here.
# exams/exams
def read_exams(request):
    if request.method == 'GET':
        return read_exams__get(request)

    raise ValueError('Error method')


# exams/exam
def create_or_update_exam(request):
    if not request.user.is_authenticated:
        return redirect("/users/login/")

    if request.method == 'GET':
        return create_or_update_exam__get(request)

    if request.method == 'POST':
        return create_or_update_exam__post(request)

    raise ValueError('Error method')


# exams/test
def read_or_create_test(request):
    if not request.user.is_authenticated:
        return redirect("/users/login/")

    if request.method == 'GET':
        return read_or_create_test__get(request)

    if request.method == 'POST':
        return read_or_create_test__post(request)

    raise ValueError('Error method')
