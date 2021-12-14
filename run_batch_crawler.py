import os

import argparse
import math

import time
import datetime

import traceback
import subprocess

import tempfile
import gzip

# Different to batch crawl
# Creates on process per repository
# Only syncs data when process finishes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class RollingAppender:

    def __init__(self, target_dir, compress = False, max_saves = -1):
        self.target_dir = target_dir
        self.max_saves = max_saves
        self.compress = compress

        self.current_file_path = None
        self.current_saves = 0
        self.num_files = 0

    def _update_file(self, n = 0):
        self.current_saves += n

        if (self.current_file_path is None
             or (self.max_saves > 0 and self.current_saves >= self.max_saves)):
            self.num_files += 1
            self.current_file_path = os.path.join(self.target_dir, "single_commits-%d.jsonl" % self.num_files)
            self.current_saves = 0
        
        return self.current_file_path

    def _open_file(self, file_path):
        if self.compress:
            return gzip.open(file_path + ".gz", "a")
        else:
            return open(file_path, "ab")


    def append(self, copy_file_path):
        with open(copy_file_path, "r") as line_stream:
            file_path = self._update_file()
            file_io = self._open_file(file_path)
            print("Transfer results to %s" % file_path)

            try:
                for line in line_stream:
                    file_io.write(line.encode("utf-8"))
                    new_path = self._update_file(1)
                    if file_path != new_path:
                        file_path = new_path
                        file_io = self._open_file(file_path)
                        print("Transfer results to %s" % file_path)
            finally:
                file_io.close()



def run_crawler(repository, target_file, lang = "python", crawl_script = "run_repo_crawler.py"):
    script_path = os.path.join(BASE_DIR, crawl_script)
    try:
        subprocess.run(["python", script_path, repository, target_file, "--lang", lang], check=True)
    except KeyboardInterrupt as e:
        raise e
    except Exception:
        traceback.print_exc()
        return False
    
    return os.path.isfile(target_file)


def chunk_repos(args, repos):
    
    if args.chunk == -1: return repos
    if args.max_chunks == -1: args.max_chunks = len(repos)

    if args.chunk >= args.max_chunks: raise ValueError("Cannot access chunk %d / %d" % (args.chunk, args.max_chunks))

    num_chunks = math.ceil(len(repos) / args.max_chunks)
    start_offset = args.chunk * num_chunks

    return repos[start_offset: start_offset + num_chunks]



def main(): 
    parser = argparse.ArgumentParser()

    parser.add_argument("index_file")
    parser.add_argument("output_dir")

    parser.add_argument("--chunk", type=int, default=-1)
    parser.add_argument("--max_chunks", type=int, default=-1)
    parser.add_argument("--max_items_per_file", type=int, default=-1)
    parser.add_argument("--lang", default = "python")
    parser.add_argument("--tmpfile")
    parser.add_argument("--compress", action="store_true")

    parser.add_argument("--crawl_script", default="run_repo_crawler.py")

    args = parser.parse_args()

    repos = []

    with open(args.index_file, "r") as i:
        for line in i: 
            repos.append(line[:-1])

    repos = chunk_repos(args, repos)

    saver = RollingAppender(args.output_dir, compress=args.compress, max_saves=args.max_items_per_file)

    expected_time = 0.0

    print("Process %d repos..." % len(repos))

    for i, repository in enumerate(repos):

        total_expected_time = (len(repos) - i) * expected_time
        total_et_str = str(datetime.timedelta(seconds=total_expected_time))

        print("[%d / %d Est. %s] Collect commits from %s" % (i, len(repos), total_et_str, repository))

        start_time = time.time()

        if args.tmpfile:
            tmpfile = args.tmpfile
            desc    = None
        else:
            desc, tmpfile = tempfile.mkstemp()

        completed = run_crawler(repository, tmpfile, lang = args.lang, crawl_script = args.crawl_script)

        if completed: saver.append(tmpfile)
        if desc: os.close(desc)
        if os.path.isfile(tmpfile): os.remove(tmpfile)

        run_time = time.time() - start_time
        expected_time += (run_time - expected_time) / (i + 1)
    

if __name__ == '__main__':
    main()