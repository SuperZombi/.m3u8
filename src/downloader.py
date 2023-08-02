# -*- coding: utf-8 -*-

__version__ = '2.0.0'
__description__ = 'A simple .m3u8 video downloader.'

import os
import sys
from utils import *
from argparse import ArgumentParser
import urllib.parse as urlparse

class FFMPEGnotInstalled(Exception): ...

class color:
    VIOLET: str = '\033[95m'
    CYAN: str = '\033[96m'
    DARK_CYAN: str = '\033[36m'
    BLUE: str = '\033[94m'
    GREEN: str = '\033[92m'
    YELLOW: str = '\033[93m'
    RED: str = '\033[91m'
    WHITE: str = '\033[37m'
    BLACK: str = '\033[30m'
    GRAY: str = '\033[38;2;125;125;125m'
    MAGENTA: str = '\033[35m'
    BOLD: str = '\033[1m'
    DIM: str = '\033[2m'
    NORMAL: str = '\033[22m'
    UNDERLINED: str = '\033[4m'
    STOP: str = '\033[0m'


EXIT_FAILURE: int = 1
EXIT_SUCCESS: int = 0

def exit(status_code: int):
    if status_code == 0:
        input()
    else:
        input(f"{color.RED}Error!{color.STOP}")


def main() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    print(f'      {color.GREEN}{color.BOLD}M3U8 VIDEO DOWNLOADER{color.STOP}\n({color.DARK_CYAN}{color.UNDERLINED}https://github.com/SuperZombi/m3u8{color.STOP})\n')
    if not ffmpeg_isInstalled():
        print(f"[ {color.RED}!{color.STOP} ] FFMPEG is not installed. (https://ffmpeg.org/download.html)")
        return exit(EXIT_FAILURE)

    parser = ArgumentParser()
    parser.add_argument('-browser', '--browser')
    args = parser.parse_args()

    if args.browser:
        url = args.browser
        params = dict(urlparse.parse_qsl(urlparse.urlparse(url).query))
        m3u8 = params['url']
        file_name = params['name'] + ".mp4"
        file = get_full_filepath(file_name)
        choice = input(f"[ {color.MAGENTA}?{color.STOP} ] {color.GRAY}Download: {color.YELLOW}{file}{color.STOP}\n[ {color.YELLOW}>{color.STOP} ] (Y/path) ")
        if choice.lower() != "y":
            choice = choice.strip('\"')
            if os.path.exists(choice):
                if os.path.isfile(choice):
                    choice = os.path.dirname(choice)
                file = get_full_filepath(os.path.join(choice, file_name))
            else:
                return exit(EXIT_FAILURE)
    else:
        m3u8: str = input(f"[ {color.MAGENTA}?{color.STOP} ] {color.GRAY}URL of the video (.m3u8 or .ts only):{color.STOP}\n[ {color.YELLOW}>{color.STOP} ] ")
        file: str = input(f"[ {color.MAGENTA}?{color.STOP} ] {color.GRAY}Name of your file (with the extension):{color.STOP}\n[ {color.YELLOW}>{color.STOP} ] ")
        file = get_full_filepath(file)

    if os.path.exists(file):
        print(f'[ {color.YELLOW}*{color.STOP} ] {color.YELLOW}File "{file}" was removed (already exists){color.STOP}')
        os.remove(file)

    duration=get_audio_duration(m3u8)
    make_ffmpeg_command(["ffmpeg", "-reconnect", "1",
                        "-reconnect_at_eof", "1",
                        "-reconnect_streamed", "1",
                        "-reconnect_delay_max", "2",
                        "-protocol_whitelist", "file,http,https,tcp,tls",
                        "-i", m3u8,
                        file], duration=duration)
    clear_last_line()
    print(f"[ {color.GREEN}>{color.STOP} ] {color.GREEN}{file}{color.STOP} ")
    print(f"[ {color.MAGENTA}*{color.STOP} ] {color.GRAY}Thanks for using our video downloader!{color.STOP}")
    return exit(EXIT_SUCCESS)

if __name__ == "__main__":
    main()
