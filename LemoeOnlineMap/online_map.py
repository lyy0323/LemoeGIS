import json

import folium
import folium.plugins as plugins
import jinja2
from branca.element import MacroElement
from flask import Flask, render_template, request
from colorpie import *
from folium import Map
from jinja2.environment import Template
import os

app = Flask(__name__)


def latlng(x, z, rsrange=8192):
    return [(-z / rsrange / 2) * 256, (x / rsrange / 2) * 256]


class LatLngPopup(MacroElement):
    """
    When one clicks on a Map that contains a LatLngPopup,
    a popup is shown that displays the latitude and longitude of the pointer.

    """
    _template = Template(u"""
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.popup();
                function latLngPop(e) {
                    {{this.get_name()}}
                        .setLatLng(e.latlng)
                        .setContent("坐标：" + 64 * e.latlng.lng.toFixed(2) + ", " + -64 * e.latlng.lat.toFixed(2))
                        .openOn({{this._parent.get_name()}});
                    }
                {{this._parent.get_name()}}.on('click', latLngPop);
            {% endmacro %}
            """)  # noqa

    def __init__(self):
        super(LatLngPopup, self).__init__()
        self._name = 'LatLngPopup'


def bk_or_w(deep):
    if deep: return '#EEEEEE'
    else: return '#111111'


_default_js = [
    ('leaflet',
     'https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.js'),
    ('jquery',
     'https://code.jquery.com/jquery-1.12.4.min.js'),
    ('bootstrap',
     'https://cdn.staticfile.org/twitter-bootstrap/3.2.0/js/bootstrap.min.js'),
    ('awesome_markers',
     'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js'),  # noqa
    ('font-size',
     '/static/font-size.js')
    ]

_default_css = [
    ('leaflet_css',
     'https://cdn.jsdelivr.net/npm/leaflet@1.6.0/dist/leaflet.css'),
    ('bootstrap_css',
     'https://cdn.staticfile.org/twitter-bootstrap/3.2.0/css/bootstrap.min.css'),
    ('bootstrap_theme_css',
     'https://cdn.staticfile.org/twitter-bootstrap/3.2.0/css/bootstrap-theme.min.css'),  # noqa
    ('awesome_markers_font_css',
     'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.6.3/css/font-awesome.min.css'),  # noqa
    ('awesome_markers_css',
     'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css'),  # noqa
    ('awesome_rotate_css',
     'https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css'),  # noqa
    ('close',
     '/static/close.css')
    ]


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
        popup_html = f'''<div align="center" padding: 0.2em style="font-size: 1.5em">
        <div margin: 0.2em><b>&ensp;{st_info[1]}（地铁站）</b><br></div><span width=100%>'''
        for metro_line in eval(st_info[2]):
            try:
                popup_html_addit = f'''<div align="center" style="background: {metro_color_dict[metro_line]}; border-radius: 0.5em; border: 0.2em; color: {bk_or_w(isDeep(metro_color_dict[metro_line]))}; padding: 0.2em; font-size: 1em; flex: 1"><b>{metro_line}</b></div>'''
                popup_html += popup_html_addit
            except:
                continue
        popup_html += f'</span>\n<div style="font-size: 1em">({st_info[3]}, {st_info[4]})</div></div>'
        folium.Marker(latlng(int(st_info[3]), int(st_info[4])), popup=folium.Popup(popup_html, parse_html=False, max_width=300), icon=folium.features.CustomIcon("./static/lemoe_icon.png", (20, 20))).add_to(metro_stations)
        folium.Marker(latlng(int(st_info[3]), int(st_info[4])), icon=folium.features.DivIcon(icon_size=(12 + 15 * len(st_info[1]), 20), html=f'<div style="text-align: left; font-size: 15px; padding: 4px; border-radius: 10px; background-color: rgba(51, 51, 51, 0.8); font-family: 黑体; color: rgba(0, 0, 0, 0)">{st_info[1]}</div>', icon_anchor=(-15, 14))).add_to(metro_stations_name)
        folium.Marker(latlng(int(st_info[3]), int(st_info[4])), popup=folium.Popup(popup_html, lazy=True, parse_html=False, max_width=500), icon=folium.features.DivIcon(icon_size=(12 + 15 * len(st_info[1]), 20), html=f'<div style="text-align: left; font-size: 15px; padding: 4px; font-family: 黑体; color: #DDD">{st_info[1]}</div>', icon_anchor=(-16, 14))).add_to(metro_stations_name)
    folium.plugins.Draw(True, 'data.geojson').add_to(m)

    filenames = os.listdir('./static/geo_objects/metro/lines_view')
    for filename in filenames:
        linename = filename.strip('.geojson')
        popup_html = f'<span width=100%><div align="center" style="background: {metro_color_dict[linename]}; border-radius: 0.5em; color: {bk_or_w(isDeep(metro_color_dict[linename]))}; padding: 0.2em; font-size: 1em; flex: 1"><b>{linename}</b></div></span>'
        folium.GeoJson(open(f'./static/geo_objects/metro/lines_view/{filename}', encoding='UTF-8').read(), popup=folium.GeoJsonPopup(fields=['ends'], aliases=[popup_html], labels=True, style='font-family: Microsoft Yahei; font-size: 1.6em'), style_function=lambda x: {"color": "#ffffff", "weight": 6, "opacity": 0.5}).add_to(metro_lines)
        folium.GeoJson(open(f'./static/geo_objects/metro/lines_view/{filename}', encoding='UTF-8').read(), popup=folium.GeoJsonPopup(fields=['ends'], aliases=[popup_html], labels=True, style='font-family: Microsoft Yahei; font-size: 1.6em'), style_function=lambda x: {"color": rtx(tuple(x['properties']['color'])), "weight": 3, "opacity": 0.9}).add_to(metro_lines)
        # folium.GeoJson(f'./static/geo_objects/metro/lines_view/{filename}', popup=folium.Popup(popup_html, parse_html=False, max_width=500), style_function=lambda x: {"color": rtx(tuple(x['properties']['color']))}).add_to(metro_lines)

    # 行政区
    districts_layer = folium.FeatureGroup(name='行政区', show=False)
    districts = os.listdir('./static/geo_objects/districts')
    districts.remove('districts_shapesheet.txt')
    for district in districts:
        shp_data = open(f'./static/geo_objects/districts/{district}', encoding='UTF-8').read()
        district_data = json.loads(shp_data)["features"][0]["properties"]
        popup_html = f'<span width=100%><div align="center" style="border-radius: 0.5em; padding: 0.2em; background: {district_data["fill_color"]}; font-size: 1em; flex: 1"><b>{district_data["district_ID"]}</b></div></span>'
        shp = folium.GeoJson(shp_data,
                             style_function=lambda x: {"fill": True, "fillColor": x["properties"]["fill_color"], "fillOpacity": 0.5, "color": "#FFFFFF", "opacity": 0.7},
                             popup=folium.GeoJsonPopup(fields=["district_name"], aliases=[popup_html], labels=True, style='font-family: Microsoft Yahei; font-size: 1.6em; font-weight: bolder'))
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
    m.default_css = _default_css
    m.default_js = _default_js
    popup0 = LatLngPopup()
    popup0.add_to(m)
    return m.get_root().render()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8963, debug=True)
