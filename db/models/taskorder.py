from db.models import Invoice


class TaskOrder(Invoice):
    """ """

    model_name = "taskorder"

    class Meta:
        db_table = "taskorder"
