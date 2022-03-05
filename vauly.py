#!/usr/bin/env python3

import argparse
import os
import pathlib
import subprocess
import sys
import yaml

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
VAULY_PLAYBOOK_FOLDER = os.getenv('VAULY_PLAYBOOK_FOLDER', SCRIPT_FOLDER)

ACTION_UNPACK = 'unpack'
ACTION_RESET = 'reset'
ACTIONS = [
    ACTION_UNPACK, ACTION_RESET
]

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
    git_repo_root = find_git_repository_root_folder(working_directory)
    arguments.extend(['-e', f'git_repository_root_folder={git_repo_root}'])
    arguments.extend(['-e', f'vault_file="{vault_file}"'])
    if unpacked_env_vars_file:
        arguments.extend(['-e', f'unpacked_vault_file="{unpacked_env_vars_file}"'])
    return arguments

def run_unpack_playbook(working_directory, unpacked_env_vars_file):
    playbook_path = os.path.join(VAULY_PLAYBOOK_FOLDER, 'vault-unpack.yml')
    vault_file = os.path.join(working_directory, 'vault.yml')
    arguments = get_unpack_playbook_arguments(working_directory, vault_file, unpacked_env_vars_file)

    if os.path.isfile(vault_file):
        # symlink ansible-playbook command and screw Ansible for not having a workingDir option
        tmp_playbook_path = os.path.join(working_directory, '.unpack-vault.yml')
        os.system(f'ln -s {playbook_path} {tmp_playbook_path}')

        result = subprocess.run(["ansible-playbook", tmp_playbook_path] + arguments, capture_output=True)
        if result.returncode:
            print('[ERROR] Failed to unpack vault:\n\n' + result.stdout.decode('utf-8'))

        os.remove(tmp_playbook_path)
    else:
        print(f'[ERROR] The vault file "{vault_file}" does not exist. Failed to load vault data!')

def find_git_repository_root_folder(working_directory):
    result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True)
    return result.stdout.decode('utf-8') if result.returncode == 0 else None

def unpack_vault(working_directory):
    run_unpack_playbook(working_directory, None)

def load_templated_files(vauly_file):
    with open(vauly_file, "r") as f:
        config = yaml.safe_load(f)
        return config['files'] if 'files' in config else []

def get_vauly_file_or_exit(working_directory):
    vauly_file = os.path.join(working_directory, 'vauly.yml')
    if not os.path.isfile(vauly_file):
        print(f'[ERROR] The vauly file "{vauly_file}" does not exist. Failed to load list of templated files!')
        sys.exit(1)
    return vauly_file

def load_existing_templated_files(working_directory):
    full_paths = [ os.path.join(working_directory, templated_file) for templated_file in load_templated_files(get_vauly_file_or_exit(working_directory))]
    return [ templated_file for templated_file in full_paths if os.path.isfile(templated_file) ]

def reset_folder(working_directory):
    for existing_templated_file in load_existing_templated_files(working_directory):
        os.remove(existing_templated_file)

def run(args):
    working_directory = pathlib.Path().resolve()
    if args.action == ACTION_UNPACK:
        unpack_vault(working_directory)
    if args.action == ACTION_RESET:
        reset_folder(working_directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Template sensitive files using an Ansible vault.')
    parser.add_argument('action', nargs='?', choices=ACTIONS, default=ACTION_UNPACK,
        help='action to be performed (unpack: template sensitive files, reset: remove templated files, init: ignore templated files in git)')

    run(parser.parse_args())
