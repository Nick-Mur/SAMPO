"""Definitions of work units.

Определения рабочих единиц.
"""

from dataclasses import dataclass

from sampo.schemas.identifiable import Identifiable
from sampo.schemas.requirements import (
    WorkerReq,
    EquipmentReq,
    MaterialReq,
    ConstructionObjectReq,
    ZoneReq,
)
from sampo.schemas.resources import Material
from sampo.schemas.serializable import AutoJSONSerializable
from sampo.utilities.serializers import custom_serializer


@dataclass
class WorkUnit(AutoJSONSerializable['WorkUnit'], Identifiable):
    """Graph vertex representing a single task.

    Вершина графа, представляющая отдельную задачу.
    """

    def __init__(
        self,
        id: str,
        name: str,
        worker_reqs: list[WorkerReq] | None = None,
        equipment_reqs: list[EquipmentReq] | None = None,
        material_reqs: list[MaterialReq] | None = None,
        object_reqs: list[ConstructionObjectReq] | None = None,
        zone_reqs: list[ZoneReq] | None = None,
        description: str = '',
        group: str = 'main project',
        priority: int = 1,
        is_service_unit: bool = False,
        volume: float = 0,
        volume_type: str = 'unit',
        display_name: str = '',
        workground_size: int = 100,
    ) -> None:
        """Initialize work unit.

        Инициализирует рабочую единицу.

        Args:
            id: Work identifier.
                Идентификатор работы.
            name: Work name.
                Название работы.
            worker_reqs: Required worker types.
                Требуемые типы рабочих.
            equipment_reqs: Required equipment.
                Необходимое оборудование.
            material_reqs: Required materials.
                Необходимые материалы.
            object_reqs: Required construction objects.
                Необходимые строительные объекты.
            zone_reqs: Required zone statuses.
                Требуемые состояния зон.
            description: Textual description.
                Текстовое описание.
            group: Work group.
                Группа работ.
            priority: Priority value.
                Значение приоритета.
            is_service_unit: Whether unit is service.
                Является ли единица сервисной.
            volume: Work volume.
                Объём работ.
            volume_type: Unit of work volume.
                Единица объёма работ.
            display_name: Display name.
                Отображаемое имя.
            workground_size: Size of workground.
                Размер рабочей площадки.
        """
        super(WorkUnit, self).__init__(id, name)
        if material_reqs is None:
            material_reqs = []
        if object_reqs is None:
            object_reqs = []
        if equipment_reqs is None:
            equipment_reqs = []
        if worker_reqs is None:
            worker_reqs = []
        if zone_reqs is None:
            zone_reqs = []
        self.worker_reqs = worker_reqs
        self.equipment_reqs = equipment_reqs
        self.object_reqs = object_reqs
        self.material_reqs = material_reqs
        self.zone_reqs = zone_reqs
        self.description = description
        self.group = group
        self.is_service_unit = is_service_unit
        self.volume = float(volume)
        self.volume_type = volume_type
        self.display_name = display_name if display_name else name
        self.priority = priority

    def __del__(self):
        for attr in self.__dict__.values():
            del attr

    def need_materials(self) -> list[Material]:
        """Return list of required materials.

        Возвращает список требуемых материалов.
        """
        return [req.material() for req in self.material_reqs]

    @custom_serializer('worker_reqs')
    @custom_serializer('zone_reqs')
    @custom_serializer('material_reqs')
    def serialize_serializable_list(self, value) -> list:
        """Serialize list of serializable values.

        Сериализует список сериализуемых значений.

        Args:
            value: Values to serialize.
                Значения для сериализации.

        Returns:
            list: Serialized values.
            list: Сериализованные значения.
        """
        return [t._serialize() for t in value]

    @classmethod
    @custom_serializer('material_reqs', deserializer=True)
    def material_reqs_deserializer(cls, value) -> list[MaterialReq]:
        """Deserialize material requirements.

        Десериализует требования к материалам.

        Args:
            value: Serialized list of material requirements.
                Сериализованный список требований к материалам.

        Returns:
            list[MaterialReq]: Material requirements list.
            list[MaterialReq]: Список требований к материалам.
        """
        return [MaterialReq._deserialize(wr) for wr in value]

    @classmethod
    @custom_serializer('worker_reqs', deserializer=True)
    def worker_reqs_deserializer(cls, value) -> list[WorkerReq]:
        """Deserialize worker requirements.

        Десериализует требования к рабочим.

        Args:
            value: Serialized list of worker requirements.
                Сериализованный список требований к рабочим.

        Returns:
            list[WorkerReq]: Worker requirements list.
            list[WorkerReq]: Список требований к рабочим.
        """
        return [WorkerReq._deserialize(wr) for wr in value]

    @classmethod
    @custom_serializer('zone_reqs', deserializer=True)
    def zone_reqs_deserializer(cls, value) -> list[ZoneReq]:
        """Deserialize zone requirements.

        Десериализует требования к зонам.

        Args:
            value: Serialized list of zone requirements.
                Сериализованный список требований к зонам.

        Returns:
            list[ZoneReq]: Zone requirements list.
            list[ZoneReq]: Список требований к зонам.
        """
        return [ZoneReq._deserialize(wr) for wr in value]

    @classmethod
    @custom_serializer('material_reqs', deserializer=True)
    def material_reqs_deserializer(cls, value) -> list[MaterialReq]:
        """
        Get list of material requirements

        :param value: serialized list of material requirements
        :return: list of material requirements
        """
        return [MaterialReq._deserialize(wr) for wr in value]

    def __getstate__(self):
        # custom method to avoid calling __hash__() on GraphNode objects
        return self._serialize()

    def __setstate__(self, state):
        new_work_unit = self._deserialize(state)
        self.worker_reqs = new_work_unit.worker_reqs
        self.equipment_reqs = new_work_unit.equipment_reqs
        self.object_reqs = new_work_unit.object_reqs
        self.material_reqs = new_work_unit.material_reqs
        self.zone_reqs = new_work_unit.zone_reqs
        self.id = new_work_unit.id
        self.name = new_work_unit.name
        self.is_service_unit = new_work_unit.is_service_unit
        self.volume = new_work_unit.volume
        self.volume_type = new_work_unit.volume_type
        self.group = new_work_unit.group
        self.display_name = new_work_unit.display_name
        self.priority = new_work_unit.priority
