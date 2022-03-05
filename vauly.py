#!/usr/bin/env python3

import os
import pathlib
import subprocess

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
ANSIBLE_PLAYBOOK_FOLDER = os.getenv('VAULY_PLAYBOOK_FOLDER', SCRIPT_FOLDER)

def get_ansible_playbook_arguments(working_directory):
    arguments = []
    # use vault password file or ask
    ansible_password_file_path = os.path.join(working_directory, '.vault_password')
    if os.path.isfile(ansible_password_file_path):
        arguments.append(f'--vault-password-file={ansible_password_file_path}')
    else:
        arguments.append(f'--ask-vault-pass')
    return arguments

def get_unpack_playbook_arguments(working_directory, vault_file, unpacked_env_vars_file):
    arguments = get_ansible_playbook_arguments(working_directory)
    # playbook-specific extra arguments
    if vault_file:
        arguments.extend(['-e', f'vault_file="{vault_file}"'])
    if unpacked_env_vars_file:
        arguments.extend(['-e', f'unpacked_vault_file="{unpacked_env_vars_file}"'])
    return arguments

def run_unpack_playbook(working_directory, unpacked_env_vars_file):
    playbook_path = os.path.join(ANSIBLE_PLAYBOOK_FOLDER, 'vault-unpack.yml')
    vault_file = os.path.join(working_directory, 'vault.yml')
    arguments = get_unpack_playbook_arguments(working_directory, vault_file, unpacked_env_vars_file)

    # symlink ansible-playbook command and screw Ansible for not having a workingDir option
    tmp_playbook_path = os.path.join(working_directory, '.unpack-vault.yml')
    os.system(f'ln -s {playbook_path} {tmp_playbook_path}')

    result = subprocess.run(["ansible-playbook", tmp_playbook_path] + arguments, capture_output=True)
    if result.returncode:
        print('[ERROR] Failed to unpack vault:\n\n' + result.stderr.decode('utf-8'))

    os.remove(tmp_playbook_path)

def unpack_vault(working_directory):
    run_unpack_playbook(working_directory, None)


if __name__ == "__main__":
    working_directory = pathlib.Path().resolve()
    unpack_vault(working_directory)
