import xml.etree.ElementTree as ET
import csv

def convert_frac_to_color(fr):
    if fr < .7:
        return '#990000'
    elif fr >= .7 and fr < .8:
        return '#bb4400'
    elif fr >= .8 and fr < .9:
        return '#dd9933'
    elif fr >= .9:
        return '#ffccaa'

state_full_names = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

state_abbreviations = {v: k for k, v in state_full_names.items()}

occupancy_data = {}
with open('hmda_lar.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        if row[0]=='count' or row[2] == '' or row[3] == '':
            pass
        else:
            county_name = row[2].lower()
            if county_name.endswith("city and borough"):
                county_name = county_name.rpartition(" city and borough")[0]
            elif county_name.endswith("census area"):
                county_name = county_name.rpartition(" census area")[0]
            elif county_name.startswith("manassas"):
                pass
            elif county_name.startswith("baltimore"):
                pass
            elif county_name.startswith("fairfax"):
                pass
            elif county_name.startswith("district of columbia"):
                pass
            elif row[3]=="Missouri" and county_name.startswith("st. louis"):
                pass
            elif row[3]=="Virginia" and county_name.startswith("richmond"):
                pass
            elif row[3]=="Virginia" and county_name.startswith("roanoke"):
                pass
            elif row[3]=="Virginia" and county_name.startswith("bedford"):
                pass
            elif row[3]=="Virginia" and county_name.startswith("franklin"):
                pass
            elif county_name.endswith("city"):
                pass
            else:
                county_name = ' '.join(county_name.split()[:-1])
            
            key = county_name + ', ' + state_abbreviations[row[3]].lower()
            
            num = float(row[0])
            if row[1] == 'Owner-occupied as a principal dwelling':
                subkey = 'ownocc'
            elif row[1] == 'Not owner-occupied as a principal dwelling':
                subkey = 'notownocc'
            if occupancy_data.has_key(key) == False:
                occupancy_data[key] = {}
            occupancy_data[key][subkey] = num

tree = ET.ElementTree()
tree.parse('./Usa_counties_large.svg')

SVG_NS = "http://www.w3.org/2000/svg"
groups = tree.findall('.//{%s}g' % SVG_NS)

for group in groups:
    if group.get('id') == 'county-group':
        country_group = group
all_fracs = []
    
county_paths = country_group.findall('.//{%s}path' % SVG_NS)
for county_path in county_paths:
    county_name = county_path.get('id').lower()
    if occupancy_data.has_key(county_name):
        #print county_name
        county_class = county_path.get('class')
        county_style = county_path.get('style')
        if occupancy_data[county_name].has_key('ownocc'):
            ownerocc = occupancy_data[county_name]['ownocc']
        else:
            ownerocc = 0
        if occupancy_data[county_name].has_key('notownocc'):
            notownerocc = occupancy_data[county_name]['notownocc']
        else:
            notownerocc = 0
        frac_this_county = ownerocc/(ownerocc + notownerocc)
        if (ownerocc + notownerocc) > 100:
            color_this_county = convert_frac_to_color(frac_this_county)
        else:
            color_this_county = '#ffffff'
        all_fracs.append(frac_this_county)
    else:
        print 'no occupancy data', county_name
        
    county_path.set('style', 'fill:'+color_this_county+';fill-opacity:1')
    #county_path.append(ET.Element('title', {'name': 'error'}))
    #child = ET.Element('title')
    #child.text = 'peter'
    #if county_class is not None:
        #begin_str = county_class+'.mouseover'
        #end_str = county_class+".mouseout"
        #child = ET.Element('text', {'x':"250", 'y':"100", 'font-size':"30", "fill":"black"})
        #child.text='peter'
        #gchild = ET.Element('set', {'attributeName': 'visibility', 'from':"hidden", 'to':"visible", 'begin':begin_str, 'end': end_str})
        #child.append(gchild)
        #county_path.append(child)

tree.write('mortgageMap.svg')

