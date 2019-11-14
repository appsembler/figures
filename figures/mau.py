

def get_mau_from_student_modules(student_modules, year, month):
    """
    Return records modified in year and month

    Inspect StudentModule records to see if modified is set to created date
    when records are created. If so, then we can just get the modified date in
    the specified month

    """
    qs = student_modules.filter(modified__year=year,
                                modified__month=month)
    return qs.values_list('student__id', flat=True).distinct()
