import ffmpeg
import imagemagick
import files
import os
import sys


def main():
    found_ffmpeg = ffmpeg.find_ffmpeg()
    if not found_ffmpeg:
        exit(1)
    im_command = imagemagick.find_imagemagick()
    if im_command is None:
        exit(1)
    videos, images, reg_files = files.enumerate_files(sys.argv[1], sys.argv[2])
    imagemagick.process_images(im_command, images)
    ffmpeg.process_videos(videos)
    files.copy(reg_files)

    video_sizes = [(os.stat(i).st_size, os.stat(o).st_size) for i, o in videos]
    image_sizes = [(os.stat(i).st_size, os.stat(o).st_size) for i, o in images]
    file_sizes = [(os.stat(i).st_size, os.stat(o).st_size) for i, o in reg_files]

    video_ratios = [i_s / o_s for i_s, o_s in video_sizes]
    image_ratios = [i_s / o_s for i_s, o_s in image_sizes]

    max_video, max_video_ratio, max_video_size = max(zip(videos, video_ratios, video_sizes), key=lambda v: v[1])
    min_video, min_video_ratio, min_video_size = min(zip(videos, video_ratios, video_sizes), key=lambda v: v[1])

    max_image, max_image_ratio, max_image_size = max(zip(images, image_ratios, image_sizes), key=lambda v: v[1])
    min_image, min_image_ratio, min_image_size = min(zip(images, image_ratios, image_sizes), key=lambda v: v[1])

    print(f" Most compressed video @ {max_video_ratio:6.2f}x - {files.sizeof_fmt(max_video_size[0])} -> {files.sizeof_fmt(max_video_size[1])}: {max_video[1]}")
    print(f"Least compressed video @ {min_video_ratio:6.2f}x - {files.sizeof_fmt(min_video_size[0])} -> {files.sizeof_fmt(min_video_size[1])}: {min_video[1]}")
    print(f" Most compressed image @ {max_image_ratio:6.2f}x - {files.sizeof_fmt(max_image_size[0])} -> {files.sizeof_fmt(max_image_size[1])}: {max_image[1]}")
    print(f"Least compressed image @ {min_image_ratio:6.2f}x - {files.sizeof_fmt(min_image_size[0])} -> {files.sizeof_fmt(min_image_size[1])}: {min_image[1]}")

    print()

    total_video_in = sum((in_size for in_size, _ in video_sizes))
    total_video_out = sum((out_size for _, out_size in video_sizes))

    total_image_in = sum((in_size for in_size, _ in image_sizes))
    total_image_out = sum((out_size for _, out_size in image_sizes))

    total_file_out = sum((out_size for _, out_size in file_sizes))

    all_in = total_video_in + total_image_in + total_file_out
    all_out = total_video_out + total_image_out + total_file_out

    print(f"Video Compression @ {files.sizeof_fmt(total_video_in)} -> {files.sizeof_fmt(total_video_out)} {total_video_in / total_video_out:6.2f}x")
    print(f"Image Compression @ {files.sizeof_fmt(total_image_in)} -> {files.sizeof_fmt(total_image_out)} {total_image_in / total_image_out:6.2f}x")
    print(f"  Unchanged Files @ {files.sizeof_fmt(total_file_out)}")
    print(f" Total Difference @ {files.sizeof_fmt(all_in)} -> {files.sizeof_fmt(all_out)} {all_in / all_out:6.2f}x")


if __name__ == '__main__':
    main()
