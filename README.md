# conga-aem-dispatcher-smoke-test

This role runs smoke tests on AEM Dispatcher for Author and Publish
instances based upon a CONGA configuration.

The following tests are executed:
* Test of SSL enforcing (when configured)
* Response code check for Author and Publish

## Requirements

This role requires Ansible 2.0 or higher and works with AEM 6.0 or
higher.

## Role Variables

    aemdst_publish_expected_http_code: 200

The expected http code of the publish dispatcher.

    aemdst_publish_follow_redirects: true

Controls if the publish dispatcher test is following redirects.

    aemdst_publish_lazy: true

Controls if there should be a strict match between expected url and
actual url.

    aemdst_author_expected_http_code: 401

The expected http code of the author dispatcher.

    aemdst_author_follow_redirects: true

Controls if the author dispatcher test is following redirects.

    aemdst_author_lazy: true

Controls if there should be a strict match between expected and
actual url.

    aemdst_ssl_enforce_lazy: false

Controls if there should be an exact match between expected and actual
url. Use together with `aemdst_ssl_enforce_follow_redirects` because
following redirects may result in a lazy match.

    aemdst_ssl_enforce_follow_redirects: false

Controls if the ssl enforce test should follow redirects. Use together
with `aemdst_ssl_enforce_lazy` because following redirects may result in
a lazy match.

## Dependencies

This role depends on the
[conga-facts](https://github.com/wcm-io-devops/ansible-conga-facts) role
for accessing the CONGA configuration model.

## Compiles the CONGA configuration and runs a smoke test for author and publish dispatcher from localhost

    - hosts: localhost
	  roles:
	    - conga-maven
	
	# run smoke tests for aem publish dispatcher
	- hosts: localhost
      vars:
        - conga_node: webserver
        - conga_role_mapping: aem-dispatcher
        - conga_variant_mapping: aem-publish
    
      roles:
      - { role: conga-aem-dispatcher-smoke-test }
    
    # run smoke tests for aem author dispatcher
    - hosts: localhost
      vars:
        - conga_node: webserver
        - conga_role_mapping: aem-dispatcher
        - conga_variant_mapping: aem-author
    
      roles:
        - { role: conga-aem-dispatcher-smoke-test }
