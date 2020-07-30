class StatusConstants:
    DRAFT = 1
    REVIEW = 2
    PENDING = 3
    RESOLVED = 4
    REJECTED = 5
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (REVIEW, 'In Review'),
        (PENDING, 'Pending'),
        (RESOLVED, 'Resolved'),
        (REJECTED, 'Rejected'),
    ]
    STATUS_COLORS = {
        DRAFT: 'text-muted',
        REVIEW: 'text-primary',
        PENDING: 'text-warning',
        RESOLVED: 'text-success',
        REJECTED: 'text-danger',
    }

STATUS_DISPLAY_CONVERTER = {
    StatusConstants.DRAFT: 'Draft',
    StatusConstants.REVIEW: 'In Review',
    StatusConstants.PENDING: 'Pending',
    StatusConstants.RESOLVED: 'Resolved',
    StatusConstants.REJECTED: 'Rejected',
}
STATUS_COLOR_CONVERTER = {
    StatusConstants.DRAFT: '#6c757d',
    StatusConstants.REVIEW: '#007bff',
    StatusConstants.PENDING: '#ffc107',
    StatusConstants.RESOLVED: '#28a745',
    StatusConstants.REJECTED: '#dc3545',
}
STATUS_VISIBLE_TO_COMMITTEE = StatusConstants.STATUS_CHOICES.copy()
STATUS_VISIBLE_TO_COMMITTEE.pop(0)