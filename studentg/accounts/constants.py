class DesignationConstants:
    ADMIN = 'ADM'
    STUDENT = 'STU'
    UNIVERSITY = 'UNI'
    INSTITUTE = 'INS'
    DEPARTMENT = 'DEP'
    UNI_HEAD = 'UNI_H'
    INS_HEAD = 'INS_H'
    DEP_HEAD = 'DEP_H'
    HEAD_DESIGNATIONS = {UNI_HEAD, INS_HEAD, DEP_HEAD}
    DESIGNATION_CHOICES = [
        (ADMIN, 'Admin'),
        (STUDENT, 'Student'),
        (UNIVERSITY, 'University Member'),
        (INSTITUTE, 'Institute Member'),
        (DEPARTMENT, 'Department Member'),
        (UNI_HEAD, 'University Head'),
        (INS_HEAD, 'Institute Head'),
        (DEP_HEAD, 'Department Head'),
    ]


class TempDesignationConstants:
    STUDENT = DesignationConstants.STUDENT
    UNIVERSITY = DesignationConstants.UNIVERSITY
    INSTITUTE = DesignationConstants.INSTITUTE
    DEPARTMENT = DesignationConstants.DEPARTMENT
    UNI_HEAD = DesignationConstants.UNI_HEAD
    INS_HEAD = DesignationConstants.INS_HEAD
    DEP_HEAD = DesignationConstants.DEP_HEAD
    HEAD_DESIGNATIONS = DesignationConstants.HEAD_DESIGNATIONS
    DESIGNATION_CHOICES = DesignationConstants.DESIGNATION_CHOICES
