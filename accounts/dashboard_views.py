from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

from .models import AcademicGroup, Course, Department, StudentProfile


# Сводка
@login_required
def dashboard_overview(request):
    names = []
    students_numbers = []
    courses_numbers = []

    for department in Department.objects.all():
        names.append(department.name)
        students_numbers.append(
            StudentProfile.objects.filter(department=department).count()
        )
        courses_numbers.append(
            Course.objects.filter(department=department).count()
        )

    return render(request, 'dashboard_overview.html', {
        'active': 'overview',
        'departments_count': Department.objects.count(),
        'groups_count': AcademicGroup.objects.count(),
        'courses_count': Course.objects.count(),
        'students_count': StudentProfile.objects.count(),
        'names': names,
        'students_numbers': students_numbers,
        'courses_numbers': courses_numbers,
    })


# Курсы
@login_required
def dashboard_courses(request):
    department_id = request.GET.get('department')

    if department_id:
        departments = Department.objects.filter(id=department_id)
        courses = Course.objects.filter(department_id=department_id)
    else:
        departments = Department.objects.all()
        courses = Course.objects.all()

    department_names = []
    department_numbers = []
    for department in departments:
        department_names.append(department.name)
        department_numbers.append(Course.objects.filter(department=department).count())

    course_names = []
    course_numbers = []
    enrollments_count = 0
    no_description_count = 0
    for course in courses:
        number = StudentProfile.objects.filter(courses=course).count()
        course_names.append(course.title)
        course_numbers.append(number)
        enrollments_count = enrollments_count + number
        if not course.description:
            no_description_count = no_description_count + 1

    return render(request, 'dashboard_courses.html', {
        'active': 'courses',
        'all_departments': Department.objects.all(),
        'department_id': department_id,
        'courses_count': courses.count(),
        'no_description_count': no_description_count,
        'enrollments_count': enrollments_count,
        'department_names': department_names,
        'department_numbers': department_numbers,
        'course_names': course_names,
        'course_numbers': course_numbers,
    })


# Группы
@login_required
def dashboard_groups(request):
    department_id = request.GET.get('department')

    if department_id:
        departments = Department.objects.filter(id=department_id)
        groups = AcademicGroup.objects.filter(department_id=department_id)
        students = StudentProfile.objects.filter(department_id=department_id)
    else:
        departments = Department.objects.all()
        groups = AcademicGroup.objects.all()
        students = StudentProfile.objects.all()

    department_names = []
    department_numbers = []
    for department in departments:
        department_names.append(department.name)
        department_numbers.append(AcademicGroup.objects.filter(department=department).count())

    group_names = []
    group_numbers = []
    for group in groups:
        group_names.append(group.name)
        group_numbers.append(students.filter(academic_group=group).count())

    return render(request, 'dashboard_groups.html', {
        'active': 'groups',
        'all_departments': Department.objects.all(),
        'department_id': department_id,
        'groups_count': groups.count(),
        'students_count': students.count(),
        'no_group_count': students.filter(academic_group__isnull=True).count(),
        'department_names': department_names,
        'department_numbers': department_numbers,
        'group_names': group_names,
        'group_numbers': group_numbers,
    })


# Студенты
@login_required
def dashboard_students(request):
    department_id = request.GET.get('department')

    if department_id:
        departments = Department.objects.filter(id=department_id)
        students = StudentProfile.objects.filter(department_id=department_id)
    else:
        departments = Department.objects.all()
        students = StudentProfile.objects.all()

    department_names = []
    department_numbers = []
    for department in departments:
        department_names.append(department.name)
        department_numbers.append(students.filter(department=department).count())

    no_courses = 0
    one_course = 0
    many_courses = 0
    total_courses = 0
    for student in students:
        number = student.courses.count()
        total_courses = total_courses + number
        if number == 0:
            no_courses = no_courses + 1
        elif number == 1:
            one_course = one_course + 1
        else:
            many_courses = many_courses + 1

    students_count = students.count()
    if students_count > 0:
        average = round(total_courses / students_count, 1)
    else:
        average = 0

    return render(request, 'dashboard_students.html', {
        'active': 'students',
        'all_departments': Department.objects.all(),
        'department_id': department_id,
        'students_count': students_count,
        'no_courses_count': no_courses,
        'average': average,
        'department_names': department_names,
        'department_numbers': department_numbers,
        'courses_names': ['Без курсов', 'Один курс', 'Два и больше'],
        'courses_numbers': [no_courses, one_course, many_courses],
    })


# Пользователи
@login_required
def dashboard_users(request):
    admins = User.objects.filter(is_superuser=True).count()
    methodists = User.objects.filter(groups__name='Методист').count()
    students = StudentProfile.objects.count()

    return render(request, 'dashboard_users.html', {
        'active': 'users',
        'users_count': User.objects.count(),
        'admins': admins,
        'methodists': methodists,
        'students': students,
        'role_names': ['Администраторы', 'Методисты', 'Студенты'],
        'role_numbers': [admins, methodists, students],
    })

