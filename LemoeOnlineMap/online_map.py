import json

import folium
import folium.plugins as plugins
from flask import Flask, render_template, request
from colorpie import *
from folium import Map
import os

app = Flask(__name__)


def latlng(x, z, rsrange=8192):
    return [(-z / rsrange / 2) * 256, (x / rsrange / 2) * 256]


def bk_or_w(deep):
    if deep: return '#EEEEEE'
    else: return '#111111'


@app.route('/')
def index():
    tiles = '/static/map_db/{z}/{x}/{y}.webp'
    m: Map = folium.Map(location=[0, 0],
                        tiles=tiles,
                        attr="<a href=http://lemoe.town/>lemoe town</a>",
                        zoom_start=3,
                        max_zoom=6,
                        min_zoom=1,
                        crs='Simple',
                        height='100%')
    metro_stations = folium.FeatureGroup(name='地铁站', show=True)
    metro_stations_name = folium.FeatureGroup(name='地铁站名', show=False)
    metro_lines = folium.FeatureGroup(name='地铁线路', show=True)
    with open('./static/dijkstra_db/st.txt', encoding='GBK') as sttxt:
        sts = sttxt.read().splitlines()
    with open('./static/dijkstra_db/color.txt', encoding='UTF-8') as clrtxt:
        color_list = clrtxt.read().splitlines()
    metro_color_dict = {}
    for color_line in color_list:
        this_color_line = color_line.split('\t')
        metro_color_dict[this_color_line[0]] = rtx((int(this_color_line[1]), int(this_color_line[2]), int(this_color_line[3])))
    for st in sts:
        st_info = st.split('\t')
        popup_html = f'''<div align="center" padding: 10px style="font-size: 1.6em">
        <div margin: 8px><b>&ensp;{st_info[1]}（地铁站）</b><br></div><span width=100%>'''
        for metro_line in eval(st_info[2]):
            try:
                popup_html_addit = f'''<div align="center" style="background: {metro_color_dict[metro_line]}; border-radius: 5px; color: {bk_or_w(isDeep(metro_color_dict[metro_line]))}; padding: 5px; font-size: 0.7em; flex: 1"><b>{metro_line}</b></div>'''
                popup_html += popup_html_addit
            except:
                continue
        popup_html += f'</span>\n<div style="font-size: 0.5em">({st_info[3]}, {st_info[4]})</div></div>'
        folium.Marker(latlng(int(st_info[3]), int(st_info[4])), popup=folium.Popup(popup_html, parse_html=False, max_width=500), icon=folium.features.CustomIcon("./static/lemoe_icon.png", (20, 20))).add_to(metro_stations)
        folium.Marker(latlng(int(st_info[3]), int(st_info[4])), icon=folium.features.DivIcon(icon_size=(14.5 * len(st_info[1]), 20), html=f'<div style="text-align: left; font-size: 1.2em; border-radius: 5px; background-color: rgba(204, 204, 204, 0.35); font-family: 黑体; color: black"><b>{st_info[1]}</b></div>', icon_anchor=(-15, 10))).add_to(metro_stations_name)
        folium.Marker(latlng(int(st_info[3]), int(st_info[4])), popup=folium.Popup(popup_html, parse_html=False, max_width=500), icon=folium.features.DivIcon(icon_size=(14.5 * len(st_info[1]), 20), html=f'<div style="text-align: left; font-size: 1.2em; font-family: 黑体; color: white">{st_info[1]}</div>', icon_anchor=(-15, 10))).add_to(metro_stations_name)
    folium.plugins.Draw(True, 'data.geojson').add_to(m)

    filenames = os.listdir('./static/geo_objects/metro/lines_view')
    for filename in filenames:
        linename = filename.strip('.geojson')
        popup_html = f'<span width=100%><div align="center" style="background: {metro_color_dict[linename]}; border-radius: 5px; color: {bk_or_w(isDeep(metro_color_dict[linename]))}; padding: 5px; font-size: 0.7em; flex: 1"><b>{linename}</b></div></span>'
        folium.GeoJson(open(f'./static/geo_objects/metro/lines_view/{filename}', encoding='UTF-8').read(), popup=folium.GeoJsonPopup(fields=['ends'], aliases=[popup_html], labels=True, style='font-family: Microsoft Yahei'), style_function=lambda x: {"color": "#ffffff", "weight": 6, "opacity": 0.5}).add_to(metro_lines)
        folium.GeoJson(open(f'./static/geo_objects/metro/lines_view/{filename}', encoding='UTF-8').read(), popup=folium.GeoJsonPopup(fields=['ends'], aliases=[popup_html], labels=True, style='font-family: Microsoft Yahei'), style_function=lambda x: {"color": rtx(tuple(x['properties']['color'])), "weight": 3, "opacity": 0.9}).add_to(metro_lines)
        # folium.GeoJson(f'./static/geo_objects/metro/lines_view/{filename}', popup=folium.Popup(popup_html, parse_html=False, max_width=500), style_function=lambda x: {"color": rtx(tuple(x['properties']['color']))}).add_to(metro_lines)

    # 行政区
    districts_layer = folium.FeatureGroup(name='行政区', show=True)
    districts = os.listdir('./static/geo_objects/districts')
    districts.remove('districts_shapesheet.txt')
    for district in districts:
        popup_html = f'<span width=100%><div align="center" style="border-radius: 5px; padding: 5px; font-size: 0.7em; flex: 1"><b>{district.strip(".geojson")}</b></div></span>'
        shp_data = open(f'./static/geo_objects/districts/{district}', encoding='UTF-8').read()
        clr = str(json.loads(shp_data)["features"][0]["properties"]["fill_color"])
        shp = folium.GeoJson(shp_data,
                             style_function=lambda feature: {"fill": True, "fillColor": clr, "fillOpacity": 0.3, "color": "#FFFFFF", "opacity": 0.7},
                             popup=folium.GeoJsonPopup(fields=["district_name"], aliases=[popup_html], labels=True, style='font-family: Microsoft Yahei'))
        shp.add_to(districts_layer)


    """folium.PolyLine(  # polyline方法为将坐标用实线形式连接起来
            [latlng(-910, 1080, 2048),
             latlng(-768, 888, 2048),
             latlng(-720, 720, 2048),
             latlng(-609, 583, 2048),
             latlng(-520, 468, 2048),
             latlng(-64, 388, 2048),
             latlng(135, 350, 2048),
             latlng(240, 355, 2048),
             latlng(321, 314, 2048),
             latlng(470, 312, 2048),
             latlng(737, 19, 2048),
             latlng(1001, -210, 2048),
             latlng(1109, -453, 2048)
             ],  # 将坐标点连接起来
            weight=8,  # 线的大小为8
            color=rtx((137, 50, 184)),  # 线的颜色
            opacity=0.9,  # 线的透明度
        ).add_to(m)"""

    districts_layer.add_to(m)
    metro_lines.add_to(m)
    metro_stations.add_to(m)
    metro_stations_name.add_to(m)
    folium.LayerControl().add_to(m)
    return m._repr_html_()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8963, debug=True)
