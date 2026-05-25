# nairobi_health_facilities_complete.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, Search, Fullscreen
import random
from typing import Tuple, Dict, List

# Page configuration
st.set_page_config(
    page_title="Nairobi Health Facilities Map - 494 Hospitals Across 17 Sub-Counties",
    page_icon="🏥",
    layout="wide"
)

# Title
st.title("🏥 Nairobi County Health Facilities Map")
st.markdown("### Complete Directory: 494 Health Facilities Across 17 Sub-Counties")

# ============================================================================
# COMPLETE FACILITIES DATA WITH COORDINATES
# ============================================================================

# All 17 sub-counties of Nairobi with their center coordinates
SUB_COUNTY_CENTERS = {
    'Kasarani': [-1.2245, 36.8762],
    'Ruaraka': [-1.2345, 36.8850],
    'Dagoretti South': [-1.2968, 36.7524],
    'Langata': [-1.3256, 36.7636],
    'Kibera': [-1.3125, 36.7875],
    'Roysambu': [-1.2145, 36.8850],
    'Westlands': [-1.2675, 36.8045],
    'Dagoretti North': [-1.2800, 36.7700],
    'Embakasi Central': [-1.3150, 36.9050],
    'Embakasi East': [-1.3350, 36.9200],
    'Embakasi North': [-1.2950, 36.8950],
    'Embakasi South': [-1.3550, 36.9100],
    'Embakasi West': [-1.3050, 36.8800],
    'Kamukunji': [-1.2850, 36.8250],
    'Makadara': [-1.3050, 36.8400],
    'Mathare': [-1.2650, 36.8550],
    'Starehe': [-1.2850, 36.8150]
}

# Complete facilities data with coordinates (generated programmatically)
def generate_facilities_data():
    """Generate complete facilities data with realistic coordinates"""
    
    facilities = []
    
    # Kasarani facilities (34)
    kasarani_facilities = [
        ("Kasarani Claycity Medical Centre", "Private"),
        ("Children Medical Clinic", "Private"),
        ("Jeytee", "Private"),
        ("St Francis Community Hospital", "Faith Based"),
        ("Shiply Medical Centre & Lab", "Private"),
        ("St Peter Dispensary", "Faith Based"),
        ("Hunters Medical Clinic", "Private"),
        ("Mugumo Medical", "Private"),
        ("Radiant Hosp Kasarani", "Private"),
        ("Flomed Med Clinic", "Private"),
        ("Kasarani Health Centre", "Public"),
        ("Loreigns Medical Services", "Private"),
        ("Denticheck Clinical Services", "Private"),
        ("Shekina Medical Clinic", "Faith Based"),
        ("Thika Road Health Services Ltd", "Private"),
        ("Kasarani Medical Health Centre", "Private"),
        ("Kwetu Medical Clinic", "Private"),
        ("Sunton CFW Clinic", "NGO"),
        ("Kenya Institute of Special Education Dispensary", "Public"),
        ("Horeb Medical Clinic", "Faith Based"),
        ("Good Samaritan Dispensary", "Faith Based"),
        ("Kasarani Maternity", "Private"),
        ("Prescort Dispensary", "Private"),
        ("Family Care Clinic Kasarani", "Private"),
        ("Karma Dispensary", "Private"),
        ("Sam-link Medical Centre", "Private"),
        ("Maximum Medical Centre", "Private"),
        ("Med-Point Dispensary", "Private"),
        ("Lea Toto", "NGO"),
        ("Kariobangi EDARP", "NGO"),
        ("Nuffield Nursing Home", "Private"),
        ("St Francis Com Hospital", "Faith Based"),
        ("AAR Kariobangi Clinic", "Private"),
        ("AAR Thika Road Clinic", "Private"),
    ]
    
    # Ruaraka facilities (71)
    ruaraka_facilities = [
        ("Ruaraka Clinic", "Public"),
        ("Destiny Medical Centre", "Private"),
        ("Kenya Utalii Dispensary", "Public"),
        ("Kariobangi Health Centre", "Public"),
        ("Kahawa Garrison Health Centre", "Public"),
        ("Compassionate Hospital", "Faith Based"),
        ("Corner Stone", "Private"),
        ("Round About Medical Dispensary", "Private"),
        ("Nimoli Medical Centre", "Private"),
        ("Kipawa Medical Centre", "Private"),
        ("Provide International Korogocho", "NGO"),
        ("Ruai Community Clinic", "Private"),
        ("Kasarani Dispensary", "Public"),
        ("Maria Medical Clinic & Diadetic Centre", "Faith Based"),
        ("Madaktari Health Clinic", "Private"),
        ("Kwetu Home Of Peace Dispensary", "Faith Based"),
        ("Kinmed Medical Clinic", "Private"),
        ("Rosadett Medical Clinic", "Private"),
        ("Ruai SDA Clinic", "Faith Based"),
        ("St Vincent Clinic", "Faith Based"),
        ("Kasarani Medical Clinic", "Private"),
        ("KWOSP", "NGO"),
        ("Karomo Medical Clinic", "Private"),
        ("EDARP Njiru Clinic", "NGO"),
        ("Mundoro Medical Clinic", "Private"),
        ("Newlight Medical Centre", "Private"),
        ("Hope Medical Clinic", "Private"),
        ("Nsis Health Centre", "Public"),
        ("Bar Hostess Empowerment Support Program VCT", "NGO"),
        ("The Arcade Medical Centre", "Private"),
        ("Delight Chemist & Lab", "Private"),
        ("Babito Medical Centre", "Private"),
        ("Unmet Health Foundation", "NGO"),
        ("Provide Inter Math Dispensary", "NGO"),
        ("Baraka Dispensary", "Faith Based"),
        ("Piemu Medical Health Centre", "Private"),
        ("Aimon Med Clinic", "Private"),
        ("Vision Peoples Inter Health Centre", "NGO"),
        ("Drugnet Medical Centre", "Private"),
        ("Baraka Medical Centre", "Faith Based"),
        ("Babadogo EDARP", "NGO"),
        ("Ngumba Medical Centre", "Private"),
        ("Tibaland Chemistry & Lab", "Private"),
        ("Ruaraka Uhai Neema Hospital", "Private"),
        ("Tumaini Mwangaza", "NGO"),
        ("Babadogo Health Centre", "Public"),
        ("St Patrick Medical Centre", "Faith Based"),
        ("Family Access Medical Centre", "Private"),
        ("Peace Medical Clinic", "Private"),
        ("Mathare North Health Centre", "Public"),
        ("Pona Mat Dispensary", "Private"),
        ("Swop Korogocho", "NGO"),
        ("Marura Nursing Home", "Private"),
        ("Crescent Medical Aid Kenya Korogocho Clinic", "NGO"),
        ("Babadogo Medical Health Centre", "Public"),
        ("Redeemed Health Centre", "Faith Based"),
        ("National Youth Service HQ Dispensary", "Public"),
        ("GSU HQ Dispensary", "Public"),
        ("Mwangaza Ulio Na Tumaini Clinic", "NGO"),
        ("Warazo Clinic", "Private"),
        ("Comboni Missionary Sisters Health Program", "Faith Based"),
        ("Ogwedhi Dispensary", "Public"),
        ("Kamiti Prison Hospital", "Public"),
        ("PSTC Health Centre", "Public"),
        ("Swop Thika Road", "NGO"),
        ("Imani Medical Clinic", "Faith Based"),
        ("Cordis Maria Dispensary", "Faith Based"),
        ("St James Medical Centre", "Faith Based"),
        ("Zimmerman Medical Dispensary", "Public"),
        ("Piemu Medical Clinic", "Private"),
        ("Focus Medical Clinic and Counselling Centre", "Private"),
    ]
    
    # Dagoretti South facilities (30)
    dagoretti_south_facilities = [
        ("Dagoretti Approved Dispensary", "Public"),
        ("Dagoretti Community Dispensary", "Public"),
        ("Orient Medical Care", "Private"),
        ("Abandoned Child Care", "NGO"),
        ("St Michael Clinic", "Faith Based"),
        ("Good Shepherd Dispensary", "Faith Based"),
        ("Lea Toto Dagoretti", "NGO"),
        ("Mutuini Sub-District Hospital", "Public"),
        ("Hope Community VCT", "NGO"),
        ("Nile Medical Care", "Private"),
        ("St Joseph's Dispensary", "Faith Based"),
        ("Uthiru Muthua Dispensary", "Public"),
        ("St Lukes (Kona) Health Centre", "Faith Based"),
        ("Chandaria Health Centre", "Private"),
        ("Orthodox Dispensary", "Faith Based"),
        ("Lea Toto Kawangware", "NGO"),
        ("Glory Health Clinic", "Faith Based"),
        ("Swop Kawangware", "NGO"),
        ("Uzima VCT Centre", "NGO"),
        ("Kivuli Dispensary", "Public"),
        ("Providence Whole Care", "Faith Based"),
        ("Mary Mission", "Faith Based"),
        ("Tumaini Africa", "NGO"),
        ("Waithaka Health Centre", "Public"),
        ("Imani Health Services", "Private"),
        ("Fremo Medical Centre", "Private"),
        ("R-Care Health Clinic", "Private"),
        ("Miliki Afya Limited", "Private"),
        ("St Anns Medical Centre", "Faith Based"),
        ("Gachui Medical Centre", "Private"),
    ]
    
    # Langata facilities (66)
    langata_facilities = [
        ("Catholic University Dispensary", "Faith Based"),
        ("Marist International University College Medical Clinic", "Faith Based"),
        ("CMIA Grace Children's Centre Dispensary", "Faith Based"),
        ("PCEA Kuwinda Health Clinic", "Faith Based"),
        ("Wellness Program KWS HQ", "Public"),
        ("Zinduka Clinic", "Private"),
        ("KTTID Dispensary", "Public"),
        ("Port Health Dispensary", "Public"),
        ("The Nairobi Hospital Out-Patient Centre Galeria", "Private"),
        ("The Zambezi Hospital Limited", "Private"),
        ("Karengata Community Medical Centre", "Private"),
        ("Beyond the Bridge Vision VCT", "NGO"),
        ("Kikoshep Kenya", "NGO"),
        ("All Care Medical Centre", "Private"),
        ("St. Catherine Catholic Church VCT", "Faith Based"),
        ("Dreams Centre Dispensary", "NGO"),
        ("Langata Hospital", "Private"),
        ("Langata Women Prison Dispensary", "Public"),
        ("AAR Healthcare Limited", "Private"),
        ("Langata Health Centre", "Public"),
        ("The Aga Khan University Hospital T Mall", "Private"),
        ("Lakeside Medical", "Private"),
        ("Rainbow Clinic", "Private"),
        ("Bomas of Kenya Dispensary", "Public"),
        ("Marie Stopes Clinic", "NGO"),
        ("Healthways Medical Centre", "Private"),
        ("Medical and Dental Clinic", "Private"),
        ("St Eliza Medical Clinic", "Faith Based"),
        ("Dr Barnados House Clinic", "Private"),
        ("Shalome Medical Clinic", "Faith Based"),
        ("Maria Dominica Dispensary", "Faith Based"),
        ("Lang'ata Comprehensive Medical Service", "Private"),
        ("Dog Unit Dispensary (Kenya Police)", "Public"),
        ("3KL Maternity & Nursing Home", "Private"),
        ("Melchizedek Hospital Karen", "Faith Based"),
        ("Multi Media University Dispensary", "Public"),
        ("Southern Health Care", "Private"),
        ("SGRR Medical Clinic", "Private"),
        ("St Aloysius Gonzaga School Dispensary", "Faith Based"),
        ("Eagle Wings Medical Centre", "Private"),
        ("Jinnah Ave Clinic", "Private"),
        ("Langata Enkima Dispensary", "Public"),
        ("Nairobi West Men's Prison Dispensary", "Public"),
        ("Strathmore University Medical Centre", "Private"),
        ("The Co-Operative University College of Kenya Dispensary", "Public"),
        ("Clinix Health Care", "Private"),
        ("Shree Cutchhi Leva Samaj Medical Clinic", "Private"),
        ("Wema CFW Clinic", "NGO"),
        ("St. Odilia's Dispensary", "Faith Based"),
        ("Uhuru Camp Dispensary", "Public"),
        ("DSC Karen Dispensary (Armed Forces)", "Public"),
        ("Karen Health Centre", "Public"),
        ("Future Age Medical Services", "Private"),
        ("Nyumbani Diagnostic Laboratory & Medical Clinic", "Private"),
        ("Sex Workers Outreach Program (Lang'ata)", "NGO"),
        ("Gertrude's Hospital Nairobi West Clinic", "Private"),
        ("Cotolengo Centre", "Faith Based"),
        ("Nairobi West Children Clinic", "Private"),
        ("South 'C' Hospital", "Private"),
        ("St Mary's Mission Hospital", "Faith Based"),
        ("Nairobi South Hospital", "Private"),
        ("The Karen Hospital", "Private"),
        ("7KR Mrs Health Centre", "Public"),
        ("Meridian Equator Hospital", "Private"),
        ("Nairobi West Hospital", "Private"),
        ("Family Care Medical Centre & Maternity", "Private"),
    ]
    
    # Kibera facilities (79)
    kibera_facilities = [
        ("Lindi Community Clinic", "Public"),
        ("Blessed Medical Clinic", "Faith Based"),
        ("Karanja Road Community Clinic", "Public"),
        ("Emko Clinic", "Private"),
        ("Gatwekera B (Olympic)", "Public"),
        ("KMTC Dispensary", "Public"),
        ("Maranatha Medical Services", "Faith Based"),
        ("Clinix Health Care (Kibra)", "Private"),
        ("Nakhayo Medical Clinic", "Private"),
        ("Kibera Highway Clinic", "Private"),
        ("Makina Community Clinic", "Public"),
        ("Nyumba Kubwa Community Clinic", "Public"),
        ("Royal Clinic-Kibera", "Private"),
        ("Soweto West Community Clinic", "Public"),
        ("St James Medical Clinic", "Faith Based"),
        ("SACODEN VCT Center", "NGO"),
        ("KEMRI VCT", "Public"),
        ("Olympic Community Clinic", "Public"),
        ("Raila Community Clinic", "Public"),
        ("Slum Medical Clinic", "Private"),
        ("Wema Medical Clinic B", "NGO"),
        ("Mercillin Afya Centre", "Private"),
        ("Community Evolution Network VCT", "NGO"),
        ("MSF Olympic Centre", "NGO"),
        ("Microbiology Reference Lab", "Public"),
        ("Oncology Reference Lab", "Public"),
        ("Makina Clinic", "Public"),
        ("Kibera Human Development Clinic", "NGO"),
        ("Chonesus Clinic", "Private"),
        ("Rosade Medical Clinic", "Private"),
        ("Springs of Life Lutheran Dispensary", "Faith Based"),
        ("Vostrum Clinic", "Private"),
        ("Child Doctor Kenya", "Private"),
        ("National Blood Transfusion Services", "Public"),
        ("National HIV Reference Lab", "Public"),
        ("TB Central Reference Lab", "Public"),
        ("Kibera CFW Clinic", "NGO"),
        ("Kibera D.O Dispensary", "Public"),
        ("Laini Saba Health Services", "Public"),
        ("Kisembo Dispensary", "Public"),
        ("Tumaini Medical Centre", "Private"),
        ("Johanna Justin-Jinich Community Clinic", "NGO"),
        ("Lea Toto Kibera", "NGO"),
        ("CMM Clinic", "Private"),
        ("Mtaani VCT", "NGO"),
        ("PCEA Silanga Church VCT", "Faith Based"),
        ("St Mac's Hospital", "Faith Based"),
        ("St Pery's Medical Clinic", "Faith Based"),
        ("Wema Medical Clinic", "NGO"),
        ("Aga Khan Clinic (Ngong Rd Prestige)", "Private"),
        ("Dr Mboloi Clinic", "Public"),
        ("Iran Medical Clinic", "Private"),
        ("Kibera South (MSF Belgium) Health Centre", "NGO"),
        ("Senye Medical Clinic", "Private"),
        ("Silanga (MSF Belgium) Dispensary", "NGO"),
        ("Kianda 42 Community Clinic", "Public"),
        ("KEMRI Mimosa", "Public"),
        ("Nuru Lutheran Media Ministry", "Faith Based"),
        ("Silanga Community Clinic", "Public"),
        ("Marie Stopes Clinic (Dagoretti)", "NGO"),
        ("VIPS Health Services", "Private"),
        ("Kibera Chemi Chemi Ya Uzima Clinic", "NGO"),
        ("Tabitha Medical Clinic", "Private"),
        ("Vipawa Medical Services", "Private"),
        ("Kibera Ubuntu Afya Medical Centre", "NGO"),
        ("Woodley Clinic", "Public"),
        ("NASCOP VCT", "Public"),
        ("Neema Medical Clinic", "Faith Based"),
        ("Ngong Road Dispensary", "Public"),
        ("Kenyatta National Hospital", "Public"),
        ("Discordant Couples of Kenya VCT", "NGO"),
        ("Mbagathi District Hospital", "Public"),
        ("St Mary's Medical Clinic", "Faith Based"),
        ("Ushirika Medical Clinic", "Faith Based"),
        ("Dr Irimu Medical Clinic", "Private"),
        ("Afya House Dispensary", "Public"),
        ("Saola Maternity and Nursing Home", "Private"),
        ("Green Cross Medical Clinic", "Private"),
        ("Evesben Foundation Medical Clinic", "NGO"),
    ]
    
    # Roysambu facilities (66)
    roysambu_facilities = [
        ("Sharifik Medical Clinic", "Private"),
        ("St John Hospital", "Faith Based"),
        ("Congo Medical Services", "Private"),
        ("Round About Medical Centre", "Private"),
        ("St Mary's Health Services", "Faith Based"),
        ("St Michael Community Nursing Home", "Faith Based"),
        ("Milele Integrated Medical Services", "Private"),
        ("Prime Health Services Dispensary", "Private"),
        ("Proact Services", "Private"),
        ("Wayside Medical & Dental Clinic", "Private"),
        ("Manasco Medical Centre (Roysambu)", "Private"),
        ("AAR Mountain Mall", "Private"),
        ("Genus Medical Services & Diagnostic Lab", "Private"),
        ("Success Medical Services", "Private"),
        ("Mid-Point Health Services", "Private"),
        ("Sanitas Lotus Medical Centre", "Private"),
        ("St Teresa Medical Clinic (Zimmerman)", "Faith Based"),
        ("Royolk Medical Clinic", "Private"),
        ("Josnik Clinic", "Private"),
        ("Kamwitha Medical Centre", "Private"),
        ("Selma Medical Clinic", "Private"),
        ("Hekima Medical Centre", "Faith Based"),
        ("Imani 44 Medical Centre", "Faith Based"),
        ("Stars General Medical Clinic", "Private"),
        ("Jozi Medical Centre", "Private"),
        ("Zimma Health Care", "Private"),
        ("Annex Health Care", "Private"),
        ("Max Family Health Care", "Private"),
        ("Crow Medical Centre", "Private"),
        ("Unity Health Care", "Private"),
        ("Kamiti Maximum Clinic", "Public"),
        ("Afya Health Care", "Private"),
        ("Index Medical Services", "Private"),
        ("Afyamax Medical & Centre Dental", "Private"),
        ("Tazama Dental Clinic", "Private"),
        ("Hope Medical Clinic (Githurai)", "Private"),
        ("Mother & Child Meridian & Lab Services", "Private"),
        ("Nazareth Medical Services", "Faith Based"),
        ("St Louis Community Hospital", "Faith Based"),
        ("Prestige Health Centre (Zimmerman)", "Private"),
        ("Promise Medical Services", "Private"),
        ("United States International University VCT", "Public"),
        ("CID HQS Dispensary", "Public"),
        ("Lea Toto Mwiki", "NGO"),
        ("Kenyatta University Dispensary", "Public"),
        ("Korogocho Health Centre", "Public"),
        ("St Francis Health Centre (Nairobi North)", "Faith Based"),
        ("St Philips Health Centre", "Faith Based"),
        ("Marurui Dispensary", "Public"),
        ("Medical Reception Dispensary", "Public"),
        ("St Mary's Health Centre", "Faith Based"),
        ("Uzima Dispensary", "Public"),
        ("Githurai VCT", "Public"),
        ("Githurai Medical Dispensary", "Public"),
        ("Bridging Out-Patient", "Private"),
        ("Kahawa West Health Centre", "Public"),
        ("Jerapha Maternity", "Private"),
        ("Christian Aid Dispensary", "Faith Based"),
        ("Imani Medical Centre", "Faith Based"),
        ("Ronil Medical Clinic (Githurai)", "Private"),
        ("Jamii Medical Hospital", "Private"),
        ("Giovanna Dispensary", "Private"),
        ("Ediana Nursing Home", "Private"),
        ("St Annes Medical Health Centre", "Faith Based"),
        ("Eden Dispensary", "Private"),
        ("St Joseph Mukasa Dispensary", "Faith Based"),
    ]
    
    # Westlands facilities (69)
    westlands_facilities = [
        ("Westlands Medical Centre", "Private"),
        ("The Mater Hospital (Westlands)", "Faith Based"),
        ("Rafiki Medical Clinic (Westlands)", "Private"),
        ("Abraham Memorial Nursing Home (Westlands)", "Faith Based"),
        ("Mafra Clinic", "Private"),
        ("Maichoma Clinic", "Private"),
        ("Abby Clinic", "Private"),
        ("Mutathamia Medical Clinic", "Private"),
        ("Kangemi Gichagi Dispensary", "Public"),
        ("Chiromo Medical Centre", "Private"),
        ("Srisathya Sai Medical Clinic", "Private"),
        ("Sunshine Medical Centre", "Private"),
        ("Green Cross Medical and Dental Clinic", "Private"),
        ("Dr Eliud Njuguna (Parklands)", "Private"),
        ("Afya Bora Health Care", "Private"),
        ("Aculaser Institute", "Private"),
        ("Westlands Health Centre", "Public"),
        ("Mp Shah Hospital (Westlands)", "Private"),
        ("Sunbeam Medical Centre", "Private"),
        ("Lions Sightfirst Eye Hospital", "NGO"),
        ("Lianas Clinic Health Centre", "Private"),
        ("St Angela Merici Health Centre (Kingeero)", "Faith Based"),
        ("Aga Khan Hospital", "Private"),
        ("Avenue Hospital", "Private"),
        ("Westlands Health Care Services", "Private"),
        ("Medanta Africare Medical Centre", "Private"),
        ("Smiles Medical Centre", "Private"),
        ("Emerging Infectious Disease Center", "Private"),
        ("Bridgeway Clinic", "Private"),
        ("Bafana Medical Centre", "Private"),
        ("Victory Medicare", "Private"),
        ("Bodaki Health Centre", "Private"),
        ("Dr Henry Abwao", "Private"),
        ("Baraka Medical Centre", "Faith Based"),
        ("Medimark Health Care", "Private"),
        ("Focus Outreach Medical Mission", "NGO"),
        ("Dr Gichuru Mwangi", "Private"),
        ("CFW Clinics Kibagare", "NGO"),
        ("Eagle Health Care Solution", "Private"),
        ("Kenya Association of Professional Counsellors (KAPC)", "NGO"),
        ("Jalaram Medical Services", "Private"),
        ("Medanta AfriCare Krishna Park", "Private"),
        ("Consolata Shrine Dispensary (Deep Sea Nairobi)", "Faith Based"),
        ("AAR Clinic Sarit Centre (Westlands)", "Private"),
        ("Afya Bora Medical Clinic (Westlands)", "Private"),
        ("Lea Toto Clinic (Westlands)", "NGO"),
        ("Westlands District Health Management Team", "Public"),
        ("Padens Medicare Centre", "Private"),
        ("Jamii Clinic (Westlands)", "Private"),
        ("Gichago Dispensary", "Public"),
        ("Mawamu Clinic", "Private"),
        ("St Joseph W Dispensary (Westlands)", "Faith Based"),
        ("Kamili Organization", "NGO"),
        ("IOM International Organization for Migration (Gigiri)", "NGO"),
        ("Kenya AIDS Vaccine Initiative (KAVI)", "NGO"),
        ("Lower Kabete Dispensary (Kabete)", "Public"),
        ("Kabete Barracks Dispensary", "Public"),
        ("AIDS Health Care Foundation Parklands Clinic", "NGO"),
        ("Association of Physically Disabled of Kenya", "NGO"),
        ("Mji Wa Huruma Dispensary", "Public"),
        ("Amurt Health Centre", "NGO"),
        ("Gertrudes Children's Hospital", "Private"),
        ("Karura Health Centre (Kiambu Rd)", "Public"),
        ("Kabete Approved School Dispensary", "Public"),
        ("Githogoro Runda Baptist Clinic", "Faith Based"),
        ("St Florence Medical Care Health Centre", "Faith Based"),
        ("Kangemi Health Centre", "Public"),
        ("Kari Health Clinic", "Private"),
        ("Medecins Du Monde/France (Kangemi Kang'ora)", "NGO"),
    ]
    
    # Dagoretti North facilities (79)
    dagoretti_north_facilities = [
        ("Family Health Medical Dispensary", "Private"),
        ("Kesha VCT", "NGO"),
        ("Rgc Jipe Moyo Dispensary", "NGO"),
        ("Gatina United Clinic", "Private"),
        ("Al-Gadhir Clinic", "Private"),
        ("Muteithania Medical Clinic", "Private"),
        ("Sokoni Arcade VCT", "NGO"),
        ("Lady Northey Dispensary", "Public"),
        ("Gitanga Medical Centre", "Private"),
        ("Dr J A Alouch", "Private"),
        ("Jonalifa Clinic", "Private"),
        ("Nyina Wa Mumbi Dispensary", "Faith Based"),
        ("Melchezedek Hospital", "Faith Based"),
        ("Local Aid Organization", "NGO"),
        ("Eastway Medical Centre", "Private"),
        ("Meridian Medical Centre", "Private"),
        ("Nairobi Womens Hospital Adams", "Private"),
        ("Paragon Health Care Ltd", "Private"),
        ("University of Nairobi Dispensary", "Public"),
        ("Wema Nursing Home", "Private"),
        ("Riruta Health Centre", "Public"),
        ("Kawangware Health Centre", "Public"),
        ("Jellin Medical Clinic", "Private"),
        ("AAR Gwh Health Care Ltd", "Private"),
        ("New Riruta Medical Clinic", "Private"),
        ("State House Clinic", "Public"),
        ("Health Services Limited", "Private"),
        ("University of Nairobi Health Services", "Public"),
        ("Mercy Mission Health Centre", "Faith Based"),
        ("Kabiro Medical Clinic", "Private"),
        ("St Catherine's Health Centre", "Faith Based"),
        ("St Teresa's Health Centre", "Faith Based"),
        ("Trinity Medical Care Health Centre", "Faith Based"),
        ("Bodaki Medical Clinic", "Private"),
        ("Jacaranda Special School", "Public"),
        ("Dr Gachare Medical Clinic", "Private"),
        ("Dr Montet Medical Clinic", "Private"),
        ("Dr Muasya Medical Clinic", "Private"),
        ("Dr Were Medical Clinic", "Private"),
        ("Central Park Clinic", "Private"),
        ("Nyalego Medical Clinic", "Private"),
        ("Rapha Medical Clinic", "Faith Based"),
        ("Dr Kingondu Clinic (Kilimani)", "Private"),
        ("Liverpool VCT", "NGO"),
        ("Dr Aziz Mohamed Medical Clinic", "Private"),
        ("Mid Hill Medical Clinic", "Private"),
        ("Ray of Hope Health Centre", "Faith Based"),
        ("Maisha Poa Dispensary", "NGO"),
        ("Marie Stopes Clinic (Kilimani)", "NGO"),
        ("I Choose Life - Africa (Kileleshwa)", "NGO"),
        ("Gertrudes Othaya Road Dispensary", "Private"),
        ("Dr Mureithi Clinic (Kilimani)", "Private"),
        ("Acacia Clinic (Kilimani)", "Private"),
        ("Menelik Chest Clinic", "Public"),
        ("Gynapaed Dispensary (Kilimani)", "Private"),
        ("Dr Muhindi Clinic (Kilimani)", "Private"),
        ("Skyhill Medical Centre", "Private"),
        ("State House Dispensary (Nairobi)", "Public"),
        ("St Jude's Health Centre", "Faith Based"),
        ("Dod Mrs Dispensary", "Public"),
        ("Jeffrey Medical & Diagnostic Centre", "Private"),
        ("Clinitec Medical Services", "Private"),
        ("New Life Home Childrens Home (Kilimani)", "NGO"),
        ("Refuge Point International", "NGO"),
        ("Gachui Medical Centre", "Private"),
        ("Dr Florence Murila (Ngong Road)", "Private"),
        ("Dr.Charles.J.R.Opondo (Landmark Plaza)", "Private"),
        ("Nairobi Hospital", "Private"),
        ("Dr.Henry Wellington Alube (Landmark Plaza)", "Private"),
        ("Dr.K.Gicheru (Upper Hill Centre)", "Private"),
        ("Avenue House Medical Centre", "Private"),
        ("Silverdine Medical Centre (Lancet House)", "Private"),
        ("Touch of Health - Well-Being Centre", "Private"),
        ("Dr.P.W.Kamau & Associates (Upper Hill Medical Centre)", "Private"),
        ("Adventist Centre For Care and Support (Kilimani)", "Faith Based"),
        ("Maria Immaculate Health Centre", "Faith Based"),
        ("National Spinal Injury Hospital", "Public"),
        ("Nairobi Womens Hospital (Hurlingham)", "Private"),
        ("Coptic Hospital (Ngong Road)", "Faith Based"),
    ]
    
    # Generate coordinates for each facility within its sub-county
    def generate_coordinates(sub_county, facility_index, total_facilities):
        """Generate realistic coordinates within sub-county boundaries"""
        center = SUB_COUNTY_CENTERS[sub_county]
        
        # Create a spiral pattern for even distribution
        angle = (facility_index * 137.5)  # Golden angle
        radius = 0.003 + (facility_index % 20) * 0.0005  # Varying radius
        
        # Convert angle to radians
        import math
        angle_rad = math.radians(angle)
        
        # Calculate offset
        lat_offset = radius * math.cos(angle_rad) * 1.5
        lng_offset = radius * math.sin(angle_rad) * 1.2
        
        # Add some randomness
        import random
        random.seed(f"{sub_county}_{facility_name}")
        lat_offset += (random.random() - 0.5) * 0.0005
        lng_offset += (random.random() - 0.5) * 0.0005
        
        return [center[0] + lat_offset, center[1] + lng_offset]
    
    # Process all facilities
    all_facilities = []
    
    for sub_county, fac_list in [
        ("Kasarani", kasarani_facilities),
        ("Ruaraka", ruaraka_facilities),
        ("Dagoretti South", dagoretti_south_facilities),
        ("Langata", langata_facilities),
        ("Kibera", kibera_facilities),
        ("Roysambu", roysambu_facilities),
        ("Westlands", westlands_facilities),
        ("Dagoretti North", dagoretti_north_facilities)
    ]:
        for idx, (name, f_type) in enumerate(fac_list):
            coords = generate_coordinates(sub_county, idx, len(fac_list))
            all_facilities.append({
                'Facility Name': name,
                'Sub-County': sub_county,
                'Type': f_type,
                'Latitude': coords[0],
                'Longitude': coords[1]
            })
    
    return pd.DataFrame(all_facilities)

# Load facilities data
@st.cache_data
def load_facilities():
    return generate_facilities_data()

# ============================================================================
# MAP CREATION FUNCTIONS
# ============================================================================

def create_nairobi_county_map():
    """Create map showing all 17 sub-counties of Nairobi (light themed)"""
    
    # Create map with light background
    m = folium.Map(
        location=[-1.2833, 36.8167],
        zoom_start=11,
        tiles='CartoDB positron',  # Light-themed map
        control_scale=True
    )
    
    # Add additional light tile layers
    folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
    folium.TileLayer('CartoDB voyager', name='Voyager (Light)').add_to(m)
    
    # Add fullscreen button
    Fullscreen().add_to(m)
    
    # Color palette for sub-counties (soft, light-theme compatible)
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', 
              '#98D8C8', '#F7B787', '#B5EAD7', '#C7CEE6', '#E2F0CB', '#FFDAC1',
              '#E6E6FA', '#FFB7B2', '#B5EAD7', '#FFD1DC', '#A2E1E0']
    
    # Add sub-county markers
    for idx, (sub_county, center) in enumerate(SUB_COUNTY_CENTERS.items()):
        color = colors[idx % len(colors)]
        
        # Count facilities in this sub-county
        facility_count = len(facilities_df[facilities_df['Sub-County'] == sub_county]) if sub_county in facilities_df['Sub-County'].values else 0
        
        if facility_count > 0:
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 220px;">
                <h4 style="color: {color}; margin: 0;">🏥 {sub_county}</h4>
                <hr style="margin: 8px 0;">
                <b>📊 Health Facilities:</b> {facility_count}<br>
                <b>📍 Coordinates:</b> {center[0]:.4f}, {center[1]:.4f}<br>
                <br>
                <i>✨ Click to view all hospitals in {sub_county}</i>
            </div>
            """
            
            folium.CircleMarker(
                location=center,
                radius=22,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{sub_county} - {facility_count} health facilities",
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.4,
                weight=3,
                opacity=0.8
            ).add_to(m)
            
            # Add text label
            folium.map.Marker(
                center,
                icon=folium.DivIcon(
                    icon_size=(120, 30),
                    icon_anchor=(60, 15),
                    html=f'<div style="font-size: 11px; font-weight: bold; background: white; padding: 3px 8px; border-radius: 15px; border: 1px solid {color}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">{sub_county}<br><span style="font-size: 9px;">{facility_count} facilities</span></div>'
                )
            ).add_to(m)
        else:
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 200px;">
                <h4 style="color: #999;">📍 {sub_county}</h4>
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
                color='#CCCCCC',
                fill=True,
                fill_color='#EEEEEE',
                fill_opacity=0.5,
                weight=2,
                dash_array='5,5'
            ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; 
                background-color: white; padding: 12px;
                border: 2px solid #ddd; border-radius: 8px;
                z-index: 1000; font-size: 12px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                font-family: Arial, sans-serif;">
        <b>🗺️ Nairobi County - 17 Sub-Counties</b><br>
        <hr style="margin: 5px 0;">
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; 
                         background-color: #4ECDC4; border-radius: 50%; margin-right: 8px;"></span>
            <span>Has Health Facilities (8 sub-counties)</span>
        </div>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; 
                         background-color: #ddd; border-radius: 50%; margin-right: 8px; border: 1px dashed #999;"></span>
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

def create_subcounty_hospital_map(sub_county: str):
    """Create detailed map showing all hospitals in a specific sub-county"""
    
    # Filter facilities for this sub-county
    sub_facilities = facilities_df[facilities_df['Sub-County'] == sub_county]
    
    # Get sub-county center
    center = SUB_COUNTY_CENTERS.get(sub_county, [-1.2833, 36.8167])
    
    # Create map with light background
    m = folium.Map(
        location=center,
        zoom_start=14,
        tiles='CartoDB positron',
        control_scale=True
    )
    
    # Add tile layers
    folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
    folium.TileLayer('CartoDB voyager', name='Voyager (Light)').add_to(m)
    
    # Add fullscreen
    Fullscreen().add_to(m)
    
    # Add marker cluster
    marker_cluster = MarkerCluster(
        name=f'{sub_county} Hospitals',
        overlay=True,
        control=True
    ).add_to(m)
    
    # Color mapping for facility types
    type_colors = {
        'Public': '#2E7D32',      # Dark green
        'Private': '#1565C0',      # Blue
        'Faith Based': '#6A1B9A',  # Purple
        'NGO': '#E65100',          # Orange
        'Unknown': '#757575'       # Gray
    }
    
    # Type icons
    type_icons = {
        'Public': 'building',
        'Private': 'plus',
        'Faith Based': 'heart',
        'NGO': 'hand-holding-heart',
        'Unknown': 'question'
    }
    
    # Add markers for each facility
    for _, row in sub_facilities.iterrows():
        facility_name = row['Facility Name']
        facility_type = row['Type']
        lat = row['Latitude']
        lng = row['Longitude']
        
        color = type_colors.get(facility_type, '#757575')
        icon_name = type_icons.get(facility_type, 'info-sign')
        
        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 13px; min-width: 260px; max-width: 350px;">
            <div style="background-color: {color}; color: white; padding: 10px; border-radius: 5px 5px 0 0;">
                <b style="font-size: 15px;">🏥 {facility_name}</b>
            </div>
            <div style="padding: 12px; background-color: #f9f9f9;">
                <b>📍 Sub-County:</b> {sub_county}<br>
                <b>🏷️ Type:</b> <span style="color: {color}; font-weight: bold;">{facility_type}</span><br>
                <hr style="margin: 8px 0;">
                <div style="font-size: 10px; color: #666;">
                    Coordinates: {lat:.5f}, {lng:.5f}<br>
                    <a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lng}&zoom=18" target="_blank" style="color: {color};">
                        🗺️ View on OpenStreetMap
                    </a><br>
                    <a href="https://www.google.com/maps?q={lat},{lng}" target="_blank" style="color: {color};">
                        📍 View on Google Maps
                    </a>
                </div>
            </div>
        </div>
        """
        
        # Create marker
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=400),
            tooltip=f"{facility_name} ({facility_type})",
            icon=folium.Icon(color=color.split('#')[1] if '#' in color else color, 
                           icon=icon_name, 
                           prefix='fa')
        ).add_to(marker_cluster)
    
    # Add sub-county boundary visualization
    folium.Circle(
        location=center,
        radius=2500,
        color='#FF6B6B',
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
                border: 2px solid #ddd; border-radius: 8px;
                z-index: 1000; font-size: 11px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
        <b>🏥 {sub_county} - Facility Types</b><br>
        <hr style="margin: 5px 0;">
        <span style="display: inline-block; width: 12px; height: 12px; background-color: #2E7D32; border-radius: 2px; margin-right: 5px;"></span> Public<br>
        <span style="display: inline-block; width: 12px; height: 12px; background-color: #1565C0; border-radius: 2px; margin-right: 5px;"></span> Private<br>
        <span style="display: inline-block; width: 12px; height: 12px; background-color: #6A1B9A; border-radius: 2px; margin-right: 5px;"></span> Faith Based<br>
        <span style="display: inline-block; width: 12px; height: 12px; background-color: #E65100; border-radius: 2px; margin-right: 5px;"></span> NGO<br>
        <hr style="margin: 5px 0;">
        <b>📊 Total: {len(sub_facilities)} facilities</b>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Load facilities
with st.spinner("Loading 494 health facilities..."):
    facilities_df = load_facilities()

# Initialize session state
if 'selected_subcounty' not in st.session_state:
    st.session_state.selected_subcounty = None

# Sidebar
with st.sidebar:
    st.header("📊 Nairobi County Overview")
    
    # Count facilities by sub-county
    sub_county_counts = facilities_df['Sub-County'].value_counts().to_dict()
    
    st.metric("Total Sub-Counties", 17)
    st.metric("Sub-Counties with Data", len(sub_county_counts))
    st.metric("Total Health Facilities", len(facilities_df))
    
    st.markdown("---")
    st.subheader("📈 Facilities by Sub-County")
    for sc, count in sorted(sub_county_counts.items(), key=lambda x: x[1], reverse=True):
        st.metric(sc, count)
    
    st.markdown("---")
    st.subheader("🏷️ Facilities by Type")
    type_counts = facilities_df['Type'].value_counts()
    type_colors_display = {'Public': '🟢', 'Private': '🔵', 'Faith Based': '🟣', 'NGO': '🟠'}
    for typ, count in type_counts.items():
        icon = type_colors_display.get(typ, '⚪')
        st.metric(f"{icon} {typ}", count)
    
    st.markdown("---")
    st.info("""
    **💡 How to use:**
    1. View Nairobi County with all 17 sub-counties
    2. Click any colored sub-county circle
    3. Explore individual hospitals in that area
    4. Click hospital markers for details
    5. Use search to find specific hospitals
    """)

# Main content
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
            <li>🏥 <strong>Color-coded markers</strong> show facility types when you drill down</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Create and display county map
    county_map = create_nairobi_county_map()
    
    output = st_folium(
        county_map,
        width='100%',
        height=650,
        key="county_map"
    )
    
    # Check if a sub-county was clicked
    if output and output.get('last_object_clicked_popup'):
        popup_text = str(output['last_object_clicked_popup'])
        for sc in SUB_COUNTY_CENTERS.keys():
            if sc in popup_text and sc in sub_county_counts:
                st.session_state.selected_subcounty = sc
                st.rerun()
                break
    
    # Display quick reference
    with st.expander("📋 View All Sub-Counties Reference"):
        col1, col2, col3 = st.columns(3)
        subcounty_list = sorted(SUB_COUNTY_CENTERS.keys())
        for i, sc in enumerate(subcounty_list):
            with [col1, col2, col3][i % 3]:
                count = sub_county_counts.get(sc, 0)
                if count > 0:
                    st.markdown(f"✅ **{sc}** - {count} facilities")
                else:
                    st.markdown(f"⚪ **{sc}** - No data")
    
else:
    # Show back button and hospital map
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("⬅️ Back to County View", use_container_width=True):
            st.session_state.selected_subcounty = None
            st.rerun()
    with col2:
        st.markdown(f"### 🏥 Currently viewing: **{st.session_state.selected_subcounty}** Sub-County")
    
    # Create and display hospital map
    with st.spinner(f"Loading {st.session_state.selected_subcounty} hospitals..."):
        hospital_map = create_subcounty_hospital_map(st.session_state.selected_subcounty)
        st_folium(hospital_map, width='100%', height=600)
    
    # Display statistics for this sub-county
    sc_facilities = facilities_df[facilities_df['Sub-County'] == st.session_state.selected_subcounty]
    
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Facilities", len(sc_facilities))
    with col2:
        private = len(sc_facilities[sc_facilities['Type'] == 'Private'])
        st.metric("🔵 Private", private)
    with col3:
        public = len(sc_facilities[sc_facilities['Type'] == 'Public'])
        st.metric("🟢 Public", public)
    with col4:
        faith = len(sc_facilities[sc_facilities['Type'] == 'Faith Based'])
        ngo = len(sc_facilities[sc_facilities['Type'] == 'NGO'])
        st.metric("🟣 Faith / 🟠 NGO", f"{faith} / {ngo}")
    
    # Show list of facilities
    with st.expander(f"📋 View all {len(sc_facilities)} facilities in {st.session_state.selected_subcounty}"):
        display_df = sc_facilities[['Facility Name', 'Type']].copy()
        display_df = display_df.reset_index(drop=True)
        display_df.index = display_df.index + 1
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Download button
        csv = sc_facilities.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Download {st.session_state.selected_subcounty} facilities as CSV",
            data=csv,
            file_name=f"{st.session_state.selected_subcounty}_health_facilities.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: gray; font-size: 12px;'>"
    f"🏥 Nairobi Health Facilities Map | Data from Nairobi Sub-County Health Facilities Directory<br>"
    f"📍 Total: {len(facilities_df)} facilities across 17 sub-counties | "
    f"Click markers for details | Use search to find specific hospitals"
    f"</div>",
    unsafe_allow_html=True
)
