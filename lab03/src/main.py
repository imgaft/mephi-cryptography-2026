"""
Лабораторная работа №3.
Создание электронной подписи в документе.

Вариант №7.
ГОСТ Р 34.10-94 (учебная реализация).
"""

from src.checksum import checksum_16, checksum_hex
from src.gost_signature import (
    GOSTSignature,
    generate_keys,
    get_report_parameters,
    message_hash,
    sign_message,
    verify_signature,
)


def print_separator():
    print("=" * 65)


def demonstrate(message: str):
    """Демонстрация формирования и проверки электронной подписи."""

    print_separator()
    print("ЛАБОРАТОРНАЯ РАБОТА №3")
    print("Создание электронной подписи в документе")
    print("Вариант №7")
    print_separator()

    # 1. Параметры алгоритма
    params = get_report_parameters()

    print("\n1. ПАРАМЕТРЫ АЛГОРИТМА")
    print(f"p = {params.p}")
    print(f"q = {params.q}")
    print(f"a = {params.a}")

    # 2. Исходное сообщение и контрольная сумма
    print("\n2. ИСХОДНОЕ СООБЩЕНИЕ")
    print(f"Сообщение: {message}")
    print(f"Контрольная сумма (HEX): {checksum_hex(message)}")
    print(f"Контрольная сумма (DEC): {checksum_16(message)}")
    print(f"Хеш для подписи (mod q): {message_hash(message, params.q)}")

    # 3. Генерация ключей
    keys = generate_keys(params)

    print("\n3. ГЕНЕРАЦИЯ КЛЮЧЕЙ")
    print(f"Закрытый ключ x = {keys.private_key}")
    print(f"Открытый ключ y = {keys.public_key}")

    # 4. Формирование подписи
    signature = sign_message(
        message,
        keys.private_key,
        params,
    )

    print("\n4. ФОРМИРОВАНИЕ ЭЛЕКТРОННОЙ ПОДПИСИ")
    print(f"r = {signature.r}")
    print(f"s = {signature.s}")
    print(f"Электронная подпись: ({signature.r}, {signature.s})")

    # 5. Проверка корректной подписи
    valid = verify_signature(
        message,
        signature,
        keys.public_key,
        params,
    )

    print("\n5. ПРОВЕРКА ИСХОДНОГО СООБЩЕНИЯ")
    print(f"Результат: {'ПОДПИСЬ ВЕРНА' if valid else 'ПОДПИСЬ НЕВЕРНА'}")

    # 6. Изменение сообщения
    # Выбираем изменение, действительно меняющее 16-битную сумму.
    modified_message = message + "!"
    if message_hash(modified_message, params.q) == message_hash(message, params.q):
        raise RuntimeError("Изменение сообщения не изменило контрольную сумму")

    modified_valid = verify_signature(
        modified_message,
        signature,
        keys.public_key,
        params,
    )

    print("\n6. ПРОВЕРКА ИЗМЕНЁННОГО СООБЩЕНИЯ")
    print(f"Изменённое сообщение: {modified_message}")
    print(
        "Результат:",
        "ПОДПИСЬ ВЕРНА" if modified_valid else "ПОДПИСЬ НЕВЕРНА",
    )

    # 7. Изменение подписи
    # Изменяем s в допустимом диапазоне и ищем отвергаемый вариант.
    # Это проверяет математическую верификацию, а не только границы.
    modified_signature = None
    for offset in range(1, 5):
        new_s = (signature.s - 1 + offset) % (params.q - 1) + 1
        if new_s == signature.s:
            continue
        candidate = GOSTSignature(r=signature.r, s=new_s)
        if not verify_signature(message, candidate, keys.public_key, params):
            modified_signature = candidate
            break
    if modified_signature is None:
        raise RuntimeError("Не удалось получить отвергаемую изменённую подпись")

    signature_valid = verify_signature(
        message,
        modified_signature,
        keys.public_key,
        params,
    )

    print("\n7. ПРОВЕРКА ИЗМЕНЁННОЙ ПОДПИСИ")
    print(
        f"Изменённая подпись: "
        f"({modified_signature.r}, {modified_signature.s})"
    )
    print(
        "Результат:",
        "ПОДПИСЬ ВЕРНА" if signature_valid else "ПОДПИСЬ НЕВЕРНА",
    )

    # 8. Итоги
    print("\n8. ИТОГИ")

    checks = {
        "Исходная подпись принимается": valid,
        "Изменённое сообщение отклоняется": not modified_valid,
        "Изменённая подпись отклоняется": not signature_valid,
    }

    for description, result in checks.items():
        print(f"{description}: {'OK' if result else 'FAIL'}")

    print_separator()

    return all(checks.values())


if __name__ == "__main__":
    examples = [
        "AB",
        "Лабораторная работа №3",
        "Электронная подпись документа",
    ]

    for example in examples:
        if not demonstrate(example):
            raise SystemExit("Ошибка демонстрации")
        print()
