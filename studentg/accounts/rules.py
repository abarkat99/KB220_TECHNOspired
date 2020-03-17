import rules

@rules.predicate
def is_unauthenticated(user):
    return not user.is_authenticated

@rules.predicate
def is_student(user):
    return user.is_authenticated and (user.designation=='UNI' or user.designation=='INS' or user.designation=='DEP')

rules.add_perm('accounts.sign_up', is_unauthenticated)