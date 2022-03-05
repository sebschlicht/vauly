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

Now simply call vauly in your project directory to have it template the missing file, containing the sensitive information:

    vauly

## Installation

You may just create a symlink in your user's binaries folder to the checked out vauly script:

    ln -s "$( pwd )/vauly.py" ~/bin/vauly

## TODO

* argparse for help
* add actions
  * unpack: default action that unpacks the vault
  * init: ignore templated files via .gitignore
  * reset: remove templated files, flag to even free the .gitignore from changes
* autocompletion
* installation instructions
* installable via ppa/snap ?
