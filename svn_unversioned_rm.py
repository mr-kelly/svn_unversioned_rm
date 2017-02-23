#encoding=utf-8

"""
Util for remove unversioned svn files

Base on: http://stackoverflow.com/questions/239340/automatically-remove-subversion-unversioned-files
Author: Kelly Peilin Chan (23110388@qq.com)

"""
import os
import re
import shutil
from subprocess import check_output
import sys

def isLink(fileName):
    """Windows isLink"""
    if sys.platform == 'win32':
        command = ['stat', fileName] # git's stat
        o0 = check_output(command, shell=True)
        return 'symbolic link' in o0
    else:
        return os.path.islink(fileName)


def removeFile(path):
    """
    windows平台时使用rm命令，支持NTFS symbol link!
    """
    if sys.platform == 'win32':
        try:
            check_output(['rm', path], shell=True)
        except:
            try:
                check_output(['del', path], shell=True)
                # os.remove(path)
            except Exception, e:
                raise e
    else:
        return os.remove(path)

    # 是否显示删除的文件？
    # print "Remove unversioned file on path: %s" % path


def checkRemove(path, lstIgnorePaths):
    # 判断是否需要跳过
    bShouldIgnorePath = False
    if lstIgnorePaths:
        for sIgnore in lstIgnorePaths:
            if sIgnore in path:
                print "ignore unversioned: %s, %s" % (sIgnore, path)

                bShouldIgnorePath = True
                break

    return bShouldIgnorePath

def removeall(path, lstIgnorePaths):
    """
    自动识别文件或文件夹进行删除
    """

    path = path.replace('\\', '/')

    if checkRemove(path, lstIgnorePaths):
        return False

    if not os.path.isdir(path) or isLink(path):
        # print 'Removing file or link: %s' % path
        removeFile(path)
        return True

    print 'Removing directory: %s' % path
    shutil.rmtree(path)


    # print "Removing unversioned path: %s" % path
    # files = os.listdir(path)
    # for x in files:
    #     fullpath=os.path.join(path, x)
    #     fullpath = fullpath.replace('\\', '/')
    #     if os.path.isfile(fullpath) or isLink(fullpath):
    #         removeFile(fullpath)
    #     elif os.path.isdir(fullpath):
    #         removeall(fullpath, lstIgnorePaths)
    # os.rmdir(path)

    return True

def do_svn(path, lstIgnorePaths=None):
    os.chdir(path)

    hasMatch = False

    lines = os.popen('svn status --no-ignore').readlines()
    for line in lines:
        firstChar = line[0]
        if firstChar == 'I' or firstChar == '?': # ignore conflict~
            path = line[1:].strip()
            removeall(path, lstIgnorePaths)
            hasMatch = True
    # unversionedRex = re.compile('^ ?[\?ID] *[1-9 ]*[a-zA-Z]* +(.*)')
    # result = os.popen('svn status --no-ignore -v').readlines()

    # for l in  result:
    #     match = unversionedRex.match(l)
    #     if match:
    #         matchPath = match.group(1)

    #         bRmResult = removeall(matchPath, lstIgnorePaths)
    #         if bRmResult and not hasMatch:
    #             hasMatch = True

    if not hasMatch:
        print 'Ignore(0 changed) unversioned files for handle on [%s]' % path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='svn directory for unversioned')
    parser.add_argument('--ignores', metavar='S', type=str, nargs='+', help='ignore paths')

    args = parser.parse_args()
    if args.path:
        do_svn(args.path, args.ignores)
