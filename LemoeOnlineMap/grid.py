from branca.element import MacroElement
from jinja2 import Template
from folium.vector_layers import path_options


class Grid(MacroElement):
    """自定义经纬线网格"""
    _template = Template("""
        {% macro script(this, kwargs) %}
                    var map = mapsPlaceholder.pop();
                    // 创建图层
                    let lonLatGridLineLayer = L.featureGroup();
                    lonLatGridLineLayer.addTo(map);
                    // 经纬网格生成方法
                    let addLonLatLine = () => {
                        let zoom = map.getZoom();
                        let bounds = map.getBounds();
                        let north = bounds.getNorth();
                        let east = bounds.getEast();
                        // 经纬度间隔
                        let d = 50 / Math.pow(2, zoom - 1);
                        // 经线网格
                        for (let index = -125; index <= 125; index += d) {
                            // 判断当前视野内
                            if (bounds.contains([north, index])) {
                                // 绘制经线
                                let lonLine = L.polyline(
                                    [
                                        [-128, index],
                                        [128, index],
                                    ],
                                    {weight: 1, color: "#00000066", className: "grid"}
                                );
                                lonLatGridLineLayer.addLayer(lonLine);
                                // 标注
                                let text = (index * 64).toFixed(0);
                                let divIcon = L.divIcon({
                                    html: `<div class="grid" style="white-space: nowrap; color:#000;">${text}</div>`,
                                    iconAnchor: [-3, -3],
                                });
                                let textMarker = L.marker([north, index], {icon: divIcon});
                                lonLatGridLineLayer.addLayer(textMarker);
                            }
                        }
                        
                        // 纬线网格
                        for (let index = -125; index <= 125; index += d) {
                            if (bounds.contains([index, east])) {
                                let lonLine = L.polyline(
                                    [
                                        [index, -128],
                                        [index, 128],
                                    ],
                                    {weight: 1, color: "#00000066", className: "grid"}
                                );
                                lonLatGridLineLayer.addLayer(lonLine);
                                // 标注
                                let text = (index * -64).toFixed(0);
                                let divIcon = L.divIcon({
                                    html: `<div class="grid" style="color:#000;">${text}</div>`,
                                    iconAnchor: [(text.length + 1) * 9, 0],
                                });
                                let textMarker = L.marker([index, east], {icon: divIcon});
                                lonLatGridLineLayer.addLayer(textMarker);
                            }
                        }
                    };
                    addLonLatLine();
                    map.on("zoomend move", () => {
                        lonLatGridLineLayer.clearLayers();
                        addLonLatLine();
                    });
                    map.touchZoom.disable()
                   {% endmacro %}
                """)

    def __init__(self, **kwargs):
        super(Grid, self).__init__()
        self._name = 'Grid'
        self.options = path_options(line=True, **kwargs)
