from rest_framework.permissions import BasePermission, SAFE_METHODS
print(SAFE_METHODS)

class ProductPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = request.user.role

        # Admin: everything
        if role == request.user.Role.ADMIN:
            return True

        # Seller: read + create + update + delete
        if role == request.user.Role.SELLER:
            return view.action in {
                "list",
                "retrieve",
                "create",
                "update",
                "partial_update",
                "destroy",
            }

        # Customer: read only
        if role == request.user.Role.CUSTOMER:
            return view.action in {
                "list",
                "retrieve",
            }

        return False

    def has_object_permission(self, request, view, obj):

        # Admin can operate on any product
        if request.user.role == request.user.Role.ADMIN:
            return True

        # Customer can only read
        if request.user.role == request.user.Role.CUSTOMER:
            return request.method in SAFE_METHODS

        # Seller:
        # can only modify their own product
        if request.user.role == request.user.Role.SELLER:

            if request.method in SAFE_METHODS:
                return True

            return obj.seller_id == request.user.id

        return False