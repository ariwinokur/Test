import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Location Collector", page_icon="🌍", layout="centered")

st.title("🌍 Location Collector")
st.markdown("Help build a list of all represented cities and states! Enter your info below.")
st.markdown("*City is optional — leave it blank if you just want to represent your state.*")

# File to store data
DATA_FILE = "locations.csv"

# Load data
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Name", "City", "State"])

# Save data
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Add new entry
def add_entry(name, city, state):
    df = load_data()
    # Use empty string for city if not provided
    city = city.strip() if city else ""
    new_row = pd.DataFrame({"Name": [name], "City": [city], "State": [state.upper()]})
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    st.cache_data.clear()  # Refresh data
    return df

# Get unique locations
def get_unique_locations():
    df = load_data()
    if df.empty:
        return []
    
    # Create a clean location string
    df_copy = df.copy()
    df_copy["Location"] = df_copy.apply(
        lambda row: f"{row['State']}" if pd.isna(row['City']) or row['City'].strip() == "" 
        else f"{row['City']}, {row['State']}", axis=1
    )
    
    unique_locations = sorted(df_copy["Location"].drop_duplicates().tolist())
    return unique_locations

# Sidebar form
with st.sidebar:
    st.header("✍️ Add Your Location")
    with st.form(key="add_form"):
        name = st.text_input("Your Name *", help="Required")
        city = st.text_input("City (optional)", help="Leave blank to represent the whole state")
        state = st.text_input("State * (e.g., CA, New York, Texas)", max_chars=30, help="Required")
        submitted = st.form_submit_button("Submit")

        if submitted:
            name = name.strip()
            city = city.strip()
            state = state.strip()

            if not name:
                st.error("Please enter your name!")
            elif not state:
                st.error("Please enter your state!")
            else:
                add_entry(name, city, state)
                display_city = city if city else "(whole state)"
                st.success(f"Thank you, {name.split()[0]}! You've added {display_city} of {state.upper()}.")
                st.balloons()

# Main content
st.markdown("### 📍 Unique Represented Locations")

locations = get_unique_locations()

if locations:
    st.write(f"**{len(locations)} unique location(s) represented so far:**")
    cols = st.columns(3)
    for i, loc in enumerate(locations):
        cols[i % 3].write(f"• {loc}")
else:
    st.info("No locations added yet. Be the first one!")

# Total entries
df = load_data()
if not df.empty:
    st.markdown(f"---\n**Total contributions:** {len(df)} people have participated.")

# Footer
st.markdown("---")
st.caption("Made with ❤️ using Streamlit • City is optional • Data saved automatically")
