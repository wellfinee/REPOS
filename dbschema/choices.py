from django.db import models

class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'ADMIN'
    DIRECTOR = 'DIRECTOR', 'DIRECTOR'
    TEACHER = 'TEACHER', 'TEACHER'
    STUDENT = 'STUDENT', 'STUDENT'
    PARENT = 'PARENT', 'PARENT'

class Weekday(models.TextChoices):
    MON = 'MON', 'MON'
    TUE = 'TUE', 'TUE'
    WED = 'WED', 'WED'
    THU = 'THU', 'THU'
    FRI = 'FRI', 'FRI'
    SAT = 'SAT', 'SAT'
    SUN = 'SUN', 'SUN'

class SubmissionStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'DRAFT'
    SUBMITTED = 'SUBMITTED', 'SUBMITTED'
    RETURNED = 'RETURNED', 'RETURNED'
    GRADED = 'GRADED', 'GRADED'

class AssessmentType(models.TextChoices):
    QUIZ = 'QUIZ', 'QUIZ'
    TEST = 'TEST', 'TEST'
    CONTROL = 'CONTROL', 'CONTROL'
    FINAL = 'FINAL', 'FINAL'

class ProductType(models.TextChoices):
    PHYSICAL = 'PHYSICAL', 'PHYSICAL'
    DIGITAL = 'DIGITAL', 'DIGITAL'

class OrderStatus(models.TextChoices):
    NEW = 'NEW', 'NEW'
    PAID = 'PAID', 'PAID'
    PROCESSING = 'PROCESSING', 'PROCESSING'
    SHIPPED = 'SHIPPED', 'SHIPPED'
    DELIVERED = 'DELIVERED', 'DELIVERED'
    CANCELLED = 'CANCELLED', 'CANCELLED'
    REFUNDED = 'REFUNDED', 'REFUNDED'

class CoinTxnType(models.TextChoices):
    EARN = 'EARN', 'EARN'
    SPEND = 'SPEND', 'SPEND'
    ADJUST = 'ADJUST', 'ADJUST'
    REFUND = 'REFUND', 'REFUND'

class RouletteOutcome(models.TextChoices):
    NONE = 'NONE', 'NONE'
    COINS = 'COINS', 'COINS'
    PRODUCT = 'PRODUCT', 'PRODUCT'
    ACHIEVEMENT = 'ACHIEVEMENT', 'ACHIEVEMENT'
