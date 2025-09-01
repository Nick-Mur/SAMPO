from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
"""Requirement models for resources and infrastructure.

Модели требований к ресурсам и инфраструктуре.
"""

from uuid import uuid4

from sampo.schemas.resources import Material
from sampo.schemas.serializable import AutoJSONSerializable
from sampo.schemas.time import Time
from sampo.schemas.zones import Zone

# Used for max_count in the demand, if it is not specified during initialization WorkerReq
DEFAULT_MAX_COUNT = 100


class BaseReq(AutoJSONSerializable['BaseReq'], ABC):
    """Generic requirement description.

    Общее описание требования.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of requirement.

        Название требования.

        Returns:
            str: Requirement name.
            str: Название требования.
        """
        ...


@dataclass(frozen=True)
class WorkerReq(BaseReq):
    """Requirements for human resources.

    Требования к человеческим ресурсам.

    Args:
        kind: Type of worker.
            Тип работника.
        volume: Volume of work.
            Объём работы.
        min_count: Minimum number of workers.
            Минимальное количество работников.
        max_count: Maximum number of workers.
            Максимальное количество работников.
        name: Optional name for requirement.
            Необязательное название требования.
    """
    kind: str
    volume: Time
    min_count: Optional[int] = 1
    max_count: Optional[int] = DEFAULT_MAX_COUNT
    name: Optional[str] = ''

    def scale_all(self, scalar: float, new_name: Optional[str] = '') -> 'WorkerReq':
        """Scale volume and max count.

        Масштабирует объём и максимальное количество.

        Args:
            scalar: Multiplier.
                Множитель.
            new_name: Name for new requirement.
                Имя нового требования.

        Returns:
            WorkerReq: Scaled requirement.
            WorkerReq: Масштабированное требование.
        """
        max_count = max(round(self.max_count * scalar), self.min_count)
        new_req = WorkerReq(self.kind, self.volume * scalar, self.min_count, max_count, new_name or self.name)
        return new_req

    def scale_volume(self, scalar: float, new_name: Optional[str] = None) -> 'WorkerReq':
        """Scale only volume value.

        Масштабирует только объём.

        Args:
            scalar: Multiplier.
                Множитель.
            new_name: Name for new requirement.
                Имя нового требования.

        Returns:
            WorkerReq: Scaled requirement.
            WorkerReq: Масштабированное требование.
        """
        new_req = WorkerReq(self.kind, self.volume * scalar, self.min_count, self.max_count, new_name or self.name)
        return new_req


@dataclass(frozen=True)
class EquipmentReq(BaseReq):
    """Requirements for equipment resources.

    Требования к оборудованию.

    Args:
        kind: Equipment type.
            Тип оборудования.
        name: Name of requirement.
            Название требования.
    """
    kind: str
    count: int
    name: Optional[str] = None


@dataclass(frozen=True)
class MaterialReq(BaseReq):
    """Requirements for consumable materials.

    Требования к расходным материалам.

    Args:
        kind: Material type.
            Тип материала.
        name: Name of requirement.
            Название требования.
    """
    kind: str
    count: int
    # need_start: int TODO Implement handling this
    name: Optional[str] = None

    def material(self) -> Material:
        return Material(str(uuid4()), self.kind, self.count)


@dataclass(frozen=True)
class ConstructionObjectReq(BaseReq):
    """Requirements for infrastructure objects.

    Требования к инфраструктурным объектам.

    Args:
        kind: Object type.
            Тип объекта.
        name: Name of requirement.
            Название требования.
    """
    kind: str
    count: int
    name: Optional[str] = None


@dataclass(frozen=True)
class ZoneReq(BaseReq):
    kind: str
    required_status: int
    name: Optional[str] = None

    def to_zone(self) -> Zone:
        """Convert to zone object.

        Преобразует в объект зоны.
        """
        return Zone(self.kind, self.required_status)
