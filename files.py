import os
import shutil
import typing


def enumerate_files(indir: str, outdir: str) -> typing.Tuple[typing.List[typing.Tuple[str, str]],
                                                             typing.List[typing.Tuple[str, str]],
                                                             typing.List[typing.Tuple[str, str]]]:
    video_files: typing.List[typing.Tuple[str, str]] = []
    image_files: typing.List[typing.Tuple[str, str]] = []
    regular_files: typing.List[typing.Tuple[str, str]] = []

    os.makedirs(outdir, exist_ok=True)

    for root, dirs, files in os.walk(indir):
        if root != indir:
            os.makedirs(os.path.join(outdir, os.path.relpath(root, start=indir)), exist_ok=True)
        for f in files:
            full_name = os.path.join(root, f)
            name, ext = os.path.splitext(full_name)
            relname = os.path.relpath(name, start=indir)
            outfile = os.path.normpath(os.path.join(outdir, relname))

            if ext[1:] in ['mp4', 'mpeg', 'mkv', 'mov', 'flv', 'webm', '3gp']:
                video_files.append((full_name, outfile + '.mkv'))
            elif ext[1:] in ['jpg', 'jpeg', 'png', 'gif', 'tiff']:
                image_files.append((full_name, outfile + '.jpg'))
            else:
                regular_files.append((full_name, outfile + ext))

    return video_files, image_files, regular_files


def copy(file_pairs: typing.List[typing.Tuple[str, str]]):
    finished_count = 0
    total_count = len(file_pairs)
    for input_file, output_file in file_pairs:
        finished_count += 1
        print(f"{finished_count:5d}/{total_count:d}: "
              f"{finished_count / total_count * 100:5.1f}%: {output_file}")
        if os.path.isfile(output_file):
            continue
        shutil.copy2(input_file, output_file)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%6.2f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%5.2f%s%s" % (num, 'Yi', suffix)
