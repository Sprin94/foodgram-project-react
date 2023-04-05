import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework.serializers import Field, ValidationError


def generate_uuid(max_length=12) -> str:
    """Генерирует 12 символов UUID"""
    return uuid.uuid4().hex[:max_length]


class Base64Field(Field):
    def to_internal_value(self, value: str):
        data = value.split(',')
        if not data[0].startswith('data:image/png;base64'):
            raise ValidationError('Не корректная строка')
        image_data = base64.b64decode(data[1])
        name = generate_uuid()
        return ContentFile(image_data, name=f'{name}.png')
