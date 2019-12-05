#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import os
import re

from ansible.module_utils._text import to_native
from ansible.plugins.action import ActionBase
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

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        self._task_vars = task_vars

        try:
            # Get conga_facts based config (whole or tenant config)
            config = self._get_arg_or_var('conga_config')

        except AnsibleOptionsError as err:
            return self._fail_result(result, err.message)

        httpd_cfg = config.get("httpd", {})
        ssl_cfg = httpd_cfg.get("ssl", {})
        ssl_enforce = ssl_cfg.get("enforce", False)

        ssl_offloading_cfg = ssl_cfg.get("offloading", {})
        ssl_offloading_enabled = ssl_offloading_cfg.get("enabled", False)

        # set defaults
        server_listen_address = httpd_cfg.get("serverListenAddressSsl", "127.0.0.1")
        server_listen_address_ssl = httpd_cfg.get("serverListenAddressSsl", "127.0.0.1")

        server_name = httpd_cfg.get("serverName", None)
        server_name_ssl = httpd_cfg.get("serverNameSsl", None)

        listen_port = httpd_cfg.get("serverPort", 80)
        listen_port_ssl = httpd_cfg.get("serverPortSsl", 443)

        initial_port = listen_port
        expected_port = listen_port

        response_test_headers = []

        # when ssl is enforced and not offloaded we are expecting the ssl port
        if ssl_enforce and not ssl_offloading_enabled:
            expected_port = listen_port_ssl

        listen_port_suffix = "" if listen_port == 80 else ":{}".format(initial_port)
        listen_port_suffix_ssl = "" if listen_port_ssl == 443 else ":{}".format(expected_port)

        ssl_enforce_initial_url = "http://{}{}".format(server_name, listen_port_suffix)
        ssl_enforce_expected_url = "https://{}{}/".format(server_name_ssl, listen_port_suffix_ssl)

        response_test_initial_url = ssl_enforce_initial_url
        response_test_expected_url = response_test_initial_url + "/"

        if ssl_enforce:
            if ssl_offloading_enabled:
                # when ssl is offloaded we have to simulate a forwareded https request
                response_test_headers.append("X-Forwarded-Proto: https")
            else:
                # when ssl is not offloaded we are expecting an ssl upgrade
                response_test_expected_url = ssl_enforce_expected_url

        results = {
            # "config": config,
            "server_listen_address": server_listen_address,
            "server_listen_address_ssl": server_listen_address_ssl,
            "listen_port": listen_port,
            "listen_port_ssl": listen_port_ssl,
            "initial_port": initial_port,
            "expected_port": expected_port,
            "listen_port_suffix": listen_port_suffix,
            "listen_port_suffix_ssl": listen_port_suffix_ssl,
            "ssl_enforce_initial_url": ssl_enforce_initial_url,
            "ssl_enforce_expected_url": ssl_enforce_expected_url,
            "response_test_headers": response_test_headers,
            "response_test_initial_url": response_test_initial_url,
            "response_test_expected_url": response_test_expected_url
        }

        result["ansible_facts"] = {
            "conga_aemdst_config": results,
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
        if is_required and not ret:
            raise AnsibleOptionsError("parameter %s is required" % name)
        else:
            return ret
