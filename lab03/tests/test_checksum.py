import unittest

from src.checksum import (
    rotate_left_16,
    checksum_16,
    checksum_hex,
)


class TestChecksum(unittest.TestCase):

    def test_rotate_left(self):
        """Проверка циклического сдвига."""
        self.assertEqual(rotate_left_16(0x8000), 0x0001)
        self.assertEqual(rotate_left_16(0x0001), 0x0002)
        self.assertEqual(rotate_left_16(0xFFFF), 0xFFFF)

    def test_empty_message(self):
        """Пустое сообщение."""
        self.assertEqual(checksum_16(""), 0)

    def test_single_block(self):
        """Один 16-битный блок: AB."""
        self.assertEqual(checksum_16("AB"), 0x8284)

    def test_multiple_blocks(self):
        """Два блока: AB и CD."""
        self.assertEqual(checksum_16("ABCD"), 0x8381)

    def test_odd_length(self):
        """Нечётное количество байтов."""
        self.assertEqual(checksum_16("A"), 0x8200)

    def test_different_messages(self):
        """Проверка контрольных сумм двух сообщений."""
        self.assertNotEqual(
            checksum_16("Hello"),
            checksum_16("World"),
        )

    def test_unicode(self):
        """Проверка корректной обработки UTF-8."""
        result = checksum_16("Привет")
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 0xFFFF)

    def test_hex_format(self):
        """Проверка шестнадцатеричного представления."""
        self.assertEqual(checksum_hex("AB"), "8284")

    def test_invalid_input(self):
        """Проверка некорректного типа данных."""
        with self.assertRaises(TypeError):
            checksum_16(123)


if __name__ == "__main__":
    unittest.main()
