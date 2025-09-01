"""Extended sorted list with merge support.

Расширенный отсортированный список с поддержкой слияния.
"""

from abc import ABC
from bisect import bisect_left, bisect_right

from sortedcontainers import SortedKeyList


class ExtendedSortedList(SortedKeyList, ABC):
    """Sorted list allowing in-place key-preserving merges.

    Отсортированный список, позволяющий слияния без изменения ключей.
    """

    def __setitem__(self, idx, value):
        """Set item by index without modifying its key.

        Устанавливает элемент по индексу без изменения его ключа.

        Args:
            idx: Index to replace.
                Индекс заменяемого элемента.
            value: New value with same key.
                Новое значение с тем же ключом.
        """
        self.merge(self[idx], value, lambda x, y: y)

    def merge(self, old, value, merger):
        """Merge ``value`` into ``old`` preserving key.

        Сливает ``value`` в ``old`` без изменения ключа.

        Runtime complexity: approximately ``O(log n)``.

        Args:
            old: Existing element in list.
                Существующий элемент списка.
            value: New value to merge.
                Новое значение для слияния.
            merger: Function combining two values.
                Функция объединения двух значений.
        """
        _lists = self._lists
        _keys = self._keys
        _maxes = self._maxes

        key = self._key(old)

        increased = True

        if _maxes:
            pos = bisect_left(_maxes, key)

            # def insert_or_merge():
            #     idx = bisect_right(_keys[pos], key)
            #     old_key = _keys[pos][idx]
            #     if old_key == key:
            #         _lists[pos][idx] = merger(_lists[pos][idx], value)
            #     else:
            #         _lists[pos].insert(idx, value)
            #         _keys[pos].insert(idx, key)

            if pos == len(_maxes):
                pos -= 1

                old_key = _keys[pos][-1]
                if old_key == key:
                    new_value = merger(_lists[pos][-1], value)
                    _lists[pos][-1] = new_value
                    # _keys[pos][-1] = self._key(new_value)
                    increased = False
                else:
                    _lists[pos].append(value)
                    _keys[pos].append(key)
                _maxes[pos] = key
            else:
                idx = bisect_right(_keys[pos], key)
                old_key = _keys[pos][idx - 1]
                if idx != 0 and old_key == key:
                    new_value = merger(_lists[pos][idx - 1], value)
                    _lists[pos][idx - 1] = new_value
                    # _keys[pos][idx - 1] = self._key(new_value)
                    increased = False
                else:
                    _lists[pos].insert(idx, value)
                    _keys[pos].insert(idx, key)

            if increased:
                self._expand(pos)
        else:
            _lists.append([value])
            _keys.append([key])
            _maxes.append(key)

        if increased:
            self._len += 1
