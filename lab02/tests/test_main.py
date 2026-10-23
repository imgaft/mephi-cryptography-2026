#!/usr/bin/env python3

"""
Автоматические тесты RSA.
Лабораторная работа №2.
"""

import sys
import unittest

from pathlib import Path


# Подключаем исходный код лабораторной
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from main import (
    P,
    Q,
    is_prime,
    are_coprime,
    modular_inverse,
    generate_keys,
    encrypt,
    decrypt,
)


class TestRSA(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.public_key, cls.private_key, cls.phi = (
            generate_keys(P, Q)
        )

    def test_prime_numbers(self):
        """Проверка простых чисел."""

        self.assertTrue(is_prime(P))
        self.assertTrue(is_prime(Q))

        self.assertFalse(is_prime(100))
        self.assertFalse(is_prime(1))

    def test_coprime_numbers(self):
        """Проверка взаимной простоты."""

        self.assertTrue(are_coprime(11, 66360))
        self.assertFalse(are_coprime(10, 66360))

    def test_key_generation(self):
        """Проверка генерации ключей."""

        self.assertEqual(
            self.public_key,
            (11, 66887)
        )

        self.assertEqual(
            self.private_key,
            (24131, 66887)
        )

        self.assertEqual(
            self.phi,
            66360
        )

    def test_modular_inverse(self):
        """Проверка обратного элемента."""

        e = self.public_key[0]
        d = self.private_key[0]

        self.assertEqual(
            (e * d) % self.phi,
            1
        )

        self.assertEqual(
            modular_inverse(e, self.phi),
            d
        )

    def test_russian_text(self):
        """Шифрование русского текста."""

        message = "Привет, мир!"

        encrypted = encrypt(
            message,
            self.public_key
        )

        decrypted = decrypt(
            encrypted,
            self.private_key
        )

        self.assertEqual(message, decrypted)

    def test_english_text(self):
        """Шифрование английского текста."""

        message = "Hello, RSA!"

        encrypted = encrypt(
            message,
            self.public_key
        )

        decrypted = decrypt(
            encrypted,
            self.private_key
        )

        self.assertEqual(message, decrypted)

    def test_numbers_and_symbols(self):
        """Шифрование цифр и символов."""

        message = "RSA 2026! @#$%"

        encrypted = encrypt(
            message,
            self.public_key
        )

        decrypted = decrypt(
            encrypted,
            self.private_key
        )

        self.assertEqual(message, decrypted)

    def test_empty_message(self):
        """Шифрование пустой строки."""

        message = ""

        encrypted = encrypt(
            message,
            self.public_key
        )

        decrypted = decrypt(
            encrypted,
            self.private_key
        )

        self.assertEqual(message, decrypted)

    def test_unicode(self):
        """Шифрование Unicode."""

        message = "Криптография 🔐 RSA"

        encrypted = encrypt(
            message,
            self.public_key
        )

        decrypted = decrypt(
            encrypted,
            self.private_key
        )

        self.assertEqual(message, decrypted)

    def test_invalid_primes(self):
        """Проверка некорректных p и q."""

        with self.assertRaises(ValueError):
            generate_keys(10, 317)

        with self.assertRaises(ValueError):
            generate_keys(211, 211)


if __name__ == "__main__":
    unittest.main(verbosity=2)
