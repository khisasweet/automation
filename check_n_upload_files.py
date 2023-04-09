import os
import schedule
import pysftp
import paramiko
from urllib.parse import urlparse

class SFTPUploader:
    def __init__(self, local_dir, sftp_host, sftp_user, sftp_key_file, sftp_remote_dir, proxy_url=None, proxy_user=None, proxy_password=None):
        self.local_dir = local_dir
        self.sftp_host = sftp_host
        self.sftp_user = sftp_user
        self.sftp_key_file = sftp_key_file
        self.sftp_remote_dir = sftp_remote_dir
        self.proxy_url = proxy_url
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password

        self.sftp_opts = {
            'host': self.sftp_host,
            'username': self.sftp_user,
            'private_key': self.sftp_key_file,
            'cnopts': pysftp.CnOpts(knownhosts='~/.ssh/known_hosts'),
        }

        self.ssh_opts = {
            'timeout': 30,
        }

        if self.proxy_url:
            proxy_parts = urlparse(self.proxy_url)
            proxy_host = proxy_parts.hostname
            proxy_port = proxy_parts.port or 80

            self.ssh_opts['sock'] = (proxy_host, proxy_port)

            if self.proxy_user:
                self.ssh_opts['username'] = self.proxy_user
                self.ssh_opts['password'] = self.proxy_password

    def upload_files(self):
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(**self.ssh_opts)
            with pysftp.Connection(**self.sftp_opts, cnopts=pysftp.CnOpts()) as sftp:
                sftp.chdir(self.sftp_remote_dir)
                local_files = os.listdir(self.local_dir)
                for local_file in local_files:
                    if os.path.isfile(os.path.join(self.local_dir, local_file)):
                        remote_file = os.path.join(self.sftp_remote_dir, local_file)
                        sftp.put(os.path.join(self.local_dir, local_file), remote_file)
                        print(f'Uploaded {local_file} to {self.sftp_host}:{remote_file}')

# Create an instance of SFTPUploader
uploader = SFTPUploader(
    local_dir='/path/to/local/directory/',
    sftp_host='example.com',
    sftp_user='username',
    sftp_key_file='/path/to/ssh/key/file',
    sftp_remote_dir='/remote/directory/',
    proxy_url='http://proxy.example.com:8080',
    proxy_user='proxy_username',
    proxy_password='proxy_password',
)

# Schedule the upload_files() method to run every 4 hours
schedule.every(4).hours.do(uploader.upload_files)

# Run the scheduler loop
while True:
    schedule.run_pending()
    time.sleep(1)
