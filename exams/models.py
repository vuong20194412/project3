from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import random
import datetime

SPLIT_LEVEL_1 = "<&>"
SPLIT_LEVEL_2 = "<#>"
ENCODE_SPLIT_LEVEL_1 = "\r\n\r\n"
ENCODE_SPLIT_LEVEL_2 = "\r\r\n\n"


def generate_code(model):
    zero_sequence = ''.join(["0" for _ in range(11)])
    code = "#" + ("%s%s" % (zero_sequence, random.randint(0, 999999)))[-6:]
    while model.objects.filter(code=code).count():
        code = "#" + ("%s%s" % (zero_sequence, random.randint(0, 999999)))[-6:]

    return code


def join_level_1(strings: list[str]):
    strings = [string.replace(SPLIT_LEVEL_1, ENCODE_SPLIT_LEVEL_1) for string in strings]
    return SPLIT_LEVEL_1.join(strings)


def join_level_2(list_strings: list[list[str]]):
    list_strings = [[string.replace(SPLIT_LEVEL_2, ENCODE_SPLIT_LEVEL_2) for string in strings] for strings in
                    list_strings]
    strings = [SPLIT_LEVEL_2.join(strings) for strings in list_strings]
    strings = [string.replace(SPLIT_LEVEL_1, ENCODE_SPLIT_LEVEL_1) for string in strings]
    return SPLIT_LEVEL_1.join(strings)


def split_level_1(string: str):
    strings = string.split(SPLIT_LEVEL_1)
    strings = [string.replace(ENCODE_SPLIT_LEVEL_1, SPLIT_LEVEL_1) for string in strings]
    return strings


def split_level_2(string: str):
    strings = string.split(SPLIT_LEVEL_1)
    strings = [string.replace(ENCODE_SPLIT_LEVEL_1, SPLIT_LEVEL_1) for string in strings]
    list_strings = [string.split(SPLIT_LEVEL_2) for string in strings]
    list_strings = [[string.replace(ENCODE_SPLIT_LEVEL_2, SPLIT_LEVEL_2) for string in strings] for strings in
                    list_strings]
    return list_strings


class ExamManager(models.Manager):
    def create(self, name, time, questions, optional_answers, correct_answers, created_by):
        exam = self.model(
            name=name,
            time=time,
            code=generate_code(Exam),
            created_by=created_by,
            created_on=datetime.datetime.now(datetime.timezone.utc),
        )
        exam.questions = questions
        exam.optional_answers = optional_answers
        exam.correct_answers = correct_answers
        exam.save(using=self._db)
        return exam

    def update(self, exam_id, name, time, questions, optional_answers, correct_answers):
        exam = Exam.objects.filter(id=exam_id).first()
        exam.name = name
        exam.time = time
        exam.questions = questions
        exam.optional_answers = optional_answers
        exam.correct_answers = correct_answers
        exam.save(using=self._db)
        return exam

    def update_constrains(self, exam_id, begin_on, end_on, user_codes):
        exam = Exam.objects.filter(id=exam_id).first()
        exam.begin_on = begin_on
        exam.end_on = end_on
        exam.user_codes = user_codes
        exam.save(using=self._db)
        return exam


class TestManager(models.Manager):
    def create(self, name: str, answers: list[str], exam_id: int, created_by: get_user_model()):
        exam = Exam.objects.filter(id=exam_id).first()
        if not exam:
            raise ValueError('No exam')

        correct_answers = exam.correct_answers
        if not correct_answers:
            raise ValueError('No correct answers')

        score = 0
        for index, correct_answer in enumerate(correct_answers):
            if str(correct_answer) == str(answers[index]):
                score += 1
        score = "%.2f" % (score * 10 / len(correct_answers))

        test = self.model(
            name=name,
            exam_id=exam,
            code=generate_code(Test),
            score=score,
            created_by=created_by,
            created_on=datetime.datetime.now(datetime.timezone.utc),
        )
        test.answers = answers,
        test.save(using=self._db)
        return test


# Create your models here.
class Exam(models.Model):
    name = models.CharField(_('name'), max_length=255, )
    code = models.CharField(_('code'), max_length=255, unique=True, )
    _questions = models.TextField(_('questions'), )
    _optional_answers = models.TextField(_('optional answers'))
    _correct_answers = models.TextField(_('correct answers'))
    _user_codes = models.TextField(_('user codes'))
    begin_on = models.DateTimeField(_('begin on'), null=True)
    end_on = models.DateTimeField(_('end on'), null=True)
    created_by = models.ForeignKey(verbose_name='created by', to=get_user_model(), on_delete=models.SET_NULL,
                                   null=True)
    created_on = models.DateTimeField(_('created on'))
    time = models.CharField(_('time'), max_length=15)

    objects = ExamManager()

    @property
    def questions(self):
        return split_level_1(self._questions)

    @questions.setter
    def questions(self, questions: list[str]):
        self._questions = join_level_1(questions)

    @property
    def optional_answers(self):
        return split_level_2(self._optional_answers)

    @optional_answers.setter
    def optional_answers(self, optional_answers: list[list[str]]):
        self._optional_answers = join_level_2(optional_answers)

    @property
    def correct_answers(self):
        return split_level_1(self._correct_answers)

    @correct_answers.setter
    def correct_answers(self, correct_answers: list[str]):
        self._correct_answers = join_level_1(correct_answers)

    @property
    def user_codes(self):
        user_codes = self._user_codes.split(SPLIT_LEVEL_1)
        user_codes_count = len(user_codes)

        User = get_user_model()
        user_codes = User.objects.filter(code__in=user_codes).values('code')
        # user_code have format <{'code': '#111111'}> because use values('code')
        user_codes = [user_code['code'] for user_code in user_codes]

        if user_codes_count > len(user_codes):
            self._user_codes = SPLIT_LEVEL_1.join(user_codes)

        return user_codes

    @user_codes.setter
    def user_codes(self, user_codes: list[str]):
        User = get_user_model()
        user_codes = User.objects.filter(code__in=user_codes).values_list('code')
        # user_code have format ('#111111', ) because use values_list('code')
        user_codes = [user_code[0] for user_code in user_codes]
        self._user_codes = SPLIT_LEVEL_1.join(user_codes)


class Test(models.Model):
    name = models.CharField(_('name'), max_length=255, )
    code = models.CharField(_('code'), max_length=255, unique=True, )
    _answers = models.TextField(_('answers'))
    exam_id = models.ForeignKey(verbose_name=_('exam'), to=Exam, on_delete=models.RESTRICT)
    score = models.FloatField(_('score'))
    created_by = models.ForeignKey(verbose_name=_('created by'), to=get_user_model(), on_delete=models.CASCADE)
    created_on = models.DateTimeField(_('created on'))

    objects = TestManager()

    @property
    def answers(self):
        return split_level_1(self._answers)

    @answers.setter
    def answers(self, answers: list[str]):
        #answers : list[str] when assign become tuple[list[str]]
        self._answers = join_level_1(answers[0])
