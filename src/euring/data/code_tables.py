from __future__ import annotations

from .code_table_accuracy_of_pullus_age import TABLE as accuracy_of_pullus_age
from .code_table_age import TABLE as age
from .code_table_brood_size import TABLE as brood_size
from .code_table_catching_lures import TABLE as catching_lures
from .code_table_catching_method import TABLE as catching_method
from .code_table_condition import TABLE as condition
from .code_table_euring_code_identifier import TABLE as euring_code_identifier
from .code_table_manipulated import TABLE as manipulated
from .code_table_metal_ring_information import TABLE as metal_ring_information
from .code_table_moved_before_the_encounter import TABLE as moved_before_the_encounter
from .code_table_other_marks_information import TABLE as other_marks_information
from .code_table_primary_identification_method import TABLE as primary_identification_method
from .code_table_pullus_age import TABLE as pullus_age
from .code_table_sex import TABLE as sex
from .code_table_status import TABLE as status
from .code_table_verification_of_the_metal_ring import TABLE as verification_of_the_metal_ring

EURING_CODE_TABLES = {
    "accuracy_of_pullus_age": accuracy_of_pullus_age,
    "age": age,
    "brood_size": brood_size,
    "catching_lures": catching_lures,
    "catching_method": catching_method,
    "condition": condition,
    "euring_code_identifier": euring_code_identifier,
    "manipulated": manipulated,
    "metal_ring_information": metal_ring_information,
    "moved_before_the_encounter": moved_before_the_encounter,
    "other_marks_information": other_marks_information,
    "primary_identification_method": primary_identification_method,
    "pullus_age": pullus_age,
    "sex": sex,
    "status": status,
    "verification_of_the_metal_ring": verification_of_the_metal_ring,
}

__all__ = ["EURING_CODE_TABLES"]
