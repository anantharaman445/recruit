from django.http import JsonResponse


def health_check(request):
    data = {'message': 'OK'}
    return JsonResponse(status=200, data=data)