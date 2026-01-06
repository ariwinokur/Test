import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Location Collector", page_icon="🌍", layout="centered")

st.title("🌍 Location Collector")
st.markdown("Help build a list of all represented cities and states! Enter your info below.")

# File to store data (works locally and on Streamlit Community Cloud)
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
    new_row = pd.DataFrame({"Name": [name], "City": [city], "State": [state.upper()]})
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    st.cache_data.clear()  # Clear cache to reload fresh data
    return df

# Get unique locations
def get_unique_locations():
    df = load_data()
    if df.empty:
        return []
    unique = df[["City", "State"]].drop_duplicates()
    unique["Location"] = unique["City"] + ", " + unique["State"]
    return sorted(unique["Location"].tolist())

# Sidebar form for new entries
with st.sidebar:
    st.header("✍️ Add Your Location")
    with st.form(key="add_form"):
        name = st.text_input("Your Name")
        city = st.text_input("City")
        state = st.text_input("State (e.g., CA, NY, Texas)", max_chars=30)
        submitted = st.form_submit_button("Submit")

        if submitted:
            if not name.strip():
                st.error("Please enter your name!")
            elif not city.strip():
                st.error("Please enter your city!")
            elif not state.strip():
                st.error("Please enter your state!")
            else:
                add_entry(name.strip(), city.strip(), state.strip())
                st.success(f"Thank you, {name.split()[0]}! You've added {city}, {state.upper()}.")
                st.balloons()

# Main content
st.markdown("### 📍 Unique Represented Locations")

locations = get_unique_locations()

if locations:
    st.write(f"**{len(locations)} unique location(s) represented so far:**")
    # Display in nice columns
    cols = st.columns(3)
    for i, loc in enumerate(locations):
        cols[i % 3].write(f"• {loc}")
else:
    st.info("No locations added yet. Be the first one!")

# Optional: Show total entries count
df = load_data()
if not df.empty:
    st.markdown(f"---\n**Total entries:** {len(df)} people have contributed.")

# Footer
st.markdown("---")
st.caption("Made with ❤️ using Streamlit • Data is saved automatically")