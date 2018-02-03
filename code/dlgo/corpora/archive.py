from __future__ import absolute_import
from __future__ import print_function
import os
import shutil
import tarfile
import tempfile
from contextlib import contextmanager

__all__ = [
    'SGF',
    'SGFLocator',
    'find_sgfs',
]


def cmp(x, y):
    return (x > y) - (x < y)


class SafetyError(Exception):
    pass


class SGF(object):
    def __init__(self, locator, contents):
        self.locator = locator
        self.contents = contents

    def __str__(self):
        return 'SGF from %s' % self.locator


class SGFLocator(object):
    # TODO Support zips and physical SGFs.
    def __init__(self, archive_path, archive_filename):
        self.archive_path = archive_path
        self.archive_filename = archive_filename

    @property
    def physical_file(self):
        return self.archive_path

    @property
    def game_file(self):
        return self.archive_filename

    def __cmp__(self, other):
        return cmp((self.physical_file, self.game_file), (other.physical_file, other.game_file))

    def __str__(self):
        return '%s:%s' % (self.archive_path, self.archive_filename)

    def serialize(self):
        return {
            'archive_path': self.archive_path,
            'archive_filename': self.archive_filename,
        }

    @classmethod
    def deserialize(cls, data):
        return SGFLocator(
            archive_path=data['archive_path'],
            archive_filename=data['archive_filename'],
        )


class TarballSGFLocator(SGFLocator):
    def __init__(self, tarball_path, archive_filename):
        self.tarball_path = tarball_path
        self.archive_filename = archive_filename

    def __str__(self):
        return '%s:%s' % (self.tarball_path, self.archive_filename)

    def contents(self):
        return tarfile.open(self.tarball_path).extractfile(self.archive_filename).read()


def find_sgfs(path):
    """Find all SGFs in a directory or archive."""
    print(('Examining %s...' % (path,)))
    if os.path.isdir(path):
        return _walk_dir(path)
    if tarfile.is_tarfile(path):
        return _walk_tarball(path)


def _walk_dir(path):
    children = os.listdir(path)
    children.sort()
    for child in children:
        full_path = os.path.join(path, child)
        for sgf in find_sgfs(full_path):
            yield sgf


@contextmanager
def tarball_iterator(tarball_path):
    tempdir = tempfile.mkdtemp(prefix='tmp-betago')
    tf = tarfile.open(tarball_path)

    # Check for unsafe filenames. Theoretically a tarball can contain
    # absolute filenames, or names like '../../whatever'
    def name_is_safe(filename):
        final_path = os.path.realpath(os.path.join(tempdir, filename))
        dir_to_check = os.path.join(os.path.realpath(tempdir), '')
        return os.path.commonprefix([final_path, dir_to_check]) == dir_to_check
    if not all(name_is_safe(tf_entry.name) for tf_entry in tf):
        raise SafetyError('Tarball %s contains unsafe filenames' % (tarball_path,))
    sgf_names = [tf_entry.name for tf_entry in tf
                 if tf_entry.isfile and tf_entry.name.endswith('.sgf')]
    sgf_names.sort()
    tf.extractall(tempdir)
    try:
        yield [SGF(SGFLocator(tarball_path, sgf_name), open(os.path.join(tempdir, sgf_name)).read())
               for sgf_name in sgf_names]
    finally:
        shutil.rmtree(tempdir)
        tf.close()


def _walk_tarball(path):
    with tarball_iterator(path) as tarball:
        for sgf in tarball:
            yield sgf
