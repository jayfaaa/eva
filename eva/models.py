from django.db import models
import random
import string

class Department(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class AppUser(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    role = models.CharField(
        max_length=255,
        choices=(
            ("admin", "Admin"),
            ("employee", "Employee"),
        ),
    )
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=None, null=True)
    secret_key = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.email

    def full_name(self):
        return self.first_name + " " + self.last_name

    def save(self, *args, **kwargs):
        self.secret_key = self.email + ":" + ''.join(random.choice(string.ascii_letters) for i in range(8))
        super().save(*args, **kwargs)

class EvaluationSheet(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    evaluator_name = models.CharField(max_length=255, null=True, blank=True)
    evaluate_group = models.CharField(max_length=255, null=True, blank=True)
    employee = models.ForeignKey(AppUser, on_delete=models.CASCADE, default=None, null=True)
    employee_name = models.CharField(max_length=255)
    evaluations = models.TextField()
    comments_and_recommendations = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.employee_name}"

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.employee:
            self.employee_name = self.employee.first_name + " " + self.employee.last_name
        self.full_clean()
        super().save(*args, **kwargs)

class AppSettings(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key} => {self.value}"


class QuestionCategory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    percentage = models.IntegerField(default=0)
    # evaluate_group = models.IntegerField(default=None, null=True)

    def __str__(self):
        return self.name

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "percentage": self.percentage
        }

class Question(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    # category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return self.name

class QuestionCategoryBridge(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    question_id = models.IntegerField(default=0)
    category_id = models.IntegerField(default=0)

class CategoryEvaluationBridge(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    evaluation_group_id = models.IntegerField(default=0)
    category_id = models.IntegerField(default=0)

class Image(models.Model):

    image = models.ImageField(upload_to='images')
    reference = models.ForeignKey(AppUser, on_delete=models.CASCADE, default=None, null=True)
    company_logo = models.BooleanField(default=False)

   
class EvaluationGroup(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    range = models.CharField(max_length=1024)
    open_date = models.CharField(max_length=1024, default=None, null=True)
    close_date = models.CharField(max_length=1024, default=None, null=True)