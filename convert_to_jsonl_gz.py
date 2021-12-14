"""
After running the batch repo crawler (run_batch_crawler.py),
we collected a lot of files inside multiple tars.

This script converts the multiple archives into a compressed jsonl format.
For all other script, we assume that we operate on this format.

Note:
If you run run_batch_crawler.py together with --compress, this script is not necessary.
"""
import os
import argparse
import tarfile
import json
import gzip

from glob import glob
from tqdm import tqdm

def load_slcs_from_tar(tar_files):

    for tar_file in tar_files:
        tar = tarfile.open(tar_file, "r:gz")

        try:
            for tarinfo in tar:
                if not tarinfo.isfile(): continue
                with tar.extractfile(tarinfo) as lines:
                    for line in lines:
                        yield json.loads(line.decode("utf-8"))  
        finally:
            tar.close()


# Save to jsonl.gz

class JsonlGzSaver:

    def __init__(self, save_dir, num_objects = 1e5):
        self.save_dir = save_dir
        self.num_objects = num_objects
        
        self.object_count = 0
        self.file_count   = 0

        self.file_handler = None
        self._find_unique_index()
        self._update_handler()

    def _file_path(self):
        return os.path.join(self.save_dir, "file-%d.jsonl.gz" % self.file_count)

    def _find_unique_index(self):
        while os.path.exists(self._file_path()):
            self.file_count += 1

    def _update_handler(self):
        
        need_update = self.file_handler is None or self.object_count >= self.num_objects
        if not need_update: return

        file_path = self._file_path()

        if self.file_handler is not None: self.file_handler.close()

        self.file_handler = gzip.open(file_path, "wb")
        self.file_count += 1
        self.object_count = 0

    def save(self, obj):
        json_obj = json.dumps(obj) + "\n"
        self.file_handler.write(json_obj.encode("utf-8"))
        self.object_count += 1
        self._update_handler()

    def close(self):
        if self.file_handler is not None:
            self.file_handler.close()
        self.file_handler = None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")

    args = parser.parse_args()

    tar_files = glob(os.path.join(args.input_dir, "*.tar.gz"))

    slc_saver = JsonlGzSaver(args.output_dir)
    num_saved = 0

    try:
        examples_from_tar = load_slcs_from_tar(tar_files)

        for slc in tqdm(examples_from_tar, total = 66e6):
            slc_saver.save(slc)
            num_saved += 1
            
        
    finally:
        slc_saver.close()

    print("Num saved commits: %d" % num_saved)



if __name__ == '__main__':
    main()