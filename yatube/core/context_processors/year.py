from datetime import date


def year(request):
    """Добавляет переменную с текущим годом."""
    dt = date.today().year
    return {
        'year': dt
    }
