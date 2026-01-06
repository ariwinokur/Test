import streamlit as st
import pandas as pd
import os
import time

# Only import map-related libraries if we're going to use them
try:
    import folium
    from streamlit_folium import st_folium
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
    MAP_AVAILABLE = True
except ImportError:
    MAP_AVAILABLE = False

st.set_page_config(page_title="Location Collector", page_icon="🌍", layout="wide")

st.title("🌍 Location Collector")
st.markdown("Help build a list of all represented cities and states!")
st.markdown("*City is optional — leave blank if you just want to represent your state.*")

DATA_FILE = "locations.csv"

# Load data
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Name", "City", "State"])

# Save data
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Add entry
def add_entry(name, city, state):
    df = load_data()
    city = city.strip() if city else ""
    new_row = pd.DataFrame({"Name": [name], "City": [city], "State": [state.upper()]})
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    st.cache_data.clear()
    return df

# Create display string
def create_location_string(row):
    city = row['City'].strip() if pd.notna(row['City']) and row['City'].strip() else ""
    state = row['State'].upper()
    return f"{city}, {state}" if city else state

# Get unique locations with coordinates (only if map libs available)
if MAP_AVAILABLE:
    geolocator = Nominatim(user_agent="location_collector_app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    @st.cache_data(ttl=3600)
    def get_unique_locations_with_coords():
        df = load_data()
        if df.empty:
            return pd.DataFrame()
        
        df_copy = df.copy()
        df_copy["Location"] = df_copy.apply(create_location_string, axis=1)
        unique_df = df_copy[["Location", "City", "State"]].drop_duplicates().reset_index(drop=True)
        
        unique_df["query"] = unique_df.apply(
            lambda row: f"{row['City']}, {row['State']}, USA" if row['City'] else f"{row['State']}, USA",
            axis=1
        )
        
        unique_df["location_obj"] = unique_df["query"].apply(geocode)
        unique_df["lat"] = unique_df["location_obj"].apply(lambda x: x.latitude if x else None)
        unique_df["lon"] = unique_df["location_obj"].apply(lambda x: x.longitude if x else None)
        
        return unique_df.dropna(subset=["lat", "lon"])[["Location", "lat", "lon"]]
else:
    get_unique_locations_with_coords = lambda: pd.DataFrame()

# Sidebar form
with st.sidebar:
    st.header("✍️ Add Your Location")
    with st.form(key="add_form"):
        name = st.text_input("Your Name *", help="Required")
        city = st.text_input("City (optional)")
        state = st.text_input("State * (e.g., CA, Texas)", help="Required")
        submitted = st.form_submit_button("Submit")

        if submitted:
            name = name.strip()
            city = city.strip()
            state = state.strip().upper()

            if not name:
                st.error("Name is required!")
            elif not state:
                st.error("State is required!")
            else:
                add_entry(name, city, state)
                display = city if city else "(whole state)"
                st.success(f"Thank you, {name.split()[0]}! Added {display} of {state}.")
                st.balloons()
                time.sleep(1)
                st.rerun()

# Main: Map (if possible)
st.markdown("### 🗺️ Live Map of Represented Locations")

locations_df = get_unique_locations_with_coords()

if not locations_df.empty and MAP_AVAILABLE:
    center_lat = locations_df["lat"].mean()
    center_lon = locations_df["lon"].mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=4)

    from folium.plugins import MarkerCluster
    cluster = MarkerCluster().add_to(m)

    for _, row in locations_df.iterrows():
        folium.Marker(
            [row["lat"], row["lon"]],
            popup=row["Location"],
            tooltip=row["Location"],
            icon=folium.Icon(color="blue", icon="map-pin", prefix="fa")
        ).add_to(cluster)

    m.fit_bounds(cluster.get_bounds())

    st_folium(m, width=1200, height=600, returned_objects=[])
    st.write(f"**{len(locations_df)} unique location(s) on the map**")
elif MAP_AVAILABLE:
    st.info("No locations yet — add some to see the map!")
else:
    st.warning("Map feature unavailable (missing dependencies). List view active below.")

# List view
st.markdown("### 📍 All Unique Locations")
df = load_data()
if not df.empty:
    df_copy = df.copy()
    df_copy["Location"] = df_copy.apply(create_location_string, axis=1)
    unique_locations = sorted(df_copy["Location"].drop_duplicates().tolist())
    
    st.write(f"**{len(unique_locations)} unique location(s) represented:**")
    cols = st.columns(3)
    for i, loc in enumerate(unique_locations):
        cols[i % 3].write(f"• {loc}")
    
    st.markdown(f"---\n**Total contributions:** {len(df)} people")
else:
    st.info("No entries yet. Be the first!")

st.markdown("---")
st.caption("Made with ❤️ using Streamlit • Data saved automatically")