import rules

@rules.predicate
def is_committee_staff(user):
    return user.is_authenticated and (user.designation=='UNI' or user.designation=='INS' or user.designation=='DEP')

@rules.predicate
def is_committee_head(user):
    return user.is_authenticated and (user.designation=='UNI_H' or user.designation=='INS_H' or user.designation=='DEP_H')
rules.add_perm('redressal.manage_members',is_committee_head)
rules.add_perm('redressal.add_subcategory',is_committee_head)

is_committee_member=is_committee_staff | is_committee_head
rules.add_perm('redressal.view_grievances',is_committee_member)

@rules.predicate
def is_committee_head_of_super_body_type(user,sub_body):
    if not user.is_authenticated:
        return False
    return (user.is_superuser and sub_body=="university") or (user.designation=='UNI_H' and sub_body=="institute") or (user.designation=='INS_H' and sub_body=="department")
rules.add_perm('redressal.add_body', is_committee_head_of_super_body_type)

@rules.predicate
def is_committee_head_of(user,staff):
    return user.is_authenticated and (staff.get_redressal_body()==user.get_redressal_body()) and user.has_perm('redressal.manage_members')
rules.add_perm('redressal.remove_member', is_committee_head_of)

@rules.predicate
def has_rbody_same_as_grievance(user,grievance):
    return user.is_authenticated and (user.get_redressal_body()==grievance.redressal_body)
is_committee_member_of_grievance= has_rbody_same_as_grievance & is_committee_member
rules.add_perm('redressal.update_grievance', is_committee_member_of_grievance)