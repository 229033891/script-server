#!/usr/bin/env python3
import argparse
import os
import sys
import logging
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile

sys.path.insert(1, os.path.join(sys.path[0], '..', 'src'))

from utils.env_utils import EnvVariables
from utils.process_utils import ProcessInvoker

DOWNLOAD_URL = 'https://github.com/bugy/script-server/releases/download/dev/script-server.zip'

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_web_files(project_path, url=DOWNLOAD_URL):
    logging.info('Downloading web files...')
    try:
        response = urlopen(url)
        with ZipFile(BytesIO(response.read())) as zipfile:
            for file in zipfile.namelist():
                if file.startswith('web/'):
                    zipfile.extract(file, project_path)
        logging.info('Web files downloaded and extracted.')
    except Exception as e:
        logging.error(f'Failed to download web files: {e}')
        raise

def build_web_files(project_path):
    process_invoker = ProcessInvoker(EnvVariables(os.environ))
    logging.info('Building web...')
    try:
        work_dir = os.path.join(project_path, 'web-src')
        process_invoker.invoke('npm install', work_dir)
        process_invoker.invoke('npm run build', work_dir)
        logging.info('Web build completed.')
    except Exception as e:
        logging.error(f'Failed to build web files: {e}')
        raise

def prepare_project(project_path, download_web=False):
    if download_web:
        download_web_files(project_path)
    else:
        build_web_files(project_path)

    runners_conf = os.path.join(project_path, 'conf', 'runners')
    if not os.path.exists(runners_conf):
        os.makedirs(runners_conf)
        logging.info(f'Created runners configuration directory at {runners_conf}')

def main():
    setup_logging()
    script_folder = sys.path[0]
    project_path = os.path.abspath(os.path.join(script_folder, '..')) if script_folder else ''
    
    parser = argparse.ArgumentParser(description='Initializes source code repo to make it runnable')
    parser.add_argument('--no-npm', action='store_true', default=False, help='Download web files instead of building with npm')
    args = vars(parser.parse_args())

    try:
        prepare_project(project_path, download_web=args['no_npm'])
    except Exception as e:
        logging.error(f'Failed to prepare project: {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()
