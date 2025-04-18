import os
import pandas as pd
import logging
from libs.oracle_db_connector import get_db_connection
from pathlib import Path
from libs import abort_manager
from config import PROJECT_PATH as BASE_PATH
from config import PROJECT_PATH as base_path
from libs.table_utils import create_index_if_columns_exist

# Logging setup
logger = logging.getLogger(__name__)

# Directory where the MIS .dat files are placed
MIS_FOLDER = base_path / "MIS"

# Layout definitions (SP, SF, FA as starting point)
LAYOUTS = {
    "AA": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB00_STUDENT_ID", 8, 17),
        ("AA01_ASSESSMENT_DATE", 17, 23),
        ("AA02_ASSESSMENT_RESULT", 23, 25),
    ],
    "CB": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("CB00_CONTROL_NUMBER", 8, 20),
        ("CB01_COURSE_DEPT_NUMBER", 20, 32),
        ("CB02_COURSE_TITLE", 32, 100),
        ("CB03_COURSE_TOP_CODE", 100, 106),
        ("CB04_COURSE_CREDIT_STATUS", 106, 107),
        ("CB05_COURSE_TRANSFER_STATUS", 107, 108),
        ("CB06_COURSE_UNITS_MAX", 108, 112),
        ("CB07_COURSE_UNITS_MIN", 112, 116),
        ("CB08_BASIC_SKILLS_STATUS", 116, 117),
        ("CB09_SAM_PRIORITY_CODE", 117, 118),
        ("CB10_COOP_ED_STATUS", 118, 119),
        ("CB11_CLASSIFICATION_CODE", 119, 120),
        ("CB12_COURSE_REPEATABILITY_DELETED", 120, 121),
        ("CB13_SPECIAL_CLASS_STATUS", 121, 122),
        ("CB14_CAN_CODE", 122, 128),
        ("CB15_CAN_SEQ_CODE", 128, 136),
        ("CB16_SAME_AS_DEPT_NUM1_DELETED", 136, 148),
        ("CB17_SAME_AS_DEPT_NUM2_DELETED", 148, 160),
        ("CB18_SAME_AS_DEPT_NUM3_DELETED", 160, 172),
        ("CB19_CROSSWALK_DEPT_NAME", 172, 179),
        ("CB20_CROSSWALK_CRS_NUMBER", 179, 188),
        ("CB21_PRIOR_TO_COLLEGE_LEVEL", 188, 189),
        ("CB22_NONCREDIT_CATEGORY", 189, 190),
        ("CB23_FUNDING_AGENCY_CATEGORY", 190, 191),
        ("CB24_PROGRAM_STATUS", 191, 192),
        ("CB25_GEN_ED_STATUS", 192, 193),
        ("CB26_SUPPORT_COURSE_STATUS", 193, 194),
        ("CB27_UPPER_DIVISION_STATUS", 194, 195),
        ("FILLER", 195, 220),
    ],
    "CC": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("CC01_CALENDAR_DAY_ID", 8, 11),
        ("CC02_CALENDAR_DAY_TERM", 11, 12),
        ("CC03_OVERLAPPING_TERM", 12, 13),
        ("CC04_INSTRUCTION_STATUS", 13, 14),
        ("CC05_FLEX_STATUS", 14, 15),
        ("CC06_CENSUS_STATUS", 15, 16),
        ("CC07_HOLIDAY_STATUS", 16, 17),
        ("CC08_EXAM_STATUS", 17, 18),
        ("FILLER", 18, 20),
    ],
    "CW": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB00_STUDENT_ID", 8, 17),
        ("SC12_WORK_ACTIVITY_STATUS", 17, 18),
        ("SC13_WORK_ACTIVITY_AREA_TOP_CODE", 18, 24),
        ("SC14_WORK_ACTIVITY_BEGIN_DATE", 24, 32),
        ("SC15_WORK_ACTIVITY_END_DATE", 32, 40),
        ("SC16_AVERAGE_HOURS_WORKED_PER_WEEK", 40, 42),
        ("SC17_HIGHEST_HOURLY_WAGE_EARNED", 42, 46),
        ("FILLER", 46, 80),
    ],
    "EB": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("EB00_EMPLOYEE_ID", 8, 17),
        ("EB01_ID_STATUS", 17, 18),
        ("EB02_BIRTH_DATE", 18, 26),
        ("EB03_GENDER", 26, 27),
        ("EB04_FILLER", 27, 29),
        ("EB05_CITIZENSHIP", 29, 30),
        ("EB06_DISABILITY_STATUS", 30, 31),
        ("EB07_EEO6_ACTIVITY", 31, 32),
        ("EB08_EMPLOYMENT_CLASS", 32, 33),
        ("EB09_EMPLOYMENT_STATUS", 33, 34),
        ("EB10_FILLER", 34, 40),
        ("EB11_CONTRACT_DURATION", 40, 41),
        ("EB12_ANNUAL_SALARY", 41, 47),
        ("EB13_ADDITIONAL_COMPENSATION", 47, 53),
        ("EB14_MULTI_ETHNICITY", 53, 74),
        ("FILLER", 74, 80),
    ],
    "EJ": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("EB00_EMPLOYEE_ID", 8, 17),
        ("EJ01_ASSIGNMENT_TYPE", 17, 19),
        ("EJ02_LEAVE_STATUS", 19, 20),
        ("EJ03_ACCOUNT_CODE", 20, 26),
        ("EJ04_WEEKLY_HOURS", 26, 29),
        ("EJ05_HOURLY_RATE", 29, 34),
        ("EJ06_FILLER", 34, 38),
        ("EJ07_FILLER", 38, 44),
        ("EJ08_FTE", 44, 49),
        ("FILLER", 49, 80),
    ],
    "FA": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("GI03_TERM_RECEIVED_ID", 8, 11),
        ("SB00_STUDENT_ID", 11, 20),
        ("SF21_AWARD_TYPE", 20, 22),
        ("SF22_AMOUNT_RECEIVED", 22, 27),
        ("FILLER", 27, 50),
    ],
    "SA": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB02_STUDENT_NAME_PARTIAL", 8, 11),
        ("SB00_STUDENT_ID", 11, 20),
        ("SA01_STUDENT_ASSESSMENT_INSTRUMENT", 20, 24),
        ("SA03_STUDENT_ASSESSMENT_ACCOMMODATION", 24, 28),
        ("SA04_STUDENT_ASSESSMENT_PURPOSE", 28, 30),
        ("SA05_STUDENT_ASSESSMENT_DATE", 30, 36),
        ("FILLER", 36, 40),
    ],
    "SB": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB02_FILLER", 8, 11),
        ("SB00_STUDENT_ID", 11, 20),
        ("SB01_ID_STATUS", 20, 21),
        ("SB03_BIRTH_DATE", 21, 29),
        ("SB04_GENDER", 29, 30),
        ("SB05_FILLER", 30, 32),
        ("SB06_CITIZENSHIP", 32, 33),
        ("SB07_FILLER", 33, 34),
        ("SB08_ZIP_CODE", 34, 43),
        ("SB09_RESIDENCE_CODE", 43, 48),
        ("SB10_FILLER", 48, 49),
        ("SB11_EDUCATION_STATUS", 49, 54),
        ("SB12_HS_LAST_ATTENDED", 54, 60),
        ("SB13_FILLER", 60, 66),
        ("SB14_EDUCATIONAL_GOAL", 66, 67),
        ("SB15_ENROLLMENT_STATUS", 67, 68),
        ("SB16_UNITS_EARNED_LOCAL", 68, 74),
        ("SB17_UNITS_EARNED_TRANSFER", 74, 80),
        ("SB18_UNITS_ATTEMPTED_LOCAL", 80, 86),
        ("SB19_UNITS_ATTEMPTED_TRANSFER", 86, 92),
        ("SB20_TOTAL_GRADE_POINTS_LOCAL", 92, 98),
        ("SB21_TOTAL_GRADE_POINTS_TRANSFERRED", 98, 104),
        ("SB22_ACADEMIC_STANDING", 104, 105),
        ("SB23_APPRENTICESHIP_STATUS", 105, 106),
        ("SB24_TRANSFER_CENTER_STATUS", 106, 107),
        ("SB25_FILLER", 107, 108),
        ("SB26_WIA_STATUS", 108, 109),
        ("SB27_FILLER", 109, 110),
        ("SB28_FIRST_NAME_PARTIAL", 110, 113),
        ("SB29_MULTI_ETHNICITY", 113, 134),
        ("SB30_BASIC_SKILLS_WAIVER_STATUS", 134, 135),
        ("SB31_FIRST_NAME", 135, 165),
        ("SB32_LAST_NAME", 165, 205),
        ("SB33_PARENT_GUARDIAN_EDU_LEVEL", 205, 207),
        ("SB34_CCC_ID", 207, 215),
        ("SB35_SS_ID", 215, 225),
        ("SB36_TRANSGENDER", 225, 226),
        ("SB37_SEXUAL_ORIENTATION", 226, 227),
        ("SB38_EXPANDED_ETHNICITY", 227, 421),
        ("SB39_DEPENDENTS", 421, 423),
        ("FILLER", 423, 430),
    ],
    "SC": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB00_STUDENT_ID", 8, 17),
        ("SC01_CALWORKS_ELIGIBILITY_STATUS", 17, 18),
        ("SC02_CASE_MANAGEMENT_SERVICES", 18, 19),
        ("SC03_CALWORKS_STUDENT_COUNSELING", 19, 20),
        ("SC04_REFERAL_TO_OTHER_SERVICES", 20, 21),
        ("SC05_OTHER_DIRECT_SUPPORT_SERVICES", 21, 26),
        ("SC06_ON_CAMPUS_CHILD_CARE_HOURS", 26, 30),
        ("SC07_OFF_CAMPUS_CHILD_CARE_HOURS", 30, 34),
        ("SC08_DEPENDENTS_RECEIVING_CHILD_CARE", 34, 36),
        ("SC09_TOTAL_NUMBER_OF_DEPENDENTS", 36, 38),
        ("SC10_STUDENT_FAMILY_STATUS", 38, 39),
        ("SC11_EMPLOYMENT_ASSISTANCE_SERVICES", 39, 45),
        ("SC18_ELIGIBILITY_TIME_LIMIT_STATUS", 45, 46),
        ("FILLER", 46, 80),
    ],
    "SD": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB02_STUDENT_NAME_PARTIAL", 8, 11),
        ("SB00_STUDENT_ID", 11, 20),
        ("SD01_PRIMARY_DISABILITY", 20, 21),
        ("SD02_FILLER", 21, 24),
        ("SD03_FILLER", 24, 25),
        ("SD04_FILLER", 25, 28),
        ("SD05_DISABILITY_DEPT_REHAB", 28, 29),
        ("SD06_ASL_INTERPRET_CAPTION", 29, 30),
        ("FILLER", 30, 40),
    ],
    "SE": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB02_STUDENT_NAME_PARTIAL", 8, 11),
        ("SB00_STUDENT_ID", 11, 20),
        ("SE01_EOPS_ELIGIBILITY_FACTOR", 20, 21),
        ("SE02_EOPS_TERM_OF_ACCEPTANCE", 21, 24),
        ("SE03_END_OF_TERM_EOPS_STATUS", 24, 25),
        ("SE04_EOPS_UNITS_PLANNED", 25, 29),
        ("SE05_EOPS_CARE_STATUS", 29, 30),
        ("SE06_CARE_TERM_OF_ACCEPTANCE", 30, 33),
        ("SE07_CARE_MARITAL_STATUS", 33, 34),
        ("SE08_CARE_NUM_DEPENDENTS", 34, 35),
        ("SE09_CARE_TANF_DURATION", 35, 36),
        ("SE10_EOPS_CARE_WITHDRAWAL_REASON", 36, 37),
        ("FILLER", 37, 40),
    ],
    "SF": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB02_STUDENT_NAME_PARTIAL", 8, 11),
        ("SB00_STUDENT_ID", 11, 20),
        ("SF01_APPLICANT_STATUS", 20, 21),
        ("SF03_BUDGET_CATEGORY", 21, 22),
        ("SF04_TOTAL_BUDGET_AMOUNT", 22, 27),
        ("SF05_DEPENDENCY_STATUS", 27, 28),
        ("SF06_HOUSEHOLD_SIZE", 28, 30),
        ("SF07_FAMILY_STATUS", 30, 32),
        ("SF08_INCOME_PARENT", 32, 39),
        ("SF09_INCOME_STUDENT", 39, 46),
        ("SF10_UNTAXED_INC_PARENT", 46, 54),
        ("SF11_UNTAXED_INC_STUDENT", 54, 62),
        ("SF17_EXPECTED_FAMILY_CONTRIBUTION", 62, 68),
        ("FILLER", 68, 80),
    ],
    "SG": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB00_STUDENT_ID", 8, 17),
        ("SG01_STUDENT_MILITARY_STATUS", 17, 21),
        ("SG02_STUDENT_MILITARY_DEPENDENT_STATUS", 21, 25),
        ("SG03_STUDENT_FOSTER_YOUTH_STATUS", 25, 26),
        ("SG04_STUDENT_INCARCERATED_STATUS", 26, 27),
        ("SG05_STUDENT_MESA_ASEM_STATUS", 27, 28),
        ("SG06_STUDENT_PUENTE_STATUS", 28, 29),
        ("SG07_STUDENT_MCHS_ECHS_STATUS", 29, 30),
        ("SG08_STUDENT_UMOJA_STATUS", 30, 31),
        ("SG09_FILLER", 31, 33),
        ("SG10_STUDENT_CAA_STATUS", 33, 34),
        ("SG11_STUDENT_CAFYES_STATUS", 34, 35),
        ("SG12_STUDENT_BACCALAUREATE_PROGRAM", 35, 40),
        ("SG13_STUDENT_CCAP_STATUS", 40, 41),
        ("SG14_STUDENT_ECONOMICALLY_DISADV_STATUS", 41, 43),
        ("SG15_STUDENT_EX_OFFENDER_STATUS", 43, 44),
        ("SG16_STUDENT_HOMELESS_STATUS", 44, 45),
        ("SG17_STUDENT_LONGTERM_UNEMPLOY_STATUS", 45, 46),
        ("SG18_STUDENT_CULTURAL_BARRIER_STATUS", 46, 47),
        ("SG19_STUDENT_SEASONAL_FARM_WORK_STATUS", 47, 48),
        ("SG20_STUDENT_LITERACY_STATUS", 48, 49),
        ("SG21_STUDENT_WORK_BASED_LEARNING_STATUS", 49, 50),
        ("SG22_STUDENT_A2MEND_STATUS", 50, 51),
        ("SG23_STUDENT_BASIC_NEEDS", 51, 58),
        ("SG24_STUDENT_YOUTH_JUSTICE_STATUS", 58, 59),
        ("SG25_STUDENT_CAMPUS_HOUSING_STATUS", 59, 60),
        ("SG26_STUDENT_DUAL_ADMISSION_STATUS", 60, 62),
        ("SG27_STUDENT_HOMELESS_HOUSING_INSECURITY", 62, 64),
        ("SG28_STUDENT_ATHLETE", 64, 68),
        ("SG29_STUDENT_RISING_SCHOLARS_NETWORK", 68, 69),
        ("FILLER", 69, 70),
    ],
    "SL": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB00_STUDENT_ID", 8, 17),
        ("SL01_PLACEMENT_DATE", 17, 23),
        ("SL02_PLACEMENT_TYPE", 23, 24),
        ("SL03_PLACEMENT_SOURCE_HIGH_SCHOOL", 24, 25),
        ("SL04_PLACEMENT_SOURCE_GUIDED_SELF", 25, 26),
        ("SL05_PLACEMENT_SOURCE_TEST", 26, 27),
        ("SL06_PLACEMENT_LEVEL", 27, 28),
    ],
    "SM": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB02_STUDENT_NAME_PARTIAL", 8, 11),
        ("SB00_STUDENT_ID", 11, 20),
        ("SM01_MATRICULATION_GOALS", 20, 24),
        ("SM02_MATRICULATION_MAJOR", 24, 30),
        ("SM03_SPECIAL_SERVICES_NEEDS", 30, 44),
        ("SM04_ORIENTATION_EXEMPT_STATUS", 44, 48),
        ("SM05_ASSESSMENT_EXEMPT_STATUS", 48, 52),
        ("SM06_COUNSELING_EXEMPT_STATUS", 52, 56),
        ("SM07_ORIENTATION_SERVICES", 56, 57),
        ("SM08_ASSESSMENT_PLACEMENT", 57, 58),
        ("SM09_OTHER_ASSESSMENT_SERVICES", 58, 61),
        ("SM12_COUNSELING_SERVICES", 61, 62),
        ("SM13_ACADEMIC_FOLLOWUP_SERVICES", 62, 63),
        ("FILLER", 63, 80),
    ],
    "SP": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB02_STUDENT_NAME_PARTIAL", 8, 11),
        ("SB00_STUDENT_ID", 11, 20),
        ("SP01_PROGRAM_TOP_CODE", 20, 26),
        ("SP02_PROGRAM_AWARD", 26, 27),
        ("SP03_AWARD_EARNED_DATE", 27, 33),
        ("GI92_RECORD_NUMBER_ID", 33, 34),
        ("SP04_PROGRAM_CONTROL_NUMBER", 34, 39),
        ("FILLER", 39, 40),
    ],
    "SS": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB02_STUDENT_NAME_PARTIAL", 8, 11),
        ("SB00_STUDENT_ID", 11, 20),
        ("SS01_EDUCATIONAL_GOAL", 20, 21),
        ("SS02_COURSE_OF_STUDY_CREDIT", 21, 27),
        ("SS03_ORIENTATION_EXEMPT_CREDIT", 27, 29),
        ("SS04_ASSESSMENT_EXEMPT_CREDIT", 29, 31),
        ("SS05_ED_PLAN_EXEMPT_CREDIT", 31, 33),
        ("SS06_ORIENTATION_SERVICES_CREDIT", 33, 34),
        ("SS07_ASSESSMENT_PLACEMENT_CREDIT", 34, 38),
        ("SS08_COUNSELING_SERVICES_CREDIT", 38, 39),
        ("SS09_ED_PLAN_CREDIT", 39, 40),
        ("SS10_PROBATION_SERVICE_CREDIT", 40, 41),
        ("SS11_OTHER_SERVICES_CREDIT", 41, 45),
        ("SS12_COURSE_OF_STUDY_NONCREDIT", 45, 51),
        ("SS13_ORIENTATION_EXEMPT_NONCREDIT", 51, 53),
        ("SS14_ASSESSMENT_EXEMPT_NONCREDIT", 53, 55),
        ("SS15_ED_PLAN_EXEMPT_NONCREDIT", 55, 57),
        ("SS16_ORIENTATION_SERVICES_NONCREDIT", 57, 58),
        ("SS17_ASSESSMENT_PLACEMENT_NONCREDIT", 58, 62),
        ("SS18_COUNSELING_SERVICES_NONCREDIT", 62, 63),
        ("SS19_ED_PLAN_NONCREDIT", 63, 64),
        ("SS20_OTHER_SERVICES_NONCREDIT", 64, 67),
        ("FILLER", 67, 80),
    ],
    "SV": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB02_STUDENT_NAME_PARTIAL", 8, 11),
        ("SB00_STUDENT_ID", 11, 20),
        ("SV01_VOCATIONAL_PROGRAM_PLAN_STATUS", 20, 21),
        ("SV02_FILLER", 21, 22),
        ("SV03_ECONOMICALLY_DISADV_STATUS", 22, 24),
        ("SV04_SINGLE_PARENT_STATUS", 24, 25),
        ("SV05_DISPLACED_HOMEMAKER_STATUS", 25, 26),
        ("SV06_COOP_ED_TYPE", 26, 27),
        ("SV07_FILLER", 27, 28),
        ("SV08_TECH_PREP_STATUS", 28, 29),
        ("SV09_MIGRANT_WORKER_STATUS", 29, 30),
        ("SV10_WIA_VETERAN_STATUS", 30, 31),
        ("FILLER", 31, 40),
    ],
    "SX": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB02_STUDENT_NAME_PARTIAL", 8, 11),
        ("SB00_STUDENT_ID", 11, 20),
        ("CB01_COURSE_DEPT_NUMBER", 20, 32),
        ("XB00_SECTION_ID", 32, 38),
        ("SX01_ENROLLMENT_EFFECTIVE_DATE", 38, 44),
        ("SX02_ENROLLMENT_DROP_DATE", 44, 50),
        ("SX03_ENROLLMENT_UNITS_EARNED", 50, 54),
        ("SX04_ENROLLMENT_GRADE", 54, 57),
        ("SX05_POSITIVE_ATTENDANCE_HOURS", 57, 62),
        ("CB00_CONTROL_NUMBER", 62, 74),
        ("SX06_APPORTIONMENT_STATUS", 74, 75),
        ("SX07_CVC_INDICATOR", 75, 76),
        ("FILLER", 76, 78),
    ],
    "SY": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("SB00_STUDENT_ID", 8, 17),
        ("CB00_COURSE_CONTROL_NUMBER", 17, 29),
        ("CB01_COURSE_DEPT_NUMBER", 29, 41),
        ("SY01_CREDIT_ASSESSMENT_DATE", 41, 47),
        ("SY02_CREDIT_ASSESSMENT_METHOD", 47, 48),
        ("SY03_CREDIT_UNITS_AWARDED", 48, 52),
        ("SY04_CREDIT_GRADE", 52, 55),
    ],
    "XB": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("GI02_FILLER", 8, 11),
        ("CB01_COURSE_DEPT_NUMBER", 11, 23),
        ("XB00_SECTION_ID", 23, 29),
        ("XB01_ACCOUNTING_METHOD", 29, 30),
        ("XB02_DATE_CENSUS_FIRST", 30, 36),
        ("XB03_FILLER", 36, 42),
        ("XB04_CONTRACT_ED_CODE", 42, 43),
        ("XB05_UNITS_MAXIMUM", 43, 47),
        ("XB06_UNITS_MINIMUM", 47, 51),
        ("XB07_FILLER", 51, 52),
        ("XB08_DSPS_SPECIAL_STATUS", 52, 53),
        ("XB09_WORK_BASED_LEARNING", 53, 54),
        ("XB10_CVC_STATUS", 54, 55),
        ("XB11_CONTACT_HOURS", 55, 61),
        ("CB00_CONTROL_NUMBER", 61, 73),
        ("XB12_MATERIAL_COST", 73, 74),
        ("FILLER", 74, 80),
    ],
    "XE": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("CB01_COURSE_DEPT_NUMBER", 8, 20),
        ("XB00_SECTION_ID", 20, 26),
        ("EB00_EMPLOYEE_ID", 26, 35),
        ("XF00_SESSION_ID", 35, 37),
        ("XE01_ASSIGNMENT_TYPE", 37, 38),
        ("XE02_ASSIGNMENT_PERCENT", 38, 41),
        ("XE03_ASSIGNMENT_FTE", 41, 46),
        ("XE04_ASSIGNMENT_HOURLY_RATE", 46, 51),
        ("CB00_CONTROL_NUMBER", 51, 63),
        ("FILLER", 63, 80),
    ],
    "XF": [
        ("GI90_RECORD_CODE", 0, 2),
        ("GI01_DISTRICT_COLLEGE_ID", 2, 5),
        ("GI03_TERM_ID", 5, 8),
        ("CB01_COURSE_DEPT_NUMBER", 8, 20),
        ("XB00_SECTION_ID", 20, 26),
        ("XF00_SESSION_ID", 26, 28),
        ("XF01_INSTRUCTION_METHOD", 28, 30),
        ("XF02_DATE_BEGINNING", 30, 36),
        ("XF03_DATE_ENDING", 36, 42),
        ("XF04_DAYS_SCHEDULED", 42, 51),
        ("XF05_TIME_BEGIN", 51, 55),
        ("XF06_TIME_END", 55, 59),
        ("XF07_TOTAL_HOURS", 59, 64),
        ("CB00_CONTROL_NUMBER", 64, 76),
        ("FILLER", 76, 80)
    ]    
}

def parse_fixed_width_file(file_path, layout):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            row = {name: line[start:end].strip() for name, start, end in layout}
            data.append(row)
    return pd.DataFrame(data)

def load_to_oracle(df, table_name, annual_code, conn, cursor):
    df.columns = [col.upper() for col in df.columns]

    cursor.execute("""
        SELECT COUNT(*) FROM all_tables 
        WHERE table_name = :1 AND owner = 'DWH'
    """, [table_name.upper()])
    exists = cursor.fetchone()[0] > 0

    if not exists:
        columns = ', '.join([
            f'{col.upper()} VARCHAR2(2)' if col.upper() == 'GI90_RECORD_CODE' else
            f'{col.upper()} VARCHAR2(3)' if col.upper() in ['GI01_DISTRICT_COLLEGE_ID', 'GI03_TERM_ID'] else
            f'{col.upper()} VARCHAR2(10)' if col.upper() == 'SB00_STUDENT_ID' else
            f'{col.upper()} VARCHAR2(4000)'
            for col in df.columns
        ])
        create_sql = f'CREATE TABLE DWH.{table_name.upper()} ({columns})'
        try:
            cursor.execute(create_sql)
            cursor.execute(f'GRANT SELECT ON DWH.{table_name.upper()} TO PUBLIC')
            abort_manager.register_created_table(table_name)
            logger.info(f"🆕 Created table {table_name} and granted SELECT to PUBLIC.")
        except Exception as e:
            logger.error(f"❌ Failed to create table {table_name}: {e}")
            return False

    # ✅ Always try to create the index, whether or not table existed
    create_index_if_columns_exist(cursor, "DWH", table_name, ["GI90_RECORD_CODE", "GI01_DISTRICT_COLLEGE_ID", "GI03_TERM_ID"])

    if 'GI03_TERM_ID' in df.columns:
        cursor.execute(f'DELETE FROM DWH.{table_name.upper()} WHERE GI03_TERM_ID = :1', [annual_code])
        logger.info(f"🧹 Deleted existing records from {table_name} for GI03_TERM_ID = {annual_code}")

    columns = ', '.join(f'{col.upper()}' for col in df.columns)
    values = ', '.join(f':{i+1}' for i in range(len(df.columns)))
    insert_sql = f'INSERT INTO DWH.{table_name.upper()} ({columns}) VALUES ({values})'

    for _, row in df.iterrows():
        if abort_manager.should_abort:
            abort_manager.cleanup_on_abort(conn, cursor)
            return False
        try:
            cursor.execute(insert_sql, tuple(row))
        except Exception as e:
            logger.error(f"❌ Failed to insert row into {table_name}: {e}")

    logger.info(f"✅ Loaded {len(df)} rows into {table_name}")
    return True


def run_mis_loader(existing_conn=None):
    conn = existing_conn or get_db_connection(force_shared=True)
    if not conn:
        logger.error("❌ Could not connect to Oracle.")
        return
    cursor = conn.cursor()

    abort_manager.reset()

    for filename in os.listdir(MIS_FOLDER):
        if filename.endswith(".dat"):
            file_path = os.path.join(MIS_FOLDER, filename)
            annual_code = filename[3:6]  # e.g., '240' from 'U86240SP.dat'
            file_code = filename[-6:-4].upper()

            if file_code not in LAYOUTS:
                logger.warning(f"⚠️ No layout defined for file type {file_code}. Skipping {filename}.")
                continue

            table_name = f"MIS_{file_code}_IN"
            if not table_name.upper().endswith("_IN"):
                logger.warning(f"❌ Skipping {filename} to avoid interacting with a production table: {table_name}")
                continue

            logger.info(f"📥 Processing {filename} into {table_name}...")
            df = parse_fixed_width_file(file_path, LAYOUTS[file_code])
            success = load_to_oracle(df, table_name, annual_code, conn, cursor)
            if not success:
                logger.warning(f"⏪ Aborted during loading {filename}. Rolling back.")
                break

    try:
        if not abort_manager.should_abort:
            conn.commit()
            logger.info("✅ All MIS files loaded and committed.")
        else:
            logger.warning("⏹️ MIS Loader aborted by user.")
    except Exception as e:
        logger.warning(f"⚠️ Commit failed or was skipped due to abort: {e}")

    try:
        cursor.close()
    except Exception as e:
        if "DPY-1001" not in str(e):
            logger.warning(f"⚠️ Failed to close cursor: {e}")

    try:
        conn.close()
    except Exception as e:
        if "DPY-1001" not in str(e):
            logger.warning(f"⚠️ Failed to close connection: {e}")

