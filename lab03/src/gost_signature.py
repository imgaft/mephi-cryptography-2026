"""
Лабораторная работа №3.
Учебная реализация электронной подписи ГОСТ Р 34.10-94.

В качестве функции хеширования используется
контрольная сумма варианта №7.
"""

import secrets
from functools import lru_cache
from dataclasses import dataclass

from src.checksum import checksum_16


@dataclass(frozen=True)
class GOSTParameters:
    p: int
    q: int
    a: int


@dataclass(frozen=True)
class GOSTKeyPair:
    private_key: int
    public_key: int


@dataclass(frozen=True)
class GOSTSignature:
    r: int
    s: int


def is_prime(n: int, rounds: int = 40) -> bool:
    """Вероятностная проверка простоты Миллера–Рабина (40 раундов)."""
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small:
        if n == prime:
            return True
        if n % prime == 0:
            return False
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        base = secrets.randbelow(n - 3) + 2
        x = pow(base, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


@lru_cache(maxsize=32)
def validate_parameters(params: GOSTParameters) -> None:
    """Проверяет простоту и групповые условия; результаты кешируются."""
    p, q, a = params.p, params.q, params.a
    if not is_prime(p):
        raise ValueError("Параметр p должен быть простым")
    if not is_prime(q):
        raise ValueError("Параметр q должен быть простым")
    if (p - 1) % q != 0:
        raise ValueError("q должен делить p - 1")
    if not (1 < a < p - 1):
        raise ValueError("Должно выполняться 1 < a < p - 1")
    if pow(a, q, p) != 1:
        raise ValueError("Должно выполняться a^q mod p = 1")


def generate_keys(params: GOSTParameters) -> GOSTKeyPair:
    """Генерация закрытого и открытого ключей."""
    validate_parameters(params)

    x = secrets.randbelow(params.q - 1) + 1
    y = pow(params.a, x, params.p)

    return GOSTKeyPair(
        private_key=x,
        public_key=y,
    )


def message_hash(message: str, q: int) -> int:
    """Вычисление хеша сообщения для алгоритма подписи."""
    h = checksum_16(message) % q

    return h if h != 0 else 1


def sign_message(
    message: str,
    private_key: int,
    params: GOSTParameters,
) -> GOSTSignature:
    """Формирование электронной подписи (r, s)."""
    validate_parameters(params)

    p, q, a = params.p, params.q, params.a

    if not (1 <= private_key < q):
        raise ValueError("Некорректный закрытый ключ")

    h = message_hash(message, q)

    while True:
        k = secrets.randbelow(q - 1) + 1

        r = pow(a, k, p) % q

        if r == 0:
            continue

        s = (private_key * r + k * h) % q

        if s == 0:
            continue

        return GOSTSignature(r=r, s=s)


def verify_signature(
    message: str,
    signature: GOSTSignature,
    public_key: int,
    params: GOSTParameters,
) -> bool:
    """Проверка электронной подписи по открытому ключу."""
    validate_parameters(params)

    p, q, a = params.p, params.q, params.a

    if not (0 < signature.r < q):
        return False

    if not (0 < signature.s < q):
        return False

    if not (1 < public_key < p):
        return False

    if pow(public_key, q, p) != 1:
        return False

    h = message_hash(message, q)

    v = pow(h, q - 2, q)

    z1 = (signature.s * v) % q
    z2 = ((q - signature.r) * v) % q

    u = (
        pow(a, z1, p) *
        pow(public_key, z2, p)
    ) % p % q

    return u == signature.r


def get_demo_parameters() -> GOSTParameters:
    """
    Небольшие учебные параметры.

    p = 23
    q = 11
    a = 2

    11 делит 22.
    2^11 mod 23 = 1.

    Не предназначены для реальной криптографии.
    """
    params = GOSTParameters(
        p=23,
        q=11,
        a=2,
    )

    validate_parameters(params)

    return params


def get_report_parameters() -> GOSTParameters:
    """Фиксированные параметры с p=512 бит и q=256 бит для лабораторной."""
    params = GOSTParameters(
        p=10384704642531197664116868987034252164839301013025827535259107039537005568296882902039420609371913725819647695675081014375901705793400586023922425046793447,
        q=111010004376550013782823712650965252593978046313480548030881300191926658557793,
        a=3767943287743788991803516647827581364354455034555335090391257050458322521166377347083735264803454294252956422693831769494718995561170055325427812028132708,
    )
    validate_parameters(params)
    return params
