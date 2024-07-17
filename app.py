import streamlit as st
import pandas as pd
import argparse
import os

def load_data(file_path):
    df = pd.read_csv(file_path, sep='\t', header=None)
    return df

def get_available_tags(tags, index):
    # Default tags
    available_tags = ["O", "B-PER", "B-LOC"]
    
    if index > 0:
        previous_tag = tags[index - 1]
        if previous_tag.startswith("B-") or previous_tag.startswith("I-"):
            # Add corresponding I- tags if previous tag is B- or I-
            class_name = previous_tag.split("-")[1]
            available_tags.extend([f"I-{class_name}"])

    # Extend available tags with default ones
    return available_tags

def update_tags_on_change(tags, index, new_tag):
    if index < 0 or index >= len(tags):
        return tags
    
    # Update the tag at the current index
    tags[index] = new_tag
    
    # If the new tag is 'O', check the following tag
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

    st.title("NER Validator")

    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    if "tags" not in st.session_state:
        st.session_state.tags = df.iloc[:, 1].tolist()

    num_tokens = len(df)
    
    # Create columns for tokens and tags with adjusted widths to minimize spacing
    col_widths = [1] * num_tokens  # Set equal width for simplicity
    cols = st.columns(num_tokens, gap="small")  # Use a small gap

    for i, row in df.iterrows():
        with cols[i]:
            # Display tokens and dropdowns in a compact way
            st.write(f"{row.iloc[0]} ", end="")  # Print token and keep cursor on the same line

            # Display tags in dropdowns
            tag_options = get_available_tags(st.session_state.tags, i)
            selected_tag = st.selectbox(
                "Tag Selection:",
                label_visibility="hidden",
                options=tag_options,
                index=tag_options.index(st.session_state.tags[i]) if st.session_state.tags[i] in tag_options else 0,
                key=f"tag_select_{i}"
            )
            if selected_tag != st.session_state.tags[i]:
                st.session_state.tags = update_tags_on_change(st.session_state.tags, i, selected_tag)
                df.iloc[:, 1] = st.session_state.tags
                df.to_csv(f"{args.file}_ANNOT", sep='\t', index=False, header=None)
                st.rerun()  # Ensure the UI updates after saving the tag

if __name__ == "__main__":
    main()

