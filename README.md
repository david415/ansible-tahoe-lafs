ansible-tahoe-lafs
==================

This is an ansible role for use with Tahoe-lafs - Least Authoratative Filesystem
https://tahoe-lafs.org/trac/tahoe-lafs

The current implementation is tor/oniongrid specific.
Specifically we identify all tahoe nodes (storage,
introducer etc) with tor hidden service addresses; onion addresses!


Role Variables
--------------

more documentation coming soon! >_<


Dependencies
------------

Currently this role requires my ansible-tor role (https://github.com/david415/ansible-tor) and torsocks.


Example Playbook: tahoe-lafs oniongrid!
---------------------------------------


```yml
---
- hosts: oniongrid-storage-nodes
  vars:
    oniongrid_node_name: "TahoeOnionNode"
    oniongrid_introducer_furl: "pb://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@kkkkkkkkkkkkkkkk.onion:9966/introducer"
    oniongrid_hidden_service_name: "tahoe-storage"
    oniongrid_tub_port: 43000
    oniongrid_web_port: 3456
    oniongrid_hidden_services_parent_dir: "/var/lib/tor/services"
    oniongrid_hidden_services: [
      { dir: "tahoe-web", ports: [{ virtport: "{{ oniongrid_web_port }}", target: "127.0.0.1:{{ oniongrid_web_port }}" }] },
      { dir: "tahoe-storage", ports: [{ virtport: "{{ oniongrid_tub_port }}", target: "127.0.0.1:{{ oniongrid_tub_port }}" }] },
    ]
  roles:
    - { role: david415.ansible-tor,
        tor_wait_for_hidden_services: yes,
        tor_distribution_release: "wheezy",
        tor_ExitPolicy: "reject *:*",
        tor_hidden_services: "{{ oniongrid_hidden_services }}",
        tor_hidden_services_parent_dir: "{{ oniongrid_hidden_services_parent_dir }}",
        sudo: yes
      }
    - { role: david415.ansible-tahoe-lafs,
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/ansible/tahoe-lafs-src,
        tahoe_client_dir: /home/ansible/tahoe_client,
        tahoe_client_config: "{{ tahoe_client_dir }}/tahoe.cfg",
        tahoe_web_port: "{{ oniongrid_web_port }}",
        tahoe_introducer_furl: "{{ oniongrid_introducer_furl }}",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        tahoe_nickname: "{{ oniongrid_node_name }}",
        tahoe_tub_port: "{{ oniongrid_tub_port }}",
        tahoe_storage_enabled: "true",
        tahoe_hidden_service_name: "{{ oniongrid_hidden_service_name }}",
        tor_hidden_services_parent_dir: "{{ oniongrid_hidden_services_parent_dir }}"
      }
```


License
-------

MIT



Feedback, feature requests and bugreports welcome!
--------------------------------------------------

https://github.com/david415/ansible-tahoe-lafs/


