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
        county_group = group
all_fracs = []
children = []
county_paths = county_group.findall('.//{%s}path' % SVG_NS)
for county_path in county_paths:
    county_name_case = county_path.get('id')
    county_name = county_name_case.lower()
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
        
    new_county_name = county_name.replace(' ', '_')
    new_county_name = new_county_name.replace(',', '_')
    county_path.set('id', new_county_name)
    county_path.set('style', 'fill:'+color_this_county+';fill-opacity:1')
    if county_class is not None:
        county_x, county_y = county_path.get('d').split()[1].split(',') # this creates a box near the county
        county_x = str(float(county_x)+40)
        county_x_rect = str(float(county_x)-10)
        county_y_rect = str(float(county_y)-14)
        own_y = str(float(county_y)+15)
        notown_y = str(float(county_y)+30)
        """
        g_el = ET.Element('ns0:g')
        #rect_el = ET.Element('ns0:rect', {"x":county_x_rect, "y":county_y_rect, "width":"350", "height":"20", "fill":"white", "visibility": "hidden"})
        rect_el = ET.Element('ns0:rect', {"x":county_x_rect, "y":county_y_rect, "width":"150", "height":"60", "fill":"white", "visibility": "hidden"})
        #text_el = ET.Element('ns0:text', {"font-size":"10", "x":county_x, "y":county_y, "fill":"black", "visibility": "hidden"})
        #text_el.text = county_name_case + ': ' + str(int(ownerocc)) + ' owner-occupied, ' + str(int(notownerocc)) + ' Not owner-occupied.'
        text_el_county = ET.Element('ns0:text', {"font-size":"10", "x":county_x, "y":county_y, "fill":"black", "visibility": "hidden"})
        text_el_county.text = county_name_case
        text_el_own = ET.Element('ns0:text', {"font-size":"10", "x":county_x, "y":own_y, "fill":"black", "visibility": "hidden"})
        text_el_own.text = str(int(ownerocc)) + ' owner-occupied'
        text_el_notown = ET.Element('ns0:text', {"font-size":"10", "x":county_x, "y":notown_y, "fill":"black", "visibility": "hidden"})
        text_el_notown.text = str(int(notownerocc)) + ' Not owner-occupied.'
        begin_str = new_county_name+".mousedown"
        end_str = new_county_name+".mouseup"
        set_el = ET.Element('ns0:set', {"attributeName":"visibility", "from":"hidden", "to":"visible", "begin":begin_str, "end":end_str})
        #animate_el = ET.Element('ns0:animate', {"dur":"15", "attributeName":"opacity", "from":"1", "to":"0", "begin":end_str, "repeatCount":"0", "fill":"freeze"})
        rect_el.append(set_el)
        #text_el.append(set_el)
        rect_el.append(animate_el)
        #text_el.append(animate_el)
        text_el_county.append(set_el)
        #text_el_county.append(animate_el)
        text_el_own.append(set_el)
        #text_el_own.append(animate_el)
        text_el_notown.append(set_el)
        #text_el_notown.append(animate_el)
        g_el.append(rect_el)
        #g_el.append(text_el)
        g_el.append(text_el_county)
        g_el.append(text_el_own)
        g_el.append(text_el_notown)
        """
        title_el = ET.Element('ns0:title')
        title_el.text = county_name_case + '\n' + str(int(ownerocc)) + ' owner-occupied,\n' + str(int(notownerocc)) + ' Not owner-occupied.'
        county_path.append(title_el)
        #children.append(g_el)
county_group.extend(children)
tree.write('mortgageMap.svg')

