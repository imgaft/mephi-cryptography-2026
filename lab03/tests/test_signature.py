"""Тестирование учебной реализации ГОСТ Р 34.10-94."""

import unittest
from unittest.mock import patch

from src.gost_signature import (
    GOSTParameters,
    GOSTSignature,
    generate_keys,
    get_demo_parameters,
    get_report_parameters,
    message_hash,
    sign_message,
    validate_parameters,
    verify_signature,
)


class TestGOSTSignature(unittest.TestCase):

    def setUp(self):
        self.params = get_demo_parameters()
        self.message = "Лабораторная работа №3"

        # Фиксированный ключ для воспроизводимости.
        self.private_key = 7
        self.public_key = pow(
            self.params.a,
            self.private_key,
            self.params.p,
        )

    def test_report_parameters(self):
        params = get_report_parameters()
        self.assertEqual(params.p.bit_length(), 512)
        self.assertEqual(params.q.bit_length(), 256)
        validate_parameters(params)

    def test_in_range_tampering(self):
        params = get_report_parameters()
        x = 7
        y = pow(params.a, x, params.p)
        sig = sign_message("AB", x, params)
        self.assertTrue(verify_signature("AB", sig, y, params))
        self.assertFalse(verify_signature("AC", sig, y, params))
        altered = GOSTSignature(sig.r, sig.s % (params.q - 1) + 1)
        self.assertTrue(0 < altered.s < params.q)
        self.assertFalse(verify_signature("AB", altered, y, params))

    def test_checksum_collision(self):
        # XOR-свёртка не обладает криптографической стойкостью.
        from src.checksum import checksum_16
        self.assertEqual(checksum_16(""), checksum_16("\x00\x00"))

    def test_collision_keeps_signature_valid(self):
        """Доказывает ограничение 16-битной суммы: коллизия проходит проверку."""
        params = get_report_parameters()
        x = 7
        y = pow(params.a, x, params.p)
        signature = sign_message("", x, params)
        self.assertTrue(verify_signature("", signature, y, params))
        self.assertTrue(verify_signature("\x00\x00", signature, y, params))

    def test_valid_parameters(self):
        """Корректные параметры принимаются."""
        self.assertIsNone(
            validate_parameters(self.params)
        )

    def test_invalid_p(self):
        """Составное p отклоняется."""
        with self.assertRaises(ValueError):
            validate_parameters(
                GOSTParameters(p=21, q=11, a=2)
            )

    def test_invalid_q(self):
        """Составное q отклоняется."""
        with self.assertRaises(ValueError):
            validate_parameters(
                GOSTParameters(p=23, q=4, a=2)
            )

    def test_invalid_divisibility(self):
        """q должно делить p - 1."""
        with self.assertRaises(ValueError):
            validate_parameters(
                GOSTParameters(p=23, q=5, a=2)
            )

    def test_invalid_a(self):
        """Проверка условия a^q mod p = 1."""
        with self.assertRaises(ValueError):
            validate_parameters(
                GOSTParameters(p=23, q=11, a=5)
            )

    def test_key_generation(self):
        """Генерация математически согласованной пары ключей."""
        keys = generate_keys(self.params)

        self.assertTrue(
            1 <= keys.private_key < self.params.q
        )

        self.assertEqual(
            keys.public_key,
            pow(
                self.params.a,
                keys.private_key,
                self.params.p,
            ),
        )

    def test_valid_signature(self):
        """Корректная подпись принимается."""
        signature = sign_message(
            self.message,
            self.private_key,
            self.params,
        )

        self.assertTrue(
            verify_signature(
                self.message,
                signature,
                self.public_key,
                self.params,
            )
        )

    def test_modified_message(self):
        """Изменение сообщения приводит к отклонению подписи."""

        params = get_report_parameters()

        private_key = 7
        public_key = pow(
            params.a,
            private_key,
            params.p,
        )

        original_message = "AB"
        modified_message = "AC"

        signature = sign_message(
            original_message,
            private_key,
            params,
        )

        self.assertTrue(
            verify_signature(
                original_message,
                signature,
                public_key,
                params,
            )
        )

        self.assertFalse(
            verify_signature(
                modified_message,
                signature,
                public_key,
                params,
            )
        )

    def test_modified_signature(self):
        """Подпись с недопустимым r отклоняется."""
        signature = GOSTSignature(r=0, s=5)

        self.assertFalse(
            verify_signature(
                self.message,
                signature,
                self.public_key,
                self.params,
            )
        )

    def test_invalid_r_boundary(self):
        """Проверка границ параметра r."""
        for r in (0, self.params.q, -1):
            with self.subTest(r=r):
                self.assertFalse(
                    verify_signature(
                        self.message,
                        GOSTSignature(r=r, s=1),
                        self.public_key,
                        self.params,
                    )
                )

    def test_invalid_s_boundary(self):
        """Проверка границ параметра s."""
        for s in (0, self.params.q, -1):
            with self.subTest(s=s):
                self.assertFalse(
                    verify_signature(
                        self.message,
                        GOSTSignature(r=1, s=s),
                        self.public_key,
                        self.params,
                    )
                )

    def test_invalid_public_key(self):
        """Некорректный открытый ключ отклоняется."""
        signature = sign_message(
            self.message,
            self.private_key,
            self.params,
        )

        self.assertFalse(
            verify_signature(
                self.message,
                signature,
                0,
                self.params,
            )
        )

    def test_hash_range(self):
        """Хеш приводится к диапазону 1..q-1."""
        h = message_hash(self.message, self.params.q)

        self.assertTrue(1 <= h < self.params.q)

    def test_zero_hash_replacement(self):
        """Нулевой остаток хеша заменяется единицей."""
        self.assertEqual(message_hash("", self.params.q), 1)

    def test_invalid_private_key(self):
        """Некорректный закрытый ключ отклоняется."""
        with self.assertRaises(ValueError):
            sign_message(
                self.message,
                0,
                self.params,
            )

    def test_deterministic_signature(self):
        """
        Проверка подписи при фиксированном k.

        Сообщение AB:
        checksum = 0x8284 = 33412
        h = 33412 mod 11 = 5

        x = 7, k = 3
        r = (2^3 mod 23) mod 11 = 8
        s = (7*8 + 3*5) mod 11 = 5
        """
        with patch(
            "src.gost_signature.secrets.randbelow",
            return_value=2,
        ):
            signature = sign_message(
                "AB",
                self.private_key,
                self.params,
            )

        self.assertEqual(
            signature,
            GOSTSignature(r=8, s=5),
        )

        self.assertTrue(
            verify_signature(
                "AB",
                signature,
                self.public_key,
                self.params,
            )
        )


if __name__ == "__main__":
    unittest.main()
