# wcm_io_devops.conga_aem_dispatcher_smoke_test

This role runs smoke tests on AEM Dispatcher for Author and Publish
instances based upon a CONGA configuration.

The following tests are executed:
* Test of SSL enforcing (when configured)
* Response code check for Author and Publish

> This role was developed as part of the
> [wcm.io DevOps Ansible Automation for AEM](http://devops.wcm.io/ansible-aem/)
> to integrate Ansible with
> [CONGA](http://devops.wcm.io/conga/).

## Requirements

This role requires Ansible 2.7 or higher and works with AEM 6.0 or
higher.

## Role Variables

    conga_aemdst_publish_expected_http_code: 200

The expected http code of the publish dispatcher.

    conga_aemdst_publish_follow_redirects: true

Controls if the publish dispatcher test is following redirects.

    conga_aemdst_publish_lazy: true

Controls if there should be a strict match between expected url and
actual url.

    conga_aemdst_author_expected_http_code: 401

The expected http code of the author dispatcher.

    conga_aemdst_author_follow_redirects: true

Controls if the author dispatcher test is following redirects.

    conga_aemdst_author_lazy: true

Controls if there should be a strict match between expected and
actual url.

    conga_aemdst_ssl_enforce_lazy: false

Controls if there should be an exact match between expected and actual
url. Use together with `conga_aemdst_ssl_enforce_follow_redirects` because
following redirects may result in a lazy match.

    conga_aemdst_ssl_enforce_follow_redirects: false

Controls if the ssl enforce test should follow redirects. Use together
with `conga_aemdst_ssl_enforce_lazy` because following redirects may result in
a lazy match.

    conga_aemdst_response_test_expected_url_overrides: []
    # example:
    #  - pattern: http:\/\/company1\.tld\/
    #    expected_url: https://sso.company1.tld/

Allows overriding of expected urls by matching the `pattern` against the
automatic calculated expected url and overwriting it with the provided
`expected_url`.

    conga_aemdst_curl_expected_http_code: 301

Default response code of the curl task.

    conga_aemdst_curl_expected_url_test_lazy: false

Default test behavior of the curl task.

    conga_aemdst_curl_follow_redirects: false

Default follow redirect behavior of curl task.

    conga_aemdst_curl_follow_redirects_expected_http_code: 200

Default expected http code when redirects are followed.

    conga_aemdst_curl_allow_insecure: false

Allow or disallow insecure certificates.

    conga_aemdst_curl_noproxy: false

When set to true the curl command is executed with `--noproxy "*"`.

    conga_aemdst_curl_connect_timeout: 10

Maximum time allowed for the connection to the dispatcher in seconds.

    conga_aemdst_curl_timeout: 60

Maximum time allowed for the dispatcher smoke test operation in seconds.

    conga_aemdst_curl_host: "{{ inventory_hostname }}"

Host from which the smoke tests are executed. Per default this is the
ansible host.

    conga_aemdst_curl_resolve:
      - host: "{{ conga_aemdst_curl_url | urlsplit('hostname') }}"
        port: "80"
        address: "127.0.0.1"
      - host: "{{ conga_aemdst_curl_url | urlsplit('hostname') }}"
        port: "443"
        address: "127.0.0.1"

Allows to overwrite/control the host resolve mechanism of curl.

## Dependencies

This role depends on the
[wcm_io_devops.conga_facts](https://github.com/wcm-io-devops/ansible-conga-facts) role
for accessing the CONGA configuration model.

## Compiles the CONGA configuration and runs a smoke test for author and publish dispatcher from localhost

    - hosts: localhost
	  roles:
	    - wcm_io_devops.conga_maven
	
	# run smoke tests for aem publish dispatcher
	- hosts: localhost
      vars:
        - conga_node: webserver
        - conga_role_mapping: aem-dispatcher
        - conga_variant_mapping: aem-publish
    
      roles:
      - { role: wcm_io_devops.conga_aem_dispatcher_smoke_test }
    
    # run smoke tests for aem author dispatcher
    - hosts: localhost
      vars:
        - conga_node: webserver
        - conga_role_mapping: aem-dispatcher
        - conga_variant_mapping: aem-author
    
      roles:
        - { role: wcm_io_devops.conga_aem_dispatcher_smoke_test }
