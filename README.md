ansible-tahoe-lafs
==================

This is an ansible role for use with Tahoe-lafs - Least Authoratative Filesystem
https://tahoe-lafs.org/trac/tahoe-lafs



Role Variables
--------------

The current implementation is no longer tor/oniongrid specific.
If you can choose to specify the tahoe endpoint using the role
variable "tahoe_tub_location". If "tahoe_tub_location" was not
specified then you must define the role variables "tor_hidden_services" and
"tor_hidden_services_parent_dir" so that the tor hidden service onion
address for the tahoe service (storage or introducer) can be retrieved
and used to templatize the tahoe.cfg configuration file.

Additionally you must specify "use_torsocks: no" in order to not
use torsocks/tor to install and run tahoe. However in the future when
tahoe-lafs uses twisted endpoints there will no longer be any need
for torsocks:

 * https://tahoe-lafs.org/trac/tahoe-lafs/ticket/517
 * http://foolscap.lothar.com/trac/ticket/203



Dependencies
------------

Works on Debian wheezy and probably Ubuntu as well.


Install an entire tahoe grid over tor hidden services
-----------------------------------------------------

This play book will install/configure tahoe-lafs introducer(s),
storage nodes and a local client using torsocks (usewithtor) and tor
hidden services. Actually the tor components are optional but I have
not test much without them.

One noteable design decision/feature is that after the introducer node
is create we save it's furl to a local file named after the
machine... and then later plays such as the tahoe-lafs storage or client node
play can access this directory and read all the introducer furls. For
the moment the first introducer furl is picked but soon we plan on
supporting multiple introducers (see tahoe-lafs repo branch truckee68
regarding mutliple introducers).


```yml
---
- hosts: oniongrid-introducer-nodes
  vars:
    node_name: "IntroducerNode"
    hidden_service_name: "tahoe-introducer"
    tub_port: "33000"
    web_port: "3456"
    hidden_services_parent_dir: "/var/lib/tor/services"
    hidden_services: [
      { dir: "tahoe-web", ports: [{ virtport: "{{ web_port }}", target: "127.0.0.1:{{ web_port }}" }] },
      { dir: "tahoe-introducer", ports: [{ virtport: "{{ tub_port }}", target: "127.0.0.1:{{ tub_port }}" }] },
    ]
  roles:
    - { role: david415.ansible-tor,
        tor_wait_for_hidden_services: yes,
        tor_distribution_release: "wheezy",
        tor_ExitPolicy: "reject *:*",
        tor_hidden_services: "{{ hidden_services }}",
        tor_hidden_services_parent_dir: "{{ hidden_services_parent_dir }}",
        sudo: yes
      }
    - { role: david415.ansible-tahoe-lafs,
        tahoe_introducer: yes,
        tahoe_local_introducers_dir: "/home/human/projects/ansible-project/tahoe-lafs_introducers",
        use_torsocks: yes,
        tahoe_hidden_service_name: "{{ hidden_service_name }}",
        tor_hidden_services_parent_dir: "{{ hidden_services_parent_dir }}",
        tahoe_introducer_port: "{{ tub_port }}",
        tahoe_web_port: "{{ web_port }}",
        tahoe_tub_port: "{{ tub_port }}",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        tahoe_nickname: "{{ node_name }}",
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/ansible/tahoe-lafs-src,
        tahoe_run_dir: /home/ansible/tahoe_introducer
      }
- hosts: oniongrid-storage-nodes
  vars:
    node_name: "storage"
    hidden_service_name: "tahoe-storage"
    tub_port: "47320"
    web_port: "4456"
    hidden_services_parent_dir: "/var/lib/tor/services"
    hidden_services: [
      { dir: "tahoe-web", ports: [{ virtport: "{{ web_port }}", target: "127.0.0.1:{{ web_port }}" }] },
      { dir: "tahoe-storage", ports: [{ virtport: "{{ tub_port }}", target: "127.0.0.1:{{ tub_port }}" }] },
    ]
  roles:
    - { role: david415.ansible-tor,
        tor_wait_for_hidden_services: yes,
        tor_distribution_release: "wheezy",
        tor_ExitPolicy: "reject *:*",
        tor_hidden_services: "{{ hidden_services }}",
        tor_hidden_services_parent_dir: "{{ hidden_services_parent_dir }}",
        sudo: yes
      }
    - { role: david415.ansible-tahoe-lafs,
        tahoe_storage_enabled: "true",
        tahoe_local_introducers_dir: "/home/human/projects/ansible-project/tahoe-lafs_introducers",
        tahoe_hidden_service_name: "{{ hidden_service_name }}",
        tor_hidden_services_parent_dir: "{{ hidden_services_parent_dir }}",
        tahoe_web_port: "{{ web_port }}",
        tahoe_tub_port: "{{ tub_port }}",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        tahoe_nickname: "{{ node_name }}",
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/ansible/tahoe-lafs-src,
        tahoe_run_dir: /home/ansible/tahoe_storage321
      }
- hosts: 127.0.0.1
  connection: local
  roles:
    - { role: david415.ansible-tahoe-lafs,
        tahoe_git_url: "https://github.com/leif/tahoe-lafs",
        tahoe_git_branch: "truckee68",
        tahoe_local_introducers_dir: "/home/human/projects/ansible-project/tahoe-lafs_introducers",
        tahoe_tub_location: "client.fakelocation:1",
        tahoe_storage_enabled: "false",
        tahoe_web_port: "3456",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        tahoe_nickname: "client",
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/human/ansible-tahoe/tahoe-lafs-src,
        tahoe_run_dir: /home/human/ansible-tahoe/tahoe_test_client,
      }
```


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
        tahoe_client: yes,
        tahoe_git_url: "https://github.com/leif/tahoe-lafs",
        tahoe_git_branch: "truckee68",
        tahoe_introducer_furl:
	"pb://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@kkkkkkkkkkkkkkkk.onion:58086/swissnum",
        tahoe_preferred_peers: ['meowwwwwwwwwwwwwwwwwwwwwwwwwwwww','mooooooooooooooooooooooooooooooo'],
        tahoe_tub_location: "client.fakelocation:1",
        tahoe_storage_enabled: "false",
        tahoe_web_port: "3456",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        tahoe_nickname: "client",
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/human/ansible-tahoe/tahoe-lafs-src,
        tahoe_run_dir: /home/human/ansible-tahoe/tahoe_client
      }
```

Run it like this:

```bash
ansible-playbook local_tahoe_client.yml
```


Example tahoe-lafs introducer node playbook
-------------------------------------------

Run a tahoe-lafs introducer node listening to a tor hidden service port:

```yml
---
- hosts: oniongrid-introducer-nodes
  vars:
    node_name: "IntroducerNode"
    hidden_service_name: "tahoe-introducer"
    tub_port: "13000"
    web_port: "1456"
    hidden_services_parent_dir: "/var/lib/tor/services"
    hidden_services: [
      { dir: "tahoe-web", ports: [{ virtport: "{{ web_port }}", target: "127.0.0.1:{{ web_port }}" }] },
      { dir: "{{ hidden_service_name }}", ports: [{ virtport: "{{ tub_port }}", target: "127.0.0.1:{{ tub_port }}" }] },
    ]
  roles:
    - { role: david415.ansible-tor,
        tor_wait_for_hidden_services: yes,
        tor_distribution_release: "wheezy",
        tor_ExitPolicy: "reject *:*",
        tor_hidden_services: "{{ hidden_services }}",
        tor_hidden_services_parent_dir: "{{ hidden_services_parent_dir }}",
        sudo: yes
      }
    - { role: david415.ansible-tahoe-lafs,
        tahoe_introducer: yes,
        use_torsocks: yes,
        tahoe_hidden_service_name: "{{ hidden_service_name }}",
        tor_hidden_services_parent_dir: "{{ hidden_services_parent_dir }}",
        tahoe_introducer_port: "{{ tub_port }}",
        tahoe_local_introducers_dir: "/home/human/projects/ansible-project/tahoe-lafs_introducers",
        tahoe_web_port: "{{ web_port }}",
        tahoe_tub_port: "{{ tub_port }}",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        tahoe_nickname: "{{ node_name }}",
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/ansible/tahoe-lafs-src,
        tahoe_run_dir: /home/ansible/tahoe_introducer
      }
```



Example tahoe-lafs over tor ("oniongrid") storage node
------------------------------------------------------


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
        tahoe_web_port: "{{ oniongrid_web_port }}",
        tahoe_tub_port: "{{ oniongrid_tub_port }}",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        tahoe_nickname: "{{ oniongrid_node_name }}",
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/ansible/tahoe-lafs-src,
        tahoe_run_dir: /home/ansible/tahoe_storage123,
      }
```


License
-------

MIT



Feedback, feature requests and bugreports welcome!
--------------------------------------------------

https://github.com/david415/ansible-tahoe-lafs/
