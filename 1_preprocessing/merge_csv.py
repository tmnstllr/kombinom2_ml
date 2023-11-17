import os
import pandas as pd


def combine_csv_files(directory, output_file):
    # Get a list of all files in the directory
    file_list = os.listdir(directory)

    # Filter out only the .csv files
    csv_files = [file for file in file_list if file.endswith('.csv')]
    csv_files.sort()

    # Create an empty DataFrame to store the combined data
    combined_data = pd.DataFrame()

    # Variable to store the total line count
    total_line_count = 0

    # Iterate through each .csv file and append its data to the combined DataFrame
    for file in csv_files:
        file_path = os.path.join(directory, file)
        data = pd.read_csv(file_path)
        combined_data = pd.concat([combined_data, data], ignore_index=True)

        # Count the number of lines in the current CSV file
        with open(file_path) as f:
            line_count = sum(1 for _ in f)

        # Add the line count to the total
        total_line_count += line_count - 1  # subtract the header line for each csv file

        # Save the combined data to a new .csv file
    combined_data.to_csv(output_file, index=False)
    print(f"Combined data saved to {output_file} successfully!")

    # Compare line counts
    combined_line_count = combined_data.shape[0]

    # this confirms that the header line is not counted for the combined data csv
    combined_line_count2 = 0
    with open(output_file) as f:
        combined_line_count2 = sum((1 for _ in f))
    print(combined_line_count2)

    print("\nLine Count Comparison:")
    print(f"Total line count of individual CSVs: {total_line_count}")
    print(f"Line count of combined CSV: {combined_line_count}")
    print(f"Difference: {total_line_count - combined_line_count}")


# Provide the directory path containing the .csv files
directory_path = ""

# Provide the name of the output file
output_file_name = ''

# Call the function to combine the .csv files
combine_csv_files(directory_path, output_file_name)