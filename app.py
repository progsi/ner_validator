import streamlit as st
import pandas as pd
import os
import datetime
import yaml
from io import StringIO

# Define your classes here!
TAGS = ["O", "B-WoA", "B-Artist"]

# Define a list of colors
COLORS = [
    "#FF8C8C",  # Light Coral
    "#4682B4",  # Steel Blue
    "#66CDAA",  # Medium Aquamarine
    "#DAA520",  # Goldenrod
    "#FF1493",  # Deep Pink
    "#FF4500",  # Orange Red
    "#20B2AA",  # Light Sea Green
    "#8A2BE2",  # Blue Violet
    "#EEE8AA",  # Pale Goldenrod
    "#BDB76B"   # Dark Khaki
]

st.set_page_config(layout="wide")

def load_data(file_path):
    if file_path.endswith(".IOB"):
        with open(file_path, "r") as f:
            content = f.read()
        df = pd.read_csv(StringIO(content.replace('"', "'").replace("\n\n", "\n\t\n")), sep='\t', quotechar='"', header=None)
    else:
        df = pd.read_csv(file_path, sep='\t', quotechar='"', header=None)
    return df

def load_metadata(file_name):
    file_path = os.path.join("data", "input", file_name)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, sep='\t')
        return df
    else:
        return pd.DataFrame()  # Return empty DataFrame if metadata file does not exist

def get_annotator_file_path(file_name, annotator):
    return os.path.join("data", "output", file_name.replace('.IOB', f'_{annotator}.IOB'))

def get_file_path(file_name, annotator):
    annotation_file_path = get_annotator_file_path(file_name, annotator)
    file_path = annotation_file_path if os.path.isfile(annotation_file_path) else os.path.join("data", "input", file_name)
    return file_path

def split_samples(df):
    samples = []
    sample = []
    for _, row in df.iterrows():
        if pd.isna(row[0]) or row[0] == '':
            if sample:
                samples.append(pd.DataFrame(sample, columns=['Token', 'Tag']))
                sample = []
        else:
            sample.append(row.tolist())
    if sample:
        samples.append(pd.DataFrame(sample, columns=['Token', 'Tag']))
    return samples

def get_available_tags(tags, index):
    available_tags = TAGS.copy()
    if index > 0:
        previous_tag = tags[index - 1]
        if previous_tag.startswith("B-") or previous_tag.startswith("I-"):
            class_name = previous_tag.split("-")[1]
            available_tags.extend([f"I-{class_name}"])
    return available_tags

def update_tags_on_change(tags, index, new_tag):
    if index < 0 or index >= len(tags):
        return tags
    tags[index] = new_tag
    if new_tag == 'O' and index + 1 < len(tags):
        next_tag = tags[index + 1]
        if next_tag.startswith('I-'):
            class_type = next_tag[2:]
            tags[index + 1] = f'B-{class_type}'
    return tags

def get_log_filepath(file_name, annotator):
    return os.path.join("logs", f"{file_name}_{annotator}.log")

def log_timestamp(file_name, annotator, index, metadata_entry):
    log_file_path = get_log_filepath(file_name, annotator)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Read existing log entries
    if os.path.exists(log_file_path):
        log_df = pd.read_csv(log_file_path, sep='\t', index_col=0)
    else:
        log_df = pd.DataFrame(columns=['Timestamp'] + list(metadata_entry.index))
    
    # Update the log entry for the given index
    log_df.loc[index] = [timestamp] + metadata_entry.tolist()
    
    # Write the updated log entries back to the file
    log_df.to_csv(log_file_path, sep='\t')

def get_current_timestamp(file_name, annotator, index):
    log_file_path = get_log_filepath(file_name, annotator)
    if os.path.exists(log_file_path):
        log_df = pd.read_csv(log_file_path, sep='\t', index_col=0)
        if index in log_df.index:
            return log_df.loc[index, 'Timestamp']
    return "Not logged"

def get_first_unlogged_index(file_name, annotator, total_samples):
    log_file_path = get_log_filepath(file_name, annotator)
    if os.path.exists(log_file_path):
        log_df = pd.read_csv(log_file_path, sep='\t', index_col=0)
        for idx in range(total_samples):
            if idx not in log_df.index:
                return idx
    return 0

def display_metadata(metadata_entry, colors):
    if not metadata_entry.empty:
        for col in metadata_entry.index:
            color = colors.get(col, '#000000')
            st.markdown(f"<span style='color:{color}; font-weight: bold;'>{col}: {metadata_entry[col]}</span>", unsafe_allow_html=True)
    else:
        st.markdown("No metadata available.")

def write_annotations(file_name, samples, annotator):
    file_path = get_file_path(file_name, annotator)
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Track the current sample index
    sample_index = 0
    changes_made = False
    
    with open(get_annotator_file_path(file_name, annotator), 'w') as file:
        for line in lines:
            if line.strip() == '':
                # Empty line indicates the end of a sample
                file.write(line)
                sample_index += 1
            else:
                if sample_index < len(samples):
                    token, _ = line.strip().split('\t', 1)
                    # Ensure the DataFrame contains the token before accessing it
                    sample_df = samples[sample_index]
                    if token in sample_df['Token'].values:
                        tag = sample_df.loc[sample_df['Token'] == token, 'Tag'].values[0]
              
                        if line.strip() != f"{token}\t{tag}":
                            changes_made = True
                        file.write(f"{token}\t{tag}\n")
                    else:
                        # If token is not found, write the original line
                        file.write(line)
                else:
                    file.write(line)
    
    return changes_made

def load_config():
    config_path = "config.yml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    else:
        config = {"annotator": "ANNOT1", "file_name": None}
    return config

def save_config(config):
    with open("config.yml", 'w') as file:
        yaml.safe_dump(config, file)

def find_iob_files(directory):
    return [file_name for file_name in os.listdir(directory) if file_name.lower().endswith('.iob')]

def main():
    # Automatically find IOB files in the data/input directory
    input_dir = os.path.join("data", "input")
    iob_files = find_iob_files(input_dir)
    
    if not iob_files:
        st.error("No .IOB files found in the 'data/input' directory.")
        return

    # Load config
    config = load_config()
    annotator = config.get("annotator", "ANNOT1")
    current_file = config.get("file_name", iob_files[0])
    
    # Sidebar for selecting annotator and IOB file
    annotator_options = ["ANNOT1", "ANNOT2", "ANNOT3", "ANNOT4", "ANNOT5"]
    selected_annotator = st.sidebar.selectbox("Annotator", annotator_options, index=annotator_options.index(annotator))
    
    # Dropdown for selecting IOB file
    selected_file = st.sidebar.selectbox("IOB File", iob_files, index=iob_files.index(current_file))
    
    if selected_annotator != annotator or selected_file != current_file:
        config["annotator"] = selected_annotator
        config["file_name"] = selected_file
        save_config(config)
        st.session_state.current_index = get_first_unlogged_index(selected_file, selected_annotator, len(split_samples(load_data(get_file_path(selected_file, selected_annotator)))))
        st.session_state.samples = split_samples(load_data(get_file_path(selected_file, selected_annotator)))
        st.session_state.metadata_df = load_metadata(selected_file.replace('.IOB', '.metadata'))
        st.rerun()

    if "current_index" not in st.session_state:
        st.session_state.current_index = get_first_unlogged_index(selected_file, selected_annotator, len(split_samples(load_data(get_file_path(selected_file, selected_annotator)))))

    if "samples" not in st.session_state:
        st.session_state.samples = split_samples(load_data(get_file_path(selected_file, selected_annotator)))

    if "metadata_df" not in st.session_state:
        st.session_state.metadata_df = load_metadata(selected_file.replace('.IOB', '.metadata'))

    current_index = st.session_state.current_index
    current_sample = st.session_state.samples[current_index]
    current_metadata_entry = st.session_state.metadata_df.iloc[current_index] if not st.session_state.metadata_df.empty else pd.Series(dtype=float)

    # Extract columns and assign light colors
    columns = [col for col in st.session_state.metadata_df.columns if 'color' not in col.lower()] if not st.session_state.metadata_df.empty else []
    colors = {col: COLORS[i % len(COLORS)] for i, col in enumerate(columns)}

    display_metadata(current_metadata_entry, colors)

    num_tokens = len(current_sample)
    max_columns = 16  # Maximum number of columns per row
    num_rows = (num_tokens + max_columns - 1) // max_columns  # Calculate number of rows needed

    # Flag to track if any changes were made
    changes_made = False

    # Create rows of columns
    for row in range(num_rows):
        with st.container():
            cols = st.columns(min(max_columns, num_tokens - row * max_columns), gap="small")
            for col in range(len(cols)):
                index = row * max_columns + col
                if index < num_tokens:
                    with cols[col]:
                        row_data = current_sample.iloc[index]
                        tag_type = row_data['Tag'].split('-')[-1]
                        token_color = colors.get(tag_type, '#ffffff')
                        st.markdown(f"<div style='border: 2px solid {token_color}; padding: 2px; margin: 2px; font-size: small;'>{row_data['Token']}</div>", unsafe_allow_html=True)
                    
                        tag_options = get_available_tags(current_sample['Tag'].tolist(), index)
                        selected_tag = st.selectbox(
                            "Tag Selection:",
                            label_visibility="hidden",
                            options=tag_options,
                            index=tag_options.index(row_data['Tag']) if row_data['Tag'] in tag_options else 0,
                            key=f"tag_select_{current_index}_{row}_{col}"  # Unique key including row and column
                        )
                                             
                        if selected_tag != row_data['Tag']:
                            current_sample['Tag'].iloc[index] = selected_tag
                            if selected_tag == 'O' and index + 1 < len(current_sample):
                                next_tag = current_sample['Tag'].iloc[index + 1]
                                if next_tag.startswith('I-'):
                                    class_type = next_tag[2:]
                                    current_sample['Tag'].iloc[index + 1] = f'B-{class_type}'
                            st.session_state.samples[current_index] = current_sample
                            changes_made = True

    if changes_made:
        write_annotations(selected_file, st.session_state.samples, selected_annotator)
        log_timestamp(selected_file, selected_annotator, current_index, current_metadata_entry)

    # Display navigation buttons at the bottom
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button('Prev'):
            if current_index > 0:
                st.session_state.current_index -= 1
                st.rerun()

    with col2:
        if st.button('Next'):
            if current_index < len(st.session_state.samples) - 1:
                st.session_state.current_index += 1
                st.rerun()

    with col3:
        if st.button('Approve and Next'):
            log_timestamp(selected_file, selected_annotator, current_index, current_metadata_entry)
            if current_index < len(st.session_state.samples) - 1:
                _ = write_annotations(selected_file, st.session_state.samples, selected_annotator)
                st.session_state.current_index += 1
                st.rerun()

    # Display current index and timestamp in the sidebar
    st.sidebar.write(f"Index: {current_index}")

    current_timestamp = get_current_timestamp(selected_file, selected_annotator, current_index)
    if current_timestamp != "Not logged":
        st.sidebar.markdown(f"<span style='color: white;'>Approved: {current_timestamp}</span>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<span style='color: orange;'>Approved: Not logged</span>", unsafe_allow_html=True)

    # Add custom CSS for horizontal scrolling and reduced margins
    st.markdown(
        """
        <style>
        .css-18e3th9 {
            flex: 1 1 0%;
            padding: 0 2rem;
        }
        .css-1d391kg {
            padding: 0 2rem;
        }
        .css-19ih76x {
            overflow-x: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

