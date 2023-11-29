import os
import argparse
import gzip
import json
import multiprocessing as mp

from glob import glob
from tqdm import tqdm

from contextlib import contextmanager


# Load files ----------------------------------------------------------------

def iter_jsonl_gz(jsonl_file_paths):
    for path in jsonl_file_paths:
        open_fn = gzip.open(path, 'r') if path.endswith('gz') else open(path)
        with open_fn as lines:
            for line in lines:
                yield json.loads(line)


# Grouping ----------------------------------------------------------------

class StreamGrouper:

    def __init__(self, group_by, buffer_size = 1e3):
        self.group_by = group_by
        self.buffer_size = buffer_size

        self.key_queue  = []
        self.key_groups = {}

    def _add_to_group(self, instance):
        instance_key = self.group_by(instance)

        if instance_key not in self.key_groups:
            self.key_groups[instance_key] = []
            self.key_queue.append(instance_key)
        
        self.key_groups[instance_key].append(instance)

    def __call__(self, instance_stream):
        
        for instance in instance_stream:
            self._add_to_group(instance)

            if len(self.key_queue) > self.buffer_size:
                emit_key = self.key_queue.pop(0)
                yield self.key_groups[emit_key]
                del self.key_groups[emit_key]

        while len(self.key_queue) > 0:
            emit_key = self.key_queue.pop(0)
            yield self.key_groups[emit_key]
            del self.key_groups[emit_key]


# Jsonl Gz reduce --------------------------------------------------------------------

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


@contextmanager
def jsonl_reduce_io(output_dir):
    saver = JsonlGzSaver(output_dir)
    try:
        
        def call_save(obj):
            saver.save(obj)

        yield call_save
    finally:
        saver.close()

# Map multiprocessing ----------------------------------------------------------------

def pmap(map_fn, data):

    cpu_count = mp.cpu_count()

    if cpu_count <= 4: # Too few CPUs for multiprocessing
        for output in map(map_fn, data):
            yield output

    with mp.Pool(processes = cpu_count) as pool:
        for output in pool.imap_unordered(map_fn, data, chunksize = 4 * cpu_count):
            yield output

# API method ----------------------------------------------------------------

def mapreduce(map_fn, reduce_fn = jsonl_reduce_io, group_by = None):

    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")

    if reduce_fn == jsonl_reduce_io:
        parser.add_argument("output_dir")

    parser.add_argument("--group_buffer", type=int, default = 100)
    parser.add_argument("--parrallel", action="store_true")

    args = parser.parse_args()

    jsonl_files = glob(os.path.join(args.input_dir, "*.jsonl.gz"))
    jsonl_files += glob(os.path.join(args.input_dir, "*.jsonl"))

    # Load instances as stream
    instance_stream = iter_jsonl_gz(jsonl_files)

    # Group if necessary
    if group_by is not None:
        instance_stream = StreamGrouper(group_by, args.group_buffer)(instance_stream)
    
    # Map all instances in parallel
    if not args.parrallel:
        mapped_instance_stream = map(map_fn, instance_stream)
    else:
        mapped_instance_stream = pmap(map_fn, instance_stream)

    if reduce_fn == jsonl_reduce_io:
        with reduce_fn(args.output_dir) as saver:
            for mapped_instances in tqdm(mapped_instance_stream, total=66e6):
                for mapped_instance in mapped_instances:
                    if mapped_instance is None: continue
                    saver(mapped_instance)
    
    else:
        for mapped_instances in tqdm(mapped_instance_stream, total = 66e6):
            for mapped_instance in mapped_instances:
                if mapped_instance is None: continue
                reduce_fn(mapped_instance)
    

