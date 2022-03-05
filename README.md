# vauly

Ansible vaults are a secure way to define sensitive information in an accessible environment.
vauly is a wrapper for Ansible and provides a convenient interface to unpack a vault on a developer machine.

Using Ansible templating mechanism, vauly templates the sensitive information into any number of template files.
Optionally, vauly can have git ignore the templated files, to keep sensitive information from leaking into the git index.

## Getting Started

To get familiar with the usage of vauly:

1. [install](#installation) vauly
2. read through the [example](#example)
3. check `vauly --help`

## Example

>Note: The files of this example can be found in the `example` folder of this repository.

Suppose you have a Docker compose file that you are using to host a service.
One of the containers requires a password, typically passed as environment variable.
Without vauly, you might have the compose file

    ...
    my_service:
      ...
      env_from:
        - mongo-credentials.env

point to an environment file, containing the password in plain:

    MONGO_INITDB_ROOT_PASSWORD=not-so-secret

This environment file can not be checked into a code versioning system without leaking your password (or a placeholder of the real password, that you have to alter manually later on).

Instead of speciyfing the password in the file directly, let vauly template the sensitive information into the file for you.  
The idea is to create a vault and specify which files you want vauly to template for you, using the sensitive information from your vault.

At first, create the vault `vault.yml` in your project folder via

    ansible-vault create vault.yml

and securely store the password inside:

    mongodb:
        initial_root_password: very-secret

Create the file `vauly.yml` in your project folder, to tell vauly which files you want to be templated:

    files:
      - mongo-credentials.env

Later on, vauly will try to read the file `mongo-credentials.env.j2` to template the specified file.
Thus, we create such a file and use the well-known Jinja syntax for templating the sensitive information:

    ...
    my_service:
      ...
      env:
        MONGODB_INIT_ROOT_PASSWORD: {{ mongodb.initial_root_password }}

Run vauly in your project directory to template the specified file:

    vauly unpack

This step will create the file `mongo-credentials.env`, containing the sensitive information from your vault.
You can now proceed to add any number of files and have them templated by vauly.

If vauly detects that you are using git for your project, templated files will automatically be added to the `.gitignore` file to help you secure your sensitive information.

## Installation

The installation scripts copies the required files to a dedicated folder in your home directory and create a symlink for the wrapper script in your user binaries folder:

    ./install.sh

## TODO

* have `.gitignore` created/updated on each unpack, if inside a git project
* autocompletion
* installable via ppa/snap ?
