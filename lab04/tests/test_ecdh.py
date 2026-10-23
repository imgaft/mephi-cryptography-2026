"""
Автоматические тесты лабораторной работы № 4.

Запуск:
python3 -m unittest discover -s lab04/tests -v
"""

import sys
import unittest
from pathlib import Path


SRC_DIR = (
    Path(__file__).resolve().parents[1] / "src"
)

sys.path.insert(0, str(SRC_DIR))


from elliptic_curve import (
    EllipticCurve,
    is_prime,
    mod_inverse,
    find_points_by_x,
)

from ecdh import (
    ECDHParameters,
    ECDHParticipant,
    perform_ecdh,
)


class TestEllipticCurve(unittest.TestCase):

    def setUp(self):
        self.curve = EllipticCurve(
            a=-1,
            b=1,
            p=29
        )

        self.g = (0, 1)

    def test_01_prime_modulus(self):
        self.assertTrue(is_prime(29))
        self.assertFalse(is_prime(21))
        self.assertFalse(is_prime(1))

    def test_02_discriminant(self):
        self.assertEqual(
            self.curve.discriminant(),
            23
        )

    def test_03_invalid_curve(self):
        with self.assertRaises(ValueError):
            EllipticCurve(
                a=0,
                b=0,
                p=29
            )

    def test_04_composite_modulus(self):
        with self.assertRaises(ValueError):
            EllipticCurve(
                a=-1,
                b=1,
                p=21
            )

    def test_05_generator_on_curve(self):
        self.assertTrue(
            self.curve.is_on_curve(self.g)
        )

    def test_06_original_generator_invalid(self):
        self.assertFalse(
            self.curve.is_on_curve((9, 27))
        )

    def test_07_invalid_point_rejected(self):
        with self.assertRaises(ValueError):
            self.curve.validate_point((9, 27))

    def test_08_mod_inverse(self):
        self.assertEqual(
            mod_inverse(7, 29),
            25
        )

    def test_09_mod_inverse_zero(self):
        with self.assertRaises(ValueError):
            mod_inverse(0, 29)

    def test_10_point_at_infinity(self):
        self.assertEqual(
            self.curve.add(self.g, None),
            self.g
        )

        self.assertEqual(
            self.curve.add(None, self.g),
            self.g
        )

    def test_11_opposite_points(self):
        negative = self.curve.negate(self.g)

        self.assertIsNone(
            self.curve.add(self.g, negative)
        )

    def test_12_point_doubling(self):
        self.assertEqual(
            self.curve.double(self.g),
            (22, 10)
        )

    def test_13_point_addition(self):
        two_g = self.curve.double(self.g)

        three_g = self.curve.add(
            two_g,
            self.g
        )

        self.assertEqual(
            three_g,
            (27, 13)
        )

    def test_14_scalar_multiplication(self):
        self.assertEqual(
            self.curve.multiply(4, self.g),
            (9, 24)
        )

    def test_15_zero_scalar(self):
        self.assertIsNone(
            self.curve.multiply(0, self.g)
        )

    def test_16_negative_scalar(self):
        self.assertEqual(
            self.curve.multiply(-1, self.g),
            self.curve.negate(self.g)
        )

    def test_17_point_order(self):
        self.assertEqual(
            self.curve.point_order(self.g),
            37
        )

    def test_18_ecdh_public_keys(self):
        params = ECDHParameters(
            self.curve,
            self.g
        )

        result = perform_ecdh(
            params,
            4,
            17
        )

        self.assertEqual(
            result["public_a"],
            (9, 24)
        )

        self.assertEqual(
            result["public_b"],
            (20, 21)
        )

    def test_19_ecdh_shared_secret(self):
        params = ECDHParameters(
            self.curve,
            self.g
        )

        result = perform_ecdh(
            params,
            4,
            17
        )

        self.assertEqual(
            result["shared_a"],
            (11, 4)
        )

        self.assertEqual(
            result["shared_b"],
            (11, 4)
        )

        self.assertTrue(
            result["keys_match"]
        )

    def test_20_independent_verification(self):
        params = ECDHParameters(
            self.curve,
            self.g
        )

        result = perform_ecdh(
            params,
            4,
            17
        )

        expected = self.curve.multiply(
            4 * 17,
            self.g
        )

        self.assertEqual(
            result["shared_a"],
            expected
        )

    def test_21_invalid_private_key(self):
        params = ECDHParameters(
            self.curve,
            self.g
        )

        with self.assertRaises(ValueError):
            ECDHParticipant(
                "Alice",
                params,
                0
            )

    def test_22_invalid_public_key(self):
        params = ECDHParameters(
            self.curve,
            self.g
        )

        alice = ECDHParticipant(
            "Alice",
            params,
            4
        )

        with self.assertRaises(ValueError):
            alice.compute_shared_secret(
                (9, 27)
            )

    def test_23_infinity_public_key(self):
        params = ECDHParameters(
            self.curve,
            self.g
        )

        alice = ECDHParticipant(
            "Alice",
            params,
            4
        )

        with self.assertRaises(ValueError):
            alice.compute_shared_secret(None)


    def test_24_corrected_generator(self):
        """Проверка исправленной точки варианта № 1."""
        generator = (9, 24)

        self.assertTrue(
            self.curve.is_on_curve(generator)
        )

        self.assertEqual(
            self.curve.point_order(generator),
            37
        )

    def test_25_corrected_generator_public_keys(self):
        """Проверка открытых ключей варианта № 1."""
        params = ECDHParameters(
            self.curve,
            (9, 24)
        )

        result = perform_ecdh(params, 4, 17)

        self.assertEqual(
            result["public_a"],
            (25, 17)
        )

        self.assertEqual(
            result["public_b"],
            (11, 4)
        )

    def test_26_corrected_generator_shared_secret(self):
        """Проверка общего секрета варианта № 1."""
        params = ECDHParameters(
            self.curve,
            (9, 24)
        )

        result = perform_ecdh(params, 4, 17)

        self.assertEqual(
            result["shared_a"],
            (28, 28)
        )

        self.assertEqual(
            result["shared_b"],
            (28, 28)
        )

        self.assertTrue(result["keys_match"])

        self.assertEqual(
            result["shared_a"],
            self.curve.multiply(68, (9, 24))
        )

    def test_27_find_points_by_x(self):
        """Поиск допустимых точек с координатой x=9."""

        points = find_points_by_x(
            self.curve,
            9
        )

        self.assertEqual(
            points,
            [(9, 5), (9, 24)]
        )

        original_y = 27

        selected = min(
            points,
            key=lambda point: (
                abs(point[1] - original_y),
                point[1]
            )
        )

        self.assertEqual(
            selected,
            (9, 24)
        )


if __name__ == "__main__":
    unittest.main()
