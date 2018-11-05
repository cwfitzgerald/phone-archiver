import subprocess
import typing
import sys
import os
import time
import multiprocessing


def find_imagemagick() -> typing.Optional[typing.List[str]]:
    try:
        result = subprocess.run(['magick', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return ['magick', 'convert']
    except FileNotFoundError:
        pass

    try:
        result = subprocess.run(['convert', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return ['convert']
    except FileNotFoundError:
        pass
    print('imagemagick not found')
    return None


def start_process(command: typing.List[str], input_file: str, output_file: str) -> subprocess.Popen:
    return subprocess.Popen(command + ['-resize', '1920x1500>',
                                       '-strip',
                                       '-interlace', 'Plane',
                                       '-sampling-factor', '4:2:0',
                                       '-quality', '70%',
                                       '-auto-orient',
                                       input_file, output_file],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)


def process_images(command: typing.List[str], input_pairs: typing.List[typing.Tuple[str, str]]):
    core_count = multiprocessing.cpu_count()
    core_count += 2 if core_count > 4 else 1

    running_processes: typing.List[subprocess.Popen] = []

    try:
        for input_file, output_file in input_pairs:
            if not os.path.isfile(output_file):
                running_processes.append(start_process(command, input_file, output_file))
            if len(running_processes) == core_count:
                break

        index = min(core_count, len(input_pairs))
        finished_count = 0

        while len(running_processes) != 0:
            is_process_finished = [p.poll() is not None for p in running_processes]
            for finished, process in zip(is_process_finished, list(running_processes)):
                if finished:
                    if process.returncode != 0:
                        print(f'Command failed: {" ".join(process.args)}')
                        print(f'stdout:\n{process.stdout.read().decode("utf8")}')
                        print(f'stderr:\n{process.stdout.read().decode("utf8")}')
                    start_size = os.stat(process.args[-2]).st_size
                    end_size = os.stat(process.args[-1]).st_size
                    finished_count += 1
                    print(f"{finished_count:5d}/{len(input_pairs):d}: "
                          f"{finished_count/len(input_pairs) * 100:5.1f}%: "
                          f"Converted {process.args[-1]}. "
                          f"Shrunk: {start_size / end_size:.2f}x")
                    running_processes.remove(process)
                    while index < len(input_pairs) and os.path.isfile(input_pairs[index][1]):
                        index += 1
                    if index < len(input_pairs):
                        running_processes.append(start_process(command, *input_pairs[index]))
                        index += 1
            time.sleep(0.05)
    except KeyboardInterrupt as k:
        for p in running_processes:
            p.kill()
            os.remove(p.args[-1])
        raise
