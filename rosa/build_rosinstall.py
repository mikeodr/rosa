#!/usr/bin/env python

from __future__ import print_function

import sys
import os
import re
import argparse
import git
import yaml

from os import path
from workspace import find_workspace

def create_repo_list(folder):
    items = [i for i in os.listdir(folder) if path.isdir(path.join(folder, i))]
    data_list = []

    for item in items:
        info = {}
        try:
            repo = git.Repo(path.join(folder, item))
        except git.InvalidGitRepositoryError:
            continue

        info['local-name'] = item
        
        try:
            info['version'] = repo.active_branch
        except git.GitCommandError:
            sha = repo.commit('HEAD').id
            info['version'] = sha

            for tag in repo.tags:
                if tag.commit.id == sha:
                    info['version'] = tag.name
                    break

        remotes = repo.git.execute(['git', 'remote', '-v']).split('\n')
        for r in remotes:
            r = re.split('\s', r)
            if r[0] == 'origin':
                info['uri'] = r[1]
        
        data_list.append({'git': info})

    return data_list

def build_rosinstall(args):
    if args.workspace:
        workspace = args.workspace
    else:
        workspace = find_workspace('.')
        if not workspace:
            sys.stderr.write('Please run the command in a workspace or specify one with -w\n')
            return

    repos = create_repo_list(path.join(workspace, 'src'))
    rosinstall = yaml.dump(repos)
    if args.output_file is not None:
        with file(args.output_file, 'w') as f:
            f.write(rosinstall)
    else:
        sys.stdout.write(rosinstall)


def add_parser(parent_subparsers):
    parser = parent_subparsers.add_parser('build_rosinstall', 
            description='Create a rosinstall from the repositories in a workspace')
    parser.add_argument('-o', '--output-file', metavar='FILE', type=str,
            help='write rosinstall to file instead of stdout')
    parser.set_defaults(func=build_rosinstall)