#!/usr/bin/env python3

"""
Лабораторная работа №2.
Изучение алгоритма RSA.

Вариант №2.
p = 211
q = 317

Реализация RSA без сторонних библиотек.
"""

from math import gcd, isqrt


# Исходные данные варианта №2
P = 211
Q = 317


def is_prime(number):
    """
    Проверяет, является ли число простым.
    """
    if number < 2:
        return False

    for divisor in range(2, isqrt(number) + 1):
        if number % divisor == 0:
            return False

    return True


def are_coprime(a, b):
    """
    Проверяет взаимную простоту двух чисел.

    Числа взаимно простые, если НОД = 1.
    """
    return gcd(a, b) == 1


def extended_gcd(a, b):
    """
    Расширенный алгоритм Евклида.

    Возвращает:
        gcd(a, b), x, y

    Такие, что:
        a*x + b*y = gcd(a, b)
    """
    if b == 0:
        return a, 1, 0

    divisor, x1, y1 = extended_gcd(b, a % b)

    x = y1
    y = x1 - (a // b) * y1

    return divisor, x, y


def modular_inverse(e, phi):
    """
    Вычисляет обратный элемент d:

        (e * d) mod phi = 1
    """
    divisor, x, _ = extended_gcd(e, phi)

    if divisor != 1:
        raise ValueError(
            "Обратный элемент не существует."
        )

    return x % phi


def generate_keys(p, q):
    """
    Генерирует открытый и закрытый ключи RSA.

    Открытый ключ: (e, n)
    Закрытый ключ: (d, n)
    """

    if not is_prime(p) or not is_prime(q):
        raise ValueError(
            "Числа p и q должны быть простыми."
        )

    if p == q:
        raise ValueError(
            "Числа p и q должны различаться."
        )

    # Модуль RSA
    n = p * q

    # Функция Эйлера
    phi = (p - 1) * (q - 1)

    # Минимальное допустимое e
    e = 2

    while e < phi:
        if are_coprime(e, phi):
            break
        e += 1
    else:
        raise ValueError(
            "Не удалось подобрать открытый показатель e."
        )

    # Закрытый показатель
    d = modular_inverse(e, phi)

    public_key = (e, n)
    private_key = (d, n)

    return public_key, private_key, phi


def encrypt(message, public_key):
    """
    Шифрует текст открытым ключом RSA.

    Текст преобразуется в UTF-8.
    Каждый байт шифруется отдельно.
    """

    e, n = public_key

    if n <= 255:
        raise ValueError(
            "Модуль RSA должен быть больше 255."
        )

    message_bytes = message.encode("utf-8")

    encrypted = []

    for byte in message_bytes:
        encrypted_byte = pow(byte, e, n)
        encrypted.append(encrypted_byte)

    return encrypted


def decrypt(encrypted, private_key):
    """
    Расшифровывает сообщение закрытым ключом RSA.
    """

    d, n = private_key

    decrypted_bytes = []

    for number in encrypted:
        if not isinstance(number, int) or not 0 <= number < n:
            raise ValueError(
                "Некорректный блок шифротекста."
            )

        decrypted_byte = pow(number, d, n)

        if not 0 <= decrypted_byte <= 255:
            raise ValueError(
                "Расшифрованное значение не является байтом."
            )

        decrypted_bytes.append(decrypted_byte)

    return bytes(decrypted_bytes).decode("utf-8")


def main():
    """
    Основная функция программы.
    """

    print("=" * 60)
    print("Лабораторная работа №2")
    print("Изучение алгоритма RSA")
    print("Вариант №2")
    print("=" * 60)

    public_key, private_key, phi = generate_keys(P, Q)

    e, n = public_key
    d, _ = private_key

    print("\n1. Генерация ключей RSA")

    print(f"p = {P}")
    print(f"q = {Q}")
    print(f"n = p * q = {n}")
    print(f"phi(n) = {phi}")
    print(f"e = {e}")
    print(f"d = {d}")

    print("\n2. Проверка взаимной простоты")

    print(f"НОД(e, phi) = {gcd(e, phi)}")
    print(f"Взаимно простые: {are_coprime(e, phi)}")

    print("\n3. Проверка закрытого показателя")

    print(f"(e * d) mod phi = {(e * d) % phi}")

    print("\n4. Ключи RSA")

    print(f"Открытый ключ: {public_key}")
    print(f"Закрытый ключ: {private_key}")

    print("\n5. Шифрование сообщения")

    message = input("Введите сообщение: ")

    encrypted = encrypt(message, public_key)

    print(f"\nИсходное сообщение: {message}")
    print(f"Зашифрованное сообщение: {encrypted}")

    print("\n6. Дешифрование сообщения")

    decrypted = decrypt(encrypted, private_key)

    print(f"Расшифрованное сообщение: {decrypted}")

    print("\n7. Проверка результата")

    if message == decrypted:
        print("УСПЕШНО: исходное сообщение восстановлено.")
    else:
        print("ОШИБКА: сообщения не совпадают.")


if __name__ == "__main__":
    main()
