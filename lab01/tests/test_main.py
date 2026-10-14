"""Тесты многоалфавитного шифрования."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import (
    ALPHABET,
    ALPHABET_1,
    ALPHABET_3,
    encrypt,
    decrypt,
    validate_alphabets,
)


def test_alphabets():
    """Проверка подстановочных алфавитов."""
    validate_alphabets()

    assert len(ALPHABET) == 34
    assert len(ALPHABET_1) == 34
    assert len(ALPHABET_3) == 34


def test_encrypt():
    """Проверка шифрования с известным результатом."""
    assert encrypt("ПРИВЕТ") == "СЯЦМЬЭ"


def test_decrypt():
    """Проверка дешифрования."""
    assert decrypt("СЯЦМЬЭ") == "ПРИВЕТ"


def test_encrypt_decrypt():
    """Проверка обратимости шифрования."""
    text = "ПРИВЕТ МИР"

    encrypted = encrypt(text)
    decrypted = decrypt(encrypted)

    assert decrypted == text


def test_spaces():
    """Проверка обработки пробелов."""
    text = "А Б"

    assert decrypt(encrypt(text)) == text


def test_lowercase():
    """Проверка строчных букв."""
    assert decrypt(encrypt("привет")) == "ПРИВЕТ"


def test_invalid_character():
    """Проверка недопустимых символов."""
    with pytest.raises(ValueError):
        encrypt("ПРИВЕТ!")


def test_empty_string():
    """Проверка пустой строки."""
    assert encrypt("") == ""
    assert decrypt("") == ""