import os
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

from taiwan_futures.transform import transform_zip_to_csv

load_dotenv()


class OnlineZipInfo(BaseModel):
    updated_time: datetime
    date: date
    download_url: str


ZIP_URL = os.getenv("ZIP_URL")
MAIN_URL = os.getenv("MAIN_URL")
ZIP_DIR = Path.cwd() / "data" / "zip"
ZIP_DIR.mkdir(exist_ok=True, parents=True)
CSV_DIR = Path.cwd() / "data" / "csv"
CSV_DIR.mkdir(exist_ok=True, parents=True)


ZIP_DATE_FORMAT = "%Y_%m_%d"
ZIP_UPDATED_TIME_FORMAT = "%Y%m%d%H%M%S"


def download_futures_data() -> None:
    zip_infos = _get_online_zip_info()

    for info in zip_infos:
        is_outdated, local_files = _is_download_zip(info)
        if not is_outdated:
            print(f"{info.date.strftime(ZIP_DATE_FORMAT)} skipped.")
            continue

        # delete local files
        for f in local_files:
            f.unlink()

        zip_file_name = ZIP_DIR / (
            info.date.strftime(ZIP_DATE_FORMAT)
            + "_"
            + info.updated_time.strftime(ZIP_UPDATED_TIME_FORMAT)
            + ".zip"
        )
        is_success = _download_single_data(info.download_url, zip_file_name)

        transform_zip_to_csv(zip_file_name, CSV_DIR)

        print(f"{info.date.strftime(ZIP_DATE_FORMAT)} {"Downloaded." if is_success else 'Failed'}.")


def _get_online_zip_info() -> list[OnlineZipInfo]:
    table = pd.read_html(MAIN_URL, encoding="UTF-8")
    raw_dates = table[1].iloc[:, 1].values
    dates = (datetime.strptime(v, "%Y/%m/%d") for v in raw_dates)

    updated_times = table[1].iloc[:, 0].values
    updated_times = (datetime.strptime(v, "%Y/%m/%d %p %I:%M:%S") for v in updated_times)

    infos = [
        OnlineZipInfo(
            updated_time=ut,
            date=dt,
            download_url=ZIP_URL.format(dt.strftime("%Y_%m_%d")),
        )
        for ut, dt in zip(updated_times, dates)
    ]

    return infos


def _is_download_zip(info: OnlineZipInfo) -> tuple[bool, list[Path]]:
    local_files = _find_file_start_with(info.date.strftime(ZIP_DATE_FORMAT))
    if not local_files:
        return True, list()

    return _is_local_zip_outdated(local_files[0], info), local_files


def _find_file_start_with(prefix: str, end: str = ".zip") -> list[Path]:
    zips = [
        file
        for file in ZIP_DIR.iterdir()
        if file.is_file() and file.name.startswith(prefix) and file.name.endswith(end)
    ]

    return zips


def _is_local_zip_outdated(local_file: Path, info: OnlineZipInfo) -> bool:
    """
    To check this `local file's updated_time` if older than `info.updated_time`.

    Args:
        local_file (Path): local file name (eg 2024_12_24_20241224055000.zip).
        info (OnlineZipInfo): OnlineZipInfo.

    Returns:
        bool: True for outdate, otherwise False.
    """
    try:
        updated_time = datetime.strptime(local_file.stem[-14:], "%Y%m%d%H%M%S")
    except ValueError:
        return True

    return updated_time < info.updated_time


def _download_single_data(
    url: str,
    filename: str,
) -> bool:
    response = requests.get(url, stream=True, allow_redirects=False)
    if response.status_code != 200:
        return False

    with open(filename, "wb") as f:
        for chunk in response.iter_content():
            f.write(chunk)

    return True
