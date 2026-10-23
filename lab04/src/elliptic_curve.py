"""
Лабораторная работа № 4.
Арифметика точек эллиптической кривой над конечным полем F_p.

Кривая:
    y^2 = x^3 + ax + b (mod p)

Точка на бесконечности представляется значением None.

Реализация предназначена для учебных целей.
"""

from dataclasses import dataclass
from typing import Optional, Tuple


Point = Optional[Tuple[int, int]]


def is_prime(n: int) -> bool:
    """Проверка простоты числа методом пробного деления."""
    if n < 2:
        return False

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    divisor = 3

    while divisor * divisor <= n:
        if n % divisor == 0:
            return False

        divisor += 2

    return True


def mod_inverse(value: int, modulus: int) -> int:
    """
    Вычисление обратного элемента по модулю
    расширенным алгоритмом Евклида.

    Возвращает x:
        value * x = 1 (mod modulus)
    """
    if modulus <= 1:
        raise ValueError("Модуль должен быть больше 1")

    value %= modulus

    if value == 0:
        raise ValueError(
            "Обратный элемент для нуля не существует"
        )

    old_r, r = modulus, value
    old_t, t = 0, 1

    while r != 0:
        quotient = old_r // r

        old_r, r = r, old_r - quotient * r
        old_t, t = t, old_t - quotient * t

    if old_r != 1:
        raise ValueError(
            "Обратный элемент не существует"
        )

    return old_t % modulus


def find_points_by_x(curve, x: int) -> list:
    """
    Поиск всех точек эллиптической кривой
    с заданной координатой x.

    Используется перебор значений y от 0 до p-1.
    Подходит для учебных кривых малого размера.
    """
    if not 0 <= x < curve.p:
        raise ValueError(
            "Координата x должна принадлежать полю F_p"
        )

    return [
        (x, y)
        for y in range(curve.p)
        if curve.is_on_curve((x, y))
    ]


@dataclass(frozen=True)
class EllipticCurve:
    """Эллиптическая кривая над простым полем F_p."""

    a: int
    b: int
    p: int

    def __post_init__(self):
        if not is_prime(self.p):
            raise ValueError(
                "Модуль p должен быть простым числом"
            )

        if self.p <= 3:
            raise ValueError(
                "Для данной реализации требуется p > 3"
            )

        discriminant = (
            4 * self.a**3 + 27 * self.b**2
        ) % self.p

        if discriminant == 0:
            raise ValueError(
                "Эллиптическая кривая вырождена"
            )

    def discriminant(self) -> int:
        """Дискриминант кривой по модулю p."""
        return (
            4 * self.a**3 + 27 * self.b**2
        ) % self.p

    def is_on_curve(self, point: Point) -> bool:
        """Проверка принадлежности точки кривой."""
        if point is None:
            return True

        x, y = point

        if not (0 <= x < self.p and 0 <= y < self.p):
            return False

        left = y**2 % self.p

        right = (
            x**3 + self.a * x + self.b
        ) % self.p

        return left == right

    def validate_point(self, point: Point) -> None:
        """Проверка корректности точки."""
        if not self.is_on_curve(point):
            raise ValueError(
                f"Точка {point} не принадлежит кривой"
            )

    def negate(self, point: Point) -> Point:
        """Получение противоположной точки."""
        self.validate_point(point)

        if point is None:
            return None

        x, y = point

        return x, (-y) % self.p

    def add(self, p1: Point, p2: Point) -> Point:
        """Сложение двух точек эллиптической кривой."""
        self.validate_point(p1)
        self.validate_point(p2)

        # P + O = P
        if p1 is None:
            return p2

        # O + P = P
        if p2 is None:
            return p1

        x1, y1 = p1
        x2, y2 = p2

        # P + (-P) = O
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None

        if p1 == p2:
            # Удвоение точки
            numerator = (
                3 * x1**2 + self.a
            ) % self.p

            denominator = (
                2 * y1
            ) % self.p

        else:
            # Сложение различных точек
            numerator = (
                y2 - y1
            ) % self.p

            denominator = (
                x2 - x1
            ) % self.p

        slope = (
            numerator
            * mod_inverse(denominator, self.p)
        ) % self.p

        x3 = (
            slope**2 - x1 - x2
        ) % self.p

        y3 = (
            slope * (x1 - x3) - y1
        ) % self.p

        result = (x3, y3)

        self.validate_point(result)

        return result

    def double(self, point: Point) -> Point:
        """Удвоение точки."""
        return self.add(point, point)

    def multiply(self, k: int, point: Point) -> Point:
        """
        Умножение точки на скаляр методом double-and-add.

        Сложность: O(log k).
        """
        self.validate_point(point)

        if not isinstance(k, int):
            raise TypeError(
                "Скаляр должен быть целым числом"
            )

        if k == 0 or point is None:
            return None

        if k < 0:
            return self.multiply(
                -k,
                self.negate(point)
            )

        result = None
        addend = point

        while k > 0:
            if k & 1:
                result = self.add(result, addend)

            addend = self.double(addend)

            k >>= 1

        return result

    def point_order(self, point: Point) -> int:
        """
        Вычисление порядка точки перебором.

        Используется только для учебных
        кривых малого размера.
        """
        self.validate_point(point)

        if point is None:
            return 1

        result = None

        # Верхняя граница по теореме Хассе
        limit = self.p + 1 + 2 * (
            self.p ** 0.5
        )

        for k in range(1, int(limit) + 2):
            result = self.add(result, point)

            if result is None:
                return k

        raise RuntimeError(
            "Не удалось определить порядок точки"
        )
