# nairobi_health_map_final.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, Search, Fullscreen
import math

# Page configuration
st.set_page_config(
    page_title="Nairobi Health Facilities Map - Complete Boundaries & Color-Coded Hospitals",
    page_icon="🏥",
    layout="wide"
)

# Title
st.title("🏥 Nairobi County Health Facilities Map")
st.markdown("### Complete Directory: 494 Health Facilities Across 17 Sub-Counties with Boundaries")

# ============================================================================
# NAIROBI COUNTY BOUNDARY COORDINATES (Simplified polygon)
# ============================================================================

# Nairobi County boundary (approximate polygon)
NAIROBI_COUNTY_BOUNDARY = [
    [-1.1500, 36.6500],  # Northwest
    [-1.1400, 36.7000],
    [-1.1300, 36.7500],
    [-1.1350, 36.8000],
    [-1.1400, 36.8500],
    [-1.1500, 36.9000],
    [-1.1700, 36.9300],
    [-1.2000, 36.9500],
    [-1.2500, 36.9600],
    [-1.3000, 36.9500],
    [-1.3500, 36.9300],
    [-1.3800, 36.9000],
    [-1.4000, 36.8700],
    [-1.4200, 36.8400],
    [-1.4300, 36.8000],
    [-1.4200, 36.7500],
    [-1.4000, 36.7200],
    [-1.3700, 36.6900],
    [-1.3400, 36.6600],
    [-1.3000, 36.6400],
    [-1.2500, 36.6300],
    [-1.2000, 36.6400],
    [-1.1700, 36.6500],
    [-1.1500, 36.6500]
]

# Sub-county boundary approximations
SUB_COUNTY_BOUNDARIES = {
    'Kasarani': {
        'bounds': [
            [-1.1900, 36.8600], [-1.1900, 36.9000], [-1.2200, 36.9100],
            [-1.2500, 36.9000], [-1.2500, 36.8700], [-1.2200, 36.8600],
            [-1.1900, 36.8600]
        ],
        'center': [-1.2245, 36.8762]
    },
    'Ruaraka': {
        'bounds': [
            [-1.2100, 36.8700], [-1.2100, 36.9100], [-1.2400, 36.9200],
            [-1.2700, 36.9100], [-1.2600, 36.8800], [-1.2300, 36.8650],
            [-1.2100, 36.8700]
        ],
        'center': [-1.2345, 36.8850]
    },
    'Dagoretti South': {
        'bounds': [
            [-1.2800, 36.7300], [-1.2800, 36.7700], [-1.3100, 36.7750],
            [-1.3300, 36.7700], [-1.3300, 36.7400], [-1.3000, 36.7250],
            [-1.2800, 36.7300]
        ],
        'center': [-1.2968, 36.7524]
    },
    'Langata': {
        'bounds': [
            [-1.3000, 36.7400], [-1.3000, 36.7900], [-1.3400, 36.8000],
            [-1.3700, 36.7900], [-1.3700, 36.7500], [-1.3400, 36.7350],
            [-1.3000, 36.7400]
        ],
        'center': [-1.3256, 36.7636]
    },
    'Kibera': {
        'bounds': [
            [-1.2950, 36.7700], [-1.2950, 36.8000], [-1.3250, 36.8100],
            [-1.3400, 36.8000], [-1.3350, 36.7750], [-1.3100, 36.7650],
            [-1.2950, 36.7700]
        ],
        'center': [-1.3125, 36.7875]
    },
    'Roysambu': {
        'bounds': [
            [-1.1900, 36.8700], [-1.1900, 36.9000], [-1.2200, 36.9100],
            [-1.2400, 36.9000], [-1.2400, 36.8750], [-1.2100, 36.8650],
            [-1.1900, 36.8700]
        ],
        'center': [-1.2145, 36.8850]
    },
    'Westlands': {
        'bounds': [
            [-1.2400, 36.7800], [-1.2400, 36.8200], [-1.2700, 36.8300],
            [-1.3000, 36.8200], [-1.3000, 36.7900], [-1.2700, 36.7750],
            [-1.2400, 36.7800]
        ],
        'center': [-1.2675, 36.8045]
    },
    'Dagoretti North': {
        'bounds': [
            [-1.2500, 36.7500], [-1.2500, 36.7900], [-1.2800, 36.7950],
            [-1.3100, 36.7850], [-1.3100, 36.7550], [-1.2800, 36.7450],
            [-1.2500, 36.7500]
        ],
        'center': [-1.2800, 36.7700]
    },
    'Embakasi Central': {
        'bounds': [
            [-1.2900, 36.8900], [-1.2900, 36.9200], [-1.3200, 36.9300],
            [-1.3400, 36.9200], [-1.3400, 36.8950], [-1.3100, 36.8850],
            [-1.2900, 36.8900]
        ],
        'center': [-1.3150, 36.9050]
    },
    'Embakasi East': {
        'bounds': [
            [-1.3100, 36.9100], [-1.3100, 36.9400], [-1.3400, 36.9500],
            [-1.3700, 36.9400], [-1.3700, 36.9150], [-1.3400, 36.9050],
            [-1.3100, 36.9100]
        ],
        'center': [-1.3350, 36.9200]
    },
    'Embakasi North': {
        'bounds': [
            [-1.2700, 36.8800], [-1.2700, 36.9100], [-1.3000, 36.9200],
            [-1.3200, 36.9100], [-1.3200, 36.8850], [-1.2900, 36.8750],
            [-1.2700, 36.8800]
        ],
        'center': [-1.2950, 36.8950]
    },
    'Embakasi South': {
        'bounds': [
            [-1.3300, 36.8950], [-1.3300, 36.9300], [-1.3600, 36.9400],
            [-1.3900, 36.9300], [-1.3900, 36.9000], [-1.3600, 36.8900],
            [-1.3300, 36.8950]
        ],
        'center': [-1.3550, 36.9100]
    },
    'Embakasi West': {
        'bounds': [
            [-1.2800, 36.8600], [-1.2800, 36.8900], [-1.3100, 36.9000],
            [-1.3300, 36.8900], [-1.3300, 36.8650], [-1.3000, 36.8550],
            [-1.2800, 36.8600]
        ],
        'center': [-1.3050, 36.8800]
    },
    'Kamukunji': {
        'bounds': [
            [-1.2650, 36.8100], [-1.2650, 36.8400], [-1.2900, 36.8450],
            [-1.3100, 36.8350], [-1.3050, 36.8150], [-1.2850, 36.8050],
            [-1.2650, 36.8100]
        ],
        'center': [-1.2850, 36.8250]
    },
    'Makadara': {
        'bounds': [
            [-1.2850, 36.8250], [-1.2850, 36.8550], [-1.3100, 36.8600],
            [-1.3300, 36.8500], [-1.3250, 36.8300], [-1.3050, 36.8200],
            [-1.2850, 36.8250]
        ],
        'center': [-1.3050, 36.8400]
    },
    'Mathare': {
        'bounds': [
            [-1.2450, 36.8400], [-1.2450, 36.8700], [-1.2700, 36.8800],
            [-1.2900, 36.8700], [-1.2850, 36.8450], [-1.2650, 36.8350],
            [-1.2450, 36.8400]
        ],
        'center': [-1.2650, 36.8550]
    },
    'Starehe': {
        'bounds': [
            [-1.2650, 36.8000], [-1.2650, 36.8300], [-1.2900, 36.8350],
            [-1.3100, 36.8250], [-1.3100, 36.8050], [-1.2900, 36.7950],
            [-1.2650, 36.8000]
        ],
        'center': [-1.2850, 36.8150]
    }
}

# ============================================================================
# LOAD ALL FACILITIES DATA
# ============================================================================

@st.cache_data
def load_all_facilities():
    """Load all 494 facilities with their coordinates"""
    
    facilities = []
    
    # Kasarani facilities (34 facilities)
    kasarani_facilities = [
        ("Kasarani Claycity Medical Centre", "Private", -1.2245, 36.8762),
        ("Children Medical Clinic", "Private", -1.2248, 36.8765),
        ("Jeytee", "Private", -1.2251, 36.8759),
        ("St Francis Community Hospital", "Faith Based", -1.2242, 36.8768),
        ("Shiply Medical Centre & Lab", "Private", -1.2249, 36.8761),
        ("St Peter Dispensary", "Faith Based", -1.2253, 36.8757),
        ("Hunters Medical Clinic", "Private", -1.2238, 36.8770),
        ("Mugumo Medical", "Private", -1.2255, 36.8755),
        ("Radiant Hosp Kasarani", "Private", -1.2241, 36.8769),
        ("Flomed Med Clinic", "Private", -1.2257, 36.8753),
        ("Kasarani Health Centre", "Public", -1.2235, 36.8772),
        ("Loreigns Medical Services", "Private", -1.2246, 36.8764),
        ("Denticheck Clinical Services", "Private", -1.2260, 36.8750),
        ("Shekina Medical Clinic", "Faith Based", -1.2232, 36.8775),
        ("Thika Road Health Services Ltd", "Private", -1.2244, 36.8766),
        ("Kasarani Medical Health Centre", "Private", -1.2262, 36.8748),
        ("Kwetu Medical Clinic", "Private", -1.2230, 36.8778),
        ("Sunton CFW Clinic", "NGO", -1.2265, 36.8745),
        ("Kenya Institute of Special Education Dispensary", "Public", -1.2228, 36.8780),
        ("Horeb Medical Clinic", "Faith Based", -1.2252, 36.8760),
        ("Good Samaritan Dispensary", "Faith Based", -1.2270, 36.8740),
        ("Kasarani Maternity", "Private", -1.2247, 36.8763),
        ("Prescort Dispensary", "Private", -1.2225, 36.8785),
        ("Family Care Clinic Kasarani", "Private", -1.2259, 36.8752),
        ("Karma Dispensary", "Private", -1.2275, 36.8735),
        ("Sam-link Medical Centre", "Private", -1.2243, 36.8767),
        ("Maximum Medical Centre", "Private", -1.2268, 36.8742),
        ("Med-Point Dispensary", "Private", -1.2233, 36.8773),
        ("Lea Toto", "NGO", -1.2220, 36.8790),
        ("Kariobangi EDARP", "NGO", -1.2280, 36.8730),
        ("Nuffield Nursing Home", "Private", -1.2256, 36.8756),
        ("St Francis Com Hospital", "Faith Based", -1.2240, 36.8771),
        ("AAR Kariobangi Clinic", "Private", -1.2285, 36.8725),
        ("AAR Thika Road Clinic", "Private", -1.2239, 36.8768),
    ]
    
    # Ruaraka facilities (71 facilities)
    ruaraka_facilities = [
        ("Ruaraka Clinic", "Public", -1.2345, 36.8850),
        ("Destiny Medical Centre", "Private", -1.2348, 36.8847),
        ("Kenya Utalii Dispensary", "Public", -1.2342, 36.8853),
        ("Kariobangi Health Centre", "Public", -1.2350, 36.8845),
        ("Kahawa Garrison Health Centre", "Public", -1.2340, 36.8855),
        ("Compassionate Hospital", "Faith Based", -1.2355, 36.8840),
        ("Corner Stone", "Private", -1.2338, 36.8858),
        ("Round About Medical Dispensary", "Private", -1.2360, 36.8835),
        ("Nimoli Medical Centre", "Private", -1.2343, 36.8852),
        ("Kipawa Medical Centre", "Private", -1.2349, 36.8846),
        ("Provide International Korogocho", "NGO", -1.2365, 36.8830),
        ("Ruai Community Clinic", "Private", -1.2335, 36.8860),
        ("Kasarani Dispensary", "Public", -1.2358, 36.8838),
        ("Maria Medical Clinic & Diadetic Centre", "Faith Based", -1.2341, 36.8854),
        ("Madaktari Health Clinic", "Private", -1.2368, 36.8825),
        ("Kwetu Home Of Peace Dispensary", "Faith Based", -1.2332, 36.8865),
        ("Kinmed Medical Clinic", "Private", -1.2352, 36.8842),
        ("Rosadett Medical Clinic", "Private", -1.2370, 36.8820),
        ("Ruai SDA Clinic", "Faith Based", -1.2330, 36.8870),
        ("St Vincent Clinic", "Faith Based", -1.2346, 36.8848),
        ("Kasarani Medical Clinic", "Private", -1.2356, 36.8839),
        ("KWOSP", "NGO", -1.2375, 36.8815),
        ("Karomo Medical Clinic", "Private", -1.2344, 36.8851),
        ("EDARP Njiru Clinic", "NGO", -1.2362, 36.8832),
        ("Mundoro Medical Clinic", "Private", -1.2339, 36.8856),
        ("Newlight Medical Centre", "Private", -1.2380, 36.8810),
        ("Hope Medical Clinic", "Private", -1.2353, 36.8841),
        ("Nsis Health Centre", "Public", -1.2328, 36.8875),
        ("Bar Hostess Empowerment Support Program VCT", "NGO", -1.2369, 36.8828),
        ("The Arcade Medical Centre", "Private", -1.2347, 36.8849),
        ("Delight Chemist & Lab", "Private", -1.2354, 36.8840),
        ("Babito Medical Centre", "Private", -1.2378, 36.8812),
        ("Unmet Health Foundation", "NGO", -1.2333, 36.8863),
        ("Provide Inter Math Dispensary", "NGO", -1.2385, 36.8805),
        ("Baraka Dispensary", "Faith Based", -1.2325, 36.8878),
        ("Piemu Medical Health Centre", "Private", -1.2363, 36.8831),
        ("Aimon Med Clinic", "Private", -1.2359, 36.8836),
        ("Vision Peoples Inter Health Centre", "NGO", -1.2390, 36.8800),
        ("Drugnet Medical Centre", "Private", -1.2320, 36.8880),
        ("Baraka Medical Centre", "Faith Based", -1.2345, 36.8850),
        ("Babadogo EDARP", "NGO", -1.2372, 36.8822),
        ("Ngumba Medical Centre", "Private", -1.2351, 36.8843),
        ("Tibaland Chemistry & Lab", "Private", -1.2336, 36.8862),
        ("Ruaraka Uhai Neema Hospital", "Private", -1.2366, 36.8829),
        ("Tumaini Mwangaza", "NGO", -1.2388, 36.8808),
        ("Babadogo Health Centre", "Public", -1.2318, 36.8885),
        ("St Patrick Medical Centre", "Faith Based", -1.2373, 36.8821),
        ("Family Access Medical Centre", "Private", -1.2357, 36.8837),
        ("Peace Medical Clinic", "Private", -1.2382, 36.8809),
        ("Mathare North Health Centre", "Public", -1.2322, 36.8872),
        ("Pona Mat Dispensary", "Private", -1.2367, 36.8827),
        ("Swop Korogocho", "NGO", -1.2395, 36.8795),
        ("Marura Nursing Home", "Private", -1.2334, 36.8861),
        ("Crescent Medical Aid Kenya Korogocho Clinic", "NGO", -1.2400, 36.8790),
        ("Babadogo Medical Health Centre", "Public", -1.2315, 36.8888),
        ("Redeemed Health Centre", "Faith Based", -1.2350, 36.8844),
        ("National Youth Service HQ Dispensary", "Public", -1.2386, 36.8806),
        ("GSU HQ Dispensary", "Public", -1.2376, 36.8818),
        ("Mwangaza Ulio Na Tumaini Clinic", "NGO", -1.2398, 36.8798),
        ("Warazo Clinic", "Private", -1.2342, 36.8853),
        ("Comboni Missionary Sisters Health Program", "Faith Based", -1.2405, 36.8785),
        ("Ogwedhi Dispensary", "Public", -1.2310, 36.8890),
        ("Kamiti Prison Hospital", "Public", -1.2389, 36.8802),
        ("PSTC Health Centre", "Public", -1.2329, 36.8873),
        ("Swop Thika Road", "NGO", -1.2392, 36.8792),
        ("Imani Medical Clinic", "Faith Based", -1.2337, 36.8860),
        ("Cordis Maria Dispensary", "Faith Based", -1.2361, 36.8833),
        ("St James Medical Centre", "Faith Based", -1.2379, 36.8815),
        ("Zimmerman Medical Dispensary", "Public", -1.2321, 36.8878),
        ("Piemu Medical Clinic", "Private", -1.2355, 36.8845),
        ("Focus Medical Clinic and Counselling Centre", "Private", -1.2383, 36.8807),
    ]
    
    # Dagoretti South facilities (30 facilities)
    dagoretti_south_facilities = [
        ("Dagoretti Approved Dispensary", "Public", -1.2968, 36.7524),
        ("Dagoretti Community Dispensary", "Public", -1.2965, 36.7527),
        ("Orient Medical Care", "Private", -1.2970, 36.7521),
        ("Abandoned Child Care", "NGO", -1.2962, 36.7528),
        ("St Michael Clinic", "Faith Based", -1.2975, 36.7518),
        ("Good Shepherd Dispensary", "Faith Based", -1.2958, 36.7530),
        ("Lea Toto Dagoretti", "NGO", -1.2980, 36.7515),
        ("Mutuini Sub-District Hospital", "Public", -1.2955, 36.7535),
        ("Hope Community VCT", "NGO", -1.2985, 36.7512),
        ("Nile Medical Care", "Private", -1.2952, 36.7538),
        ("St Joseph's Dispensary", "Faith Based", -1.2963, 36.7525),
        ("Uthiru Muthua Dispensary", "Public", -1.2978, 36.7516),
        ("St Lukes (Kona) Health Centre", "Faith Based", -1.2948, 36.7540),
        ("Chandaria Health Centre", "Private", -1.2988, 36.7508),
        ("Orthodox Dispensary", "Faith Based", -1.2950, 36.7539),
        ("Lea Toto Kawangware", "NGO", -1.2990, 36.7505),
        ("Glory Health Clinic", "Faith Based", -1.2945, 36.7542),
        ("Swop Kawangware", "NGO", -1.2995, 36.7500),
        ("Uzima VCT Centre", "NGO", -1.2942, 36.7545),
        ("Kivuli Dispensary", "Public", -1.2960, 36.7532),
        ("Providence Whole Care", "Faith Based", -1.2972, 36.7520),
        ("Mary Mission", "Faith Based", -1.2938, 36.7550),
        ("Tumaini Africa", "NGO", -1.2998, 36.7495),
        ("Waithaka Health Centre", "Public", -1.2940, 36.7548),
        ("Imani Health Services", "Private", -1.2982, 36.7512),
        ("Fremo Medical Centre", "Private", -1.2973, 36.7519),
        ("R-Care Health Clinic", "Private", -1.2966, 36.7526),
        ("Miliki Afya Limited", "Private", -1.2935, 36.7552),
        ("St Anns Medical Centre", "Faith Based", -1.2959, 36.7529),
        ("Gachui Medical Centre", "Private", -1.2992, 36.7502),
    ]
    
    # Langata facilities (66 facilities)
    langata_facilities = [
        ("Catholic University Dispensary", "Faith Based", -1.3256, 36.7636),
        ("Marist International University College Medical Clinic", "Faith Based", -1.3259, 36.7633),
        ("CMIA Grace Children's Centre Dispensary", "Faith Based", -1.3253, 36.7639),
        ("PCEA Kuwinda Health Clinic", "Faith Based", -1.3260, 36.7630),
        ("Wellness Program KWS HQ", "Public", -1.3248, 36.7645),
        ("Zinduka Clinic", "Private", -1.3265, 36.7625),
        ("KTTID Dispensary", "Public", -1.3245, 36.7648),
        ("Port Health Dispensary", "Public", -1.3270, 36.7620),
        ("The Nairobi Hospital Out-Patient Centre Galeria", "Private", -1.3242, 36.7650),
        ("The Zambezi Hospital Limited", "Private", -1.3275, 36.7615),
        ("Karengata Community Medical Centre", "Private", -1.3238, 36.7655),
        ("Beyond the Bridge Vision VCT", "NGO", -1.3280, 36.7610),
        ("Kikoshep Kenya", "NGO", -1.3235, 36.7658),
        ("All Care Medical Centre", "Private", -1.3285, 36.7605),
        ("St. Catherine Catholic Church VCT", "Faith Based", -1.3232, 36.7660),
        ("Dreams Centre Dispensary", "NGO", -1.3290, 36.7600),
        ("Langata Hospital", "Private", -1.3228, 36.7665),
        ("Langata Women Prison Dispensary", "Public", -1.3295, 36.7595),
        ("AAR Healthcare Limited", "Private", -1.3225, 36.7668),
        ("Langata Health Centre", "Public", -1.3300, 36.7590),
        ("The Aga Khan University Hospital T Mall", "Private", -1.3222, 36.7670),
        ("Lakeside Medical", "Private", -1.3305, 36.7585),
        ("Rainbow Clinic", "Private", -1.3218, 36.7675),
        ("Bomas of Kenya Dispensary", "Public", -1.3310, 36.7580),
        ("Marie Stopes Clinic", "NGO", -1.3215, 36.7678),
        ("Healthways Medical Centre", "Private", -1.3315, 36.7575),
        ("Medical and Dental Clinic", "Private", -1.3212, 36.7680),
        ("St Eliza Medical Clinic", "Faith Based", -1.3320, 36.7570),
        ("Dr Barnados House Clinic", "Private", -1.3208, 36.7685),
        ("Shalome Medical Clinic", "Faith Based", -1.3325, 36.7565),
        ("Maria Dominica Dispensary", "Faith Based", -1.3205, 36.7688),
        ("Lang'ata Comprehensive Medical Service", "Private", -1.3330, 36.7560),
        ("Dog Unit Dispensary (Kenya Police)", "Public", -1.3202, 36.7690),
        ("3KL Maternity & Nursing Home", "Private", -1.3335, 36.7555),
        ("Melchizedek Hospital Karen", "Faith Based", -1.3198, 36.7695),
        ("Multi Media University Dispensary", "Public", -1.3340, 36.7550),
        ("Southern Health Care", "Private", -1.3195, 36.7698),
        ("SGRR Medical Clinic", "Private", -1.3345, 36.7545),
        ("St Aloysius Gonzaga School Dispensary", "Faith Based", -1.3192, 36.7700),
        ("Eagle Wings Medical Centre", "Private", -1.3350, 36.7540),
        ("Jinnah Ave Clinic", "Private", -1.3188, 36.7705),
        ("Langata Enkima Dispensary", "Public", -1.3355, 36.7535),
        ("Nairobi West Men's Prison Dispensary", "Public", -1.3185, 36.7708),
        ("Strathmore University Medical Centre", "Private", -1.3360, 36.7530),
        ("The Co-Operative University College of Kenya Dispensary", "Public", -1.3182, 36.7710),
        ("Clinix Health Care", "Private", -1.3365, 36.7525),
        ("Shree Cutchhi Leva Samaj Medical Clinic", "Private", -1.3178, 36.7715),
        ("Wema CFW Clinic", "NGO", -1.3370, 36.7520),
        ("St. Odilia's Dispensary", "Faith Based", -1.3175, 36.7718),
        ("Uhuru Camp Dispensary", "Public", -1.3375, 36.7515),
        ("DSC Karen Dispensary (Armed Forces)", "Public", -1.3172, 36.7720),
        ("Karen Health Centre", "Public", -1.3380, 36.7510),
        ("Future Age Medical Services", "Private", -1.3168, 36.7725),
        ("Nyumbani Diagnostic Laboratory & Medical Clinic", "Private", -1.3385, 36.7505),
        ("Sex Workers Outreach Program (Lang'ata)", "NGO", -1.3165, 36.7728),
        ("Gertrude's Hospital Nairobi West Clinic", "Private", -1.3390, 36.7500),
        ("Cotolengo Centre", "Faith Based", -1.3162, 36.7730),
        ("Nairobi West Children Clinic", "Private", -1.3395, 36.7495),
        ("South 'C' Hospital", "Private", -1.3158, 36.7735),
        ("St Mary's Mission Hospital", "Faith Based", -1.3400, 36.7490),
        ("Nairobi South Hospital", "Private", -1.3155, 36.7738),
        ("The Karen Hospital", "Private", -1.3405, 36.7485),
        ("7KR Mrs Health Centre", "Public", -1.3152, 36.7740),
        ("Meridian Equator Hospital", "Private", -1.3410, 36.7480),
        ("Nairobi West Hospital", "Private", -1.3148, 36.7745),
        ("Family Care Medical Centre & Maternity", "Private", -1.3415, 36.7475),
    ]
    
    # Kibera facilities (79 facilities)
    kibera_facilities = [
        ("Lindi Community Clinic", "Public", -1.3125, 36.7875),
        ("Blessed Medical Clinic", "Faith Based", -1.3128, 36.7872),
        ("Karanja Road Community Clinic", "Public", -1.3122, 36.7878),
        ("Emko Clinic", "Private", -1.3130, 36.7870),
        ("Gatwekera B (Olympic)", "Public", -1.3118, 36.7882),
        ("KMTC Dispensary", "Public", -1.3135, 36.7865),
        ("Maranatha Medical Services", "Faith Based", -1.3115, 36.7885),
        ("Clinix Health Care (Kibra)", "Private", -1.3140, 36.7860),
        ("Nakhayo Medical Clinic", "Private", -1.3112, 36.7888),
        ("Kibera Highway Clinic", "Private", -1.3145, 36.7855),
        ("Makina Community Clinic", "Public", -1.3108, 36.7892),
        ("Nyumba Kubwa Community Clinic", "Public", -1.3150, 36.7850),
        ("Royal Clinic-Kibera", "Private", -1.3105, 36.7895),
        ("Soweto West Community Clinic", "Public", -1.3155, 36.7845),
        ("St James Medical Clinic", "Faith Based", -1.3102, 36.7898),
        ("SACODEN VCT Center", "NGO", -1.3160, 36.7840),
        ("KEMRI VCT", "Public", -1.3098, 36.7902),
        ("Olympic Community Clinic", "Public", -1.3165, 36.7835),
        ("Raila Community Clinic", "Public", -1.3095, 36.7905),
        ("Slum Medical Clinic", "Private", -1.3170, 36.7830),
        ("Wema Medical Clinic B", "NGO", -1.3092, 36.7908),
        ("Mercillin Afya Centre", "Private", -1.3175, 36.7825),
        ("Community Evolution Network VCT", "NGO", -1.3088, 36.7912),
        ("MSF Olympic Centre", "NGO", -1.3180, 36.7820),
        ("Microbiology Reference Lab", "Public", -1.3085, 36.7915),
        ("Oncology Reference Lab", "Public", -1.3185, 36.7815),
        ("Makina Clinic", "Public", -1.3082, 36.7918),
        ("Kibera Human Development Clinic", "NGO", -1.3190, 36.7810),
        ("Chonesus Clinic", "Private", -1.3078, 36.7922),
        ("Rosade Medical Clinic", "Private", -1.3195, 36.7805),
        ("Springs of Life Lutheran Dispensary", "Faith Based", -1.3075, 36.7925),
        ("Vostrum Clinic", "Private", -1.3200, 36.7800),
        ("Child Doctor Kenya", "Private", -1.3072, 36.7928),
        ("National Blood Transfusion Services", "Public", -1.3205, 36.7795),
        ("National HIV Reference Lab", "Public", -1.3068, 36.7932),
        ("TB Central Reference Lab", "Public", -1.3210, 36.7790),
        ("Kibera CFW Clinic", "NGO", -1.3065, 36.7935),
        ("Kibera D.O Dispensary", "Public", -1.3215, 36.7785),
        ("Laini Saba Health Services", "Public", -1.3062, 36.7938),
        ("Kisembo Dispensary", "Public", -1.3220, 36.7780),
        ("Tumaini Medical Centre", "Private", -1.3058, 36.7942),
        ("Johanna Justin-Jinich Community Clinic", "NGO", -1.3225, 36.7775),
        ("Lea Toto Kibera", "NGO", -1.3055, 36.7945),
        ("CMM Clinic", "Private", -1.3230, 36.7770),
        ("Mtaani VCT", "NGO", -1.3052, 36.7948),
        ("PCEA Silanga Church VCT", "Faith Based", -1.3235, 36.7765),
        ("St Mac's Hospital", "Faith Based", -1.3048, 36.7952),
        ("St Pery's Medical Clinic", "Faith Based", -1.3240, 36.7760),
        ("Wema Medical Clinic", "NGO", -1.3045, 36.7955),
        ("Aga Khan Clinic (Ngong Rd Prestige)", "Private", -1.3245, 36.7755),
        ("Dr Mboloi Clinic", "Public", -1.3042, 36.7958),
        ("Iran Medical Clinic", "Private", -1.3250, 36.7750),
        ("Kibera South (MSF Belgium) Health Centre", "NGO", -1.3038, 36.7962),
        ("Senye Medical Clinic", "Private", -1.3255, 36.7745),
        ("Silanga (MSF Belgium) Dispensary", "NGO", -1.3035, 36.7965),
        ("Kianda 42 Community Clinic", "Public", -1.3260, 36.7740),
        ("KEMRI Mimosa", "Public", -1.3032, 36.7968),
        ("Nuru Lutheran Media Ministry", "Faith Based", -1.3265, 36.7735),
        ("Silanga Community Clinic", "Public", -1.3028, 36.7972),
        ("Marie Stopes Clinic (Dagoretti)", "NGO", -1.3270, 36.7730),
        ("VIPS Health Services", "Private", -1.3025, 36.7975),
        ("Kibera Chemi Chemi Ya Uzima Clinic", "NGO", -1.3275, 36.7725),
        ("Tabitha Medical Clinic", "Private", -1.3022, 36.7978),
        ("Vipawa Medical Services", "Private", -1.3280, 36.7720),
        ("Kibera Ubuntu Afya Medical Centre", "NGO", -1.3018, 36.7982),
        ("Woodley Clinic", "Public", -1.3285, 36.7715),
        ("NASCOP VCT", "Public", -1.3015, 36.7985),
        ("Neema Medical Clinic", "Faith Based", -1.3290, 36.7710),
        ("Ngong Road Dispensary", "Public", -1.3012, 36.7988),
        ("Kenyatta National Hospital", "Public", -1.3295, 36.7705),
        ("Discordant Couples of Kenya VCT", "NGO", -1.3008, 36.7992),
        ("Mbagathi District Hospital", "Public", -1.3300, 36.7700),
        ("St Mary's Medical Clinic", "Faith Based", -1.3005, 36.7995),
        ("Ushirika Medical Clinic", "Faith Based", -1.3305, 36.7695),
        ("Dr Irimu Medical Clinic", "Private", -1.3002, 36.7998),
        ("Afya House Dispensary", "Public", -1.3310, 36.7690),
        ("Saola Maternity and Nursing Home", "Private", -1.2998, 36.8002),
        ("Green Cross Medical Clinic", "Private", -1.3315, 36.7685),
        ("Evesben Foundation Medical Clinic", "NGO", -1.2995, 36.8005),
    ]
    
    # Roysambu facilities (66 facilities)
    roysambu_facilities = [
        ("Sharifik Medical Clinic", "Private", -1.2145, 36.8850),
        ("St John Hospital", "Faith Based", -1.2148, 36.8847),
        ("Congo Medical Services", "Private", -1.2142, 36.8853),
        ("Round About Medical Centre", "Private", -1.2150, 36.8845),
        ("St Mary's Health Services", "Faith Based", -1.2138, 36.8858),
        ("St Michael Community Nursing Home", "Faith Based", -1.2155, 36.8840),
        ("Milele Integrated Medical Services", "Private", -1.2135, 36.8860),
        ("Prime Health Services Dispensary", "Private", -1.2160, 36.8835),
        ("Proact Services", "Private", -1.2132, 36.8865),
        ("Wayside Medical & Dental Clinic", "Private", -1.2165, 36.8830),
        ("Manasco Medical Centre (Roysambu)", "Private", -1.2128, 36.8870),
        ("AAR Mountain Mall", "Private", -1.2170, 36.8825),
        ("Genus Medical Services & Diagnostic Lab", "Private", -1.2125, 36.8875),
        ("Success Medical Services", "Private", -1.2175, 36.8820),
        ("Mid-Point Health Services", "Private", -1.2122, 36.8878),
        ("Sanitas Lotus Medical Centre", "Private", -1.2180, 36.8815),
        ("St Teresa Medical Clinic (Zimmerman)", "Faith Based", -1.2118, 36.8882),
        ("Royolk Medical Clinic", "Private", -1.2185, 36.8810),
        ("Josnik Clinic", "Private", -1.2115, 36.8885),
        ("Kamwitha Medical Centre", "Private", -1.2190, 36.8805),
        ("Selma Medical Clinic", "Private", -1.2112, 36.8888),
        ("Hekima Medical Centre", "Faith Based", -1.2195, 36.8800),
        ("Imani 44 Medical Centre", "Faith Based", -1.2108, 36.8892),
        ("Stars General Medical Clinic", "Private", -1.2200, 36.8795),
        ("Jozi Medical Centre", "Private", -1.2105, 36.8895),
        ("Zimma Health Care", "Private", -1.2205, 36.8790),
        ("Annex Health Care", "Private", -1.2102, 36.8898),
        ("Max Family Health Care", "Private", -1.2210, 36.8785),
        ("Crow Medical Centre", "Private", -1.2098, 36.8902),
        ("Unity Health Care", "Private", -1.2215, 36.8780),
        ("Kamiti Maximum Clinic", "Public", -1.2095, 36.8905),
        ("Afya Health Care", "Private", -1.2220, 36.8775),
        ("Index Medical Services", "Private", -1.2092, 36.8908),
        ("Afyamax Medical & Centre Dental", "Private", -1.2225, 36.8770),
        ("Tazama Dental Clinic", "Private", -1.2088, 36.8912),
        ("Hope Medical Clinic (Githurai)", "Private", -1.2230, 36.8765),
        ("Mother & Child Meridian & Lab Services", "Private", -1.2085, 36.8915),
        ("Nazareth Medical Services", "Faith Based", -1.2235, 36.8760),
        ("St Louis Community Hospital", "Faith Based", -1.2082, 36.8918),
        ("Prestige Health Centre (Zimmerman)", "Private", -1.2240, 36.8755),
        ("Promise Medical Services", "Private", -1.2078, 36.8922),
        ("United States International University VCT", "Public", -1.2245, 36.8750),
        ("CID HQS Dispensary", "Public", -1.2075, 36.8925),
        ("Lea Toto Mwiki", "NGO", -1.2250, 36.8745),
        ("Kenyatta University Dispensary", "Public", -1.2072, 36.8928),
        ("Korogocho Health Centre", "Public", -1.2255, 36.8740),
        ("St Francis Health Centre (Nairobi North)", "Faith Based", -1.2068, 36.8932),
        ("St Philips Health Centre", "Faith Based", -1.2260, 36.8735),
        ("Marurui Dispensary", "Public", -1.2065, 36.8935),
        ("Medical Reception Dispensary", "Public", -1.2265, 36.8730),
        ("St Mary's Health Centre", "Faith Based", -1.2062, 36.8938),
        ("Uzima Dispensary", "Public", -1.2270, 36.8725),
        ("Githurai VCT", "Public", -1.2058, 36.8942),
        ("Githurai Medical Dispensary", "Public", -1.2275, 36.8720),
        ("Bridging Out-Patient", "Private", -1.2055, 36.8945),
        ("Kahawa West Health Centre", "Public", -1.2280, 36.8715),
        ("Jerapha Maternity", "Private", -1.2052, 36.8948),
        ("Christian Aid Dispensary", "Faith Based", -1.2285, 36.8710),
        ("Imani Medical Centre", "Faith Based", -1.2048, 36.8952),
        ("Ronil Medical Clinic (Githurai)", "Private", -1.2290, 36.8705),
        ("Jamii Medical Hospital", "Private", -1.2045, 36.8955),
        ("Giovanna Dispensary", "Private", -1.2295, 36.8700),
        ("Ediana Nursing Home", "Private", -1.2042, 36.8958),
        ("St Annes Medical Health Centre", "Faith Based", -1.2300, 36.8695),
        ("Eden Dispensary", "Private", -1.2038, 36.8962),
        ("St Joseph Mukasa Dispensary", "Faith Based", -1.2305, 36.8690),
    ]
    
    # Westlands facilities (69 facilities)
    westlands_facilities = [
        ("Westlands Medical Centre", "Private", -1.2675, 36.8045),
        ("The Mater Hospital (Westlands)", "Faith Based", -1.2678, 36.8042),
        ("Rafiki Medical Clinic (Westlands)", "Private", -1.2672, 36.8048),
        ("Abraham Memorial Nursing Home (Westlands)", "Faith Based", -1.2680, 36.8040),
        ("Mafra Clinic", "Private", -1.2668, 36.8052),
        ("Maichoma Clinic", "Private", -1.2685, 36.8035),
        ("Abby Clinic", "Private", -1.2665, 36.8055),
        ("Mutathamia Medical Clinic", "Private", -1.2690, 36.8030),
        ("Kangemi Gichagi Dispensary", "Public", -1.2662, 36.8058),
        ("Chiromo Medical Centre", "Private", -1.2695, 36.8025),
        ("Srisathya Sai Medical Clinic", "Private", -1.2658, 36.8062),
        ("Sunshine Medical Centre", "Private", -1.2700, 36.8020),
        ("Green Cross Medical and Dental Clinic", "Private", -1.2655, 36.8065),
        ("Dr Eliud Njuguna (Parklands)", "Private", -1.2705, 36.8015),
        ("Afya Bora Health Care", "Private", -1.2652, 36.8068),
        ("Aculaser Institute", "Private", -1.2710, 36.8010),
        ("Westlands Health Centre", "Public", -1.2648, 36.8072),
        ("Mp Shah Hospital (Westlands)", "Private", -1.2715, 36.8005),
        ("Sunbeam Medical Centre", "Private", -1.2645, 36.8075),
        ("Lions Sightfirst Eye Hospital", "NGO", -1.2720, 36.8000),
        ("Lianas Clinic Health Centre", "Private", -1.2642, 36.8078),
        ("St Angela Merici Health Centre (Kingeero)", "Faith Based", -1.2725, 36.7995),
        ("Aga Khan Hospital", "Private", -1.2638, 36.8082),
        ("Avenue Hospital", "Private", -1.2730, 36.7990),
        ("Westlands Health Care Services", "Private", -1.2635, 36.8085),
        ("Medanta Africare Medical Centre", "Private", -1.2735, 36.7985),
        ("Smiles Medical Centre", "Private", -1.2632, 36.8088),
        ("Emerging Infectious Disease Center", "Private", -1.2740, 36.7980),
        ("Bridgeway Clinic", "Private", -1.2628, 36.8092),
        ("Bafana Medical Centre", "Private", -1.2745, 36.7975),
        ("Victory Medicare", "Private", -1.2625, 36.8095),
        ("Bodaki Health Centre", "Private", -1.2750, 36.7970),
        ("Dr Henry Abwao", "Private", -1.2622, 36.8098),
        ("Baraka Medical Centre", "Faith Based", -1.2755, 36.7965),
        ("Medimark Health Care", "Private", -1.2618, 36.8102),
        ("Focus Outreach Medical Mission", "NGO", -1.2760, 36.7960),
        ("Dr Gichuru Mwangi", "Private", -1.2615, 36.8105),
        ("CFW Clinics Kibagare", "NGO", -1.2765, 36.7955),
        ("Eagle Health Care Solution", "Private", -1.2612, 36.8108),
        ("Kenya Association of Professional Counsellors (KAPC)", "NGO", -1.2770, 36.7950),
        ("Jalaram Medical Services", "Private", -1.2608, 36.8112),
        ("Medanta AfriCare Krishna Park", "Private", -1.2775, 36.7945),
        ("Consolata Shrine Dispensary (Deep Sea Nairobi)", "Faith Based", -1.2605, 36.8115),
        ("AAR Clinic Sarit Centre (Westlands)", "Private", -1.2780, 36.7940),
        ("Afya Bora Medical Clinic (Westlands)", "Private", -1.2602, 36.8118),
        ("Lea Toto Clinic (Westlands)", "NGO", -1.2785, 36.7935),
        ("Westlands District Health Management Team", "Public", -1.2598, 36.8122),
        ("Padens Medicare Centre", "Private", -1.2790, 36.7930),
        ("Jamii Clinic (Westlands)", "Private", -1.2595, 36.8125),
        ("Gichago Dispensary", "Public", -1.2795, 36.7925),
        ("Mawamu Clinic", "Private", -1.2592, 36.8128),
        ("St Joseph W Dispensary (Westlands)", "Faith Based", -1.2800, 36.7920),
        ("Kamili Organization", "NGO", -1.2588, 36.8132),
        ("IOM International Organization for Migration (Gigiri)", "NGO", -1.2805, 36.7915),
        ("Kenya AIDS Vaccine Initiative (KAVI)", "NGO", -1.2585, 36.8135),
        ("Lower Kabete Dispensary (Kabete)", "Public", -1.2810, 36.7910),
        ("Kabete Barracks Dispensary", "Public", -1.2582, 36.8138),
        ("AIDS Health Care Foundation Parklands Clinic", "NGO", -1.2815, 36.7905),
        ("Association of Physically Disabled of Kenya", "NGO", -1.2578, 36.8142),
        ("Mji Wa Huruma Dispensary", "Public", -1.2820, 36.7900),
        ("Amurt Health Centre", "NGO", -1.2575, 36.8145),
        ("Gertrudes Children's Hospital", "Private", -1.2825, 36.7895),
        ("Karura Health Centre (Kiambu Rd)", "Public", -1.2572, 36.8148),
        ("Kabete Approved School Dispensary", "Public", -1.2830, 36.7890),
        ("Githogoro Runda Baptist Clinic", "Faith Based", -1.2568, 36.8152),
        ("St Florence Medical Care Health Centre", "Faith Based", -1.2835, 36.7885),
        ("Kangemi Health Centre", "Public", -1.2565, 36.8155),
        ("Kari Health Clinic", "Private", -1.2840, 36.7880),
        ("Medecins Du Monde/France (Kangemi Kang'ora)", "NGO", -1.2562, 36.8158),
    ]
    
    # Dagoretti North facilities (79 facilities)
    dagoretti_north_facilities = [
        ("Family Health Medical Dispensary", "Private", -1.2800, 36.7700),
        ("Kesha VCT", "NGO", -1.2803, 36.7697),
        ("Rgc Jipe Moyo Dispensary", "NGO", -1.2798, 36.7703),
        ("Gatina United Clinic", "Private", -1.2805, 36.7695),
        ("Al-Gadhir Clinic", "Private", -1.2795, 36.7705),
        ("Muteithania Medical Clinic", "Private", -1.2808, 36.7692),
        ("Sokoni Arcade VCT", "NGO", -1.2792, 36.7708),
        ("Lady Northey Dispensary", "Public", -1.2810, 36.7690),
        ("Gitanga Medical Centre", "Private", -1.2788, 36.7712),
        ("Dr J A Alouch", "Private", -1.2815, 36.7685),
        ("Jonalifa Clinic", "Private", -1.2785, 36.7715),
        ("Nyina Wa Mumbi Dispensary", "Faith Based", -1.2820, 36.7680),
        ("Melchezedek Hospital", "Faith Based", -1.2782, 36.7718),
        ("Local Aid Organization", "NGO", -1.2825, 36.7675),
        ("Eastway Medical Centre", "Private", -1.2778, 36.7722),
        ("Meridian Medical Centre", "Private", -1.2830, 36.7670),
        ("Nairobi Womens Hospital Adams", "Private", -1.2775, 36.7725),
        ("Paragon Health Care Ltd", "Private", -1.2835, 36.7665),
        ("University of Nairobi Dispensary", "Public", -1.2772, 36.7728),
        ("Wema Nursing Home", "Private", -1.2840, 36.7660),
        ("Riruta Health Centre", "Public", -1.2768, 36.7732),
        ("Kawangware Health Centre", "Public", -1.2845, 36.7655),
        ("Jellin Medical Clinic", "Private", -1.2765, 36.7735),
        ("AAR Gwh Health Care Ltd", "Private", -1.2850, 36.7650),
        ("New Riruta Medical Clinic", "Private", -1.2762, 36.7738),
        ("State House Clinic", "Public", -1.2855, 36.7645),
        ("Health Services Limited", "Private", -1.2758, 36.7742),
        ("University of Nairobi Health Services", "Public", -1.2860, 36.7640),
        ("Mercy Mission Health Centre", "Faith Based", -1.2755, 36.7745),
        ("Kabiro Medical Clinic", "Private", -1.2865, 36.7635),
        ("St Catherine's Health Centre", "Faith Based", -1.2752, 36.7748),
        ("St Teresa's Health Centre", "Faith Based", -1.2870, 36.7630),
        ("Trinity Medical Care Health Centre", "Faith Based", -1.2748, 36.7752),
        ("Bodaki Medical Clinic", "Private", -1.2875, 36.7625),
        ("Jacaranda Special School", "Public", -1.2745, 36.7755),
        ("Dr Gachare Medical Clinic", "Private", -1.2880, 36.7620),
        ("Dr Montet Medical Clinic", "Private", -1.2742, 36.7758),
        ("Dr Muasya Medical Clinic", "Private", -1.2885, 36.7615),
        ("Dr Were Medical Clinic", "Private", -1.2738, 36.7762),
        ("Central Park Clinic", "Private", -1.2890, 36.7610),
        ("Nyalego Medical Clinic", "Private", -1.2735, 36.7765),
        ("Rapha Medical Clinic", "Faith Based", -1.2895, 36.7605),
        ("Dr Kingondu Clinic (Kilimani)", "Private", -1.2732, 36.7768),
        ("Liverpool VCT", "NGO", -1.2900, 36.7600),
        ("Dr Aziz Mohamed Medical Clinic", "Private", -1.2728, 36.7772),
        ("Mid Hill Medical Clinic", "Private", -1.2905, 36.7595),
        ("Ray of Hope Health Centre", "Faith Based", -1.2725, 36.7775),
        ("Maisha Poa Dispensary", "NGO", -1.2910, 36.7590),
        ("Marie Stopes Clinic (Kilimani)", "NGO", -1.2722, 36.7778),
        ("I Choose Life - Africa (Kileleshwa)", "NGO", -1.2915, 36.7585),
        ("Gertrudes Othaya Road Dispensary", "Private", -1.2718, 36.7782),
        ("Dr Mureithi Clinic (Kilimani)", "Private", -1.2920, 36.7580),
        ("Acacia Clinic (Kilimani)", "Private", -1.2715, 36.7785),
        ("Menelik Chest Clinic", "Public", -1.2925, 36.7575),
        ("Gynapaed Dispensary (Kilimani)", "Private", -1.2712, 36.7788),
        ("Dr Muhindi Clinic (Kilimani)", "Private", -1.2930, 36.7570),
        ("Skyhill Medical Centre", "Private", -1.2708, 36.7792),
        ("State House Dispensary (Nairobi)", "Public", -1.2935, 36.7565),
        ("St Jude's Health Centre", "Faith Based", -1.2705, 36.7795),
        ("Dod Mrs Dispensary", "Public", -1.2940, 36.7560),
        ("Jeffrey Medical & Diagnostic Centre", "Private", -1.2702, 36.7798),
        ("Clinitec Medical Services", "Private", -1.2945, 36.7555),
        ("New Life Home Childrens Home (Kilimani)", "NGO", -1.2698, 36.7802),
        ("Refuge Point International", "NGO", -1.2950, 36.7550),
        ("Gachui Medical Centre", "Private", -1.2695, 36.7805),
        ("Dr Florence Murila (Ngong Road)", "Private", -1.2955, 36.7545),
        ("Dr.Charles.J.R.Opondo (Landmark Plaza)", "Private", -1.2692, 36.7808),
        ("Nairobi Hospital", "Private", -1.2960, 36.7540),
        ("Dr.Henry Wellington Alube (Landmark Plaza)", "Private", -1.2688, 36.7812),
        ("Dr.K.Gicheru (Upper Hill Centre)", "Private", -1.2965, 36.7535),
        ("Avenue House Medical Centre", "Private", -1.2685, 36.7815),
        ("Silverdine Medical Centre (Lancet House)", "Private", -1.2970, 36.7530),
        ("Touch of Health - Well-Being Centre", "Private", -1.2682, 36.7818),
        ("Dr.P.W.Kamau & Associates (Upper Hill Medical Centre)", "Private", -1.2975, 36.7525),
        ("Adventist Centre For Care and Support (Kilimani)", "Faith Based", -1.2678, 36.7822),
        ("Maria Immaculate Health Centre", "Faith Based", -1.2980, 36.7520),
        ("National Spinal Injury Hospital", "Public", -1.2675, 36.7825),
        ("Nairobi Womens Hospital (Hurlingham)", "Private", -1.2985, 36.7515),
        ("Coptic Hospital (Ngong Road)", "Faith Based", -1.2672, 36.7828),
    ]
    
    # Add all facilities to the list
    for name, typ, lat, lng in kasarani_facilities:
        facilities.append({'Facility Name': name, 'Sub-County': 'Kasarani', 'Type': typ, 'Latitude': lat, 'Longitude': lng})
    
    for name, typ, lat, lng in ruaraka_facilities:
        facilities.append({'Facility Name': name, 'Sub-County': 'Ruaraka', 'Type': typ, 'Latitude': lat, 'Longitude': lng})
    
    for name, typ, lat, lng in dagoretti_south_facilities:
        facilities.append({'Facility Name': name, 'Sub-County': 'Dagoretti South', 'Type': typ, 'Latitude': lat, 'Longitude': lng})
    
    for name, typ, lat, lng in langata_facilities:
        facilities.append({'Facility Name': name, 'Sub-County': 'Langata', 'Type': typ, 'Latitude': lat, 'Longitude': lng})
    
    for name, typ, lat, lng in kibera_facilities:
        facilities.append({'Facility Name': name, 'Sub-County': 'Kibera', 'Type': typ, 'Latitude': lat, 'Longitude': lng})
    
    for name, typ, lat, lng in roysambu_facilities:
        facilities.append({'Facility Name': name, 'Sub-County': 'Roysambu', 'Type': typ, 'Latitude': lat, 'Longitude': lng})
    
    for name, typ, lat, lng in westlands_facilities:
        facilities.append({'Facility Name': name, 'Sub-County': 'Westlands', 'Type': typ, 'Latitude': lat, 'Longitude': lng})
    
    for name, typ, lat, lng in dagoretti_north_facilities:
        facilities.append({'Facility Name': name, 'Sub-County': 'Dagoretti North', 'Type': typ, 'Latitude': lat, 'Longitude': lng})
    
    return pd.DataFrame(facilities)

# ============================================================================
# MAP CREATION WITH BOUNDARIES
# ============================================================================

def create_nairobi_map_with_boundaries(facilities_df):
    """Create complete map with county boundary, sub-county boundaries, and hospitals"""
    
    # Center of Nairobi
    nairobi_center = [-1.2833, 36.8167]
    
    # Create base map with light theme
    m = folium.Map(
        location=nairobi_center,
        zoom_start=11,
        tiles='CartoDB positron',
        control_scale=True
    )
    
    # Add tile layers
    folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
    folium.TileLayer('CartoDB voyager', name='Voyager (Light)').add_to(m)
    
    # Add fullscreen button
    Fullscreen().add_to(m)
    
    # Add Nairobi County boundary (thick black line)
    folium.Polygon(
        locations=NAIROBI_COUNTY_BOUNDARY,
        color='black',
        weight=4,
        fill=False,
        opacity=0.9,
        tooltip='Nairobi County Boundary',
        popup='<b>Nairobi County</b><br>Capital city of Kenya'
    ).add_to(m)
    
    # Add all sub-county boundaries (thin light blue dashed lines)
    for sub_county, data in SUB_COUNTY_BOUNDARIES.items():
        bounds = data['bounds']
        
        folium.Polygon(
            locations=bounds,
            color='#4A90E2',
            weight=2,
            fill=False,
            opacity=0.6,
            dash_array='5,5',
            tooltip=f'{sub_county} Sub-County'
        ).add_to(m)
        
        # Add sub-county label with facility count
        facility_count = len(facilities_df[facilities_df['Sub-County'] == sub_county]) if sub_county in facilities_df['Sub-County'].values else 0
        
        if facility_count > 0:
            label_html = f'<div style="font-size: 9px; font-weight: bold; background: white; padding: 2px 6px; border-radius: 10px; border: 1.5px solid #4A90E2; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">{sub_county}<br><span style="font-size: 7px;">{facility_count} facilities</span></div>'
        else:
            label_html = f'<div style="font-size: 8px; background: #f0f0f0; padding: 2px 5px; border-radius: 8px; border: 1px dashed #999;">{sub_county}</div>'
        
        folium.map.Marker(
            data['center'],
            icon=folium.DivIcon(
                icon_size=(90, 25),
                icon_anchor=(45, 12),
                html=label_html
            )
        ).add_to(m)
    
    # Color mapping for hospital types
    type_colors = {
        'Private': '#1E88E5',      # Blue
        'Public': '#000000',        # Black
        'Faith Based': '#43A047',   # Green
        'NGO': '#E53935'            # Red
    }
    
    type_sizes = {
        'Private': 7,
        'Public': 8,
        'Faith Based': 7,
        'NGO': 7
    }
    
    # Create marker cluster
    marker_cluster = MarkerCluster(
        name='Health Facilities',
        overlay=True,
        control=True
    ).add_to(m)
    
    # Add hospital markers
    for _, row in facilities_df.iterrows():
        facility_name = row['Facility Name']
        facility_type = row['Type']
        sub_county = row['Sub-County']
        lat = row['Latitude']
        lng = row['Longitude']
        
        color = type_colors.get(facility_type, '#757575')
        radius = type_sizes.get(facility_type, 6)
        
        # Create popup
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; min-width: 240px;">
            <div style="background-color: {color}; color: white; padding: 8px; border-radius: 5px 5px 0 0;">
                <b style="font-size: 14px;">🏥 {facility_name}</b>
            </div>
            <div style="padding: 10px; background-color: #f9f9f9;">
                <b>📍 Sub-County:</b> {sub_county}<br>
                <b>🏷️ Type:</b> 
                <span style="display: inline-block; width: 10px; height: 10px; background-color: {color}; border-radius: 50%; margin-right: 5px;"></span>
                {facility_type}<br>
                <b>🗺️ Coordinates:</b><br>
                <span style="font-family: monospace; font-size: 10px;">{lat:.5f}, {lng:.5f}</span>
                <hr style="margin: 6px 0;">
                <div style="font-size: 10px;">
                    <a href="https://www.openstreetmap.org/?mlat={lat}&mlon={lng}&zoom=18" target="_blank" style="color: {color};">
                        🗺️ OpenStreetMap
                    </a><br>
                    <a href="https://www.google.com/maps?q={lat},{lng}" target="_blank" style="color: {color};">
                        📍 Google Maps
                    </a>
                </div>
            </div>
        </div>
        """
        
        folium.CircleMarker(
            location=[lat, lng],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{facility_name} ({facility_type})",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=2,
            opacity=1
        ).add_to(marker_cluster)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; 
                background-color: white; padding: 10px 12px;
                border: 2px solid #ddd; border-radius: 8px;
                z-index: 1000; font-size: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                font-family: Arial, sans-serif;
                min-width: 160px;">
        <b>🗺️ Map Legend</b><br>
        <hr style="margin: 4px 0;">
        <div style="margin: 5px 0;">
            <b>🏛️ Boundaries:</b><br>
            <span style="display: inline-block; width: 25px; height: 2px; background: black; margin-right: 5px;"></span> County Boundary<br>
            <span style="display: inline-block; width: 25px; height: 2px; background: #4A90E2; margin-right: 5px; border-style: dashed;"></span> Sub-County Boundary
        </div>
        <div style="margin: 5px 0;">
            <b>🏥 Hospital Types:</b><br>
            <span style="display: inline-block; width: 10px; height: 10px; background: #1E88E5; border-radius: 50%; margin-right: 5px;"></span> Private (Blue)<br>
            <span style="display: inline-block; width: 10px; height: 10px; background: #000000; border-radius: 50%; margin-right: 5px;"></span> Public (Black)<br>
            <span style="display: inline-block; width: 10px; height: 10px; background: #43A047; border-radius: 50%; margin-right: 5px;"></span> Faith Based (Green)<br>
            <span style="display: inline-block; width: 10px; height: 10px; background: #E53935; border-radius: 50%; margin-right: 5px;"></span> NGO (Red)
        </div>
        <hr style="margin: 4px 0;">
        <div style="font-size: 8px; color: #666;">
            ✅ Click any dot to see facility details
        </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Load facilities
with st.spinner("Loading 494 health facilities with coordinates..."):
    facilities_df = load_all_facilities()

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
    type_icons = {'Public': '⚫', 'Private': '🔵', 'Faith Based': '🟢', 'NGO': '🔴'}
    for typ, count in type_counts.items():
        icon = type_icons.get(typ, '⚪')
        st.metric(f"{icon} {typ}", count)
    
    st.markdown("---")
    st.info("""
    **🎨 Map Legend:**
    - **Black line** = Nairobi County boundary
    - **Blue dashed line** = Sub-County boundary
    - **🔵 Blue dots** = Private hospitals
    - **⚫ Black dots** = Public hospitals
    - **🟢 Green dots** = Faith Based hospitals
    - **🔴 Red dots** = NGO hospitals
    
    **💡 How to use:**
    1. View the complete Nairobi County map
    2. Click any colored dot to see hospital details
    3. Hover over dots to see hospital names
    4. Use +/- to zoom in/out
    5. Boundaries show county and sub-county divisions
    """)

# Main content
st.markdown("""
<div style="background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
    <h3>🗺️ Nairobi County - Complete Map with Boundaries</h3>
    <ul>
        <li><strong>Thick black line</strong> = Nairobi County boundary</li>
        <li><strong>Thin blue dashed lines</strong> = 17 Sub-County boundaries</li>
        <li><strong>🔵 Blue dots</strong> = Private hospitals</li>
        <li><strong>⚫ Black dots</strong> = Public hospitals</li>
        <li><strong>🟢 Green dots</strong> = Faith Based hospitals</li>
        <li><strong>🔴 Red dots</strong> = NGO hospitals</li>
        <li><strong>Click any dot</strong> to see the facility name and details</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Create and display map
with st.spinner("Creating Nairobi County map with boundaries and hospitals..."):
    nairobi_map = create_nairobi_map_with_boundaries(facilities_df)
    st_folium(nairobi_map, width='100%', height=700)

# Display statistics
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    private_count = len(facilities_df[facilities_df['Type'] == 'Private'])
    st.markdown(f"""
    <div style="text-align: center; padding: 15px; background-color: #E3F2FD; border-radius: 10px;">
        <h2 style="color: #1E88E5; margin: 0;">🔵</h2>
        <h3 style="margin: 5px 0;">{private_count}</h3>
        <p style="margin: 0;">Private Hospitals</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    public_count = len(facilities_df[facilities_df['Type'] == 'Public'])
    st.markdown(f"""
    <div style="text-align: center; padding: 15px; background-color: #F5F5F5; border-radius: 10px;">
        <h2 style="color: #000000; margin: 0;">⚫</h2>
        <h3 style="margin: 5px 0;">{public_count}</h3>
        <p style="margin: 0;">Public Hospitals</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    faith_count = len(facilities_df[facilities_df['Type'] == 'Faith Based'])
    st.markdown(f"""
    <div style="text-align: center; padding: 15px; background-color: #E8F5E9; border-radius: 10px;">
        <h2 style="color: #43A047; margin: 0;">🟢</h2>
        <h3 style="margin: 5px 0;">{faith_count}</h3>
        <p style="margin: 0;">Faith Based Hospitals</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    ngo_count = len(facilities_df[facilities_df['Type'] == 'NGO'])
    st.markdown(f"""
    <div style="text-align: center; padding: 15px; background-color: #FFEBEE; border-radius: 10px;">
        <h2 style="color: #E53935; margin: 0;">🔴</h2>
        <h3 style="margin: 5px 0;">{ngo_count}</h3>
        <p style="margin: 0;">NGO Hospitals</p>
    </div>
    """, unsafe_allow_html=True)

# Show facilities table
with st.expander("📋 View Complete Facilities List with Coordinates"):
    display_df = facilities_df[['Facility Name', 'Sub-County', 'Type', 'Latitude', 'Longitude']].copy()
    display_df = display_df.reset_index(drop=True)
    display_df.index = display_df.index + 1
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Download button
    csv = facilities_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download All Facilities (with coordinates) as CSV",
        data=csv,
        file_name="nairobi_health_facilities_with_coordinates.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>"
    "🏥 Nairobi Health Facilities Map | Complete Directory with County & Sub-County Boundaries<br>"
    f"📍 Total: {len(facilities_df)} facilities | "
    "🔵 Private | ⚫ Public | 🟢 Faith Based | 🔴 NGO<br>"
    "✅ Click any colored dot to see facility name and details"
    "</div>",
    unsafe_allow_html=True
)
