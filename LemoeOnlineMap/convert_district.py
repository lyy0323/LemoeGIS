import json
import pandas as pd
import colorpie


districts_list = {}
geojson_templates = dict(type="FeatureCollection", features=[{"type": "Feature", "properties": {},
                                                              "geometry": {"type": "Polygon", "coordinates": [[]]}}])

shapes = open('./static/geo_objects/districts/districts_shapesheet.txt', encoding='utf-8').read().strip('SHAPESHEET : ').split('\n\nSHAPESHEET : ')[1:]
shape_dict = {}
district_info = (0, 'undefined')
for shape in shapes:
    if ' ' in shape.split('\n\n', maxsplit=1)[0]:
        district_info = tuple(shape.split('\n\n', maxsplit=1)[0].split(' ')[0].split('-'))
        clr = colorpie.rtx(eval(shape.split('FillFore', maxsplit=1)[1].split('\nFillFore', maxsplit=1)[0].split('\t')[1][3:]))
        districts_list[district_info] = dict(type="FeatureCollection",
                                             features=[{"type": "Feature",
                                                        "properties": {"district_ID": int(district_info[0]),
                                                                       "district_name": district_info[1],
                                                                       "fill_color": clr},
                                                        "geometry": {"type": "MultiPolygon",
                                                                     "coordinates": [[]]}
                                                        }]
                                             )
        district_loc = shape.split('Pin', maxsplit=1)[1].split('\nFlipX', maxsplit=1)[0]
        locs = [float(foo.split('\t')[1].split(' ')[0]) for foo in district_loc.split('\n')]
        abs_x = locs[0] - locs[2]
        abs_y = locs[1] - locs[3]

        if "Geometry1.X1" in shape:
            districts_list[district_info]["features"][0]["geometry"]["coordinates"][0].append([])
            coords_str = shape.split('Geometry1.X1', maxsplit=1)[1].split('\nEnd Section', maxsplit=1)[0]
            coords = [float(foo.split('\t')[1].split(' ')[0]) for foo in coords_str.split('\n')]
            for i in range(len(coords) // 2):
                districts_list[district_info]["features"][0]["geometry"]["coordinates"][0][-1].append([(coords[2 * i] - 1500 + abs_x) / 32, (coords[2 * i + 1] - 1750 + abs_y) / 32])
    else:
        sub_district_loc = shape.split('Pin', maxsplit=1)[1].split('\nFlipX', maxsplit=1)[0]
        locs = [float(foo.split('\t')[1].split(' ')[0]) for foo in sub_district_loc.split('\n')]
        sub_abs_x = locs[0] - locs[2]
        sub_abs_y = locs[1] - locs[3]
        if not districts_list[district_info]["features"][0]["geometry"]["coordinates"][0]:
            districts_list[district_info]["features"][0]["geometry"]["coordinates"][0].append([])
        if districts_list[district_info]["features"][0]["geometry"]["coordinates"][0][-1]:
            districts_list[district_info]["features"][0]["geometry"]["coordinates"][0].append([])
        coords_str = shape.split('Geometry1.X1', maxsplit=1)[1].split('\nEnd Section', maxsplit=1)[0]
        coords = [float(foo.split('\t')[1].split(' ')[0]) for foo in coords_str.split('\n')]
        for i in range(len(coords) // 2):
            districts_list[district_info]["features"][0]["geometry"]["coordinates"][0][-1].append([(coords[2 * i] - 1500 + abs_x + sub_abs_x) / 32, (coords[2 * i + 1] - 1750 + abs_y + sub_abs_y) / 32])


# coords = pd.read_excel('D:/PythonProjects/LemoeGIS/LemoeOnlineMap/static/geo_objects/districts/taochaun.xlsx', header=None).iloc[:, 2].to_list()
# for i in range(len(coords) // 2):
#     geojson_templates["features"][0]["geometry"]["coordinates"][0].append([coords[2 * i] / 32 - 1.54, coords[2 * i + 1] / 32 - 10.47])
#

for key, itm in districts_list.items():
    with open(f'./static/geo_objects/districts/{key[1]}.geojson', mode='w', encoding='utf-8') as f:
        f.write(json.dumps(itm, ensure_ascii=False, indent=2))
