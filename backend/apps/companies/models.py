import uuid

from django.db import models


class Company(models.Model):
    class CompanyType(models.TextChoices):
        COMMERCIAL = "COMMERCIAL", "Commercial"
        PRODUCTION = "PRODUCTION", "Production"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
    )

    national_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
    )

    company_type = models.CharField(
        max_length=20,
        choices=CompanyType.choices,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "companies"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.national_id})"
