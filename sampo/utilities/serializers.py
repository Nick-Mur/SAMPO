"""Helpers for custom serialization.

Вспомогательные функции для пользовательской сериализации.
"""

from functools import partial
from io import StringIO
from typing import Union, Callable

import numpy as np
import pandas as pd

CUSTOM_FIELD_SERIALIZER = '_serializer_for_fields'
CUSTOM_FIELD_DESERIALIZER = '_deserializer_for_fields'
CUSTOM_TYPE_SERIALIZER = '_serializer_for_types'
CUSTOM_TYPE_DESERIALIZER = '_deserializer_for_types'


def custom_serializer(type_or_field: Union[type, str], deserializer: bool = False) -> Callable:
    """Meta-decorator for custom serializers or deserializers.

    Мета-декоратор для пользовательских сериализаторов или десериализаторов.

    Args:
        type_or_field: Field name or type to serialize.
            Имя поля или тип, который требуется сериализовать.
        deserializer: If ``True``, marks function as deserializer.
            Если ``True``, помечает функцию как десериализатор.

    Returns:
        Callable: Decorator for the target function.
            Callable: Декоратор для целевой функции.
    """
    type_of_entity = type(type_or_field)
    if type_of_entity is type:
        # if callable(deserializer):
        #     _decorate_serializer(func=deserializer,
        #                          collection_name=CUSTOM_TYPE_DESERIALIZER,
        #                          new_element=type_or_field)
        # elif deserializer:
        if deserializer:
            return custom_type_deserializer(type_or_field)
        return custom_type_serializer(type_or_field)

    elif type_of_entity is str:
        # if callable(deserializer):
        #     _decorate_serializer(func=deserializer,
        #                          collection_name=CUSTOM_FIELD_DESERIALIZER,
        #                          new_element=type_or_field)
        # elif deserializer:
        if deserializer:
            return custom_field_deserializer(type_or_field)
        return custom_field_serializer(type_or_field)

    raise TypeError(f'Unexpected type of param type_or_field: {type(type_or_field)} instead of Union[type, str]')


def custom_field_serializer(field_name: str) -> Callable:
    """Create field serializer decorator.

    Создаёт декоратор для сериализации поля.

    Args:
        field_name: Name of the field.
            Имя поля.

    Returns:
        Callable: Decorator for serialization.
            Callable: Декоратор для сериализации.
    """
    return partial(
        _decorate_serializer,
        collection_name=CUSTOM_FIELD_SERIALIZER,
        new_element=field_name,
    )


def custom_field_deserializer(field_name: str) -> Callable:
    """Create field deserializer decorator.

    Создаёт декоратор для десериализации поля.

    Args:
        field_name: Name of the field.
            Имя поля.

    Returns:
        Callable: Decorator for deserialization.
            Callable: Декоратор для десериализации.
    """
    return partial(
        _decorate_serializer,
        collection_name=CUSTOM_FIELD_DESERIALIZER,
        new_element=field_name,
    )


def custom_type_serializer(__type: type | str) -> Callable:
    """Create type serializer decorator.

    Создаёт декоратор для сериализации типа.

    Args:
        __type: Type identifier to serialize.
            Тип, который требуется сериализовать.

    Returns:
        Callable: Decorator for serialization.
            Callable: Декоратор для сериализации.
    """
    return partial(
        _decorate_serializer,
        collection_name=CUSTOM_TYPE_SERIALIZER,
        new_element=__type,
    )


def custom_type_deserializer(__type: type | str) -> Callable:
    """Create type deserializer decorator.

    Создаёт декоратор для десериализации типа.

    Args:
        __type: Type identifier to deserialize.
            Тип, который требуется десериализовать.

    Returns:
        Callable: Decorator for deserialization.
            Callable: Декоратор для десериализации.
    """
    return partial(
        _decorate_serializer,
        collection_name=CUSTOM_TYPE_DESERIALIZER,
        new_element=__type,
    )


def _decorate_serializer(func, collection_name, new_element) -> Callable:
    if not hasattr(func, collection_name):
        setattr(func, collection_name, [])
    getattr(func, collection_name).append(new_element)
    return func


def default_ndarray_serializer(array: np.ndarray) -> list:
    """Serialize NumPy array to list.

    Сериализует массив NumPy в список.

    Args:
        array: Array to serialize.
            Массив для сериализации.

    Returns:
        list: List representation of array.
            list: Списковое представление массива.
    """
    return array.tolist()


def default_ndarray_deserializer(__list: list) -> np.ndarray:
    """Deserialize list to NumPy array.

    Десериализует список в массив NumPy.

    Args:
        __list: List to convert.
            Список для преобразования.

    Returns:
        np.ndarray: Restored array.
            np.ndarray: Восстановленный массив.
    """
    return np.array(__list)


def default_dataframe_serializer(df: pd.DataFrame) -> str:
    """Serialize DataFrame to CSV string.

    Сериализует DataFrame в строку CSV.

    Args:
        df: DataFrame to serialize.
            DataFrame для сериализации.

    Returns:
        str: CSV representation.
            str: Представление CSV.
    """
    return df.to_csv(encoding='utf-8')


def default_dataframe_deserializer(str_repr: str) -> pd.DataFrame:
    """Deserialize CSV string to DataFrame.

    Десериализует строку CSV в DataFrame.

    Args:
        str_repr: CSV string.
            Строка CSV.

    Returns:
        pd.DataFrame: Restored DataFrame.
            pd.DataFrame: Восстановленный DataFrame.
    """
    return pd.read_csv(StringIO(str_repr), encoding='utf-8')


def default_np_int_serializer(n) -> int:
    """Serialize NumPy integer to Python int.

    Сериализует NumPy-число в Python int.

    Args:
        n: Number to convert.
            Число для преобразования.

    Returns:
        int: Converted integer.
            int: Преобразованное целое число.
    """
    return int(n)


def default_np_int_deserializer(n) -> np.int32:
    """Deserialize to NumPy int32.

    Десериализует в NumPy int32.

    Args:
        n: Number to convert.
            Число для преобразования.

    Returns:
        np.int32: Converted value.
            np.int32: Преобразованное значение.
    """
    return np.int32(n)


def default_np_long_serializer(n) -> int:
    """Serialize NumPy int64 to Python int.

    Сериализует NumPy int64 в Python int.

    Args:
        n: Number to convert.
            Число для преобразования.

    Returns:
        int: Converted integer.
            int: Преобразованное целое число.
    """
    return int(n)


def default_np_long_deserializer(n) -> np.int64:
    """Deserialize to NumPy int64.

    Десериализует в NumPy int64.

    Args:
        n: Number to convert.
            Число для преобразования.

    Returns:
        np.int64: Converted value.
            np.int64: Преобразованное значение.
    """
    return np.int64(n)
