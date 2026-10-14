"""Лабораторная работа № 1. Многоалфавитное шифрование.

Вариант № 6.
Подстановочные алфавиты № 1 и № 3.
"""

# Исходный русский алфавит (33 буквы и пробел).
ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЫЭЮЯ "

# Подстановочный алфавит № 1.
ALPHABET_1 = "".join([
    "Б", "Ю", "Г", "Ы", "Е", "Ь", "З", "Ш", "Й", "Ц",
    "Л", "Ф", "Н", "Т", "П", "Р", "С", "О", "У", "М",
    "Х", "К", "Ч", "И", "Щ", "Ж", "Ъ", "Д", "Э", "В",
    "Я", " ", "А", "Ё"
])

# Подстановочный алфавит № 3.
ALPHABET_3 = "".join([
    "О", "П", "М", "Н", "Х", "Л", "И", "Й", "Ж", "З",
    "Д", "Е", "В", "Г", "А", "Б", "Ю", "Я", "Ы", "Э",
    "Ь", " ", "Ш", "Щ", "Ц", "Ч", "Ф", "К", "Т", "У",
    "Р", "С", "Ъ", "Ё"
])


def validate_alphabets() -> None:
    """Проверяет корректность подстановочных алфавитов."""

    for number, alphabet in ((1, ALPHABET_1), (3, ALPHABET_3)):

        if len(alphabet) != len(ALPHABET):
            raise ValueError(
                f"Алфавит № {number}: неверное количество символов"
            )

        if set(alphabet) != set(ALPHABET):
            raise ValueError(
                f"Алфавит № {number}: неверный набор символов"
            )


def encrypt(text: str) -> str:
    """Шифрует текст с чередованием алфавитов № 1 и № 3."""
    result = []

    for i, char in enumerate(text.upper()):
        if char not in ALPHABET:
            raise ValueError(f"Недопустимый символ: {char}")

        index = ALPHABET.index(char)

        if i % 2 == 0:
            encrypted_char = ALPHABET_1[index]
        else:
            encrypted_char = ALPHABET_3[index]

        result.append(encrypted_char)

    return "".join(result)


def decrypt(text: str) -> str:
    """Восстанавливает исходный текст по криптограмме."""
    result = []

    for i, char in enumerate(text):
        if i % 2 == 0:
            alphabet = ALPHABET_1
        else:
            alphabet = ALPHABET_3

        if char not in alphabet:
            raise ValueError(f"Недопустимый символ: {char}")

        index = alphabet.index(char)
        result.append(ALPHABET[index])

    return "".join(result)
def main() -> None:
    """Запускает шифрование и дешифрование текста."""
    validate_alphabets()

    print("Лабораторная работа № 1")
    print("Вариант № 6")
    print("Метод: многоалфавитное шифрование")
    print()

    text = input("Введите исходный текст: ").upper()

    encrypted = encrypt(text)
    decrypted = decrypt(encrypted)

    print()
    print(f"Исходный текст:       {text}")
    print(f"Криптограмма:         {encrypted}")
    print(f"Расшифрованный текст: {decrypted}")
    print(f"Проверка совпадения:  {text == decrypted}")


if __name__ == "__main__":
    main()