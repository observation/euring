from __future__ import annotations

from .code_table_accuracy_of_coordinates import TABLE as accuracy_of_coordinates
from .code_table_accuracy_of_date import TABLE as accuracy_of_date
from .code_table_accuracy_of_pullus_age import TABLE as accuracy_of_pullus_age
from .code_table_age import TABLE as age
from .code_table_alula import TABLE as alula
from .code_table_bill_method import TABLE as bill_method
from .code_table_brood_patch import TABLE as brood_patch
from .code_table_brood_size import TABLE as brood_size
from .code_table_carpal_covert import TABLE as carpal_covert
from .code_table_catching_lures import TABLE as catching_lures
from .code_table_catching_method import TABLE as catching_method
from .code_table_circumstances import TABLE as circumstances
from .code_table_circumstances_presumed import TABLE as circumstances_presumed
from .code_table_condition import TABLE as condition
from .code_table_euring_code_identifier import TABLE as euring_code_identifier
from .code_table_fat_score_method import TABLE as fat_score_method
from .code_table_manipulated import TABLE as manipulated
from .code_table_metal_ring_information import TABLE as metal_ring_information
from .code_table_moult import TABLE as moult
from .code_table_moved_before_the_encounter import TABLE as moved_before_the_encounter
from .code_table_other_marks_information import TABLE as other_marks_information
from .code_table_pectoral_muscle_score import TABLE as pectoral_muscle_score
from .code_table_place_code import TABLE as place_code
from .code_table_plumage_code import TABLE as plumage_code
from .code_table_primary_identification_method import TABLE as primary_identification_method
from .code_table_primary_moult import TABLE as primary_moult
from .code_table_pullus_age import TABLE as pullus_age
from .code_table_ringing_scheme import TABLE as ringing_scheme
from .code_table_sex import TABLE as sex
from .code_table_sexing_method import TABLE as sexing_method
from .code_table_species import TABLE as species
from .code_table_state_of_wing_point import TABLE as state_of_wing_point
from .code_table_status import TABLE as status
from .code_table_tarsus_method import TABLE as tarsus_method
from .code_table_verification_of_the_metal_ring import TABLE as verification_of_the_metal_ring

EURING_CODE_TABLES = {
    "accuracy_of_coordinates": accuracy_of_coordinates,
    "accuracy_of_date": accuracy_of_date,
    "accuracy_of_pullus_age": accuracy_of_pullus_age,
    "age": age,
    "alula": alula,
    "bill_method": bill_method,
    "brood_patch": brood_patch,
    "brood_size": brood_size,
    "carpal_covert": carpal_covert,
    "catching_lures": catching_lures,
    "catching_method": catching_method,
    "condition": condition,
    "circumstances": circumstances,
    "circumstances_presumed": circumstances_presumed,
    "euring_code_identifier": euring_code_identifier,
    "fat_score_method": fat_score_method,
    "manipulated": manipulated,
    "metal_ring_information": metal_ring_information,
    "moved_before_the_encounter": moved_before_the_encounter,
    "moult": moult,
    "other_marks_information": other_marks_information,
    "place_code": place_code,
    "plumage_code": plumage_code,
    "pectoral_muscle_score": pectoral_muscle_score,
    "primary_identification_method": primary_identification_method,
    "primary_moult": primary_moult,
    "pullus_age": pullus_age,
    "ringing_scheme": ringing_scheme,
    "sex": sex,
    "sexing_method": sexing_method,
    "species": species,
    "state_of_wing_point": state_of_wing_point,
    "status": status,
    "tarsus_method": tarsus_method,
    "verification_of_the_metal_ring": verification_of_the_metal_ring,
}

__all__ = ["EURING_CODE_TABLES"]
