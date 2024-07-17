import streamlit as st
import pandas as pd
import argparse
import os

def load_data(file_path):
    df = pd.read_csv(file_path, sep='\t', header=None)
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
    available_tags = ["O", "B-PER", "B-LOC"]
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

def main():
    parser = argparse.ArgumentParser(description="NER Validator")
    parser.add_argument("--file", type=str, required=True, help="Path to the IOB dataset file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        st.error(f"File {args.file} does not exist.")
        return

    df = load_data(args.file)
    samples = split_samples(df)

    st.title("NER Validator")

    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    if "samples" not in st.session_state:
        st.session_state.samples = samples

    current_index = st.session_state.current_index
    current_sample = st.session_state.samples[current_index]

    num_tokens = len(current_sample)
    col_widths = [1] * num_tokens
    cols = st.columns(num_tokens, gap="small")

    # Display tokens and tags for the current sample
    for i, row in current_sample.iterrows():
        with cols[i]:
            st.write(f"{row['Token']} ", end="")
            tag_options = get_available_tags(current_sample['Tag'].tolist(), i)
            selected_tag = st.selectbox(
                "Tag Selection:",
                label_visibility="hidden",
                options=tag_options,
                index=tag_options.index(row['Tag']) if row['Tag'] in tag_options else 0,
                key=f"tag_select_{i}"
            )
            if selected_tag!= row['Tag']:
                current_sample['Tag'].iloc[i] = selected_tag
                if selected_tag == 'O' and i + 1 < len(current_sample):
                    next_tag = current_sample['Tag'].iloc[i + 1]
                    if next_tag.startswith('I-'):
                        class_type = next_tag[2:]
                        current_sample['Tag'].iloc[i + 1] = f'B-{class_type}'
                st.session_state.samples[current_index] = current_sample
                updated_df = pd.concat(st.session_state.samples, ignore_index=True)
                updated_df.to_csv(f"{args.file}_ANNOT", sep='\t', index=False, header=None)
                st.rerun()

    col1, col2 = st.columns([1, 1])
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

if __name__ == "__main__":
    main()
