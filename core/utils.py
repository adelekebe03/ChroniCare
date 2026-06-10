from .models import AuditLog

def log_action(user, action, description, table):
    AuditLog.objects.create(
        user=user,
        action=action,
        description=description,
        table_concernee=table
    )