﻿#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Code Collaborator git svn client """

import datetime
import hashlib
import os
import re
import sys
import xmlrpclib


cc_url = ''
cc_supported_version = 810
cc_guid = ''

svn_login = ''
svn_pwd = ''
svn_root = ''
svn_prefix = ''
svn_uuid = ''
svn_url = ''
local_guid = ''


def init_cc_vars():
    cc_cfg_file = open(
        os.path.expanduser('~/.smartbear/com.smartbear.ccollab.client.txt')
    )
    lines = cc_cfg_file.readlines()
    cfg_infos = (line.rstrip('\n').split('=') for line in lines)
    global cc_url, cc_guid
    for info in cfg_infos:
        if info[0] == 'url':
            cc_url = info[1].replace('\\', '') + '/xmlrpc/server'
        elif info[0] == 'clientguid':
            cc_guid = info[1]


def init_svn_vars():
    lines = os.popen('cat ~/.subversion/auth/svn.simple/*').readlines()
    global svn_login, svn_pwd
    if len(lines) > 15:
        svn_login = lines[15].rstrip('\n')
        svn_pwd = lines[7].rstrip('\n')
    else:
        import getpass
        username = getpass.getuser()
        svn_login = raw_input('Enter username [{0}]:'.format(username))
        if not svn_login:
            svn_login = username
        if len(lines) > 7:
            svn_pwd = lines[7].rstrip('\n')
        else:
            svn_pwd = getpass.getpass('Enter password:')


def init_git_vars():
    lines = os.popen('git svn info').readlines()
    infos = (line.rstrip('\n').split(': ') for line in lines)
    global svn_root, svn_uuid, svn_url, svn_prefix
    for info in infos:
        if info[0] == 'Repository Root':
            svn_root = info[1]
        elif info[0] == 'Repository UUID':
            svn_uuid = info[1]
        elif info[0] == 'URL':
            svn_url = info[1]

    if svn_url.startswith(svn_root):
        svn_prefix = svn_url[len(svn_root):]
    else:
        print 'SVN_URL {0} does not start from SVN_ROOT {1}'\
            .format(svn_url, svn_root)


def get_str_md5(str):
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()


def init_vars():
    global local_guid
    local_guid = get_str_md5(str(datetime.datetime.now()))
    init_cc_vars()
    init_svn_vars()
    init_git_vars()


def get_svn_last_commit_hash():
    return os.popen('git svn dcommit -n').readlines()[-1]\
        .rstrip('\n').split()[1]


def get_files(hash_id, argv):
    result = []
    lines = os.popen('git diff-index {0}'.format(hash_id)).readlines()
    files_info = (line.rstrip('\n').split() for line in lines)
    print
    for file_info in files_info:
        if len(argv) > 0:
            for file in argv:
                if file == file_info[5]:
                    break
            else:
                continue
        if file_info[4] != 'M' and file_info[4] != 'A' and file_info[4] != 'D':
            print 'Unsupported action type: {0}'.format(file_info[4])
            exit(3)
        result.append({'op_type': file_info[4], 'name': file_info[5]})
        print '{0} {1}'.format(file_info[4], file_info[5])

    if len(result) < 1:
        print 'Files for review not found.'
        exit(3)

    print '\nPress Enter to continue...',
    sys.stdin.readline()
    print '\n'

    return result


def parse_revision_id(revision):
    re_m = re.match('r(\d+)', revision.lower())
    if re_m:
        return int(re_m.group(1))
    else:
        print 'Can not parse revision in "{0}"'.format(revision)
        exit(2)


def get_svn_revision(filename):
    lines = os.popen('git svn info {0}'.format(filename)).readlines()
    infos = (line.rstrip('\n').split(': ') for line in lines)
    for info in infos:
        if info[0] == 'Revision':
            return info[1]

    return Nil


def get_svn_commit_info(filename):
    last_commit_info = os.popen('git svn log --limit 1 {0}'\
        .format(filename)).readlines()[1].rstrip('\n').split(' | ')
    commit_revision = str(parse_revision_id(last_commit_info[0]))
    commit_author = last_commit_info[1]
    commit_time = datetime.datetime.strptime(
        last_commit_info[2][:19], '%Y-%m-%d %H:%M:%S'
    )
    return commit_revision, commit_author, commit_time


def get_git_last_commit_message():
    commit_msg = os.popen('git log -n 1 --format=format:"%B"')\
        .readline().rstrip('\n').replace('@noreview', '')\
        .replace('\\\'', '\'').replace('\\\"', '\"')\
        .rstrip(' ')

    if commit_msg.find('worked') >= 0 or commit_msg.find('fixed') >= 0:
        commit_msg = re.sub(
            ':(?:fixed|worked)\(.*\)', '', commit_msg
        )

    return commit_msg


def updade_commit_msg(review_id):
    commit_msg = os.popen('git log -n 1 --format=format:"%B"')\
        .read()
    if commit_msg.find('@noreview') >= 0:
        os.popen('git commit --amend -F -', 'w').write(
            commit_msg.replace('@noreview', '@' + str(review_id))
        )

    return


def get_cc_server():
    cc_server = xmlrpclib.ServerProxy(cc_url)
    #if os.environ['CC_DEBUG']:
    #    cc_server.set_debug()
    cc_version = cc_server.ccollab3.getServerVersion()
    if cc_version != cc_supported_version:
        print 'Unknown server version: {0}'.format(cc_version)
        exit(2)

#    result = cc_server.ccollab.sessionAffirm(svn_login, svn_pwd)
#        {'password-type': 'plaintext', 'password-value': ''}
#    )

#    if 'error' in result:
#        print 'CodeCollaborator login error: {0}'.format(result['error'])
    return cc_server


def create_cc_review(cc_server):
    title = get_git_last_commit_message()
    if title == '':
        title = 'Untitled'
    return cc_server.ccollab3.reviewCreate(svn_login, title)


def update_cc_review(cc_server, review_id, commit_hash_id, files):
    new_review = True
    if review_id == 0:
        review_id = create_cc_review(cc_server)
    else:
        new_review = False

    result = cc_server.ccollab3.queryObjectsSimple(
        'com.smartbear.ccollab.datamodel.ScmData',
        {
            'configB': svn_uuid, 'configA': svn_root, 'provider': 'subversion'
        }, 1
    )
    scm_id = result[0]['id']

    print 'Creating changelist ...',
    local_changelist_id = cc_server.ccollab3.changelistCreate(
        '', scm_id, local_guid, datetime.datetime.now(), svn_login,
        'Local changes', cc_guid
    )
    print 'Ok!'

    for file in files:
        print 'Uploading file {0} ...'.format(file['name']),

        abs_file_name = os.path.abspath(file['name'])
        svn_path_name = os.path.join(svn_prefix, file['name'])

        if new_review and file['op_type'] == 'M':
            commit_revision, commit_author, commit_time = \
                get_svn_commit_info(file['name'])
            file_changelist_id = cc_server.ccollab3.changelistCreate(
                commit_revision, scm_id, '', commit_time, commit_author,
                'fake comment', cc_guid
            )
            prev_version_id = cc_server.ccollab3.versionCreate(
                file_changelist_id, svn_path_name,
                abs_file_name, commit_revision, 'A'
            )

            content = os.popen(
                'git show {0}:{1}'.format(commit_hash_id, file['name'])
            ).read()
            content_md5 = get_str_md5(content)

            prev_version_found = cc_server.ccollab3.versionSetContentByMd5(
                prev_version_id, content_md5
            )
            if not prev_version_found:
                cc_server.ccollab3.versionSetContent(
                    prev_version_id, xmlrpclib.Binary(content)
                )

            cc_server.ccollab3.save(
                'com.smartbear.ccollab.datamodel.VersionData', {
                    'changelistId': file_changelist_id,
                    'contentMd5': content_md5,
                    'id': prev_version_id, 'scmVersionName': commit_revision,
                    'filePath': svn_path_name,
                    'changeType': 'A', 'localType': 'C',
                    'localFilePath': '', 'prevVersionId': 0,
                }
            )

            commit_revision = str(get_svn_revision(file['name']))
            version_id = cc_server.ccollab3.versionCreate(
                local_changelist_id, svn_path_name,
                abs_file_name, commit_revision, 'M'
            )

            cc_server.ccollab3.save(
                'com.smartbear.ccollab.datamodel.VersionData', {
                    'changelistId': local_changelist_id, 'contentMd5': '',
                    'id': version_id, 'scmVersionName': commit_revision,
                    'filePath': svn_path_name,
                    'changeType': 'M', 'localType': 'L',
                    'localFilePath': abs_file_name,
                    'prevVersionId': prev_version_id
                }
            )
        else:  # existing review
            prev_version_id = 0
            if file['op_type'] == 'M':
                commit_revision = str(get_svn_revision(file['name']))
            else:
                commit_revision = ''

            if file['op_type'] != 'D':
                version_id = cc_server.ccollab3.versionCreate(
                    local_changelist_id, svn_path_name,
                    abs_file_name, commit_revision, file['op_type']
                )

        if file['op_type'] != 'D':
            file_h = open(file['name'], 'rb')
            content = file_h.read()
            content_md5 = get_str_md5(content)

            cc_server.ccollab3.versionSetContentByMd5(version_id, content_md5)

            cc_server.ccollab3.versionSetContent(
                version_id, xmlrpclib.Binary(content)
            )

            cc_server.ccollab3.save(
                'com.smartbear.ccollab.datamodel.VersionData', {
                    'changelistId': local_changelist_id, 'contentMd5': content_md5,
                    'id': version_id, 'scmVersionName': commit_revision,
                    'filePath': svn_path_name,
                    'changeType': 'M', 'localType': 'L',
                    'localFilePath': abs_file_name,
                    'prevVersionId': prev_version_id
                }
            )

        print 'Ok!'

    cc_server.ccollab3.reviewAddChangelist(review_id, local_changelist_id)

    if new_review:
        print '\nReview with id {0} was created.'.format(review_id)
        updade_commit_msg(review_id)
    else:
        print '\nReview with id {0} was updated.'.format(review_id)
#    print 'http://{0}/index.jsp?page=ReviewDisplay&reviewid={1}'.format(
#        cc_url, review_id
#    )


def main(argv):
    # unbuffered stdout
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    review_id = 0
    if len(argv) > 0 and argv[0].isdigit():
        review_id = int(argv.pop(0))

    init_vars()
    commit_hash_id = get_svn_last_commit_hash()
    files = get_files(commit_hash_id, argv)

    cc_server = get_cc_server()
    update_cc_review(cc_server, review_id, commit_hash_id, files)


if __name__ == "__main__":
    main(sys.argv[1:])

# vim: ts=4 sw=4
