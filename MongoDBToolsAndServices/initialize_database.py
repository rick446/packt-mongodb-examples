import logging
import argparse

import pymongo

log = logging.getLogger('load')


def main():
    logging.basicConfig(format='%(processName)s / %(threadName)s: %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(description='Generate load for MongoDB')
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
        '--shard', '-s', action='store_true')
    parser.add_argument(
        '--routeable', '-r', action='store_true')
    parser.add_argument(
        'uri', nargs='?', help='The MongoDB DBURI to target',
        default='mongodb://localhost:27017/test')
    args = parser.parse_args()
    log.info('Starting MongoDB database initializer with the following parameters:')
    for arg in ('num_ix_b', 'num_ix_n', 'collection', 'database', 'shard', 'uri'):
        log.info('%20s: %s', arg, getattr(args, arg))
    cli = pymongo.MongoClient(args.uri)
    db = cli[args.database]
    coll = db[args.collection]
    coll.drop()
    if args.shard:
        try:
            cli.admin.command('enableSharding', args.database)
        except Exception:
            log.exception('Exception in enabling sharding, continuing...')
        if args.routeable:
            cli.admin.command(
                'shardCollection',
                '{}.{}'.format(args.database, args.collection),
                key={'ix_n': 'hashed'})
        else:
            cli.admin.command(
                'shardCollection',
                '{}.{}'.format(args.database, args.collection),
                key={'ix_n': '1'})
    for ix_n in range(args.num_ix_n):
        block = [
            {'ix_n': ix_n, 'ix_b': ix_b}
            for ix_b in range(args.num_ix_b)]
        coll.insert_many(block)
        if ix_n % 40 == 0:
            print()
        print('.', end='', flush=True)
    print()
    coll.create_index([
        ('ix_n', 1),
        ('ix_b', 1)
    ])

if __name__ == '__main__':
    main()