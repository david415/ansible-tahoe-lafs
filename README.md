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

Works on Debian wheezy and probably Ubuntu as well.


How to install the tahoe-lafs client locally?
---------------------------------------------

Firstly, make sure you are using ansible according to the best practices directory-layout specified here:

http://docs.ansible.com/playbooks_best_practices.html#directory-layout

Secondly, if you are running ansible from within a python virtualenv
then you will want to create that virtualenv like this:

```bash
# after extracting your gpg verified virtualenv tarball...
virtualenv-x.xx.x/virtualenv.py --system-site-packages ~/virtenv-ansible
```

That way when ansible builds tahoe-lafs on localhost it will be able to access
python dependencies outside of the virtualenv (installed via apt) that
it runs from.

Here's an example playbook to setup a tahoe client on the local host:

local_tahoe_client.yml
```yml
---
- hosts: 127.0.0.1
  connection: local
  roles:
    - { role: david415.ansible-tahoe-lafs,
        tahoe_git_url: "https://github.com/leif/tahoe-lafs",
        tahoe_git_branch: "truckee68",
	use_torsocks: yes,
        tahoe_introducer_furl: "pb://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@kkkkkkkkkkkkkkkk.onion:58086/introducer",
        tahoe_preferred_peers: ['meowwwwwwwwwwwwwwwwwwwwwwwwwwwww','mooooooooooooooooooooooooooooooo'],
        tahoe_tub_location: "client.fakelocation:1",
        tahoe_storage_enabled: "false",
        tahoe_web_port: "tcp:3456:interface=127.0.0.1",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        tahoe_nickname: "client",
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/human/ansible-tahoe/tahoe-lafs-src,
        tahoe_client_dir: /home/human/ansible-tahoe/tahoe_client,
        tahoe_client_config: "{{ tahoe_client_dir }}/tahoe.cfg"
      }
```

Run it like this:

```bash
ansible-playbook local_tahoe_client.yml
```




Example Playbook: tahoe-lafs oniongrid storage node!
----------------------------------------------------


```yml
---
- hosts: oniongrid-storage-nodes
  vars:
    oniongrid_node_name: "TahoeOnionNode"
    oniongrid_introducer_furl: "pb://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@kkkkkkkkkkkkkkkk.onion:9966/introducer"
    oniongrid_hidden_service_name: "tahoe-storage"
    oniongrid_tub_port: "43000"
    oniongrid_web_port: "3456"
    oniongrid_hidden_services_parent_dir: "/var/lib/tor/services"
    oniongrid_hidden_services: [
      { dir: "tahoe-web", ports: [{ virtport: "{{ oniongrid_web_port }}", target: "127.0.0.1:{{ oniongrid_web_port }}" }] },
      { dir: "tahoe-storage", ports: [{ virtport: "{{ oniongrid_tub_port }}", target: "127.0.0.1:{{ oniongrid_tub_port }}" }] },
    ]
  roles:
        # https://github.com/david415/ansible-tor
    - { role: david415.ansible-tor,
        tor_wait_for_hidden_services: yes,
        tor_distribution_release: "wheezy",
        tor_ExitPolicy: "reject *:*",
        tor_hidden_services: "{{ oniongrid_hidden_services }}",
        tor_hidden_services_parent_dir: "{{ oniongrid_hidden_services_parent_dir }}",
        sudo: yes
      }
    - { role: david415.ansible-tahoe-lafs,
        tahoe_introducer_furl: "{{ oniongrid_introducer_furl }}",
        tahoe_storage_enabled: "true",
        tahoe_hidden_service_name: "{{ oniongrid_hidden_service_name }}",
        tor_hidden_services_parent_dir: "{{ oniongrid_hidden_services_parent_dir }}",
        tahoe_web_port: "tcp:{{ oniongrid_web_port }}:interface=127.0.0.1",
        tahoe_tub_port: "tcp:{{ oniongrid_tub_port }}:interface=127.0.0.1",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        tahoe_nickname: "{{ oniongrid_node_name }}",
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/ansible/tahoe-lafs-src,
        tahoe_client_dir: /home/ansible/tahoe_client,
        tahoe_client_config: "{{ tahoe_client_dir }}/tahoe.cfg"
      }
```


License
-------

MIT



Feedback, feature requests and bugreports welcome!
--------------------------------------------------

https://github.com/david415/ansible-tahoe-lafs/


