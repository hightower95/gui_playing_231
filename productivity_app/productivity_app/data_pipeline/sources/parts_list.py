from abc import ABC, abstractmethod
from enum import Enum

from dataclasses import dataclass, replace


from productivity_app.data_pipeline.models.parameter import Parameter, DataTypes


PartsList = Parameter.DataSource(
    name="parts_list",  # Assigned when used
    data_type=DataTypes.PartsList,
    description="A data source containing a parts list"
)
