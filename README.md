# csvtohttp

Automates the process of sending HTTP requests based on the data specified in a CSV file.

This tool is especially useful for batch processing large datasets and sending customized requests without manual intervention.

## Features

- **CSV Input**: Takes any CSV file as input.
- **Flexible Templating**: Uses Handlebars templates to format HTTP requests.
- **Filtering**: Supports filtering CSV columns to process only specific rows.
- **Batch Processing**: Processes records in batches, allowing for efficient data handling.
- **Dry Run Option**: Allows users to perform a dry run to see the output without sending actual requests.

## Usage

The basic usage of the script is outlined below:

```bash
csvtohttp <filename> <template> [options]

Arguments
  filename: The path to the CSV file.
  template: The path to the Handlebars template file used for formatting the HTTP requests.

Options
  -f, --filter: Apply filters to the CSV data (e.g., name=value).
  -d, --data: Provide additional data for the template (e.g., key=value).
  -b, --batch-size: Specify the number of CSV records per HTTP request.
  -v, --verbose: Enable detailed logging.
  --run: Execute the HTTP requests (without this, the tool will run in dry mode).

csvtohttp data.csv request.hbs --run
csvtohttp data.csv request.hbs --filter "status=active" --data "api_key=12345" --run
csvtohttp data.csv request.hbs -b 50 --run
```

## Installation

Ensure you have Python 3.7+ installed on your machine. Clone this repository,
and install via the `pipx` command.

```
pipx install -e .
```
