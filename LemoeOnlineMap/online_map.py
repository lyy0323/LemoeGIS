import json
import folium
import folium.plugins as plugins
import jinja2
from branca.element import MacroElement
from flask import Flask, render_template, request
from colorpie import *
from folium import Map
from jinja2.environment import Template
from grid import Grid
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
     '/static/js/leaflet.js'),
    ('jquery',
     '/static/js/jquery-1.12.4.min.js'),
    ('bootstrap',
     '/static/js/bootstrap.min.js'),
    ('awesome_markers',
     '/static/js/leaflet.awesome-markers.js'),  # noqa
    ('font-size',
     '/static/js/font-size.js'),
    ('leaflet_draw',
     '/static/js/leaflet.draw.js'),
    ('grid-shift',
     '/static/js/grid-shift.js')
    ]

_default_css = [
    ('leaflet_css',
     '/static/css/leaflet.css'),
    ('bootstrap_css',
     '/static/css/bootstrap.min.css'),
    ('bootstrap_theme_css',
     '/static/css/bootstrap-theme.min.css'),  # noqa
    ('awesome_markers_font_css',
     '/static/css/font-awesome.min.css'),  # noqa
    ('awesome_markers_css',
     '/static/css/leaflet.awesome-markers.css'),  # noqa
    ('awesome_rotate_css',
     '/static/css/leaflet.awesome.rotate.min.css'),  # noqa
    ('leaflet-draw',
     '/static/css/leaflet.draw.css'),
    ('close',
     '/static/css/close.css'),
    ]


@app.route('/')
def index():
    tiles = '/static/map_db/{z}/{x}/{y}.webp'
    m: Map = folium.Map(location=[0, 0],
                        tiles=tiles,
                        attr="<a href=http://lemoe.town/>lemoe town</a>",
                        zoom_start=4,
                        max_zoom=7,
                        min_zoom=1,
                        crs='Simple',
                        prefer_canvas=True,
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
        <div margin: 0.2em><b>&ensp;{st_info[1]}</b>（地铁站）<br></div><span width=100%>'''
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

    # 据点
    home_layer = folium.FeatureGroup(name='据点', show=True)
    # 据点名称
    home_layer1 = folium.FeatureGroup(name='据点名称', show=False)
    # 据点坐标集
    home_info = {}
    homes = os.listdir('./static/geo_objects/homes')
    for home in homes:
        home_data = open(f'./static/geo_objects/homes/{home}', encoding='UTF-8').read()
        home_coord = json.loads(home_data)["features"][0]["geometry"]["coordinates"]
        home_coord1 = [int(home_coord[0] * 64), int(home_coord[1] * -64)]
        home_coord.reverse()
        home_name = home.strip('.geojson')
        if tuple(home_coord1) not in home_info.keys():
            home_info[tuple(home_coord1)] = {"loc": home_coord, "name": home_name}
        else:
            if type(home_info[tuple(home_coord1)]["name"]) is list:
                home_info[tuple(home_coord1)]["name"].append(home_name)
            else:
                home_info[tuple(home_coord1)]["name"] = [home_info[tuple(home_coord1)]["name"], home_name]
    for loca, data in home_info.items():
        if type(data['name']) is str:
            popup_html = f'<span width=100%><div align="center" style="border-radius: 0.5em; padding: 0.2em; font-size: 1em; flex: 1">{"&ensp;" * ("（" in data["name"])}{data["name"]}<br>{int(loca[0])}, {int(loca[1])}</div></span>'
            folium.Marker(data["loc"], popup=folium.Popup(popup_html, parse_html=False, max_width=300), icon=folium.features.CustomIcon("./static/home_icon.png", (20, 20))).add_to(home_layer)
            folium.Marker(data["loc"], icon=folium.features.DivIcon(icon_size=(12 + 15 * len(data["name"]), 20), html=f'<div style="text-align: left; font-size: 15px; padding: 4px; border-radius: 10px; background-color: rgba(0, 0, 0, 0.8); font-family: 黑体; color: rgba(0, 0, 0, 0)">{data["name"]}</div>', icon_anchor=(-15, 14))).add_to(home_layer1)
            folium.Marker(data["loc"], icon=folium.features.DivIcon(icon_size=(12 + 15 * len(data["name"]), 20), html=f'<div style="text-align: left; font-size: 15px; padding: 4px; font-family: 黑体; color: #DDD">{data["name"]}</div>', icon_anchor=(-16, 14))).add_to(home_layer1)
        else:
            popup_html = f'<span width=100%><div align="center" style="border-radius: 0.5em; padding: 0.2em; font-size: 1em; flex: 1">{"&ensp;" * ("（" in data["name"])}{"、".join(data["name"])}<br>{int(loca[0])}, {int(loca[1])}</div></span>'
            folium.Marker(data["loc"], popup=folium.Popup(popup_html, parse_html=False, max_width=300), icon=folium.features.CustomIcon("./static/home_icon.png", (20, 20))).add_to(home_layer)
            folium.Marker(data["loc"], icon=folium.features.DivIcon(icon_size=(12 + 15 * len("、".join(data["name"])), 20), html=f'<div style="text-align: left; font-size: 15px; padding: 4px; border-radius: 10px; background-color: rgba(0, 0, 0, 0.8); font-family: 黑体; color: rgba(0, 0, 0, 0)">{"、".join(data["name"])}</div>', icon_anchor=(-15, 14))).add_to(home_layer1)
            folium.Marker(data["loc"], icon=folium.features.DivIcon(icon_size=(12 + 15 * len("、".join(data["name"])), 20), html=f'<div style="text-align: left; font-size: 15px; padding: 4px; font-family: 黑体; color: #DDD">{"、".join(data["name"])}</div>', icon_anchor=(-16, 14))).add_to(home_layer1)

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
    home_layer.add_to(m)
    home_layer1.add_to(m)
    folium.LayerControl().add_to(m)
    m.default_css = _default_css
    m.default_js = _default_js
    popup0 = LatLngPopup()
    popup0.add_to(m)
    init_script = """
        var mapsPlaceholder = [];
        L.Map.addInitHook(function () {mapsPlaceholder.push(this);});
    """
    m.get_root().script.add_child(folium.Element(init_script))
    Grid().add_to(m)
    return m.get_root().render()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8963, debug=True)
