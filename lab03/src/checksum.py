"""
Лабораторная работа №3.
Вариант №7.

Вычисление 16-битной контрольной суммы:
- разбиение сообщения на блоки по 16 бит;
- XOR каждого блока с накопленной суммой;
- циклический сдвиг результата влево на 1 бит.
"""

MASK_16 = 0xFFFF


def rotate_left_16(value: int) -> int:
    """Циклический сдвиг 16-битного числа влево на 1 бит."""
    value &= MASK_16
    return ((value << 1) | (value >> 15)) & MASK_16


def checksum_16(message: str) -> int:
    """
    Вычисляет контрольную сумму сообщения по варианту №7.

    Кодировка: UTF-8.
    Порядок байтов: big-endian.
    Неполный последний блок дополняется нулями справа.
    Для каждого блока: checksum = ROL16(checksum XOR block).

    Args:
        message: Исходное текстовое сообщение.

    Returns:
        Контрольная сумма в диапазоне 0..65535.
    """
    if not isinstance(message, str):
        raise TypeError("Сообщение должно быть строкой")

    data = message.encode("utf-8")

    if len(data) % 2 != 0:
        data += b"\x00"

    checksum = 0

    for i in range(0, len(data), 2):
        block = int.from_bytes(
            data[i:i + 2],
            byteorder="big"
        )

        checksum ^= block
        checksum = rotate_left_16(checksum)

    return checksum


def checksum_hex(message: str) -> str:
    """Возвращает контрольную сумму в шестнадцатеричном виде."""
    return f"{checksum_16(message):04X}"
