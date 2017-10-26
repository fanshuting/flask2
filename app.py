# -*- coding: UTF-8 -*-
import getopt
from ftplib import FTP
import os, sys, string, time
import socket
from datetime import datetime, timedelta

class MyFTP:
    def __init__(self, hostaddr, username, password, remotedir, port=21):
        self.hostaddr = hostaddr
        self.username = username
        self.password = password
        self.remotedir = remotedir
        self.port = port
        self.ftp = FTP()
        self.file_list = []

    def __del__(self):
        self.ftp.close()

    def login(self):
        ftp = self.ftp
        try:
            timeout = 60
            socket.setdefaulttimeout(timeout)
            ftp.set_pasv(True)
            print 'start connect %s' % self.hostaddr
            ftp.connect(self.hostaddr, self.port)
            print 'success connect %s' % self.hostaddr
            print 'start login %s' % self.hostaddr
            ftp.login(self.username, self.password)
            print 'success login %s' % self.hostaddr
            print ftp.getwelcome()
        except Exception:
            print 'connect failed'
            sys.exit()
        try:
            ftp.cwd(self.remotedir)
        except(Exception):
            print 'cmd failed'
            sys.exit()

    def is_same_size(self, localfile, remotefile):
        try:
            remotefile_size = self.ftp.size(remotefile)
        except:
            remotefile_size = -1
        try:
            localfile_size = os.path.getsize(localfile)
        except:
            localfile_size = -1
        # print 'lo:%d  re:%d' %(localfile_size, remotefile_size)
        if remotefile_size == localfile_size:
            return 1
        else:
            return 0

    def download_file(self, localfile, remotefile):
        # 过滤掉一些格式的文件
        if remotefile.split('.')[-1] in ('bak', 'pyc'):
            print '%s file format pass' % localfile
            return ''
        # 如果本地存在文件，则比较本地文件和服务器文件的最后修改日期，如果本地文件是最新的则不下载
        if os.path.exists(localfile):
            remote_date = datetime.strptime(self.ftp.sendcmd('MDTM ' + remotefile)[4:], "%Y%m%d%H%M%S") + timedelta(hours=8)
            local_date = datetime.fromtimestamp(os.path.getmtime(localfile))
            # 如果本地文件为最新，并且与服务器文件大小一致，则跳过此文件
            if local_date >= remote_date:
                # print '%s latest file pass' % localfile
                # print 1
                if self.is_same_size(localfile, remotefile) == 1:
                    # print 2
                    return ''
        print '>>>>>>>>>>>>download %s ... ...' % localfile
        # 判断文件的目录是否存在，如不存在则创建该目录
        localfile_dir = '/'.join(localfile.split('/')[:-1])
        if not os.path.exists(localfile_dir):
            os.mkdir(localfile_dir)
        file_handler = open(localfile.decode('utf8'), 'wb')
        self.ftp.retrbinary('RETR %s' % remotefile, file_handler.write)
        file_handler.close()

    def download_files(self, localdir='./', remotedir='./'):
        try:
            self.ftp.cwd(remotedir)
        except:
            print 'dir %s not exist，continue...' % remotedir
            return
        if not os.path.isdir(localdir):
            os.makedirs(localdir)
        print 'cmd dir %s' % self.ftp.pwd()
        self.file_list = []
        self.ftp.dir(self.get_file_list)
        remotenames = self.file_list
        # 本地目录文件
        local_files = os.listdir(localdir)
        # 远程目录文件
        remote_files = []
        for item in remotenames:
            filetype = item[0]
            filename = item[1]
            local = os.path.join(localdir, filename)
            if filetype == 'd':
                self.download_files(local, filename)
            elif filetype == '-':
                remote_files.append(filename)
                self.download_file(local, filename)
        # 删除本地文件，该文件远程目录不存在
        for local_file in local_files:
            if local_file not in remote_files and os.path.isfile(os.path.join(localdir, local_file)):
                os.remove(os.path.join(localdir, local_file))
        self.ftp.cwd('..')
        # print 'back dir %s' %self.ftp.pwd()

    def get_file_list(self, line):
        ret_arr = []
        file_arr = self.get_filename(line)
        if file_arr[1] not in ['.', '..']:
            self.file_list.append(file_arr)

    def get_filename(self, line):
        file_arr = [line[0], line.split(' ')[-1]]
        return file_arr


ip = '***.***.***.***'
port = 1234
username = '****'
password = '****'
ftp = MyFTP(ip, username, password, './', port)

if __name__ == '__main__':
    ftp.login()
    ftp.download_files('C:/derhino_player/data_service', './data_service')
