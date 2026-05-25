# app.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import requests
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Nairobi Health Facilities Map",
    page_icon="🏥",
    layout="wide"
)

# Title and description
st.title("🏥 Nairobi Health Facilities Interactive Map")
st.markdown("Click on any hospital marker to see its name and details")

# Load the Excel file (assuming it's in the same directory or provide upload)
@st.cache_data
def load_data():
    """Load and combine all health facilities data from the Excel file"""
    file_path = "NS_HealthFacilities.xlsx"
    
    # Dictionary of sheet names and their corresponding sub-county
    sheets_data = {
        'Kasarani': 'Kasarani',
        'Ruaraka': 'Ruaraka',
        'Dagoretti South': 'Dagoretti South',
        'Langata': 'Langata',
        'Kibera': 'Kibera',
        'Roysambu': 'Roysambu',
        'Westlands': 'Westlands',
        'Dagoretti North': 'Dagoretti North'
    }
    
    all_facilities = []
    
    try:
        # Try to read the Excel file
        for sheet_name, sub_county in sheets_data.items():
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
                df['Sub-County'] = sub_county
                all_facilities.append(df)
            except Exception as e:
                st.warning(f"Could not read sheet {sheet_name}: {e}")
        
        if all_facilities:
            combined_df = pd.concat(all_facilities, ignore_index=True)
            return combined_df
        else:
            return None
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None

# Function to extract coordinates from location text using Nominatim
@st.cache_resource
def get_geocoder():
    """Initialize geocoder with user agent"""
    return Nominatim(user_agent="nairobi_health_facilities_map")

def geocode_address(address, sub_county, facility_name, geocoder, retries=3):
    """Geocode an address with retries and fallback to sub-county center"""
    # Clean up the address
    if pd.isna(address) or address == "" or address == ".":
        address = ""
    
    search_string = ""
    if address and address != "":
        search_string = f"{address}, {sub_county}, Nairobi, Kenya"
    else:
        search_string = f"{sub_county}, Nairobi, Kenya"
    
    # Add facility name for better matching
    search_string = f"{facility_name}, {search_string}"
    
    for attempt in range(retries):
        try:
            location = geocoder.geocode(search_string, timeout=10)
            if location:
                return (location.latitude, location.longitude)
            else:
                # Try with just sub-county
                location = geocoder.geocode(f"{sub_county}, Nairobi, Kenya", timeout=10)
                if location:
                    return (location.latitude, location.longitude)
            time.sleep(1)  # Rate limiting
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
    return None

def get_sub_county_center(sub_county):
    """Get approximate center coordinates for a sub-county"""
    centers = {
        'Kasarani': (-1.2245, 36.8762),
        'Ruaraka': (-1.2345, 36.8850),
        'Dagoretti South': (-1.2968, 36.7524),
        'Langata': (-1.3256, 36.7636),
        'Kibera': (-1.3125, 36.7875),
        'Roysambu': (-1.2145, 36.8850),
        'Westlands': (-1.2675, 36.8045),
        'Dagoretti North': (-1.2800, 36.7700)
    }
    return centers.get(sub_county, (-1.2833, 36.8167))  # Default Nairobi center

# Main function to create the map
def create_map(data_df):
    """Create a folium map with all facilities"""
    
    # Center of Nairobi
    nairobi_center = [-1.2833, 36.8167]
    
    # Create map
    m = folium.Map(
        location=nairobi_center,
        zoom_start=12,
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    # Add tile layers for reference
    folium.TileLayer('CartoDB positron', name='Light Map').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Dark Map').add_to(m)
    
    # Add fullscreen button
    folium.plugins.Fullscreen().add_to(m)
    
    # Create marker cluster group
    marker_cluster = MarkerCluster(
        name='All Facilities',
        overlay=True,
        control=True,
        icon_create_function=None
    ).add_to(m)
    
    # Color mapping for facility types
    type_colors = {
        'Public': 'green',
        'Private': 'blue',
        'Faith Based': 'purple',
        'NGO': 'orange',
        'Unknown': 'red'
    }
    
    # Counters for statistics
    facility_stats = {}
    
    # Add markers for each facility
    for idx, row in data_df.iterrows():
        facility_name = row.get('Facility Name', 'Unknown')
        facility_type = row.get('Type', 'Unknown')
        sub_county = row.get('Sub-County', 'Unknown')
        services = row.get('Services Offered', '')
        contact = row.get('Location / Contact', '')
        
        # Get coordinates (simplified - using sub-county centers for demo)
        # In production, you would use actual geocoded coordinates
        lat, lon = get_sub_county_center(sub_county)
        
        # Add some random offset to spread markers within sub-county
        import random
        random.seed(hash(facility_name) % 2**32)
        lat += random.uniform(-0.015, 0.015)
        lon += random.uniform(-0.015, 0.015)
        
        # Get color for marker
        color = type_colors.get(facility_type, 'red')
        
        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial; font-size: 14px; max-width: 300px;">
            <b style="font-size: 16px; color: #2c3e50;">🏥 {facility_name}</b><br>
            <hr style="margin: 5px 0;">
            <b>📍 Sub-County:</b> {sub_county}<br>
            <b>🏷️ Type:</b> {facility_type}<br>
            <b>📋 Services:</b><br>
            <div style="margin-left: 10px; font-size: 12px;">{str(services)[:200]}{'...' if len(str(services)) > 200 else ''}</div>
            <b>📞 Contact/Location:</b><br>
            <div style="margin-left: 10px; font-size: 12px;">{str(contact)[:150]}</div>
        </div>
        """
        
        # Create marker
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{facility_name} ({facility_type})",
            icon=folium.Icon(color=color, icon='plus', prefix='fa')
        ).add_to(marker_cluster)
        
        # Update statistics
        if facility_type not in facility_stats:
            facility_stats[facility_type] = 0
        facility_stats[facility_type] += 1
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; 
                background-color: white; 
                padding: 10px;
                border: 2px solid grey;
                border-radius: 5px;
                z-index: 1000;
                font-size: 12px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
        <b>Facility Types</b><br>
        <i class="fa fa-circle" style="color:green"></i> Public<br>
        <i class="fa fa-circle" style="color:blue"></i> Private<br>
        <i class="fa fa-circle" style="color:purple"></i> Faith Based<br>
        <i class="fa fa-circle" style="color:orange"></i> NGO<br>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m, facility_stats

# Alternative: Use OpenStreetMap Nominatim for geocoding (commented due to rate limits)
# def geocode_all_facilities(data_df):
#     """Geocode all facilities to get real coordinates"""
#     geocoder = get_geocoder()
#     geocode_with_retry = RateLimiter(geocoder.geocode, delay=1)
#     
#     coordinates = []
#     for idx, row in data_df.iterrows():
#         address = row.get('Location / Contact', '')
#         sub_county = row.get('Sub-County', '')
#         facility_name = row.get('Facility Name', '')
#         
#         coords = geocode_address(address, sub_county, facility_name, geocoder)
#         if coords:
#             coordinates.append(coords)
#         else:
#             coordinates.append(get_sub_county_center(sub_county))
#         time.sleep(1)
#     
#     return coordinates

def main():
    # Sidebar
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Data loading section
        st.subheader("📂 Data Source")
        
        # Option to upload file or use default
        uploaded_file = st.file_uploader(
            "Upload Excel file (optional)",
            type=['xlsx', 'xls'],
            help="Upload your own Excel file with health facility data"
        )
        
        if uploaded_file:
            # Load from uploaded file
            try:
                excel_data = pd.ExcelFile(uploaded_file)
                sheets_data = {}
                for sheet_name in excel_data.sheet_names:
                    if sheet_name != 'Overview':
                        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=1)
                        df['Sub-County'] = sheet_name
                        sheets_data[sheet_name] = df
                
                if sheets_data:
                    data_df = pd.concat(sheets_data.values(), ignore_index=True)
                    st.success(f"✅ Loaded {len(data_df)} facilities from uploaded file")
                else:
                    st.error("No facility data found in uploaded file")
                    data_df = None
            except Exception as e:
                st.error(f"Error reading uploaded file: {e}")
                data_df = None
        else:
            # Try to load default file
            data_df = load_data()
            if data_df is None:
                st.error("""
                Could not find the Excel file. Please:
                1. Make sure 'NS_HealthFacilities.xlsx' is in the same directory
                2. Or use the file uploader above to upload your Excel file
                """)
        
        if data_df is not None:
            # Display filters
            st.subheader("🏥 Filter Facilities")
            
            # Get unique values for filters
            facility_types = ['All'] + sorted(data_df['Type'].dropna().unique().tolist())
            sub_counties = ['All'] + sorted(data_df['Sub-County'].dropna().unique().tolist())
            
            # Type filter
            selected_type = st.selectbox("Facility Type", facility_types)
            
            # Sub-county filter
            selected_subcounty = st.selectbox("Sub-County", sub_counties)
            
            # Search by name
            search_term = st.text_input("🔎 Search by facility name", "")
            
            # Apply filters
            filtered_df = data_df.copy()
            
            if selected_type != 'All':
                filtered_df = filtered_df[filtered_df['Type'] == selected_type]
            
            if selected_subcounty != 'All':
                filtered_df = filtered_df[filtered_df['Sub-County'] == selected_subcounty]
            
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['Facility Name'].str.contains(search_term, case=False, na=False)
                ]
            
            st.metric("📊 Facilities Shown", len(filtered_df))
            
            # Statistics section
            st.subheader("📈 Statistics")
            stats = filtered_df['Type'].value_counts()
            for facility_type, count in stats.items():
                st.metric(facility_type, count)
    
    # Main content area
    if data_df is not None and len(filtered_df) > 0:
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "📋 Facilities List", "ℹ️ About"])
        
        with tab1:
            st.info("💡 Click on any marker to see the hospital name and details. Use the filters in the sidebar to narrow down facilities.")
            
            # Create and display map
            with st.spinner("Creating map..."):
                m, facility_stats = create_map(filtered_df)
                st_folium(m, width='100%', height=600)
        
        with tab2:
            # Display filtered data in a table
            st.subheader("Health Facilities List")
            
            # Select columns to display
            display_columns = ['Facility Name', 'Sub-County', 'Type', 'Services Offered']
            display_df = filtered_df[display_columns].copy()
            display_df.columns = ['Facility Name', 'Sub-County', 'Type', 'Services']
            
            # Add search within table
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400,
                column_config={
                    "Facility Name": st.column_config.TextColumn("Facility Name", width="medium"),
                    "Sub-County": st.column_config.TextColumn("Sub-County", width="small"),
                    "Type": st.column_config.TextColumn("Type", width="small"),
                    "Services": st.column_config.TextColumn("Services", width="large"),
                }
            )
            
            # Download button
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download filtered data as CSV",
                data=csv,
                file_name="nairobi_health_facilities.csv",
                mime="text/csv"
            )
        
        with tab3:
            st.subheader("About this Application")
            st.markdown("""
            ### 🏥 Nairobi Health Facilities Map
            
            This interactive map displays health facilities across Nairobi's sub-counties including:
            
            - **Kasarani**
            - **Ruaraka**
            - **Dagoretti South**
            - **Langata**
            - **Kibera**
            - **Roysambu**
            - **Westlands**
            - **Dagoretti North**
            
            ### Features:
            - Click on any marker to see facility details
            - Filter by facility type (Public, Private, Faith Based, NGO)
            - Filter by sub-county
            - Search for specific facilities by name
            - View facilities in list format
            - Download filtered data as CSV
            
            ### Facility Types:
            - 🟢 **Public**: Government-run facilities
            - 🔵 **Private**: Privately owned facilities
            - 🟣 **Faith Based**: Religious organization facilities
            - 🟠 **NGO**: Non-governmental organization facilities
            
            ### Note:
            Map markers are positioned based on sub-county centers for visualization purposes. 
            For exact coordinates, the actual addresses would need to be geocoded.
            """)
    
    elif data_df is None:
        st.warning("⚠️ Please upload the Excel file or ensure 'NS_HealthFacilities.xlsx' is in the current directory.")
    else:
        st.warning("⚠️ No facilities match your filter criteria. Please adjust your filters.")

if __name__ == "__main__":
    main()
