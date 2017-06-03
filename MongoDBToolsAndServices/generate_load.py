import time
import random
import logging
import argparse
import threading
import multiprocessing
from collections import Counter

import pymongo


log = logging.getLogger('load')


def main():
    logging.basicConfig(format='%(processName)s / %(threadName)s: %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(description='Generate load for MongoDB')
    parser.add_argument(
        '--processes', '-p', type=int,
        default=multiprocessing.cpu_count(),
        help='number of processes to start')
    parser.add_argument(
        '--threads', '-t', type=int,
        default=3,
        help='number of threads to start per process')
    parser.add_argument(
        '--num_ix_b', type=int, default=1000)
    parser.add_argument(
        '--num_ix_n', type=int, default=1000)
    parser.add_argument(
        '--collection', '-c',
        default='stress')
    parser.add_argument(
        '--database', '-d',
        default='test')
    parser.add_argument(
        '--limit', '-l', type=int, default=10,
        help='limit used for queries')
    parser.add_argument(
        '--read_preference', '-r', default='primary',
        help='limit used for queries')
    parser.add_argument(
        'uri', nargs='?', help='The MongoDB DBURI to target',
        default='mongodb://localhost:27017/test')
    args = parser.parse_args()
    log.info('Starting MongoDB load test with the following parameters:')
    for arg in ('processes', 'threads', 'num_ix_b', 'num_ix_n', 'collection', 'database', 'limit', 'read_preference', 'uri'):
        log.info('%20s: %s', arg, getattr(args, arg))
    stat_queue = multiprocessing.Queue()
    pargs = (
        stat_queue, args.uri, args.read_preference, args.database, args.collection,
        args.threads, args.num_ix_b, args.num_ix_n, args.limit)
    processes = [
        multiprocessing.Process(target=ptarget, args=pargs, daemon=True)
        for i in range(args.processes)]
    for p in processes:
        p.start()
    rl = RateLogger(log)
    while True:
        msg = stat_queue.get()
        rl.log(msg)


class RateLogger(object):
    headers = ''

    def __init__(self, logger, interval=10):
        self.logger = logger
        self.interval = interval
        self.counters = Counter()
        self.last_printed = time.time()
        self.num_prints = 0

    def log(self, name):
        self.counters[name] += 1
        now = time.time()
        elapsed = now - self.last_printed
        if elapsed <= self.interval:
            return
        fields = sorted(self.counters.keys())
        counters = [self.counters[f] for f in fields]
        rates = [c / elapsed for c in counters]
        colw = max(len(f) for f in fields)
        colw = max(colw, 5)
        f_header = ['%{}s'.format(colw)]
        d_header = ['%{}.2f'.format(colw)]
        if self.num_prints % 10 == 0:
            self.logger.info(' | '.join(f_header * len(fields)), *fields)
        self.logger.info(' | '.join(d_header * len(fields)), *rates)
        for k in self.counters:
            self.counters[k] = 0
        self.num_prints += 1
        self.last_printed = now



def ptarget(stat_queue, uri, read_preference, dbname, cname, threads, num_ix_b, num_ix_n, limit):
    cli = pymongo.MongoClient(uri, readPreference=read_preference)
    time.sleep(1)
    print(cli.nodes)
    coll = cli[dbname][cname]
    targs = (stat_queue, coll, num_ix_b, num_ix_n, limit)
    threads = [
        threading.Thread(target=ttarget, args=targs)
        for i in range(threads)]
    for t in threads:
        t.setDaemon(True)
    for t in threads:
        t.start()
    while True:
        time.sleep(30)


def ttarget(stat_queue, coll, num_ix_b, num_ix_n, limit):
    threads = [
        threading.Thread(
            target=query_test, args=(stat_queue, coll, num_ix_b, num_ix_n, limit)),
        threading.Thread(
            target=update_test, args=(stat_queue, coll, num_ix_b, num_ix_n))]
    for t in threads:
        t.setDaemon(True)
    for t in threads:
        t.start()


def query_test(stat_queue, coll, num_ix_b, num_ix_n, limit):
    while True:
        stat_queue.put('query')
        rv_n = random.randint(0, num_ix_b)
        rv_b = random.randint(0, num_ix_n)
        res = coll.find({
            'ix_n': rv_n,
            'ix_b': {'$gt': rv_b}
        }).limit(limit)
        list(res)


def update_test(stat_queue, coll, num_ix_b, num_ix_n):
    while True:
        stat_queue.put('update')
        rv_n = random.randint(0, num_ix_b)
        rv_b = random.randint(0, num_ix_n)
        coll.update_one(
            {'ix_n': rv_n, 'ix_b': rv_b},
            {'$inc': {'x': 1}})


if __name__ == '__main__':
    main()