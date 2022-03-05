# vauly

Ansible vaults are a secure way to define sensitive information in an accessible environment.
vauly is a wrapper for Ansible and provides a convenient interface to unpack a vault on a developer machine.

Using Ansible templating mechanism, vauly templates the sensitive information into any number of template files.
Optionally, vauly can have git ignore the templated files, to keep sensitive information from leaking into the git index.

## Usage

Suppose you have a Docker compose file that you are using to host a service.
One of the containers requires a password, typically passed as environment variable.
Instead of speciyfing the password in the compose file directly, you can have vauly template an environment file (`mongo-credentials.env`) for you.

    version: ...
    services:
      my_service:
        ...
        env_from:
          - mongo-credentials.env

Currently, this file is not even existing.
You would create a Jinja template (using the same filename but with a `.j2` suffix, here `mongo-credentials.env.j2`)

    MONGODB_INIT_ROOT_PASSWORD={{ mongodb.initial_root_password }}

and place an Ansible vault with the following content

    mongodb:
      initial_root_password: very-secret
    
    files:
      - mongo-credentials.env

in your project directory.

The `files` variable lists all files that should be templated by vauly.
When templating, Ansible can replace all variables that have been defined in the vault (here `mongodb.initial_root_password`).

Run vauly in your project directory to template all specified files:

    vauly

This process will create the missing `mongo-credentials.env` with the following content:

    MONGODB_INIT_ROOT_PASSWORD=very-secret

## Installation

The installation scripts copies the required files to a dedicated folder in your home directory and create a symlink for the wrapper script in your user binaries folder:

    ./install.sh

## TODO

* argparse for help
* add actions
  * unpack: default action that unpacks the vault
  * init: ignore templated files via .gitignore
  * reset: remove templated files, flag to even free the .gitignore from changes
* autocompletion
* installable via ppa/snap ?
