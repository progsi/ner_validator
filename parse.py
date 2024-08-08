import os
import pandas as pd
import numpy as np
from typing import Tuple, List

def read_IOB_file(path: str) -> Tuple[List[np.array], List[np.array]]:
    """Read in an IOB textfile.
    Args:
        path (str): path to IOB file
    Returns:
        Tuple[List[np.array], List[np.array]]: list of texts and list of IOBs
    """
    with open(path, "r") as f:
        content = f.readlines()
    
    cur_words = []
    cur_tags = []
    words = []
    tags = []
    for row in content:
        if row == "\n":
            words.append(np.array(cur_words, dtype="object"))
            tags.append(np.array(cur_tags, dtype="object"))
            cur_words = []
            cur_tags = []
        else:
            row = row.replace("\n", "").split("\t")
            cur_words.append(row[0])
            cur_tags.append(row[1])
    return words, tags


def read_log_file(path: str) -> pd.DataFrame:
    """Read in a log file and return it as a DataFrame.
    Args:
        path (str): path to log file
    Returns:
        pd.DataFrame: DataFrame containing the log file data
    """
    return pd.read_csv(path, sep='\t').set_index("Unnamed: 0")  # Read the log file into a DataFrame


def process_directory(iob_directory: str, log_directory: str) -> pd.DataFrame:
    """Processes directories containing .IOB and .log files into a pandas DataFrame.
    
    Args:
        iob_directory (str): Path to the directory containing .IOB files.
        log_directory (str): Path to the directory containing .log files.
        
    Returns:
        pd.DataFrame: A pandas DataFrame containing the combined contents of the .IOB and .log files.
    """
    combined_data = []
    
    for file_name in os.listdir(log_directory):
        if file_name.endswith('.log'):
            # Identify corresponding .IOB file
            base_name = file_name.replace('.log', '')
            dataset_name, annotator = base_name.rsplit('_', 1)
            dataset_name = dataset_name.replace(".IOB", "")
            
            # Construct the corresponding file names
            log_file_path = os.path.join(log_directory, file_name)
            iob_file_path = os.path.join(iob_directory, f"{dataset_name}_{annotator}.IOB")
            
            # Read the log file into a DataFrame
            df_log = read_log_file(log_file_path)
            
            if os.path.exists(iob_file_path):
                tokens, tags = read_IOB_file(iob_file_path)

                df = pd.DataFrame(zip(tokens,tags), columns=["TEXT", "IOB"])
                df_log["Annotator"] = annotator
                df_log["Subset"] = dataset_name
                df_combined = df_log.join(df)
                
                # Append to combined_data list
                combined_data.append(df_combined)
    
    # Combine all DataFrames into a single DataFrame
    final_df = pd.concat(combined_data, ignore_index=True)
    return final_df


def main():
    # Define paths
    iob_directory = "data/output"
    log_directory = "logs"
    
    # Process directories
    human_annotations_df = process_directory(iob_directory, log_directory)
    
    # Perform pivot operation
    pivoted_df = human_annotations_df.pivot(
        index=["set_id", "yt_id", "WoA", "Artist", "Subset"], 
        columns=["Annotator"], 
        values=["TEXT", "IOB"])

    pivoted_df.to_parquet("data_annotated.parquet")


if __name__ == "__main__":
    main()

