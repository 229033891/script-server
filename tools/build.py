#!/usr/bin/env python3

import json
import os
import shutil
import zipfile
import logging
from os.path import join

import init
from utils import file_utils
from utils.env_utils import EnvVariables
from utils.process_utils import ProcessInvoker

VERSION_FILE = 'version.txt'
BUILD_FOLDER = 'build'


class BuildInfo:
    def __init__(self):
        self.files = set()

    def include(self, path):
        matching_files = file_utils.search_glob(path, recursive=True)
        logging.info(f"Including files: {matching_files}")
        for file in matching_files:
            self.files.add(file)

    def exclude(self, path):
        matching_files = file_utils.search_glob(path, recursive=True)
        logging.info(f"Excluding files: {matching_files}")
        for excluded in matching_files:
            if excluded in self.files:
                self.files.remove(excluded)
            if os.path.isdir(excluded):
                files_to_remove = [file for file in self.files if os.path.commonprefix([excluded, file]) == excluded]
                for file_to_remove in files_to_remove:
                    self.files.remove(file_to_remove)

    def get_files(self):
        return self.files


def get_npm_version():
    package_json = json.loads(file_utils.read_file(join('web-src', 'package.json')))
    if 'version' in package_json:
        return parse_semver_str(package_json['version'])
    raise Exception('Failed to find version parameter in package.json')


def parse_semver_str(version_string):
    return [int(v) for v in version_string.split('.')]


def create_version_file():
    process_invoker = ProcessInvoker(EnvVariables(os.environ))

    current_branch = os.getenv('TRAVIS_BRANCH', process_invoker.invoke('git rev-parse --abbrev-ref HEAD').strip())

    npm_version = get_npm_version()
    if current_branch == 'stable':
        last_tag = process_invoker.invoke('git describe --exclude dev --abbrev=0 --tags').strip()
        last_tag_version = parse_semver_str(last_tag)
        if (last_tag_version[0] == npm_version[0]) and (last_tag_version[1] == npm_version[1]):
            new_version = [last_tag_version[0], last_tag_version[1], last_tag_version[2] + 1]
        else:
            new_version = npm_version
        new_version = '.'.join([str(v) for v in new_version])
    else:
        git_hash = process_invoker.invoke('git rev-parse --short HEAD').strip()
        new_version = f"{npm_version[0]}.{npm_version[1] + 1}.0-{current_branch}@{git_hash}"
    
    file_utils.write_file(VERSION_FILE, new_version)
    logging.info(f"Version file created with version: {new_version}")


def prepare_build_folder():
    if os.path.exists(BUILD_FOLDER):
        shutil.rmtree(BUILD_FOLDER)
    os.mkdir(BUILD_FOLDER)
    logging.info(f"Build folder {BUILD_FOLDER} prepared.")


def main():
    logging.basicConfig(level=logging.INFO)
    try:
        prepare_build_folder()
        init.prepare_project('')
        create_version_file()

        build_info = BuildInfo()
        build_info.include('launcher.py')
        build_info.include('requirements.txt')
        build_info.include(VERSION_FILE)
        build_info.include(os.path.join('src', '**', '*.py'))
        build_info.include(os.path.join('conf', 'logging.json'))
        build_info.include(os.path.join('web', '**'))
        build_info.include(os.path.join('conf', 'runners'))
        build_info.exclude(os.path.join('src', 'tests'))
        build_info.exclude(os.path.join('src', 'e2e_tests'))
        build_info.exclude('tools')
        build_info.exclude('samples')
        build_info.exclude(BUILD_FOLDER)

        with zipfile.ZipFile(os.path.join(BUILD_FOLDER, 'script-server.zip'), 'w', zipfile.ZIP_DEFLATED) as zip:
            for file in build_info.get_files():
                zip.write(file)
                logging.info(f"File added to zip: {file}")

        os.remove(VERSION_FILE)
        logging.info("Version file removed after zipping.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
