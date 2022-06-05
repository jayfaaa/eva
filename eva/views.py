import json
from functools import reduce
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from .models import EvaluationSheet, AppUser, Department, AppSettings, Question, QuestionCategory, Image, EvaluationGroup, QuestionCategoryBridge, CategoryEvaluationBridge
from .utils import calc_evaluations
from .forms import ImageForm
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


def index(request):
    return render(request, "eva/index.html")


def login(request):
    def get():
        id = request.session.get("id")
        if id:
            redirect_url = '/app'
            user = AppUser.objects.get(pk=id)
            if user.role == "employee":
                redirect_url = '/profile'
            return HttpResponseRedirect(redirect_url)
        return render(request, "eva/login.html")

    def post():
        email = request.POST.get("email")
        user = AppUser.objects.filter(email=email).first()
        if user == None or user.password != request.POST.get("password"):
            error = 'Unable to login. Please check your email/password.'
            return render(request, "eva/login.html", {"error": error})

        request.session["id"] = user.id
        request.session["full_name"] = user.full_name()
        request.session["role"] = user.role
        
        image = Image.objects.filter(reference=user.id)
        if image:
            image = image[len(image)-1]
            request.session["image"] = image.image.url

        redirect_url = '/app'
        if user.role == 'employee':
            redirect_url = '/profile'

        return HttpResponseRedirect(redirect_url)

    if request.method == 'POST':
        return post()

    return get()


def login_qr(request):
    def get():
        id = request.session.get("id")
        if id:
            redirect_url = '/app'
            user = AppUser.objects.get(pk=id)
            if user.role == "employee":
                redirect_url = '/profile'
            return HttpResponseRedirect(redirect_url)
        return render(request, "eva/login_qr.html")
    
    def post():
        qr = request.POST.get("qr")
        if qr == None:
            error = 'Unable to login. Please check your QR code.'
            return render(request, "eva/login_qr.html", {"error": error})
    
        user = AppUser.objects.filter(secret_key=qr).first()
        if user == None:
            error = 'Unable to login. Please check your QR code.'
            return render(request, "eva/login_qr.html", {"error": error})

        request.session["id"] = user.id

        redirect_url = '/app'
        if user.role == 'employee':
            redirect_url = '/profile'

        return HttpResponseRedirect(redirect_url)

    if request.method == 'POST':
        return post()

    return get()


def logout(request):
    request.session.pop("id")
    return HttpResponseRedirect('/login')


def register(request):
    def validate_password(password, confirm_password):
        if password != confirm_password:
            raise ValidationError("Password is not the same as confirm password")

    def validate_email(email):
        app_user = AppUser.objects.filter(email=email)
        if app_user.exists():
            raise ValidationError("User is already registered")

    def make_app_user(data):
        app_user = AppUser(**data)
        app_user.role = "admin"
        app_user.save()

    if request.session.get("id"):
        return HttpResponseRedirect('/app')

    errors = {}
    success = None
    if request.method == 'POST':
        data = request.POST.dict()
        data.pop("csrfmiddlewaretoken")

        try:
            validate_password(data.get("password"), data.get("confirm_password"))
            validate_email(data.get("email"))
            data.pop("confirm_password")
            make_app_user(data)
            success = "Successfully created a user"
            
        except Exception as e:
            errors = e.error_list

    admins = AppUser.objects.filter(role='admin').count()
    enable_admin_registration = AppSettings.objects.filter(key='enable_admin_registration').get_or_create()[0]
    registration_closed = admins > 0 and enable_admin_registration.value != 'on'

    return render(request, "eva/register.html", {"errors": errors, "success": success, "registration_closed": registration_closed})


def evaluate(request):
    employees = AppUser.objects.filter(role='employee').all()
    return render(request, "eva/evaluate.html", {"employees": employees})

def evaluate_group(request):
    employees = AppUser.objects.filter(role='employee').all()
    return render(request, "eva/evaluate.html", {"employees": employees})

def evaluate_employee(request):
    # categories = QuestionCategory.objects.all()
    # questions = Question.objects.all()
    # employees = AppUser.objects.filter(role='admin').all()
    # disable_evaluation_form = AppSettings.objects.filter(key='disable_evaluation_form').get_or_create()[0]
    # disable_evaluation_form = disable_evaluation_form.value == 'on'
    
    # return render(request, "eva/evaluate_employee.html", {
    #     "employees": employees,
    #     "categories": categories,
    #     "questions": questions,
    #     "disable_evaluation_form": disable_evaluation_form
    # })

    employees = AppUser.objects.filter(role='employee').all()
    categories = QuestionCategory.objects.all()
    questions = Question.objects.all()
    disable_evaluation_form = AppSettings.objects.filter(key='disable_evaluation_form').get_or_create()[0]
    disable_evaluation_form = disable_evaluation_form.value == 'on'

    import datetime

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # print(today)
    
    data = EvaluationGroup.objects.all()
  

    return render(request, "eva/evaluate_employee.html", {
        "employees": employees,
        "categories": categories,
        "questions": questions,
        "disable_evaluation_form": disable_evaluation_form,
        "data": data,
        "date_today": today
    })


def evaluate_employee_detail(request, pk):
    # data = get_object_or_404(EvaluationGroup, pk=pk)

    # employees = AppUser.objects.filter(role='employee').all()
    # categories = CategoryEvaluationBridge.objects.all().filter(evaluation_group_id = pk)
    # questions = Question.objects.all()
    # # disable_evaluation_form = AppSettings.objects.filter(key='disable_evaluation_form').get_or_create()[0]
    # # disable_evaluation_form = disable_evaluation_form.value == 'on'
    
    # # data = EvaluationGroup.objects.all()

    
    # import datetime

    # today = datetime.datetime.now().strftime("%Y-%m-%d")
  


    # return render(request, "eva/evaluate_employee_detail.html",{
    #     "employees": employees,
    #     "categories": categories,
    #     "questions": questions,
    #     # "disable_evaluation_form": disable_evaluation_form,
    #     "data": data,
    #     "date_today": today
    # })

    data = get_object_or_404(EvaluationGroup, pk=pk)

    employees = AppUser.objects.filter(role='employee').all()
    categories = CategoryEvaluationBridge.objects.all().filter(evaluation_group_id = pk)
    categories = CategoryEvaluationBridge.objects.raw(
        f"""
            SELECT t2.id, t2.name FROM eva_categoryevaluationbridge t1
            LEFT JOIN (SELECT * from eva_questioncategory) t2 
            ON t1.category_id = t2.id
            WHERE t1.evaluation_group_id = {pk}
        """
    )

    

    questions = Question.objects.raw(
        """ 
            SELECT t1.id, t1.question_id, t2.name, t1.category_id FROM eva_questioncategorybridge t1
            LEFT JOIN (SELECT * FROM eva_question) t2 
            ON t1.question_id = t2.id
        """
    )
    # disable_evaluation_form = AppSettings.objects.filter(key='disable_evaluation_form').get_or_create()[0]
    # disable_evaluation_form = disable_evaluation_form.value == 'on'
    
    # data = EvaluationGroup.objects.all()

    print(questions)

    
    import datetime

    today = datetime.datetime.now().strftime("%Y-%m-%d")
  


    return render(request, "eva/evaluate_group_admin_detail.html",{
        "employees": employees,
        "categories": categories,
        "questions": questions,
        # "disable_evaluation_form": disable_evaluation_form,
        "data": data,
        "date_today": today
    })

    

def evaluate_admin(request):
    employees = AppUser.objects.filter(role='employee').all()
    categories = QuestionCategory.objects.all()
    questions = Question.objects.all()
    disable_evaluation_form = AppSettings.objects.filter(key='disable_evaluation_form').get_or_create()[0]
    disable_evaluation_form = disable_evaluation_form.value == 'on'

    import datetime

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # print(today)
    
    data = EvaluationGroup.objects.all()
  

    return render(request, "eva/evaluate_admin.html", {
        "employees": employees,
        "categories": categories,
        "questions": questions,
        "disable_evaluation_form": disable_evaluation_form,
        "data": data,
        "date_today": today
    })

def evaluate_group_admin(request):
    # employees = AppUser.objects.filter(role='employee').all()
    # categories = QuestionCategory.objects.all()
    # questions = Question.objects.all()
    # disable_evaluation_form = AppSettings.objects.filter(key='disable_evaluation_form').get_or_create()[0]
    # disable_evaluation_form = disable_evaluation_form.value == 'on'
    success = None
    if request.method == "POST":
        print("post")
        name = request.POST.get("name")
        range = request.POST.get("range")
        open_date = request.POST.get("open_date")
        close_date = request.POST.get("close_date")
        new_eval_group = EvaluationGroup(name=name,range=range,open_date=open_date,close_date=close_date)
        new_eval_group.save()
        success = "Successfully added a new Evaluation Group."

        
    data = EvaluationGroup.objects.all()
    # return render(request, "eva/departments.html", {"data": data, "success": success})

    return render(request, "eva/evaluate_group_admin.html", {"data": data, "success": success})



def app(request):
    evaluation_count = EvaluationSheet.objects.count()
    employee_count = AppUser.objects.filter(role='employee').count()
    department_count = Department.objects.count()
    return render(request, "eva/app.html", {"evaluation_count": evaluation_count, "employee_count": employee_count, "department_count": department_count})

def reports(request):
    def make_data(total, x):
        department = x.department.id if x.department else "Unspecified"
        total_employees = total.get(department) or 0
        total[department] = total_employees + 1
        return total

    def make_evaluations_data(evaluations):
        return calc_evaluations(json.loads(evaluations))

    def make_levels_data(total, x):
        total_sum = total.get(x) or 0
        total[x] = total_sum + 1
        return total

    employees = AppUser.objects.filter(role='employee').all()

    departments = {x.id: x.name for x in Department.objects.all()}
    departments["Unspecified"] = "Unspecified"
    employees_count_by_department = reduce(make_data, employees, {})
    data = [employees_count_by_department.get(x) or 0 for x in departments.keys()]
    employees_by_department = {
        "labels": list(departments.values()),
        "data": data
    }

    satisfactory_levels_labels = ["Unsatisfactory", "Fair", "Satisfactory", "Very Satisfactory"]
    last_evaluations = EvaluationSheet.objects.order_by('-id')[:10]
    evaluations_data = {x.id: make_evaluations_data(x.evaluations) for x in last_evaluations}
    ratings = [x.get("descriptive_rating") for x in evaluations_data.values()]
    ratings_by_levels = reduce(make_levels_data, ratings, {})
    satisfactory_levels_data = [ratings_by_levels.get(x) or 0 for x in satisfactory_levels_labels]
    satisfactory_levels = {
        "labels": satisfactory_levels_labels,
        "data": satisfactory_levels_data,
    }

    return render(request, "eva/reports.html", {
        "employees_by_department": employees_by_department,
        "satisfactory_levels": satisfactory_levels
    })

def evaluation(request):
    # data = []
    # if request.method == 'POST':
    #     employee = request.POST.get("employee")
    #     data = EvaluationSheet.objects.raw(f"""
    #         SELECT t1.id, t1.created_at, t1.evaluator_name, t1.employee_name, t1.evaluations, t1.comments_and_recommendations, t1.employee_id, t1.evaluate_group, t2.eval_name 
    #         from eva_evaluationsheet t1
    #         left join (select name eval_name, id from eva_evaluationgroup) t2 on CAST(t1.evaluate_group AS INT) = t2.id
    #         where t1.employee_id = {int(employee)}
    #         """)
    # employees = AppUser.objects.filter(role='employee').all()
    # return render(request, "eva/evaluation.html", {"data": data, "employees": employees})

    employees = AppUser.objects.filter(role='employee').all()
    categories = QuestionCategory.objects.all()
    questions = Question.objects.all()
    disable_evaluation_form = AppSettings.objects.filter(key='disable_evaluation_form').get_or_create()[0]
    disable_evaluation_form = disable_evaluation_form.value == 'on'
    count_employee = AppUser.objects.count()

    import datetime

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # print(today)
    
    data = EvaluationGroup.objects.raw("""
        SELECT t1.*, t2.cnt FROM eva_evaluationgroup t1
        left join (SELECT evaluate_group, count(*) cnt from eva_evaluationsheet group by evaluate_group) t2 on 
        t1.id = t2.evaluate_group;
    """)
  

    return render(request, "eva/evaluation_2.html", {
        "employees": employees,
        "categories": categories,
        "questions": questions,
        "disable_evaluation_form": disable_evaluation_form,
        "data": data,
        "date_today": today,
        "count_employee": count_employee
    })

def evaluate_list_group(request, pk):
    eval_name = EvaluationGroup.objects.get(pk=pk)
    data = EvaluationGroup.objects.raw(f"""
        with base as (
            select t1.id id, t1.id department_id, min(t1.name) department_name, t2.id evaluation_group_id, count(*) department_total from eva_department t1
            cross join eva_evaluationgroup t2
            left join eva_appuser t3 on t1.id = t3.department_id
            group by t1.id, t2.id)
            select *, 
            (select count(*) from eva_evaluationsheet e1 
            left join (select department_id, id from eva_appuser) ea1
            on e1.employee_id = ea1.id
            where e1.evaluate_group = base.evaluation_group_id and
            ea1.department_id = base.department_id) evaluated 
            from base
            where base.evaluation_group_id = {pk};
    """)

    return render(request, "eva/evaluate_list_group.html", {
        "data": data,
        "eval_name": eval_name,
        "group_id": pk
    })

def evaluate_list_group_ranking(request, group_id, department_id):

    # data = EvaluationSheet.objects.raw(f"""
    #     select t1.*, t2.department_id from eva_evaluationsheet t1
    #     left join (select * from eva_appuser) t2 on t1.employee_id = t2.id
    #     where t2.department_id = {department_id} and t1.evaluate_group = {group_id};
    # """)

    department_name = Department.objects.get(pk=department_id)
    group_name = EvaluationGroup.objects.get(pk=group_id)

    data = EvaluationSheet.objects.raw(f"""
            SELECT t1.id, t1.created_at, t1.evaluator_name, t1.employee_name, 
            t1.evaluations, t1.comments_and_recommendations, t1.employee_id, t1.evaluate_group, t2.eval_name,
            z1.name department_name
            from eva_evaluationsheet t1
            left join (select name eval_name, id from eva_evaluationgroup) t2 on CAST(t1.evaluate_group AS INT) = t2.id
            left join (
                select * from eva_appuser au 
                left join (select id, name from eva_department) dep 
                on au.department_id = dep.id
            ) z1 on t1.employee_id = z1.id
            where z1.department_id = {department_id} and t1.evaluate_group = {group_id};
            """)
    format_data = []
    evaluate_group_ids = []
    employees = []
    for i in data:
        evaluations = json.loads(i.evaluations)
        calculated_evaluations = calc_evaluations(evaluations)
        format_data.append({"name" : i.employee_name, "calculated": calculated_evaluations, "evaluate_group_id": i.evaluate_group, "evaluate_group_name": i.eval_name})
        if i.evaluate_group not in evaluate_group_ids:
            evaluate_group_ids.append(i.evaluate_group)
        if i.employee_name not in employees:
            employees.append(i.employee_name)
    print(evaluate_group_ids)
    print(format_data)
    # print(evaluate_group_ids)

    final_format = []

    for group in evaluate_group_ids:
        print("group " + str(group))
        for person in employees:
            total = 0
            divisor = 0
            form_placeholder = None
            for crawler in format_data:
                if (person == crawler['name'] and crawler['evaluate_group_id'] == group):
                    total += crawler['calculated']['overall_total']
                    divisor += 1
                    form_placeholder = crawler['evaluate_group_name']
            
            if divisor != 0:
                final_format.append(
                    {
                        "name": person,
                        "average": total/divisor,
                        "evaluation_form": form_placeholder
                    }
                )

    # print(final_format)

    newlist = sorted(final_format, key=lambda x: ( x['evaluation_form'], x['average']), reverse=True)
    
    print(newlist)
    return render(request, "eva/ranking_2.html", 
    {
        "data": newlist ,
        "department_name": department_name,
        "group_name": group_name  
    })
    


def evaluation_sheet(request, pk):
    data = EvaluationSheet.objects.get(pk=pk)
    evaluations = json.loads(data.evaluations)
    calculated_evaluations = calc_evaluations(evaluations)
    return render(request, "eva/evaluation_sheet.html", {
        "data": data,
        "questions": evaluations.get("questions"),
        "categories": evaluations.get("categories"),
        "ratings": calculated_evaluations,
    })

def ranking_employee(request):
    data = EvaluationSheet.objects.raw(f"""
            SELECT t1.id, t1.created_at, t1.evaluator_name, t1.employee_name, t1.evaluations, t1.comments_and_recommendations, t1.employee_id, t1.evaluate_group, t2.eval_name 
            from eva_evaluationsheet t1
            left join (select name eval_name, id from eva_evaluationgroup) t2 on CAST(t1.evaluate_group AS INT) = t2.id
            """)
    format_data = []
    evaluate_group_ids = []
    employees = []
    for i in data:
        evaluations = json.loads(i.evaluations)
        calculated_evaluations = calc_evaluations(evaluations)
        format_data.append({"name" : i.employee_name, "calculated": calculated_evaluations, "evaluate_group_id": i.evaluate_group, "evaluate_group_name": i.eval_name})
        if i.evaluate_group not in evaluate_group_ids:
            evaluate_group_ids.append(i.evaluate_group)
        if i.employee_name not in employees:
            employees.append(i.employee_name)
    print(evaluate_group_ids)
    print(format_data)
    # print(evaluate_group_ids)

    final_format = []

    for group in evaluate_group_ids:
        print("group " + str(group))
        for person in employees:
            total = 0
            divisor = 0
            form_placeholder = None
            for crawler in format_data:
                if (person == crawler['name'] and crawler['evaluate_group_id'] == group):
                    total += crawler['calculated']['overall_total']
                    divisor += 1
                    form_placeholder = crawler['evaluate_group_name']
            
            if divisor != 0:
                final_format.append(
                    {
                        "name": person,
                        "average": total/divisor,
                        "evaluation_form": form_placeholder
                    }
                )

    # print(final_format)

    newlist = sorted(final_format, key=lambda x: ( x['evaluation_form'], x['average']), reverse=True)
    
    print(newlist)
    return render(request, "eva/ranking_employee.html", {"data": newlist })
    # for i in
    # print(calculated_evaluations)
    # return render(request, 'test')


def ranking(request):
    data = EvaluationSheet.objects.raw(f"""
            SELECT t1.id, t1.created_at, t1.evaluator_name, t1.employee_name, t1.evaluations, t1.comments_and_recommendations, t1.employee_id, t1.evaluate_group, t2.eval_name 
            from eva_evaluationsheet t1
            left join (select name eval_name, id from eva_evaluationgroup) t2 on CAST(t1.evaluate_group AS INT) = t2.id
            """)
    format_data = []
    evaluate_group_ids = []
    employees = []
    for i in data:
        evaluations = json.loads(i.evaluations)
        calculated_evaluations = calc_evaluations(evaluations)
        format_data.append({"name" : i.employee_name, "calculated": calculated_evaluations, "evaluate_group_id": i.evaluate_group, "evaluate_group_name": i.eval_name})
        if i.evaluate_group not in evaluate_group_ids:
            evaluate_group_ids.append(i.evaluate_group)
        if i.employee_name not in employees:
            employees.append(i.employee_name)
    print(evaluate_group_ids)
    print(format_data)
    # print(evaluate_group_ids)

    final_format = []

    

    for group in evaluate_group_ids:
        print("group " + str(group))
        for person in employees:
            total = 0
            divisor = 0
            form_placeholder = None
            for crawler in format_data:
                if (person == crawler['name'] and crawler['evaluate_group_id'] == group):
                    total += crawler['calculated']['overall_total']
                    divisor += 1
                    form_placeholder = crawler['evaluate_group_name']
            
            if divisor != 0:
                final_format.append(
                    {
                        "name": person,
                        "average": total/divisor,
                        "evaluation_form": form_placeholder
                    }
                )

    # print(final_format)

    newlist = sorted(final_format, key=lambda x: ( x['evaluation_form'], x['average']), reverse=True)
    
    print(newlist)
    return render(request, "eva/ranking.html", {"data": newlist })
    # for i in
    # print(calculated_evaluations)
    # return render(request, 'test')


def employees(request):
    data = AppUser.objects.filter(role='employee').all()
    return render(request, "eva/employees.html", {"data": data})


def employees_new(request):
    def validate(data):
        required_fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
        ]
        for x in required_fields:
            if not data.get(x):
                raise ValidationError("Please fill up all the fields")

    def validate_password(password, confirm_password):
        if password != confirm_password:
            raise ValidationError("Password is not the same as confirm password")

    def validate_email(email):
        app_user = AppUser.objects.filter(email=email)
        if app_user.exists():
            raise ValidationError("User is already registered")

    def make_app_user(data):
        data["department"] = Department.objects.get(pk=data.get("department"))
        app_user = AppUser(**data)
        app_user.role = "employee"
        app_user.save()

    errors = {}
    success = None
    if request.method == "POST":
        data = request.POST.dict()
        data.pop("csrfmiddlewaretoken")
        try:
            validate(data)
            validate_password(data.get("password"), data.get("confirm_password"))
            data.pop("confirm_password")

            validate_email(data.get("email"))
            make_app_user(data)
            import socket
            socket.gethostbyname('www.google.com')
            try:
                send_mail(
                    'Subject here',
                    'Here is the message.',
                    'blil2tink@gmail.com',
                    ['bliltinked@gmail.com'],
                    fail_silently=False,
                )
                
                success = "Successfully added an employee and sent an email!"
            except Exception as e:
                success = "Successfully added an employee! But error on sending an email"
                print(e)
        except Exception as e:
            errors = e.error_list

    departments = Department.objects.all()

    return render(request, "eva/employees_new.html", {"errors": errors, "success": success, "departments": departments})


def profile(request):
    id = request.session.get("id")
    if not id:
        HttpResponseRedirect('/login')
    user = AppUser.objects.get(pk=id)

    errors = None
    success = None

    def set_password():
        user.password = request.POST.get("password")
        user.save()

    def validate_password():
        if not request.POST.get("password") or not request.POST.get("confirm_password"):
            raise ValidationError("Please input password")

        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            raise ValidationError("Confirm password is incorrect. Please make sure your new password is the same with confirm password.")

    if request.method == 'POST':
        change_password = request.POST.get("change_password")
        if change_password:
            try:
                validate_password()
                set_password()
            except Exception as e:
                errors = e.error_list
        else:
            set_info()

        if not errors:
            success = "Successfully updated"

    form = ImageForm()
    image = Image.objects.filter(reference=id)
    if image:
        image = image[len(image)-1]

    return render(request, "eva/profile.html", {
            "errors": errors,
            "success": success,
            "data": user,
            "form": form,
            "image": image})

def profile_admin(request):
    id = request.session.get("id")
    if not id:
        HttpResponseRedirect('/login')
    user = AppUser.objects.get(pk=id)
    image = Image.objects.filter(reference=id)
    if image:
        image = image[len(image)-1]    
    return render(request, "eva/profile_admin.html", {"data": user, "image": image})


def evaluation_employee(request):
    id = request.session.get("id")
    user = AppUser.objects.get(pk=id) if id else None
    data = EvaluationSheet.objects.filter(employee=user).all() if user else []
    return render(request, "eva/evaluation_employee.html", {"data": data})


def evaluation_list_sheet(request, pk):
    # data = EvaluationSheet.objects.get(pk=pk)
    # evaluations = json.loads(data.evaluations)
    # calculated_evaluations = calc_evaluations(evaluations)
    # return render(request, "eva/evaluation_list_sheet.html", {
    #    "data": data,
    #     "evaluations": evaluations,
    #     "ratings": calculated_evaluations,
    #     # "job_understanding": [{'question': evaluations.get('questions').get(str(x)), 'answer': evaluations.get('answers').get(str(x))} for x in evaluations.get('categories').get('job understanding')],
    #     # "job_skills": [{'question': evaluations.get('questions').get(str(x)), 'answer': evaluations.get('answers').get(str(x))} for x in evaluations.get('categories').get('job skills')],
    #     # "attitude": [{'question': evaluations.get('questions').get(str(x)), 'answer': evaluations.get('answers').get(str(x))} for x in evaluations.get('categories').get('attitude')],
    #     # "job_rules_and_regulations": [{'question': evaluations.get('questions').get(str(x)), 'answer': evaluations.get('answers').get(str(x))} for x in evaluations.get('categories').get('job rules and regulations')],
    # })
    data = EvaluationSheet.objects.get(pk=pk)
    evaluations = json.loads(data.evaluations)
    calculated_evaluations = calc_evaluations(evaluations)
    return render(request, "eva/evaluation_sheet.html", {
        "data": data,
        "questions": evaluations.get("questions"),
        "categories": evaluations.get("categories"),
        "ratings": calculated_evaluations,
    })


def departments(request):
    success = ""
    if request.method == "POST":
        name = request.POST.get("name")
        new_department = Department(name=name)
        new_department.save()
        success = "Successfully added a new department."
    data = Department.objects.all()
    return render(request, "eva/departments.html", {"data": data, "success": success})


def questions(request):
    success = ""
    if request.method == "POST":
        name = request.POST.get("name")
        # category = request.POST.get("category")
        # question_category = QuestionCategory.objects.get(pk=category)
        question = Question(name=name)
        question.save()
        success = "Successfully added a new question."
    data = Question.objects.all()
    categories = QuestionCategory.objects.all()
    return render(request, "eva/questions.html", {"data": data, "categories": categories, "success": success})


def question_categories(request):
    success = ""
    if request.method == "POST":
        name = request.POST.get("name")
        percentage = request.POST.get("percentage")
        # evaluation_group = request.POST.get("evaluation_group")
        new_data = QuestionCategory(name=name, percentage=int(percentage))
        new_data.save()
        success = "Successfully added a new question category."
    data = QuestionCategory.objects.all()
    # evaluation_group = EvaluationGroup.objects.all()
    # evaluation_group_query = EvaluationGroup.objects.only('id').all()
    # test = QuestionCategory.objects.values('id', 'created_at', 'name', 'percentage', 'evaluate_group', 'name')
    # test = QuestionCategory.objects.raw("""
    #     Select t1.id, t1.created_at, t1.name, t1.percentage, t1.evaluate_group , t2.eval_name
    #     from eva_questioncategory t1
    #     left join (select name eval_name, id from eva_evaluationgroup) t2 on CAST(t1.evaluate_group AS INT) = t2.id
    # """)
    return render(request, "eva/question_categories.html", {"data": data, "success": success})

def question_link_category(request,pk, success = ''):
    category = QuestionCategory.objects.get(pk=pk)
    questions = Question.objects.all()
    if success == 'success':
        success = "Successfully added a new question to the category."

    data = QuestionCategoryBridge.objects.raw(f"""
            SELECT 
                t1.id,
                t2.name
            from eva_questioncategorybridge t1
            left join
                (SELECT * from eva_question) t2 
            on t1.question_id = t2.id
            where t1.category_id = {pk}
            """)
    return render(request, "eva/question_link_category.html", {"data": data, "category": category, "questions": questions, "success": success})

def evaluation_link_category(request,pk, success= ''):
    category = QuestionCategory.objects.all()
    evaluation_group = EvaluationGroup.objects.get(pk=pk)
    if success == 'success':
        success = "Successfully added a new category to the evaluation group."

    data = QuestionCategoryBridge.objects.raw(f"""
            SELECT 
                t1.id,
                t2.name
            from eva_categoryevaluationbridge t1
            left join
                (SELECT * from eva_questioncategory) t2 
            on t1.category_id = t2.id
            where t1.evaluation_group_id = {pk}
            """)
    return render(request, "eva/evaluation_link_category.html", {"data": data, "category": category, "evaluation_group": evaluation_group, "success": success})


def add_question_category_link(request, category_id, question_id):
    cat = category_id
    ques = question_id
    new_data = QuestionCategoryBridge(question_id=ques, category_id=cat)
    new_data.save()
    

    # response = HttpResponse(status=302)
    # response['Location'] = f'/question_link_category/{cat}'
    # return response

    return redirect(f'/question_link_category/{cat}/success')

def add_evaluation_category_link(request, evaluation_group_id, category_id):
    cat = category_id
    eval = evaluation_group_id
    new_data = CategoryEvaluationBridge(evaluation_group_id=eval, category_id=cat)
    new_data.save()
    

    # response = HttpResponse(status=302)
    # response['Location'] = f'/question_link_category/{cat}'
    # return response

    return redirect(f'/evaluation_link_category/{evaluation_group_id}/success')

def question_category_delete(request, pk):
    data = get_object_or_404(QuestionCategory, pk=pk)
    if request.method == "POST":
        data.delete()
    return redirect("/question_categories")

def question_category_link_delete(request,cat,pk):
    data = get_object_or_404(QuestionCategoryBridge, pk=pk)
    if request.method == "POST":
        data.delete()
    return redirect(f"/question_link_category/{cat}")


def question_category_detail(request, pk):
    data = get_object_or_404(QuestionCategory, pk=pk)
    
    errors = None
    success = None

    if request.method == 'POST':
        data.name = request.POST.get("name")
        data.percentage = int(request.POST.get("percentage"))
        data.save()
        success = "Successfully updated"

    return render(
        request,
        "eva/question_category_detail.html",
        {
            "errors": errors,
            "success": success,
            "data": data,
        })

def evaluate_group_admin_detail(request, pk):
    data = get_object_or_404(EvaluationGroup, pk=pk)

    employees = AppUser.objects.filter(role='employee').all()
    categories = CategoryEvaluationBridge.objects.all().filter(evaluation_group_id = pk)
    categories = CategoryEvaluationBridge.objects.raw(
        f"""
            SELECT t2.id, t2.name FROM eva_categoryevaluationbridge t1
            LEFT JOIN (SELECT * from eva_questioncategory) t2 
            ON t1.category_id = t2.id
            WHERE t1.evaluation_group_id = {pk}
        """
    )

    

    questions = Question.objects.raw(
        """ 
            SELECT t1.id, t1.question_id, t2.name, t1.category_id FROM eva_questioncategorybridge t1
            LEFT JOIN (SELECT * FROM eva_question) t2 
            ON t1.question_id = t2.id
        """
    )
    # disable_evaluation_form = AppSettings.objects.filter(key='disable_evaluation_form').get_or_create()[0]
    # disable_evaluation_form = disable_evaluation_form.value == 'on'
    
    # data = EvaluationGroup.objects.all()

    print(questions)

    
    import datetime

    today = datetime.datetime.now().strftime("%Y-%m-%d")
  


    return render(request, "eva/evaluate_group_admin_detail.html",{
        "employees": employees,
        "categories": categories,
        "questions": questions,
        # "disable_evaluation_form": disable_evaluation_form,
        "data": data,
        "date_today": today
    })



def post_evaluate(request):
    if request.method == 'GET':
        return HttpResponse('Not allowed')
    filtered_cat = QuestionCategory.objects.raw(
        f"""
            SELECT * FROM eva_questioncategory where id in (SELECT category_id from eva_categoryevaluationbridge where evaluation_group_id = {request.POST.get("evaluate_group")})
        """
    )
    filtered_cat_id = CategoryEvaluationBridge.objects.values('category_id').filter(evaluation_group_id =  request.POST.get("evaluate_group"))
    arr = []
    for i in filtered_cat_id:
        arr.append(str(i['category_id']))
    print(','.join(arr))
    categories = [x.to_json() for x in filtered_cat]
    # questions = [{"id": x.id, "name": x.name, "category": x.category.id, "answer": request.POST.get(str(x.id))} for x in Question.objects.all().filter(category_id__in = filtered_cat_id)]
    questions = [{"id": x.id, "name": x.name, "category": x.category_id, "answer": request.POST.get(str(x.id))} for x in Question.objects.raw(f"""SELECT t2.id id, t2.name name, t3.id category_id 
FROM eva_questioncategorybridge t1 
left join eva_question t2 
on t1.question_id = t2.id 
left join eva_questioncategory t3 
on t1.category_id = t3.id
where t1.category_id in ({','.join(arr)});""")]


    # print(questions)

    # for field in fields_to_check:
    #     if not request.POST.get(field):
    #         return render(request, "eva/error.html")

    # New evaluation sheet data
    data = EvaluationSheet()
    data.evaluator_name = request.POST.get("evaluator")
    data.comments_and_recommendations = request.POST.get("comments", None) or None

    employee_id = int(request.POST.get("employee"))

    employee = AppUser.objects.get(pk=employee_id)
    data.employee = employee
    
    data.evaluate_group = request.POST.get("evaluate_group")
    data.evaluations = json.dumps({'categories': categories, 'questions': questions})
    
    # print(data)
    # print("test")
    data.save()

    return render(request, "eva/success.html")


def department_delete(request, pk):
    data = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        data.delete()
    return redirect("/departments")


def employee_delete(request, pk):
    data = get_object_or_404(AppUser, pk=pk)
    if request.method == "POST":
        data.delete()
    return redirect("/employees")


def question_delete(request, pk):
    data = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        data.delete()
    return redirect("/questions")


def employee_detail(request, pk):
    data = get_object_or_404(AppUser, pk=pk)

    errors = None
    success = None

    def set_info():
        data.first_name = request.POST.get("first_name")
        data.last_name = request.POST.get("last_name")
        data.email = request.POST.get("email")
        data.department = Department.objects.get(pk=request.POST.get("department"))
        data.save()

    def set_password():
        data.password = request.POST.get("password")
        data.save()

    def validate_password():
        if not request.POST.get("password") or not request.POST.get("confirm_password"):
            raise ValidationError("Please input password")

        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            raise ValidationError("Confirm password is incorrect. Please make sure your new password is the same with confirm password.")

    if request.method == 'POST':
        change_password = request.POST.get("change_password")
        if change_password:
            try:
                validate_password()
                set_password()
            except Exception as e:
                errors = e.error_list
        else:
            set_info()

        if not errors:
            success = "Successfully updated"

    departments = Department.objects.all()
    return render(
        request,
        "eva/employee_detail.html",
        {
            "errors": errors,
            "success": success,
            "departments": departments,
            "data": data,
        })

def admin_detail(request, pk):
    data = get_object_or_404(AppUser, pk=pk)

    errors = None
    success = None

    def set_info():
        data.first_name = request.POST.get("first_name")
        data.last_name = request.POST.get("last_name")
        data.email = request.POST.get("email")
        data.save()

    def set_password():
        data.password = request.POST.get("password")
        data.save()

    def validate_password():
        if not request.POST.get("password") or not request.POST.get("confirm_password"):
            raise ValidationError("Please input password")

        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            raise ValidationError("Confirm password is incorrect. Please make sure your new password is the same with confirm password.")

    if request.method == 'POST':
        change_password = request.POST.get("change_password")
        if change_password:
            try:
                validate_password()
                set_password()
            except Exception as e:
                errors = e.error_list
        else:
            set_info()

        if not errors:
            success = "Successfully updated"
    form = ImageForm()

    return render(
        request,
        "eva/admin_detail.html",
        {
            "errors": errors,
            "success": success,
            "departments": departments,
            "data": data,
            "form": form,
        })

def post_image_admin_detail(request, pk):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            
            form.instance.reference = get_object_or_404(AppUser, pk=pk)
            form.save()
            # Get the current instance object to display in the template
            return HttpResponseRedirect('/profile_admin')
         
def post_image_employee(request, pk):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            
            form.instance.reference = get_object_or_404(AppUser, pk=pk)
            form.save()
            # Get the current instance object to display in the template
            return HttpResponseRedirect('/profile')

def post_image_company(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            
            form.instance.company_logo = True
            form.save()
            # Get the current instance object to display in the template
            return HttpResponseRedirect('/about')

def company_detail(request):

    errors = None
    success = None

    def set_info():

        if request.method == 'POST':
            company_name = AppSettings.objects.filter(key='company_name').get_or_create()[0]
            company_name.key = 'company_name'
            company_name.value = request.POST.get("company_name")
            company_name.save()
         
            address = AppSettings.objects.filter(key='address').get_or_create()[0]
            address.key = 'address'
            address.value = request.POST.get("address")
            address.save()
         
            telephone_number = AppSettings.objects.filter(key='telephone_number').get_or_create()[0]
            telephone_number.key = 'telephone_number'
            telephone_number.value = request.POST.get("telephone_number")
            telephone_number.save()
         
            email = AppSettings.objects.filter(key='email').get_or_create()[0]
            email.key = 'email'
            email.value = request.POST.get("email")
            email.save()
         
        
        success = "Successfully saved"

    set_info()
    
    return render(
        request,
        "eva/company_detail.html",
        {
            "errors": errors,
            "success": success,
        })


def department_detail(request, pk):
    data = get_object_or_404(Department, pk=pk)
    
    errors = None
    success = None

    if request.method == 'POST':
        data.name = request.POST.get("name")
        data.save()
        success = "Successfully updated"

    return render(
        request,
        "eva/department_detail.html",
        {
            "errors": errors,
            "success": success,
            "data": data,
        })


def settings(request):
    success = None

    if request.method == 'POST':
        enable_admin_registration = AppSettings.objects.filter(key='enable_admin_registration').get_or_create()[0]
        enable_admin_registration.key = 'enable_admin_registration'
        enable_admin_registration.value = request.POST.get("enable_admin_registration", 'off') or 'off'
        enable_admin_registration.save()
     
        disable_evaluation_form = AppSettings.objects.filter(key='disable_evaluation_form').get_or_create()[0]
        disable_evaluation_form.key = 'disable_evaluation_form'
        disable_evaluation_form.value = request.POST.get("disable_evaluation_form", 'off') or 'off'
        disable_evaluation_form.save()
        
        success = "Successfully saved"


    settings = AppSettings.objects.all()
    data = {x.key: x.value for x in settings}

    return render(
        request,
        "eva/settings.html",
        {
            "success": success,
            "data": data
        }
    )

def about(request):
    success = None
    settings = AppSettings.objects.all()
    data = {x.key: x.value for x in settings}
    

    form = ImageForm()
    image = Image.objects.filter(company_logo=True)
    if image:
        image = image[len(image)-1]

    return render(
        request, "eva/about.html",
         {
            "success": success,
            "data": data,
            "form": form,
            "image": image
        }

        )

def about_employee(request):
    success = None
    settings = AppSettings.objects.all()
    data = {x.key: x.value for x in settings}

    form = ImageForm()
    image = Image.objects.filter(company_logo=True)
    if image:
        image = image[len(image)-1]

    return render(
        request, "eva/about_employee.html",
         {
            "success": success,
            "data": data,
            "form": form,
            "image": image
        }

        )

