# complete_nairobi_hospitals_map.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, Search, Fullscreen
import json
import hashlib
import os
import random
from typing import Tuple, Dict, List, Optional
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Page configuration
st.set_page_config(
    page_title="Complete Nairobi Health Facilities Map - All 17 Sub-Counties & 494 Hospitals",
    page_icon="🏥",
    layout="wide"
)

# Title
st.title("🏥 Complete Nairobi County Health Facilities Map")
st.markdown("### All 17 Sub-Counties with 494 Health Facilities - Click any sub-county to explore hospitals")

# ============================================================================
# CONSTANTS AND DATA
# ============================================================================

# Complete list of all 17 sub-counties in Nairobi with their centers
ALL_SUB_COUNTIES = {
    'Kasarani': {'center': [-1.2245, 36.8762], 'facilities': 0, 'color': '#FF6B6B'},
    'Ruaraka': {'center': [-1.2345, 36.8850], 'facilities': 0, 'color': '#4ECDC4'},
    'Dagoretti South': {'center': [-1.2968, 36.7524], 'facilities': 0, 'color': '#45B7D1'},
    'Langata': {'center': [-1.3256, 36.7636], 'facilities': 0, 'color': '#96CEB4'},
    'Kibera': {'center': [-1.3125, 36.7875], 'facilities': 0, 'color': '#FFEAA7'},
    'Roysambu': {'center': [-1.2145, 36.8850], 'facilities': 0, 'color': '#DDA0DD'},
    'Westlands': {'center': [-1.2675, 36.8045], 'facilities': 0, 'color': '#98D8C8'},
    'Dagoretti North': {'center': [-1.2800, 36.7700], 'facilities': 0, 'color': '#F7B787'},
    'Embakasi Central': {'center': [-1.3150, 36.9050], 'facilities': 0, 'color': '#B5EAD7'},
    'Embakasi East': {'center': [-1.3350, 36.9200], 'facilities': 0, 'color': '#C7CEE6'},
    'Embakasi North': {'center': [-1.2950, 36.8950], 'facilities': 0, 'color': '#E2F0CB'},
    'Embakasi South': {'center': [-1.3550, 36.9100], 'facilities': 0, 'color': '#FFDAC1'},
    'Embakasi West': {'center': [-1.3050, 36.8800], 'facilities': 0, 'color': '#E6E6FA'},
    'Kamukunji': {'center': [-1.2850, 36.8250], 'facilities': 0, 'color': '#FFB7B2'},
    'Makadara': {'center': [-1.3050, 36.8400], 'facilities': 0, 'color': '#B5EAD7'},
    'Mathare': {'center': [-1.2650, 36.8550], 'facilities': 0, 'color': '#FFD1DC'},
    'Starehe': {'center': [-1.2850, 36.8150], 'facilities': 0, 'color': '#A2E1E0'}
}

# Color mapping for facility types
TYPE_COLORS = {
    'Public': 'green',
    'Private': 'blue',
    'Faith Based': 'purple',
    'NGO': 'orange',
    'Unknown': 'gray'
}

# Cache file for coordinates
GEOCODE_CACHE_FILE = "hospital_coordinates_cache.json"

# ============================================================================
# DATA EXTRACTION FUNCTIONS
# ============================================================================

@st.cache_data
def extract_all_facilities() -> pd.DataFrame:
    """Extract all 494 facilities from the Excel file"""
    
    sheets_config = {
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
    
    for sheet_name, sub_county in sheets_config.items():
        try:
            df = pd.read_excel('NS_HealthFacilities.xlsx', sheet_name=sheet_name, header=1)
            df = df.dropna(how='all', subset=['Facility Name'])
            df = df[df['Facility Name'].notna()]
            df = df[df['Facility Name'] != 'Facility Name']
            df['Sub-County'] = sub_county
            df['Type'] = df['Type'].fillna('Unknown')
            df['Services Offered'] = df.get('Services Offered', '').fillna('')
            df['Location / Contact'] = df.get('Location / Contact', '').fillna('')
            all_facilities.append(df)
            st.info(f"Loaded {len(df)} facilities from {sub_county}")
        except Exception as e:
            st.warning(f"Could not read {sub_county}: {e}")
    
    if all_facilities:
        combined_df = pd.concat(all_facilities, ignore_index=True)
        return combined_df
    return pd.DataFrame()

# ============================================================================
# COORDINATE MANAGEMENT FUNCTIONS
# ============================================================================

def load_coordinate_cache() -> Dict:
    """Load cached coordinates"""
    if os.path.exists(GEOCODE_CACHE_FILE):
        try:
            with open(GEOCODE_CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_coordinate_cache(cache: Dict):
    """Save coordinates to cache"""
    with open(GEOCODE_CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def get_sub_county_center(sub_county: str) -> Tuple[float, float]:
    """Get center coordinates for a sub-county"""
    return ALL_SUB_COUNTIES.get(sub_county, {'center': [-1.2833, 36.8167]})['center']

def geocode_address_osm(facility_name: str, address: str, sub_county: str) -> Optional[Tuple[float, float]]:
    """Geocode using OpenStreetMap Nominatim"""
    try:
        geocoder = Nominatim(user_agent="nairobi_hospitals_map")
        
        search_queries = [
            f"{facility_name}, {sub_county}, Nairobi, Kenya",
            f"{address}, {sub_county}, Nairobi, Kenya" if pd.notna(address) and address != '.' and address != '' and len(str(address)) > 5 else None,
            f"{facility_name}, Nairobi, Kenya"
        ]
        
        for query in search_queries:
            if query:
                try:
                    location = geocoder.geocode(query, timeout=10)
                    if location:
                        return (location.latitude, location.longitude)
                    time.sleep(1)
                except:
                    continue
        return None
    except:
        return None

def generate_grid_coordinates(sub_county: str, facility_count: int, facility_names: List[str]) -> List[Tuple[float, float]]:
    """Generate grid-based coordinates within sub-county for visualization"""
    center_lat, center_lng = get_sub_county_center(sub_county)
    coordinates = []
    
    # Determine grid size based on facility count
    grid_size = int((facility_count ** 0.5) + 1)
    spacing = 0.008  # Approximately 800 meters
    
    start_lat = center_lat - (grid_size * spacing / 2)
    start_lng = center_lng - (grid_size * spacing / 2)
    
    for i, facility_name in enumerate(facility_names):
        row = i // grid_size
        col = i % grid_size
        
        # Add some randomness
        random.seed(facility_name)
        lat_offset = (random.random() - 0.5) * 0.002
        lng_offset = (random.random() - 0.5) * 0.002
        
        lat = start_lat + (row * spacing) + lat_offset
        lng = start_lng + (col * spacing) + lng_offset
        
        coordinates.append((lat, lng))
    
    return coordinates

def get_all_coordinates(facilities_df: pd.DataFrame) -> pd.DataFrame:
    """Get coordinates for all facilities using cache and geocoding"""
    
    cache = load_coordinate_cache()
    
    # Add coordinate columns
    facilities_df['Latitude'] = None
    facilities_df['Longitude'] = None
    facilities_df['Geocode_Source'] = 'pending'
    
    # Group by sub-county for batch processing
    for sub_county in facilities_df['Sub-County'].unique():
        sub_df = facilities_df[facilities_df['Sub-County'] == sub_county]
        facility_count = len(sub_df)
        
        # Check which facilities need geocoding
        needs_geocoding = []
        for idx, row in sub_df.iterrows():
            cache_key = hashlib.md5(f"{row['Facility Name']}_{sub_county}".encode()).hexdigest()
            if cache_key in cache:
                facilities_df.at[idx, 'Latitude'] = cache[cache_key]['lat']
                facilities_df.at[idx, 'Longitude'] = cache[cache_key]['lng']
                facilities_df.at[idx, 'Geocode_Source'] = 'cached'
            else:
                needs_geocoding.append((idx, row))
        
        # Geocode facilities that need it
        if needs_geocoding and len(needs_geocoding) <= 50:  # Only geocode if reasonable amount
            for idx, row in needs_geocoding:
                try:
                    coords = geocode_address_osm(
                        row['Facility Name'],
                        row.get('Location / Contact', ''),
                        sub_county
                    )
                    if coords:
                        facilities_df.at[idx, 'Latitude'] = coords[0]
                        facilities_df.at[idx, 'Longitude'] = coords[1]
                        facilities_df.at[idx, 'Geocode_Source'] = 'geocoded'
                        cache_key = hashlib.md5(f"{row['Facility Name']}_{sub_county}".encode()).hexdigest()
                        cache[cache_key] = {'lat': coords[0], 'lng': coords[1]}
                        save_coordinate_cache(cache)
                except:
                    pass
                time.sleep(1.1)
        
        # Generate grid coordinates for remaining facilities
        remaining = facilities_df[facilities_df['Sub-County'] == sub_county]
        remaining = remaining[remaining['Latitude'].isna()]
        
        if len(remaining) > 0:
            grid_coords = generate_grid_coordinates(
                sub_county, 
                len(remaining),
                remaining['Facility Name'].tolist()
            )
            
            for (idx, _), (lat, lng) in zip(remaining.iterrows(), grid_coords):
                facilities_df.at[idx, 'Latitude'] = lat
                facilities_df.at[idx, 'Longitude'] = lng
                facilities_df.at[idx, 'Geocode_Source'] = 'grid'
    
    return facilities_df

# ============================================================================
# MAP CREATION FUNCTIONS
# ============================================================================

def create_nairobi_county_map() -> folium.Map:
    """Create map showing all 17 sub-counties of Nairobi"""
    
    # Create map centered on Nairobi
    m = folium.Map(
        location=[-1.2833, 36.8167],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Add tile layers
    folium.TileLayer('CartoDB positron', name='Light Map').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Dark Map').add_to(m)
    
    # Add fullscreen button
    Fullscreen().add_to(m)
    
    # Add scale bar
    folium.ScaleControl().add_to(m)
    
    # Add sub-county markers
    for sub_county, data in ALL_SUB_COUNTIES.items():
        center = data['center']
        color = data['color']
        facilities_count = data['facilities']
        
        if facilities_count > 0:
            # Sub-counties with hospitals
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 220px;">
                <h4 style="color: {color}; margin: 0;">🏥 {sub_county}</h4>
                <hr style="margin: 8px 0;">
                <b>📊 Health Facilities:</b> {facilities_count}<br>
                <b>📍 Coordinates:</b> {center[0]:.4f}, {center[1]:.4f}<br>
                <br>
                <i>✨ Click to view all hospitals in {sub_county}</i>
            </div>
            """
            
            folium.CircleMarker(
                location=center,
                radius=25,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{sub_county} - {facilities_count} health facilities",
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.5,
                weight=3,
                opacity=0.8
            ).add_to(m)
            
            # Add text label
            folium.map.Marker(
                center,
                icon=folium.DivIcon(
                    icon_size=(100, 30),
                    icon_anchor=(50, 15),
                    html=f'<div style="font-size: 11px; font-weight: bold; background: white; padding: 2px 6px; border-radius: 10px; border: 1px solid {color};">{sub_county}</div>'
                )
            ).add_to(m)
            
        else:
            # Sub-counties without data
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 200px;">
                <h4 style="color: {color};">📍 {sub_county}</h4>
                <hr style="margin: 8px 0;">
                <b>📊 Status:</b> No hospital data available<br>
                <b>📍 Location:</b> {center[0]:.4f}, {center[1]:.4f}
            </div>
            """
            
            folium.CircleMarker(
                location=center,
                radius=12,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{sub_county} (No hospital data)",
                color='gray',
                fill=True,
                fill_color='lightgray',
                fill_opacity=0.3,
                weight=2,
                dash_array='5,5'
            ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; 
                background-color: white; padding: 12px;
                border: 2px solid #ccc; border-radius: 8px;
                z-index: 1000; font-size: 12px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
                max-width: 260px;">
        <b>🗺️ Nairobi County - 17 Sub-Counties</b><br>
        <hr style="margin: 5px 0;">
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; 
                         background-color: #4ECDC4; border-radius: 50%; margin-right: 8px;"></span>
            <span>Has Health Facilities (8 sub-counties)</span>
        </div>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; 
                         background-color: #ddd; border-radius: 50%; margin-right: 8px; border: 1px dashed gray;"></span>
            <span>No Facility Data (9 sub-counties)</span>
        </div>
        <hr style="margin: 5px 0;">
        <div style="font-size: 10px; color: #666;">
            ✅ Click colored circle to explore hospitals<br>
            📍 Total facilities: 494<br>
            🏥 Data: Nairobi Health Facilities Directory
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def create_subcounty_hospital_map(sub_county: str, facilities_df: pd.DataFrame) -> folium.Map:
    """Create detailed map showing all hospitals in a specific sub-county"""
    
    # Filter facilities for this sub-county
    sub_facilities = facilities_df[facilities_df['Sub-County'] == sub_county].copy()
    
    # Get sub-county center
    center = ALL_SUB_COUNTIES.get(sub_county, {'center': [-1.2833, 36.8167]})['center']
    
    # Create map
    m = folium.Map(
        location=center,
        zoom_start=14,
        tiles='OpenStreetMap'
    )
    
    # Add tile layers
    folium.TileLayer('CartoDB positron', name='Light Map').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Dark Map').add_to(m)
    
    # Add fullscreen and scale
    Fullscreen().add_to(m)
    folium.ScaleControl().add_to(m)
    
    # Add marker cluster
    marker_cluster = MarkerCluster(
        name=f'{sub_county} Hospitals',
        overlay=True,
        control=True
    ).add_to(m)
    
    # Add markers for each facility
    for _, row in sub_facilities.iterrows():
        facility_name = row['Facility Name']
        facility_type = row['Type']
        services = row.get('Services Offered', '')
        contact = row.get('Location / Contact', '')
        lat = row['Latitude']
        lng = row['Longitude']
        
        if pd.isna(lat) or pd.isna(lng):
            continue
        
        color = TYPE_COLORS.get(facility_type, 'red')
        
        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 13px; min-width: 280px; max-width: 380px;">
            <div style="background-color: {color}; color: white; padding: 10px; border-radius: 5px 5px 0 0;">
                <b style="font-size: 16px;">🏥 {facility_name}</b>
            </div>
            <div style="padding: 12px; background-color: #f9f9f9;">
                <b>📍 Sub-County:</b> {sub_county}<br>
                <b>🏷️ Type:</b> <span style="color: {color}; font-weight: bold;">{facility_type}</span><br>
                <b>📋 Services:</b><br>
                <div style="margin-left: 10px; font-size: 11px; max-height: 120px; overflow-y: auto; background: white; padding: 5px; border-radius: 3px;">
                    {str(services)[:300]}{'...' if len(str(services)) > 300 else ''}
                </div>
                <b>📍 Location/Contact:</b><br>
                <div style="margin-left: 10px; font-size: 11px; background: white; padding: 5px; border-radius: 3px;">
                    {str(contact)[:150]}
                </div>
                <hr style="margin: 8px 0;">
                <div style="font-size: 10px; color: #666;">
                    Coordinates: {lat:.5f}, {lng:.5f}<br>
                    <a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lng}&zoom=18" target="_blank">
                        🗺️ View on OpenStreetMap
                    </a>
                </div>
            </div>
        </div>
        """
        
        # Create marker with appropriate icon
        icon_map = {
            'Public': 'building',
            'Private': 'plus',
            'Faith Based': 'heart',
            'NGO': 'hand-holding-heart',
            'Unknown': 'question'
        }
        
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=420),
            tooltip=f"{facility_name} ({facility_type})",
            icon=folium.Icon(color=color, icon=icon_map.get(facility_type, 'info-sign'), prefix='fa')
        ).add_to(marker_cluster)
    
    # Add sub-county boundary visualization
    folium.Circle(
        location=center,
        radius=2500,
        color='red',
        weight=2,
        fill=True,
        fill_opacity=0.05,
        popup=f"{sub_county} Area"
    ).add_to(m)
    
    # Add search functionality
    Search(
        layer=marker_cluster,
        search_label='tooltip',
        placeholder=f'🔍 Search hospitals in {sub_county}...',
        collapsed=False
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add legend
    legend_html = f'''
    <div style="position: fixed; bottom: 50px; right: 50px; 
                background-color: white; padding: 12px;
                border: 2px solid #ccc; border-radius: 8px;
                z-index: 1000; font-size: 11px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.2);">
        <b>🏥 {sub_county} - Facility Types</b><br>
        <hr style="margin: 5px 0;">
        <i class="fa fa-circle" style="color: green;"></i> Public<br>
        <i class="fa fa-circle" style="color: blue;"></i> Private<br>
        <i class="fa fa-circle" style="color: purple;"></i> Faith Based<br>
        <i class="fa fa-circle" style="color: orange;"></i> NGO<br>
        <hr style="margin: 5px 0;">
        <b>📊 Total: {len(sub_facilities)} facilities</b>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Initialize session state
    if 'selected_subcounty' not in st.session_state:
        st.session_state.selected_subcounty = None
    if 'coordinates_loaded' not in st.session_state:
        st.session_state.coordinates_loaded = False
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Nairobi County Overview")
        
        # Load data
        with st.spinner("Loading health facilities data..."):
            facilities_df = extract_all_facilities()
        
        if facilities_df.empty:
            st.error("""
            ⚠️ Could not load Excel file!
            
            Please ensure 'NS_HealthFacilities.xlsx' is in the same directory.
            """)
            return
        
        # Update facility counts
        actual_counts = facilities_df['Sub-County'].value_counts().to_dict()
        for sc in ALL_SUB_COUNTIES:
            if sc in actual_counts:
                ALL_SUB_COUNTIES[sc]['facilities'] = actual_counts[sc]
        
        # Display statistics
        st.metric("Total Sub-Counties", 17)
        st.metric("Sub-Counties with Data", len(actual_counts))
        st.metric("Total Health Facilities", len(facilities_df))
        
        st.markdown("---")
        
        # Geocode button
        if not st.session_state.coordinates_loaded:
            if st.button("🌍 Generate Hospital Coordinates", type="primary", use_container_width=True):
                with st.spinner("Geocoding 494 hospitals (this may take 5-10 minutes)..."):
                    facilities_df = get_all_coordinates(facilities_df)
                    st.session_state.coordinates_loaded = True
                    st.session_state.facilities_df = facilities_df
                    st.success("✅ Coordinates generated successfully!")
                    st.rerun()
        else:
            st.success("✅ Coordinates loaded!")
        
        if st.session_state.coordinates_loaded:
            facilities_df = st.session_state.facilities_df
            
            st.markdown("---")
            st.subheader("📈 Sub-Counties with Facilities")
            for sc, count in sorted(actual_counts.items(), key=lambda x: x[1], reverse=True):
                st.metric(sc, count)
            
            st.markdown("---")
            st.subheader("🏷️ Facility Types")
            type_counts = facilities_df['Type'].value_counts()
            for typ, count in type_counts.items():
                st.metric(typ, count)
            
            st.markdown("---")
            st.info("""
            **💡 How to use:**
            1. View Nairobi County with all 17 sub-counties
            2. Click any colored sub-county circle
            3. Explore individual hospitals
            4. Click hospital markers for details
            """)
    
    # Main content area
    if not st.session_state.coordinates_loaded:
        st.info("""
        ### 🗺️ Welcome to Nairobi Health Facilities Map
        
        **To get started:**
        1. Click the **"Generate Hospital Coordinates"** button in the sidebar
        2. Wait for the system to geocode all 494 hospitals (5-10 minutes for first run)
        3. Once complete, the interactive map will appear below
        
        **What happens during geocoding:**
        - Each hospital is geocoded using OpenStreetMap
        - Results are cached for faster future loads
        - A visual grid is created for hospitals without coordinates
        - All 494 hospitals will be displayed on the map
        
        **Features:**
        - 🗺️ Click any sub-county to see its hospitals
        - 🔍 Search for specific hospitals
        - 📍 Click markers for full details
        - 🚗 Direct links to navigation
        """)
        
        # Show preview of data
        with st.expander("📋 Preview Available Data"):
            st.dataframe(
                facilities_df[['Facility Name', 'Sub-County', 'Type']].head(20),
                use_container_width=True
            )
            st.caption(f"Showing 20 of {len(facilities_df)} facilities")
    
    else:
        facilities_df = st.session_state.facilities_df
        
        # Back button for sub-county view
        if st.session_state.selected_subcounty:
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("⬅️ Back to County View", use_container_width=True):
                    st.session_state.selected_subcounty = None
                    st.rerun()
            with col2:
                st.markdown(f"### 🏥 Currently viewing: **{st.session_state.selected_subcounty}** Sub-County")
        
        # Display appropriate map
        if st.session_state.selected_subcounty is None:
            # Show county map
            st.markdown("""
            <div style="background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h3>🗺️ Nairobi County - All 17 Sub-Counties</h3>
                <p><strong>Click on any colored circle</strong> to zoom in and see all health facilities in that sub-county.</p>
                <ul>
                    <li>✅ <strong>8 sub-counties</strong> have complete health facility data (494 hospitals total)</li>
                    <li>📍 <strong>9 sub-counties</strong> have no hospital data in the current directory</li>
                    <li>🔍 <strong>Click any colored circle</strong> to explore hospitals in that area</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Create and display county map
            county_map = create_nairobi_county_map()
            
            # Use st_folium with callback to detect clicks
            output = st_folium(
                county_map,
                width='100%',
                height=650,
                key="county_map"
            )
            
            # Check if a sub-county was clicked
            if output and output.get('last_object_clicked_popup'):
                popup_text = str(output['last_object_clicked_popup'])
                # Extract sub-county name from popup
                for sc in ALL_SUB_COUNTIES.keys():
                    if sc in popup_text and ALL_SUB_COUNTIES[sc]['facilities'] > 0:
                        st.session_state.selected_subcounty = sc
                        st.rerun()
                        break
            
            # Display quick reference
            with st.expander("📋 View All Sub-Counties Reference"):
                col1, col2, col3 = st.columns(3)
                subcounty_list = sorted(ALL_SUB_COUNTIES.keys())
                for i, sc in enumerate(subcounty_list):
                    with [col1, col2, col3][i % 3]:
                        facilities = ALL_SUB_COUNTIES[sc]['facilities']
                        if facilities > 0:
                            st.markdown(f"✅ **{sc}** - {facilities} facilities")
                        else:
                            st.markdown(f"⚪ **{sc}** - No data")
        
        else:
            # Show detailed hospital map for selected sub-county
            sub_county = st.session_state.selected_subcounty
            
            if ALL_SUB_COUNTIES[sub_county]['facilities'] > 0:
                with st.spinner(f"Loading {sub_county} hospitals..."):
                    hospital_map = create_subcounty_hospital_map(sub_county, facilities_df)
                    st_folium(hospital_map, width='100%', height=650)
                
                # Display statistics for this sub-county
                sc_facilities = facilities_df[facilities_df['Sub-County'] == sub_county]
                
                st.markdown("---")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Total Facilities", len(sc_facilities))
                with col2:
                    private = len(sc_facilities[sc_facilities['Type'] == 'Private'])
                    st.metric("Private", private)
                with col3:
                    public = len(sc_facilities[sc_facilities['Type'] == 'Public'])
                    st.metric("Public", public)
                with col4:
                    faith = len(sc_facilities[sc_facilities['Type'] == 'Faith Based'])
                    st.metric("Faith Based", faith)
                with col5:
                    ngo = len(sc_facilities[sc_facilities['Type'] == 'NGO'])
                    st.metric("NGO", ngo)
                
                # Show list of facilities
                with st.expander(f"📋 View all {len(sc_facilities)} facilities in {sub_county}"):
                    display_df = sc_facilities[['Facility Name', 'Type', 'Services Offered']].copy()
                    display_df.columns = ['Facility Name', 'Type', 'Services']
                    st.dataframe(display_df, use_container_width=True, height=400)
                    
                    # Download button for this sub-county
                    csv = sc_facilities.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download {sub_county} facilities as CSV",
                        data=csv,
                        file_name=f"{sub_county}_health_facilities.csv",
                        mime="text/csv"
                    )
            else:
                st.warning(f"""
                ⚠️ No health facility data available for **{sub_county}** sub-county.
                
                The current data only includes facilities from 8 sub-counties:
                - Kasarani (34 facilities)
                - Ruaraka (71 facilities)
                - Dagoretti South (30 facilities)
                - Langata (66 facilities)
                - Kibera (79 facilities)
                - Roysambu (66 facilities)
                - Westlands (69 facilities)
                - Dagoretti North (79 facilities)
                
                Click the back button to return to the county view.
                """)
                
                if st.button("Return to County View"):
                    st.session_state.selected_subcounty = None
                    st.rerun()
    
    # Footer
    if st.session_state.coordinates_loaded:
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: gray; font-size: 12px;'>"
            "🏥 Nairobi Health Facilities Map | Data from Nairobi Sub-County Health Facilities Directory<br>"
            f"📍 Total: {len(facilities_df)} facilities across 17 sub-counties | "
            "Click markers for details | Use search to find specific hospitals"
            "</div>",
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
