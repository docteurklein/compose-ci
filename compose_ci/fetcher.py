from urllib import request
from os import path
import tarfile

class Fetcher:
    def __init__(self, base_path, token, logger):
        self.base_path = base_path
        self.token = token
        self.logger = logger

    def fetch(self, repo, commit):
        url = 'https://api.github.com/repos/%s/tarball/%s' % (repo, commit)
        self.logger.info('fetching %s' % (url))
        req = request.Request(url)
        if self.token:
            req.add_header('Authorization', 'token %s' % (self.token))

        with request.urlopen(req) as res:
            with tarfile.open(fileobj=res, mode='r:gz') as archive:
                directory = archive.next()
                self.logger.info('extracting %s' % (directory.name))
                
                import os
                
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(archive, self.base_path)
                return path.join(self.base_path, directory.name)

