# Data Preparation / Подготовка данных

This guide explains how to prepare graphs and contractors for the SAMPO scheduler. For hands-on examples, see [data_preparation.ipynb](../../examples/data_preparation.ipynb).
В этом руководстве описано, как подготовить графы и подрядчиков для планировщика SAMPO. Интерактивные примеры см. в ноутбуке [data_preparation.ipynb](../../examples/data_preparation.ipynb).

## Введение

Здесь приведены базовые шаги для создания графов работ и ресурсов подрядчиков, которые могут быть запланированы в SAMPO.

## Генерация графа

### Синтетические графы

* Импорт: `SimpleSynthetic`, `SyntheticGraphType`.
* Воспроизводимость: фиксируем зерно `r_seed`.
* Базовый граф: кластерная структура с ограничениями на число работ.
* Продвинутый граф: задаём верхние границы по числу работ и уникальных сущностей.

```python
from sampo.generator.base import SimpleSynthetic
from sampo.generator.types import SyntheticGraphType

r_seed = 231
ss = SimpleSynthetic(r_seed)

# Basic synthetic graph
# Базовый синтетический граф
simple_wg = ss.work_graph(
    mode=SyntheticGraphType.GENERAL,
    cluster_counts=10,
    bottom_border=100,
    top_border=200,
)

# Advanced synthetic graph
# Продвинутый синтетический граф
adv_wg = ss.advanced_work_graph(
    works_count_top_border=2000,
    uniq_works=300,
    uniq_resources=100,
)
```
This snippet demonstrates synthetic graph generation (see [data_preparation.ipynb](../../examples/data_preparation.ipynb)).
Этот пример демонстрирует генерацию синтетического графа (см. [data_preparation.ipynb](../../examples/data_preparation.ipynb)).

### Сохранение/загрузка WorkGraph

* Сохранение: `WorkGraph.dump(dir, name)` → `name.json`.
* Загрузка: `WorkGraph.load(dir, name)`.
* Проверка идентичности по числу вершин.

```python
from sampo.schemas.graph import WorkGraph

# Save and load the graph
# Сохранение и загрузка графа
simple_wg.dump(".", "wg")
loaded_simple_wg = WorkGraph.load(".", "wg")
assert simple_wg.vertex_count == loaded_simple_wg.vertex_count
```
This snippet demonstrates persisting a WorkGraph (see [data_preparation.ipynb](../../examples/data_preparation.ipynb)).
Этот пример демонстрирует сохранение WorkGraph (см. [data_preparation.ipynb](../../examples/data_preparation.ipynb)).

## Генерация подрядчиков

### Ручная генерация подрядчика

* Импорт: `Contractor`, `Worker`, `uuid4`.
* Заполняем имя и набор ресурсов с количествами.

```python
from uuid import uuid4
from sampo.schemas.contractor import Contractor
from sampo.schemas.resources import Worker

# Create contractor manually
# Ручное создание подрядчика
manual_contractor = Contractor(
    id=str(uuid4()),
    name="OOO Berezka",
    workers={
        "builder": Worker(id=str(uuid4()), name="builder", count=100),
    },
)
```
This snippet shows manual contractor definition (see [data_preparation.ipynb](../../examples/data_preparation.ipynb)).
Этот пример показывает ручное определение подрядчика (см. [data_preparation.ipynb](../../examples/data_preparation.ipynb)).

### Синтетическая генерация подрядчиков

* Быстрая генерация тестовых подрядчиков по масштабу ресурсообеспечения.

```python
# Generate contractors with increasing capacity
# Генерация подрядчиков с увеличивающимся масштабом
c5 = ss.contractor(5)
c10 = ss.contractor(10)
c15 = ss.contractor(15)
```
This snippet demonstrates synthetic contractor generation (see [data_preparation.ipynb](../../examples/data_preparation.ipynb)).
Этот пример демонстрирует синтетическую генерацию подрядчиков (см. [data_preparation.ipynb](../../examples/data_preparation.ipynb)).
### Генерация подрядчика из графа

* Генерация покрытия потребностей конкретного графа.

```python
from sampo.generator.environment import get_contractor_by_wg

# Generate contractor based on a work graph
# Генерация подрядчика на основе графа
contractors = [get_contractor_by_wg(simple_wg)]
```
This snippet derives a contractor from a WorkGraph (see [data_preparation.ipynb](../../examples/data_preparation.ipynb)).
Этот пример получает подрядчика из WorkGraph (см. [data_preparation.ipynb](../../examples/data_preparation.ipynb)).

### Сохранение/загрузка Contractor

* Сохранение: `Contractor.dump(dir, name)` → `name.json`.
* Загрузка: `Contractor.load(dir, name)`.

```python
# Save and load the contractor
# Сохранение и загрузка подрядчика
contractors[0].dump(".", "contractor")

from sampo.schemas.contractor import Contractor
loaded_contractor = Contractor.load(".", "contractor")
```
This snippet demonstrates contractor persistence (see [data_preparation.ipynb](../../examples/data_preparation.ipynb)).
Этот пример демонстрирует сохранение подрядчика (см. [data_preparation.ipynb](../../examples/data_preparation.ipynb)).

## Итоги

Мы рассмотрели базовые способы создания графов работ и подрядчиков, а также их сохранение и загрузку. Дополнительные примеры приведены в ноутбуке [data_preparation.ipynb](../../examples/data_preparation.ipynb).

