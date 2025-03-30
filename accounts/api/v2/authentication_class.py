import base64
import binascii

from django.utils.translation import ugettext_lazy as _

from rest_framework import HTTP_HEADER_ENCODING, exceptions
from rest_framework.authentication import (
    BasicAuthentication,
    get_authorization_header,
)

from defender import utils
from defender import config
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
class BasicAuthenticationDefender(JSONWebTokenAuthentication):

    def get_username_from_request(self, request):
        auth = get_authorization_header(request).split()
        return base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(':')[0]

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'basic':
            return None

        if len(auth) == 1:
            msg = _('Invalid basic header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid basic header. Credentials string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        if utils.is_already_locked(request, get_username=self.get_username_from_request):
            detail = "You have attempted to login {failure_limit} times, with no success." \
                     "Your account is locked for {cooloff_time_seconds} seconds" \
                     "".format(
                        failure_limit=config.FAILURE_LIMIT,
                        cooloff_time_seconds=config.COOLOFF_TIME
                     )
            raise exceptions.AuthenticationFailed(_(detail))

        try:
            auth_parts = base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(':')
        except (TypeError, UnicodeDecodeError, binascii.Error):
            msg = _('Invalid basic header. Credentials not correctly base64 encoded.')
            raise exceptions.AuthenticationFailed(msg)

        userid, password = auth_parts[0], auth_parts[2]
        login_unsuccessful = False
        login_exception = None
        try:
            response = self.authenticate_credentials(userid, password)
        except exceptions.AuthenticationFailed as e:
            login_unsuccessful = True
            login_exception = e

        utils.add_login_attempt_to_db(request,
                                      login_valid=not login_unsuccessful,
                                      get_username=self.get_username_from_request)
        # add the failed attempt to Redis in case of a failed login or resets the attempt count in case of success
        utils.check_request(request,
                            login_unsuccessful=login_unsuccessful,
                            get_username=self.get_username_from_request)
        if login_unsuccessful:
            raise login_exception

        return response
