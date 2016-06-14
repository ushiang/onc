from django.core.exceptions import ValidationError

def validate_even(value):
    if value % 2 != 0:
        raise ValidationError('%s is not an even number' % value)

def min_length(value, length, field):
    if len(value) < length:
        raise ValidationError('"%s" must be equal to or more than %s characters long' % (field, length))

def date_range(end, start, field):
    if len(value) < length:
        raise ValidationError('"%s" must be equal to or more than %s characters long' % (field, length))
