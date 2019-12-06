#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import re

from ansible.plugins.action import ActionBase
from ansible.template import Templar
from ansible.errors import AnsibleOptionsError

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display

    display = Display()


class ActionModule(ActionBase):
    TRANSFERS_FILES = False

    def __init__(self, task, connection, play_context, loader, templar, shared_loader_obj):
        super(ActionModule, self).__init__(task, connection, play_context, loader, templar, shared_loader_obj)
        self._task_vars = None
        self._templar = templar

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        self._task_vars = task_vars

        try:
            # Get config values
            conga_aemdst_curl_url = self._get_arg_or_var('conga_aemdst_curl_url')
            conga_aemdst_curl_expected_http_code = self._get_arg_or_var('conga_aemdst_curl_expected_http_code')
            conga_aemdst_curl_follow_redirects_expected_http_code = self._get_arg_or_var('conga_aemdst_curl_follow_redirects_expected_http_code')
            conga_aemdst_curl_follow_redirects = self._get_arg_or_var('conga_aemdst_curl_follow_redirects')
            conga_aemdst_curl_allow_insecure = self._get_arg_or_var('conga_aemdst_curl_allow_insecure')
            conga_aemdst_curl_noproxy = self._get_arg_or_var('conga_aemdst_curl_noproxy')
            conga_aemdst_curl_resolve = self._get_arg_or_var('conga_aemdst_curl_resolve', [], False)
            conga_aemdst_curl_headers = self._get_arg_or_var('conga_aemdst_curl_headers', [], False)
            conga_aemdst_curl_timeout = self._get_arg_or_var('conga_aemdst_curl_timeout')
            conga_aemdst_curl_connect_timeout = self._get_arg_or_var('conga_aemdst_curl_connect_timeout')

        except AnsibleOptionsError as err:
            return self._fail_result(result, err.message)

        # set defaults
        curl_cmdline_args = [
            '--max-time {}'.format(conga_aemdst_curl_timeout),
            '--connect-timeout {}'.format(conga_aemdst_curl_connect_timeout),
        ]
        write_out_arg = "%{redirect_url}\n%{http_code}"
        expected_http_code = conga_aemdst_curl_expected_http_code

        if conga_aemdst_curl_allow_insecure:
            curl_cmdline_args.append('--insecure')

        for resolve in conga_aemdst_curl_resolve:
            host = resolve.get("host")
            port = resolve.get("port")
            address = resolve.get("address")
            curl_cmdline_args.append("--resolve '{}:{}:{}'".format(host, port, address))

        if conga_aemdst_curl_follow_redirects:
            curl_cmdline_args.append('--location')
            write_out_arg = "%{url_effective}\n%{http_code}"
            expected_http_code = conga_aemdst_curl_follow_redirects_expected_http_code

        if conga_aemdst_curl_noproxy:
            curl_cmdline_args.append('--noproxy "*"')

        for header in conga_aemdst_curl_headers:
            curl_cmdline_args.append('--header "{}"'.format(header))

        curl_base_command = "curl {}".format(" ".join(curl_cmdline_args))
        curl_internal_command = '{} --write-out "{}" --output /dev/null --silent {}'.format(curl_base_command,
                                                                                            write_out_arg,
                                                                                            conga_aemdst_curl_url)
        curl_debug_command = "{} {}".format(curl_base_command, conga_aemdst_curl_url)

        results = {
            "curl_base_command": curl_base_command,
            "curl_internal_command": curl_internal_command,
            "curl_debug_command": curl_debug_command,
            "expected_http_code": expected_http_code,
        }

        result["ansible_facts"] = {
            "conga_aemdst_curl_cmdline": results,
        }

        # Always display resolved role and mapping
        display.display(
            "[[%s] => %s" %
            (task_vars['inventory_hostname'], results))

        return result

    @staticmethod
    def _fail_result(result, message):
        result['failed'] = True
        result['msg'] = message
        return result

    def _get_arg_or_var(self, name, default=None, is_required=True):
        ret = self._task.args.get(name, self._task_vars.get(name, default))
        ret = self._templar.template(ret)
        if is_required and ret is None:
            raise AnsibleOptionsError("parameter %s is required" % name)
        else:
            return ret