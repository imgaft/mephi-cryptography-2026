"""
НИЯУ МИФИ
Лабораторная работа № 4

Тема:
Реализация протокола Диффи–Хеллмана
на эллиптических кривых.

Студент: Гафт Илья Маратович
Номер в списке: 30
Вариант: 1
"""

from elliptic_curve import (
    EllipticCurve,
    find_points_by_x,
)
from ecdh import ECDHParameters, perform_ecdh


def print_separator():
    print("=" * 65)


def main():
    print_separator()
    print("ЛАБОРАТОРНАЯ РАБОТА № 4")
    print("Протокол Диффи–Хеллмана на эллиптических кривых")
    print("Вариант № 1")
    print_separator()

    # Исходные параметры варианта № 1
    a = -1
    b = 1
    p = 29

    original_g = (9, 27)

    k1 = 4
    k2 = 17

    print("\n1. ИСХОДНЫЕ ДАННЫЕ")

    print(f"a = {a}")
    print(f"b = {b}")
    print(f"p = {p}")
    print(f"G из методички = {original_g}")
    print(f"k1 = {k1}")
    print(f"k2 = {k2}")

    # Создание и проверка кривой
    curve = EllipticCurve(a, b, p)

    print("\n2. ПРОВЕРКА КРИВОЙ")

    print(
        "Уравнение: "
        "y^2 = x^3 - x + 1 (mod 29)"
    )

    print(
        "Дискриминант:",
        curve.discriminant()
    )

    print("Кривая корректна: ДА")

    # Проверка точки из методички
    print("\n3. ПРОВЕРКА БАЗОВОЙ ТОЧКИ")

    x, y = original_g

    left = y ** 2 % p
    right = (x ** 3 + a * x + b) % p

    print(f"Исходная точка G = {original_g}")

    print("\nПроверка уравнения:")
    print(f"y² mod {p} = {left}")
    print(f"(x³ + ax + b) mod {p} = {right}")

    if curve.is_on_curve(original_g):
        print("\nТочка принадлежит кривой: ДА")
        generator = original_g

    else:
        print(f"\n{left} != {right}")
        print("Точка принадлежит кривой: НЕТ")

        print("\nПОИСК КОРРЕКТНОЙ БАЗОВОЙ ТОЧКИ")

        print(f"Сохраняем координату x = {x}")

        candidates = find_points_by_x(curve, x)

        print(
            f"\ny² = ({x}³ + ({a})*{x} + {b}) mod {p}"
        )
        print(f"y² = {right} (mod {p})")

        print("\nНайденные точки:")

        for point in candidates:
            print(f"G = {point}")

        if not candidates:
            raise ValueError(
                "Не найдены точки с заданной координатой x"
            )

        # Выбираем допустимую точку,
        # максимально близкую к исходной по y.
        generator = min(
            candidates,
            key=lambda point: (
                abs(point[1] - y),
                point[1]
            )
        )

        print(
            "\nКритерий выбора: минимальное "
            "изменение координаты y"
        )

        print(f"Выбрана точка G = {generator}")

        gx, gy = generator

        new_left = gy ** 2 % p

        new_right = (
                            gx ** 3 + a * gx + b
                    ) % p

        print("\nПовторная проверка:")
        print(f"{gy}² mod {p} = {new_left}")
        print(
            f"({gx}³ + ({a})*{gx} + {b}) "
            f"mod {p} = {new_right}"
        )

        assert new_left == new_right

        print("\nТочка принадлежит кривой: ДА")

    # Проверка выбранной точки
    curve.validate_point(generator)

    parameters = ECDHParameters(
        curve,
        generator
    )

    order = curve.point_order(generator)

    print("\n4. ПАРАМЕТРЫ ПРОТОКОЛА")

    print(f"G = {generator}")
    print(f"Порядок точки G = {order}")

    # Демонстрация операций
    print("\n5. ОПЕРАЦИИ НАД ТОЧКАМИ")

    double_g = curve.double(generator)

    triple_g = curve.add(
        double_g,
        generator
    )

    print(f"2G = {double_g}")
    print(f"3G = {triple_g}")

    # Выполнение ECDH
    print("\n6. ОБМЕН ОТКРЫТЫМИ КЛЮЧАМИ")

    result = perform_ecdh(
        parameters,
        k1,
        k2
    )

    print(
        f"Alice: QA = {k1}G = "
        f"{result['public_a']}"
    )

    print(
        f"Bob:   QB = {k2}G = "
        f"{result['public_b']}"
    )

    print("\n7. ВЫЧИСЛЕНИЕ ОБЩЕГО СЕКРЕТА")

    print(
        f"Alice: K = {k1} * QB = "
        f"{result['shared_a']}"
    )

    print(
        f"Bob:   K = {k2} * QA = "
        f"{result['shared_b']}"
    )

    print("\n8. ПРОВЕРКА СОВПАДЕНИЯ")

    print(
        "Общие секреты совпадают:",
        result["keys_match"]
    )

    assert result["keys_match"], (
        "Ошибка: общие секреты не совпадают"
    )

    # Независимая математическая проверка
    expected = curve.multiply(
        k1 * k2,
        generator
    )

    print(
        "Контрольное вычисление "
        "(k1*k2)*G:",
        expected
    )

    assert expected == result["shared_a"]

    print("\nРЕЗУЛЬТАТ: ПРОТОКОЛ ВЫПОЛНЕН УСПЕШНО")

    print_separator()


if __name__ == "__main__":
    main()
