"""

This module provides canned courses to test specific criteria
TODO:
* Add self-paced flag
"""

COURSE_OVERVIEW_DATA = [
    dict(
        id='course-v1:StarFleetAcademy+SFA01+2161',
        display_name='Intro to Astronomy',
        org='StarFleetAcademy',
        display_org_with_default='StarFleetAcademy',
        number='SFA01',
        created='2018-07-01',
        enrollment_start='2018-08-01',
        enrollment_end='2018-12-31',
        ),
    # The following provide two identical courses with different runs
    dict(
        id='course-v1:StarFleetAcademy+SFA02+2161',
        display_name='Intro to Xenology',
        org='StarFleetAcademy',
        display_org_with_default='StarFleetAcademy',
        number='SFA02',
        created='2018-09-01',
        enrollment_start='2018-10-05',
        enrollment_end='2019-02-02',
        ),
    dict(
        id='course-v1:StarFleetAcademy+SFA02+2162',
        display_name='Intro to Xenology',
        org='StarFleetAcademy',
        display_org_with_default='StarFleetAcademy',
        number='SFA03',
        created='2019-09-01',
        enrollment_start='2019-10-05',
        enrollment_end='2020-02-02',
        ),
]
