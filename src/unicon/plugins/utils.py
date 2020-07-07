""" Utilities used by multiple plugins.

Module:
    unicon.plugins

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    Module for defining utilities used across various plugins.
"""

import re
from unicon.utils import to_plaintext
from unicon.core.errors import (UniconAuthenticationError,
    CredentialsExhaustedError, )

def _fallback_cred(context):
    return [context['default_cred_name']] \
        if 'default_cred_name' in context else []

def _get_creds_to_try(context):
    """ Get list of credentials to try. """
    creds_to_try =  context.get('cred_list', _fallback_cred(context))

    if creds_to_try is None:
        creds_to_try = _fallback_cred(context)

    if not isinstance(creds_to_try, list):
        creds_to_try = [creds_to_try]
    return creds_to_try


def get_current_credential(context, session):
    """ Gets the current credential name to try, if available.

    If a current credential name has not been set, try to get the next
    credential name from the credential list.

    The following optional context keys may be set:
        - credentials - Dict of all known credentials, keyed by name.

        - cred_list - List of credential names to try.
            If not specified, or specified as None, defaults to
            [context.default_cred_name] if set, otherwise [].
            If specified as a non-list, then it is reassigned to a single-
            element list.

        - default_cred_name - Default credential name.

    The following session variables are used:
        - current_credential : The credential currently being used.
          This credential is set to the next credential in the cred_list if
          not previously set.

        - cred_iter : Initialized to an iterable based on cred_list, keeps
          track of which credential to try next.

    Raises
    ------
        CredentialsExhaustedError
            If the session's current_credential was not set and all credential
            names in cred_list have already been tried.
    """
    credentials = context.get('credentials')
    current_credential = None
    if credentials:
        current_credential = session.get('current_credential')
        if not current_credential:
            creds_to_try = session.get('cred_iter',
                iter(_get_creds_to_try(context)))
            session['cred_iter'] = creds_to_try
            try:
                current_credential = next(creds_to_try)
            except StopIteration:
                # All credentials in the list have already been tried.
                pass

        if not current_credential:
            raise CredentialsExhaustedError(
                creds_tried=_get_creds_to_try(context))
        else:
            session['current_credential'] = current_credential

    return current_credential


def invalidate_current_credential(context, session):
    """ The current credential is no longer to be used.
    Save aside the previous credential name in the context so it outlives
    the session.
    """
    context['previous_credential'] = session['current_credential']
    session['current_credential'] = None


def common_cred_username_handler(spawn, context, credential):
    """ Send the current credential's username. """
    try:
        spawn.sendline(to_plaintext(
            context['credentials'][credential]['username']))
    except KeyError:
        raise UniconAuthenticationError("No username found "
            "for credential {}.".format(credential))


def common_cred_password_handler(spawn, context, session, credential,
        reuse_current_credential=False):
    """ Send the current credential's password.

    The current credential is then invalidated as long as
    reuse_current_credential is set to `False`.

    Invalidating a credential means that if any subsequent usernames/passwords
    are requested, the next credential in session['cred_iter'] is consumed.
    """
    try:
        spawn.sendline(to_plaintext(
            context['credentials'][credential]['password']))
    except KeyError:
        raise UniconAuthenticationError("No password found "
            "for credential {}.".format(credential))
    if not reuse_current_credential:
        invalidate_current_credential(context=context, session=session)


def slugify(text):
    """ Simple slugify

    Returns string stripped of special chars, replaced with _
    """
    text = text.lower()
    pattern = re.compile(r'[^a-z0-9]+')
    text = re.sub(pattern, '_', text)
    text = re.sub(r'_{2,}', '_', text).strip('_')
    return text
