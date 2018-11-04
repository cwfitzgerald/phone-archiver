import subprocess
import typing
import sys
import re
import json


ffmpeg_status_decomp_regex = r'frame=\s*([-.\d]+)\s*fps=\s*([-.\d]+)\s*q=\s*([-.\d]+)\s*L*size=\s*([-.\dBkmg]+)\s*time=\s*([-.:\d]+)\s*bitrate=\s*([-.\dkmg]+)bits\/s\s*(?:dup=\s*([\d]+)\s*)*(?:drop=\s*([\d]+)\s*)*speed=\s*([.\d]+)x\s*'
ffmpeg_status_decomp_prog = re.compile(ffmpeg_status_decomp_regex, re.UNICODE)


def find_ffmpeg() -> bool:
    result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print('command ffmpeg not found')
        return False

    result = subprocess.run(['ffprobe', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print('command ffprobe not found')
        return False
    return True


def get_info(video: str) -> typing.Tuple[float, int]:
    result = subprocess.run(['ffprobe', '-hide_banner', '-v', 'quiet',
                             '-print_format', 'json',
                             '-show_format', "-show_streams",
                             video],
                            stdout=subprocess.PIPE)

    parsed = json.loads(result.stdout.decode('utf8'))

    return \
        [eval(s['avg_frame_rate']) for s in parsed['streams']
         if 'avg_frame_rate' in s and s["codec_type"] == "video"][0], \
        int(parsed['format']['size'])


def encode_video(video: str, output_file: str):
    # TODO: Duration
    frame_rate, size = get_info(video)
    process = subprocess.Popen(['ffmpeg', '-hide_banner', '-v', 'warning', '-stats', '-y',
                                '-i', video,
                                '-pix_fmt', 'yuv420p',
                                '-vf', 'scale=w=1920:h=1080:force_original_aspect_ratio=decrease',
                                '-c:v', 'hevc', '-crf:v', '28', '-preset:v', 'faster',
                                '-c:a', 'libopus', '-b:a', '64k',
                                output_file],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    output = ""
    try:
        while True:
            value = process.stderr.read(25).decode('utf8').replace('\r', '\n')
            if value == '':
                break
            output += value
            lines = output.split('\n')
            output = lines[-1]

            for line in lines[-2::-1]:
                match = ffmpeg_status_decomp_prog.match(line)

                if match is None:
                    continue

                sys.stdout.write("\rFrame: {:0>5d} Time: {:.2f}".format(int(match.group(1)),
                                                                        float(match.group(1)) / frame_rate))
                sys.stdout.flush()
    except KeyboardInterrupt as e:
        process.kill()
        raise

    process.wait()

    shrink = size / get_info(output_file)[1]

    print(f"\nShrunk {shrink:.2f}x")


def process_videos(file_pairs: typing.List[typing.Tuple[str, str]]):
    finished_count = 0
    total_count = len(file_pairs)
    for input_file, output_file in file_pairs:
        finished_count += 1
        print(f"{finished_count:5d}/{total_count:d}: "
              f"{finished_count / total_count * 100:5.1f}%: {output_file}")
        encode_video(input_file, output_file)
