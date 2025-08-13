from utilities.choices import ChoiceSet


class CRStatusChoices(ChoiceSet):
    key = "ChangeRequest.status"

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"

    CHOICES = [
        (PENDING, "Pending"),
        (IN_REVIEW, "In review"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (SCHEDULED, "Scheduled"),
        (IMPLEMENTED, "Implemented"),
        (CANCELLED, "Cancelled"),
    ]
