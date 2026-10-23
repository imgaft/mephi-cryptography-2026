"""
Лабораторная работа № 4.
Протокол Диффи–Хеллмана на эллиптических кривых.
"""

from dataclasses import dataclass

from elliptic_curve import EllipticCurve, Point


@dataclass(frozen=True)
class ECDHParameters:
    """Параметры протокола ECDH."""

    curve: EllipticCurve
    generator: Point

    def __post_init__(self):
        if self.generator is None:
            raise ValueError(
                "Базовая точка не может быть O"
            )

        self.curve.validate_point(self.generator)

        if self.curve.point_order(self.generator) <= 2:
            raise ValueError(
                "Порядок базовой точки слишком мал"
            )


class ECDHParticipant:
    """Участник протокола ECDH."""

    def __init__(
        self,
        name: str,
        parameters: ECDHParameters,
        private_key: int
    ):
        self.name = name
        self.parameters = parameters

        order = parameters.curve.point_order(
            parameters.generator
        )

        if not isinstance(private_key, int):
            raise TypeError(
                "Закрытый ключ должен быть целым числом"
            )

        if not 1 <= private_key < order:
            raise ValueError(
                f"Закрытый ключ должен быть "
                f"в диапазоне [1, {order - 1}]"
            )

        self.private_key = private_key

        self.public_key = (
            parameters.curve.multiply(
                private_key,
                parameters.generator
            )
        )

        if self.public_key is None:
            raise ValueError(
                "Открытый ключ не может быть O"
            )

    def compute_shared_secret(
        self,
        other_public_key: Point
    ) -> Point:
        """Вычисление общего секрета."""

        curve = self.parameters.curve

        curve.validate_point(other_public_key)

        if other_public_key is None:
            raise ValueError(
                "Получен недопустимый открытый ключ O"
            )

        order = curve.point_order(
            self.parameters.generator
        )

        if curve.multiply(
            order,
            other_public_key
        ) is not None:
            raise ValueError(
                "Открытый ключ не принадлежит "
                "подгруппе базовой точки"
            )

        shared_secret = curve.multiply(
            self.private_key,
            other_public_key
        )

        if shared_secret is None:
            raise ValueError(
                "Общий секрет не может быть O"
            )

        return shared_secret


def perform_ecdh(
    parameters: ECDHParameters,
    k1: int,
    k2: int
) -> dict:
    """Моделирование обмена ключами."""

    alice = ECDHParticipant(
        "Alice",
        parameters,
        k1
    )

    bob = ECDHParticipant(
        "Bob",
        parameters,
        k2
    )

    # Обмен открытыми ключами
    public_a = alice.public_key
    public_b = bob.public_key

    # Независимое вычисление секрета
    shared_a = alice.compute_shared_secret(
        public_b
    )

    shared_b = bob.compute_shared_secret(
        public_a
    )

    return {
        "public_a": public_a,
        "public_b": public_b,
        "shared_a": shared_a,
        "shared_b": shared_b,
        "keys_match": shared_a == shared_b,
    }
