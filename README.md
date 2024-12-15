# Taiwan Futures Data

## Overview

taiwan-futures-data is a Python project for downloading, extracting, transforming, and analyzing Taiwan Futures market data. This project automates the retrieval of compressed data files, processes them into a standardized format, and prepares them for analysis.

## Installation

### Prerequisites

- Python 3.12 or later
- Poetry for dependency management

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/DOUIF/taiwan-futures-data.git
   cd taiwan-futures-data
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

## Usage

### Run the Program

To execute the script, simply run the following command:

```bash
python main.py
```

This will:

1.  Download the latest futures data.
2.  Process the data and save it as CSV files in the data/csv folder.

### Output

- ZIP Files: Stored in data/zip/.
- Processed CSV Files: Stored in data/csv/.

## Code Structure

```plaintext
.
├── data/                  # Directory for ZIP and CSV data
├── taiwan_futures/
│   ├── download.py        # Handles data download
│   └── transform.py       # Processes and transforms data
├── main.py                # Main entry point
├── pyproject.toml         # Poetry configuration file
└── README.md              # Project documentation
```

### Main Components

1.  [download.py](taiwan_futures/download.py):

    - Retrieves ZIP files from the specified URLs.
    - Ensures only the latest data is downloaded.
    - Deletes outdated files.

2.  [transform.py](taiwan_futures/transform.py):

    - Extracts ZIP files to a temporary directory.
    - Converts raw data into a structured format.
    - Resamples data at 1-minute intervals.

3.  [main.py](main.py):

    - Orchestrates the downloading and transformation process.

## License

The source code for this project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

However, please note that this project depends on third-party libraries, each of which may have its own license. By using this project, you agree to comply with the licenses of all dependencies as specified in their respective repositories or documentation. Below is a list of key
