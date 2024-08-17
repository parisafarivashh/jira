import logging

from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status


class RequestLimitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if RequestLimit.check_ip_is_blocked(request):
            return JsonResponse(data=dict(), status=status.HTTP_400_BAD_REQUEST)


class CaptureFailedLoginMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path == '/api/member/token' and \
                response.status_code != 200:
            logging.info(f'Request Path Is: {request.path}')
            RequestLimit.attempt(request=request)

        return response


class RequestLimit:
    MAX_ATTEMPT_NUMBER = 3
    ATTEMPT_RESSET_TIME = 2

    @classmethod
    def check_ip_is_blocked(cls, request):
        ip_address = cls.get_ip_from_request(request)
        logging.info(f'Ip block is: {cache.get(f"ip_blocked_{ip_address}")}')
        if cache.get(f'ip_blocked_{ip_address}'):
            return True
        return False

    @staticmethod
    def get_ip_from_request(request) -> int:
        ip_address = request.META.get('REMOTE_ADDR')
        return ip_address

    @classmethod
    def block_ip_address(cls, ip_address):
        cache.set(f'ip_blocked_{ip_address}', ip_address, cls.ATTEMPT_RESSET_TIME)
        logging.info(f'Ip Block Address Is :ip_blocked_{ip_address}')
        return True

    @classmethod
    def attempt(cls, request):
        ip_address = cls.get_ip_from_request(request)
        cache_value = cache.get(f'attempt_{ip_address}', 1)
        value = cache_value + 1
        if value > cls.MAX_ATTEMPT_NUMBER:
            cls.block_ip_address(ip_address)
        else:
            cache.set(f'attempt_{ip_address}', value, cls.ATTEMPT_RESSET_TIME)

