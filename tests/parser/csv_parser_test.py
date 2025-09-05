import os
import sys

import pandas as pd
import pytest

from sampo.userinput.parser.csv_parser import CSVParser
from sampo.userinput.parser.exception import WorkGraphBuildingException


def test_work_graph_csv_parser():
    try:
        history = pd.DataFrame(columns=['marker_for_glue', 'work_name', 'first_day', 'last_day',
                                                            'upper_works', 'work_name_clear_old', 'smr_name',
                                                            'work_name_clear', 'granular_smr_name'])
        works_info = CSVParser.read_graph_info(project_info=os.path.join(sys.path[0], 'tests/parser/test_wg.csv'),
                                               history_data=history,
                                               all_connections=True)
        works_info.to_csv(os.path.join(sys.path[0], 'tests/parser/repaired.csv'), sep=';')
        wg, contractors = CSVParser.work_graph_and_contractors(works_info)
        print(f'\n\nWork graph has works: {wg.nodes}, and the number of contractors is {len(contractors)}\n\n')
    except Exception as e:
        raise WorkGraphBuildingException(f'There is no way to build work graph, {e}')

    os.remove(os.path.join(sys.path[0], 'tests/parser/repaired.csv'))


def test_incomplete_csv_raises_work_graph_building_exception():
    """Ensure missing mandatory columns trigger WorkGraphBuildingException.

    Убедитесь, что отсутствие обязательных столбцов вызывает WorkGraphBuildingException.
    """
    history = pd.DataFrame(columns=['marker_for_glue', 'work_name', 'first_day', 'last_day',
                                    'upper_works', 'work_name_clear_old', 'smr_name',
                                    'work_name_clear', 'granular_smr_name'])
    with pytest.raises(WorkGraphBuildingException):
        CSVParser.read_graph_info(
            project_info=os.path.join(sys.path[0], 'tests/parser/incomplete_wg.csv'),
            history_data=history,
            all_connections=True,
        )


def test_corrupted_csv_raises_work_graph_building_exception():
    """Ensure malformed CSV structure raises WorkGraphBuildingException.

    Убедитесь, что некорректная структура CSV вызывает WorkGraphBuildingException.
    """
    history = pd.DataFrame(columns=['marker_for_glue', 'work_name', 'first_day', 'last_day',
                                    'upper_works', 'work_name_clear_old', 'smr_name',
                                    'work_name_clear', 'granular_smr_name'])
    with pytest.raises(WorkGraphBuildingException):
        CSVParser.read_graph_info(
            project_info=os.path.join(sys.path[0], 'tests/parser/corrupted_wg.csv'),
            history_data=history,
            all_connections=True,
        )
