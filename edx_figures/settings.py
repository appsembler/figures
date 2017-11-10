'''
This module provides default values for running edx-figures

'''

EDX_FIGURES = {
    'DEFAULT_REPORT_ENCODING': 'utf-8',
    'REPORT_ROW_BUILDERS': {
        'learners': 'edx_figures.builders.DemographicReportRowBuilder',
        'grades': 'edx_figures.builders.GradeReportRowBuilder',
    }
}
