"""Scheduling pipeline constructors and types.

Конструкторы конвейера планирования и их типы.
"""

from enum import Enum


class PipelineError(Exception):
    """Raised when any pipeline error occurs.

    Вызывается при возникновении ошибки конвейера.

    This is similar to ``IllegalStateException`` and indicates an
    incorrect internal state of the pipeline.

    Это похоже на ``IllegalStateException`` и указывает на некорректное
    внутреннее состояние конвейера.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


from sampo.pipeline.base import InputPipeline
from sampo.pipeline.default import DefaultInputPipeline


class PipelineType(Enum):
    """Available pipeline implementations.

    Доступные реализации конвейеров.
    """

    DEFAULT = 0


class SchedulingPipeline:
    """Factory for constructing scheduling pipelines.

    Фабрика для создания конвейеров планирования.
    """

    @staticmethod
    def create(pipeline_type: PipelineType = PipelineType.DEFAULT) -> InputPipeline:
        """Create pipeline of selected type.

        Создаёт конвейер выбранного типа.

        Args:
            pipeline_type: Desired pipeline type.
                Желаемый тип конвейера.

        Returns:
            InputPipeline: Configured pipeline instance.
            InputPipeline: Настроенный экземпляр конвейера.
        """
        match pipeline_type:
            case PipelineType.DEFAULT:
                return DefaultInputPipeline()
            case _:
                raise PipelineError('Unknown pipeline type')
