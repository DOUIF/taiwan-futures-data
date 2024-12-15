from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile

import pandas as pd

ZIP_DIR = Path.cwd() / "data" / "zip"
CSV_DIR = Path.cwd() / "data" / "csv"
ZIP_DIR.mkdir(exist_ok=True, parents=True)
CSV_DIR.mkdir(exist_ok=True, parents=True)


def _unzip(file: Path, output_folder: Path | str) -> list[Path]:
    if isinstance(output_folder, str):
        output_folder = Path(output_folder)

    try:
        with ZipFile(file, "r") as f:
            f.extractall(output_folder)
            return [output_folder / _f for _f in f.namelist()]

    except BadZipFile:
        print(f"{file} can't be unzipped.")
        return list()


def _transform(file: Path, output_folder: Path | str) -> Path:
    # Read csv
    df = pd.read_csv(
        file,
        encoding="big5",
        dtype={
            "成交日期": str,
            "商品代號": str,
            "到期月份(週別)": str,
            "成交時間": str,
            "成交價格": float,
            "成交數量(B+S)": int,
        },
    )

    # Preprocess CSV
    df.columns = df.columns.str.strip()
    df["time"] = pd.to_datetime(
        df["成交日期"] + " " + df["成交時間"],
        format="%Y%m%d %H%M%S",
    )
    df["成交數量(B+S)"] = (df["成交數量(B+S)"] / 2).astype(int)

    df = (
        df.drop(columns=["成交日期", "成交時間", "近月價格", "遠月價格", "開盤集合競價"])
        .rename(
            columns={
                "成交價格": "price",
                "成交數量(B+S)": "volume",
                "商品代號": "symbol",
                "到期月份(週別)": "exp_month",
            }
        )
        .map(lambda x: x.strip() if isinstance(x, str) else x)
        .set_index("time")
    )

    # Resample CSV
    price_ohlc = df.groupby(["symbol", "exp_month"])["price"].resample("1min").ohlc()
    volume_sum = df.groupby(["symbol", "exp_month"])["volume"].resample("1min").sum()

    # Combine the results
    df = pd.concat([price_ohlc, volume_sum], axis=1).reset_index()
    df = df.dropna(how="any")

    # Save CSV
    output_path = output_folder / file.name
    df.to_csv(output_path, index=False)
    return output_path


def transform_zip_to_csv(zip_file: Path, output_folder: Path) -> None:
    with TemporaryDirectory() as temp_dir:
        print(f"Unzip {zip_file}...", end="\r")
        unzip_files = _unzip(zip_file, temp_dir)
        print(f"Unzip {zip_file} success")

        for temp_csv in unzip_files:
            print(f"Transform {temp_csv}...", end="\r")
            csv_path = _transform(temp_csv, output_folder)
            print(f"Transform {csv_path} success")


def main() -> None:
    for file in (Path.cwd() / "data" / "zip").glob("*.zip"):
        transform_zip_to_csv(file, CSV_DIR)


if __name__ == "__main__":
    main()
