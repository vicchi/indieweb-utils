from dataclasses import dataclass
from typing import List, Optional
from urllib import parse as url_parse

import requests

from ..utils.urls import _is_http_url
from . import discovery


@dataclass
class Header:
    name: str
    value: str


class MissingSourceError(Exception):
    pass


class MissingTargetError(Exception):
    pass


class UnsupportedProtocolError(Exception):
    pass


class TargetIsNotApprovedDomain(Exception):
    pass


class GenericWebmentionError(Exception):
    pass


class CouldNotConnectToWebmentionEndpoint(Exception):
    pass


@dataclass
class SendWebmentionResponse:
    title: str
    description: str
    url: str
    success: bool
    status_code: Optional[int]
    headers: List[Header]


def send_webmention(source: str, target: str, me: str = "") -> SendWebmentionResponse:
    """
    Send a webmention to a target URL.

    :param source: The source URL of the webmention.
    :type source: str
    :param target: The target URL to which you want to send the webmention.
    :type target: str
    :param me: The URL of the user.
    :type me: str
    :return: The response from the webmention endpoint.
    :rtype: SendWebmentionResponse
    """
    if not source:
        raise MissingSourceError("A source was not provided.")

    if not target:
        raise MissingTargetError("A target was not provided.")

    if not _is_http_url(source) or not _is_http_url(target):
        raise UnsupportedProtocolError("Only HTTP/HTTPS URLs are supported.")

    # if domain is not approved, don't allow access
    if me != "":
        target_domain = url_parse.urlsplit(target).scheme

        if "/" in me.strip("/"):
            raw_domain = url_parse.urlsplit(me).scheme
        else:
            raw_domain = me

        if not target_domain.endswith(raw_domain):
            raise TargetIsNotApprovedDomain("Target must be a {me} post.")

    response = discovery.discover_webmention_endpoint(target)

    if response.endpoint == "":
        raise GenericWebmentionError(response.message)

    # make post request to endpoint with source and target as values
    try:
        r = requests.post(
            response.endpoint,
            data={"source": source, "target": target},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    except requests.exceptions.RequestException:
        raise CouldNotConnectToWebmentionEndpoint("Could not connect to the receiver's webmention endpoint.")

    message = str(r.json()["message"])

    valid_status_codes = (200, 201, 202)

    headers = [Header(name=str(k), value=str(v)) for k, v in r.headers.items()]

    if r.status_code not in valid_status_codes:
        raise GenericWebmentionError(message)

    return SendWebmentionResponse(
        title=message, description=message, url=target, success=True, status_code=r.status_code, headers=headers
    )
