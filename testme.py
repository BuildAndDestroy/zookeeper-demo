#!/usr/bin/env python3
"""Test app for zookeeper

Original script found here, this is not my code nor do I own any rights to it. This is a demo on how to use ZooKeeper:
https://sleeplessbeastie.eu/2021/10/18/how-to-use-zookeeper-to-lock-resources-with-a-python-script/
https://kazoo.readthedocs.io/en/latest/basic_usage.html

python3 lock_example.py --chroot /sleeper_app --identifier client_1 --path /particular_resource --time 10 --zookeeper 172.16.0.111:2181,172.16.0.112:2181,172.16.0.113:2181
"""

import argparse
import time
from datetime import datetime

from kazoo.client import KazooClient


class ApplicationNode(object):

    lock_time: int

    def __init__(self, chroot, lock_path, lock_identifier, lock_time, zookeeper_hosts):
        self.zookeeper = KazooClient(hosts=zookeeper_hosts)

        self.patch_chroot = chroot
        self.lock_path = lock_path
        self.lock_identifier = lock_identifier

        self.lock_time = lock_time

        self.connect()
        self.chroot()

    def connect(self):
        self.zookeeper.start()

    def chroot(self):
        self.zookeeper.ensure_path(self.patch_chroot)
        self.zookeeper.chroot = self.patch_chroot

    def lock(self):
        lock = self.zookeeper.Lock(self.lock_path, self.lock_identifier)
        with lock:
            print("At {0} the {1} got lock {2} (will sleep for {3}s)".format(
                (datetime.now()).strftime("%B %d, %Y %H:%M:%S"), self.lock_identifier,
                self.lock_path,
                self.lock_time)
            )
            time.sleep(self.lock_time)

    def __del__(self):
        self.zookeeper.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ZooKeeper example application')
    parser.add_argument('--chroot')
    parser.add_argument('--path')
    parser.add_argument('--identifier')
    parser.add_argument('--time', type=int)
    parser.add_argument('--zookeeper')

    args = parser.parse_args()

    locker = ApplicationNode(lock_path=args.path, lock_identifier=args.identifier, chroot=args.chroot,
                             lock_time=args.time, zookeeper_hosts=args.zookeeper)

    while True:
        locker.lock()

