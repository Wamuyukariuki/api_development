from rest_framework.response import Response

def standard_response(data=None, errors=None, status=200, message=""):
    """
    Standard response format for API views.
    """
    response_data = {
        "data": data,
        "errors": errors,
        "message": message
    }
    return Response(response_data, status=status)
