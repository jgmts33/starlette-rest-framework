class BasePermission:
    message = 'You do not have permission to perform that action.'
    status_code = 403

    def has_permission(self, request, endpoint):
        return True
