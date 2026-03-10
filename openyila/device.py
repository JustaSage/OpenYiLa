"""YiLa device data model."""

from dataclasses import dataclass, field

from openyila.i18n import t


@dataclass
class YilaDevice:
    """Represents a YiLa BLE door opener device."""

    address: str
    name: str = ""
    password: str = ""
    open_time: int = 650
    wait_time: int = 2000
    close_time: int = 650
    attribute: int = 0  # 0=normal, 1=reverse
    sort_order: int = 0
    battery_level: int = -1

    @property
    def is_reverse(self) -> bool:
        return self.attribute == 1

    @property
    def battery_text(self) -> str:
        mapping = {
            1: t("bat.low"),
            2: t("bat.25"),
            3: t("bat.50"),
            4: t("bat.75"),
            5: t("bat.100"),
        }
        return mapping.get(self.battery_level, t("bat.unknown"))

    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "name": self.name,
            "password": self.password,
            "open_time": self.open_time,
            "wait_time": self.wait_time,
            "close_time": self.close_time,
            "attribute": self.attribute,
            "sort_order": self.sort_order,
            "battery_level": self.battery_level,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "YilaDevice":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
