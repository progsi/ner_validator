import streamlit as st
import pandas as pd
import argparse
import os
import datetime

TAGS = ["O", "B-PER", "B-LOC"]

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

def load_data(file_path):
    df = pd.read_csv(file_path, sep='\t', header=None)
    return df

def load_metadata(file_path):
    df = pd.read_csv(file_path, sep='\t')
    return df

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

def log_timestamp(file_name, index):
    log_file_path = os.path.join("logs", f"{file_name}.log")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Read existing log entries
    if os.path.exists(log_file_path):
        log_df = pd.read_csv(log_file_path, sep='\t', index_col=0)
    else:
        log_df = pd.DataFrame(columns=['Timestamp'])
    
    # Update the log entry for the given index
    log_df.loc[index] = [timestamp]
    
    # Write the updated log entries back to the file
    log_df.to_csv(log_file_path, sep='\t')

def get_current_timestamp(file_name, index):
    log_file_path = os.path.join("logs", f"{file_name}.log")
    if os.path.exists(log_file_path):
        log_df = pd.read_csv(log_file_path, sep='\t', index_col=0)
        if index in log_df.index:
            return log_df.loc[index, 'Timestamp']
    return "Not logged"

def get_first_unlogged_index(file_name, total_samples):
    log_file_path = os.path.join("logs", f"{file_name}.log")
    if os.path.exists(log_file_path):
        log_df = pd.read_csv(log_file_path, sep='\t', index_col=0)
        for idx in range(total_samples):
            if idx not in log_df.index:
                return idx
    return 0

def display_metadata(metadata_entry, colors):
    for col in metadata_entry.index:
        color = colors.get(col, '#000000')
        st.markdown(f"<span style='color:{color}'>{col}: {metadata_entry[col]}</span>", unsafe_allow_html=True)

def write_annotations(file_path, samples):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Track the current sample index
    sample_index = 0
    changes_made = False
    
    with open(file_path.replace('.IOB', '_ANNOT.IOB'), 'w') as file:
        for line in lines:
            if line.strip() == '':
                # Empty line indicates the end of a sample
                file.write(line)
                sample_index += 1
            else:
                if sample_index < len(samples):
                    token, _ = line.strip().split('\t', 1)
                    tag = samples[sample_index].loc[samples[sample_index]['Token'] == token, 'Tag'].values[0]
                    if line.strip() != f"{token}\t{tag}":
                        changes_made = True
                    file.write(f"{token}\t{tag}\n")
                else:
                    file.write(line)
    
    return changes_made

def main():
    parser = argparse.ArgumentParser(description="NER Validator")
    parser.add_argument("--file", type=str, required=True, help="Path to the IOB dataset file")
    args = parser.parse_args()
    
    file_path = os.path.join("data", args.file)
    metadata_file_path = file_path.replace('.IOB', '.metadata')

    if not os.path.exists(file_path):
        st.error(f"File {args.file} does not exist.")
        return

    if not os.path.exists(metadata_file_path):
        st.error(f"Metadata file for {args.file} does not exist.")
        return

    df = load_data(file_path)
    metadata_df = load_metadata(metadata_file_path)
    samples = split_samples(df)

    st.title("NER Validator")

    if "current_index" not in st.session_state:
        st.session_state.current_index = get_first_unlogged_index(args.file, len(samples))

    if "samples" not in st.session_state:
        st.session_state.samples = samples

    if "metadata_df" not in st.session_state:
        st.session_state.metadata_df = metadata_df

    current_index = st.session_state.current_index
    current_sample = st.session_state.samples[current_index]
    current_metadata_entry = st.session_state.metadata_df.iloc[current_index]

    # Extract columns and assign light colors
    columns = [col for col in metadata_df.columns if 'color' not in col.lower()]
    colors = {col: COLORS[i % len(COLORS)] for i, col in enumerate(columns)}

    display_metadata(current_metadata_entry, colors)

    num_tokens = len(current_sample)
    cols = st.columns(num_tokens, gap="small")

    # Flag to track if any changes were made
    changes_made = False

    # Display tokens and tags for the current sample
    for i, row in current_sample.iterrows():
        with cols[i]:
            tag_type = row['Tag'].split('-')[-1]
            token_color = colors.get(tag_type, '#ffffff')
            st.markdown(f"<div style='border: 2px solid {token_color}; padding: 2px; margin: 2px; font-size: small;'>{row['Token']}</div>", unsafe_allow_html=True)
            tag_options = get_available_tags(current_sample['Tag'].tolist(), i)
            selected_tag = st.selectbox(
                "Tag Selection:",
                label_visibility="hidden",
                options=tag_options,
                index=tag_options.index(row['Tag']) if row['Tag'] in tag_options else 0,
                key=f"tag_select_{i}"
            )
            if selected_tag != row['Tag']:
                current_sample['Tag'].iloc[i] = selected_tag
                if selected_tag == 'O' and i + 1 < len(current_sample):
                    next_tag = current_sample['Tag'].iloc[i + 1]
                    if next_tag.startswith('I-'):
                        class_type = next_tag[2:]
                        current_sample['Tag'].iloc[i + 1] = f'B-{class_type}'
                st.session_state.samples[current_index] = current_sample
                changes_made = True

    if changes_made:
        write_annotations(file_path, st.session_state.samples)
        log_timestamp(args.file, current_index)

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
            log_timestamp(args.file, current_index)
            if current_index < len(st.session_state.samples) - 1:
                _ = write_annotations(file_path, st.session_state.samples)
                st.session_state.current_index += 1
                st.rerun()
		
    # Display current index and timestamp in the sidebar
    st.sidebar.write(f"Index: {current_index}")

    current_timestamp = get_current_timestamp(args.file, current_index)
    if current_timestamp != "Not logged":
        st.sidebar.markdown(f"<span style='color: white;'>Approved: {current_timestamp}</span>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<span style='color: orange;'>Approved: Not logged</span>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

