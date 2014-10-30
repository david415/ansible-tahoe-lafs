ansible-tahoe-lafs
==================

Use this Ansible role with Tahoe-lafs - Least Authoratative Filesystem
https://tahoe-lafs.org/trac/tahoe-lafs

This ansible role can help you reduce the complexity to a single
command for deploying one or more Tahoe-LAFS storage servers,
introducers and clients.


Disclaimer
----------

There are probably bugs. This Ansible role is designed to be used with
Tor and Tahoe-LAFS. It is possible it could also be used to configure
Tahoe-LAFS grids without Tor... however this isn't how I use
Tahoe-LAFS, so I only tested it with Tor (torsocks + Tor Hidden Services).


A word about Ansible
--------------------

Make sure you are using ansible according to the best practices
directory-layout specified here:

http://docs.ansible.com/playbooks_best_practices.html#directory-layout

This Ansible role belongs in your "roles" directory.


Tor integration
---------------

Why would anyone want to run Tahoe-LAFS over Tor?

Tor augments the security guarantees of Tahoe-LAFS in a good way.
File storage infrastructure that can be hosted and accessed anonymously with
verified end to end crypto and data redundancy could be very useful
for a wide range of projects. In particular, this has a lot of
potential to aid censorship resistance of sensitive documents for
instance. Many important tools could be built using this Tor +
Tahoe-LAFS integration... and those tools may prove to be extremely
valuable in helping to protect against violations of freespeech and
human rights.


What is an onion grid?

An onion grid is a Tahoe-LAFS grid which is only accessible through
the Tor network because the introducer and storage nodes only listen for
connections on Tor Hidden Servies. This means that both the storage
servers and the clients will be anonymous. It also means the
introducer FURL will contain a Tor onion address. Currently it is
recommended that Leif Ryge's "truckee68" branch be used for this
purpose; it is especially important for Tahoe clients to set their
"tub location", otherwise their IP address could be leaked. Like this:

```
tahoe_tub_location: "client.fakelocation:1"
```

I am currently working on native Tor integration for
Tahoe-LAFS which will have many advantages over the current Tor
integration system which uses torsocks. I do not currently have a
time-estimate of when I will be done :

```
 * https://tahoe-lafs.org/trac/tahoe-lafs/ticket/517
 * http://foolscap.lothar.com/trac/ticket/203
```


How does this Ansible role configure Tor?

If you look at the example playbooks below you'll see that they all
use my "ansible-tor" role; here's the github url for that:

https://github.com/david415/ansible-tor

In the future, when the native Tor integration for Tahoe-LAFS is
complete then it may become unnecessary to use the ansible-tor role
with Tahoe-LAFS.


Role Variables
--------------

"tahoe_nickname" is a hostvar... meaning that you can set this variable
in your host inventory file or in a host group variable file.
For example your inventory file could have an entry that looks like
this:

192.168.1.123 tahoe_nickname=AnsibleTahoeStorage77


If the "tahoe_tub_location" role variable was not specified then you
must define the role variables "tor_hidden_services" and 
"tor_hidden_services_parent_dir" so that the tor hidden service onion
address for the tahoe service (storage or introducer) can be retrieved
and used to templatize the tahoe.cfg configuration file.


Dependencies
------------

Works on Debian wheezy and Ubuntu.


Example tahoe-lafs over tor ("oniongrid") storage node
------------------------------------------------------


```yml
---
- hosts: onion-storage
  connection: ssh
  vars:
    oniongrid_introducer_furl: "pb://aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@kkkkkkkkkkkkkkkk.onion:9966/introducer"
    oniongrid_hidden_service_name: "tahoe-storage"
    oniongrid_tub_port: "34000"
    oniongrid_web_port: "3456"
    oniongrid_hidden_services_parent_dir: "/var/lib/tor/services"
    oniongrid_hidden_services: [
      { dir: "lafs-rpg", ports: [{ virtport: "80", target: "127.0.0.1:7766" }] },
      { dir: "tahoe-web", ports: [{ virtport: "{{ oniongrid_web_port }}", target: "127.0.0.1:{{ oniongrid_web_port }}" }] },
      { dir: "tahoe-storage", ports: [{ virtport: "{{ oniongrid_tub_port }}", target: "127.0.0.1:{{ oniongrid_tub_port }}" }] },
    ]
  roles:
# XXX configure openssh customized configuration?
#    - { role: ansible-openssh-hardened,
#        backports_url: "http://ftp.de.debian.org/debian/",
#        backports_distribution_release: "wheezy-backports",
#        ssh_admin_ed25519pubkey_path: "/home/amnesia/.ssh/id_ed25519.pub",
#        sudo: yes
#      }
    - { role: ansible-tor,
        tor_wait_for_hidden_services: yes,
        tor_distribution_release: "wheezy",
        tor_ExitPolicy: "reject *:*",
        tor_hidden_services: "{{ oniongrid_hidden_services }}",
        tor_hidden_services_parent_dir: "{{ oniongrid_hidden_services_parent_dir }}",
        sudo: yes
      }
    - { role: ansible-tahoe-lafs,
        tahoe_introducer_furl: "{{ oniongrid_introducer_furl }}",
        tahoe_storage_enabled: "true",
        tahoe_hidden_service_name: "{{ oniongrid_hidden_service_name }}",
        tor_hidden_services_parent_dir: "{{ oniongrid_hidden_services_parent_dir }}",
        tahoe_web_port: "{{ oniongrid_web_port }}",
        tahoe_tub_port: "{{ oniongrid_tub_port }}",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/human/tahoe-lafs-src,
        tahoe_run_dir: /home/human/tahoe_client
      }
```


Install a onion storage node and introducer node on one machine
---------------------------------------------------------------

If you want to setup an new onion grid with some friends then it might
make sense for you to start off by running this playbook. It'll configure
a single machine to run two instances of Tahoe-LAFS: one for an introducer
and one for a storage node.

It will generate an introducer FURL... and store it locally in a file...
and you can distribute this introducer FURL to your friends so that they
can configure their storage servers to join the onion grid.

You'll probably have to change the tahoe_local_introducers_dir, tahoe_source_dir and tahoe_run_dir variables in this playbook to match how you'd like to store your data. As you can see from the way I've specified tahoe_local_introducers_dir I'm obviously running Ansible from a Tails workstation... and the way I've set tahoe_server_dir and tahoe_run_dir indicates that I've got a user on that remote system called "human"... and I'm storing the tahoe directories in human's home directory.

```yml
---
- hosts: onion-introducer-storage
  vars:
    hidden_services_parent_dir: "/var/lib/tor/services"
    introducer_node_name: "IntroducerNode"
    introducer_tub_port: "33000"
    introducer_web_port: "33001"
    storage_service_name: "storage"
    storage_tub_port: "34000"
    storage_web_port: "34001"
    hidden_services: [
      { dir: "intro-web", ports: [{ virtport: "{{ introducer_web_port }}", target: "127.0.0.1:{{ introducer_web_port }}" }] },
      { dir: "introducer", ports: [{ virtport: "{{ introducer_tub_port }}", target: "127.0.0.1:{{ introducer_tub_port }}" }] },
      { dir: "storage-web", ports: [{ virtport: "{{ storage_web_port }}", target: "127.0.0.1:{{ storage_web_port }}" }] },
      { dir: "storage", ports: [{ virtport: "{{ storage_tub_port }}", target: "127.0.0.1:{{ storage_tub_port }}" }] },
    ]
  roles:
    - { role: ansible-tor,
        tor_wait_for_hidden_services: yes,
        tor_distribution_release: "wheezy",
        tor_ExitPolicy: "reject *:*",
        tor_hidden_services: "{{ hidden_services }}",
        tor_hidden_services_parent_dir: "{{ hidden_services_parent_dir }}",
        sudo: yes
      }
    - { role: ansible-tahoe-lafs,
        tahoe_introducer: yes,
        tahoe_local_introducers_dir: "/home/amnesia/Persistent/projects/ansible-base/tahoe-lafs_introducers",
        use_torsocks: yes,
        tahoe_hidden_service_name: "introducer",
        tor_hidden_services_parent_dir: "{{ hidden_services_parent_dir }}",
        tahoe_introducer_port: "{{ introducer_tub_port }}",
        tahoe_web_port: "{{ introducer_web_port }}",
        tahoe_tub_port: "{{ introducer_tub_port }}",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: "/home/human/tahoe-lafs-src",
        tahoe_run_dir: "/home/human/tahoe_introducer"
      }
    - { role: ansible-tahoe-lafs,
        tahoe_local_introducers_dir: "/home/amnesia/Persistent/projects/ansible-base/tahoe-lafs_introducers",
        tahoe_storage_enabled: "true",
        tahoe_hidden_service_name: "storage",
        tor_hidden_services_parent_dir: "{{ hidden_services_parent_dir }}",
        tahoe_web_port: "{{ storage_web_port }}",
        tahoe_tub_port: "{{ storage_tub_port }}",
        tahoe_shares_needed: 2,
        tahoe_shares_happy: 3,
        tahoe_shares_total: 4,
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: "/home/human/tahoe-lafs-src",
        tahoe_run_dir: "/home/human/tahoe_storage"
      }
```

Install an entire Tahoe-LAFS onion grid
---------------------------------------


One noteable feature when configuring Tahoe-LAFS introducers, is that
after the introducer node is created, we save it's FURL to a local
file located in the parent directory of your choosing.

After the introducer node is created... the other Ansible "plays" that need the
introducer FURLs get it from this local introducer FURL list. For the moment only
the first introducer furl is used... but soon we plan on supporting
multiple introducers (see tahoe-lafs repo branch truckee68 regarding
mutliple introducers).


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
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/human/ansible-tahoe/tahoe-lafs-src,
        tahoe_run_dir: /home/human/ansible-tahoe/tahoe_test_client,
      }
```


How to install the tahoe-lafs client locally?
---------------------------------------------

If you are running ansible from within a python virtualenv
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
        backports_url: "http://ftp.de.debian.org/debian/",
        backports_distribution_release: "wheezy-backports",
        tahoe_source_dir: /home/ansible/tahoe-lafs-src,
        tahoe_run_dir: /home/ansible/tahoe_introducer
      }
```


License
-------

MIT



Feedback, feature requests and bugreports welcome!
--------------------------------------------------

https://github.com/david415/ansible-tahoe-lafs/
