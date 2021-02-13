from django import template

# Это чтобы register.filter работал
register = template.Library()

# Расскажем django о нашем крутом фильтре
@register.filter
def rupluralize(value, arg="результат,результата,результатов"):
    args = arg.split(",")
    number = abs(int(value))
    a = number % 10
    b = number % 100

    if (a == 1) and (b != 11):
        return args[0]
    elif (a >= 2) and (a <= 4) and ((b < 10) or (b >= 20)):
        return args[1]
    else:
        return args[2]