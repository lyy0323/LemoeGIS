$(function(){
//    document.body.insertAdjacentHTML('afterend', '<a href="#" id="gridControl" onclick="gridDisplayShift()">关闭网格线</a>');
//    document.body.insertAdjacentHTML('afterend', '<script>var searchLayer = L.layerGroup().addTo(map);map.addControl( new L.Control.Search({layer: searchLayer, propertyName: "district_name"}) );</script>');
})
function gridDisplayShift(){
    lonLatGridLineLayer.removeLayer()
}
