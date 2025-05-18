# src/domain/errors.py

class DomainError(Exception):
    """Базовый класс ошибок домена."""
    pass

class InvalidAction(DomainError):
    """Невалидное действие (выход за границы, не тот тип цели, недостаточно AP)."""
    pass

class OutOfBounds(InvalidAction):
    """Попытка выйти за пределы поля."""
    pass

class InsufficientAP(InvalidAction):
    """Недостаточно очков действия для выполнения способности."""
    pass

class LineOfSightBlocked(InvalidAction):
    """Линия видимости заблокирована препятствием."""
    pass

class WrongTargetType(InvalidAction):
    """Цель не соответствует требованиям способности (enemy/ally/dead)."""
    pass
