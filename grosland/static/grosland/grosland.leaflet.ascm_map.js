//  Base function   ----------------------------------------------------------------------------------------------------
function saveHistory(message) {
    fetch('/api/history', {
        method: 'POST',
        body: message,
    }).catch(error => console.error('Error saving history:', error));
};

//  Map initialization  ------------------------------------------------------------------------------------------------
var map = L.map('map').setView([51.05, -114.07], 0);
map.doubleClickZoom.disable();


//  RestoreView --------------------------------------------------------------------------------------------------------
if (!map.restoreView()) { map.setView([51.05, -114.07], 11) };


//  LocateControl   ----------------------------------------------------------------------------------------------------
L.control.locate({
    enableHighAccuracy: true,
    showPopup: false,
}).addTo(map);

//  ASCM   -------------------------------------------------------------------------------------------------------------
ascm = L.vectorGrid.protobuf(
    'https://grosland.fun/geoserver/gwc/service/tms/1.0.0/grosland:ascm@EPSG%3A900913@pbf/{z}/{x}/{-y}.pbf', {
        minZoom: 14,
        maxZoom: 18,
        interactive: true,
        getFeatureId: (feature) => feature.code,
        vectorTileLayerStyles: {
            ascm: (properties, zoom) => {
                return {
                    color: properties.color,
                    fill: true,
                    radius: 10.1, //  You should use a radius bigger than 10!
                }
            },
        }
    }
)
.on('click', function(event) {
    let coordinates = event.latlng
    let properties = event.layer.properties;

    L.popup()
    .setLatLng(coordinates)
    .setContent('ASCM ID: ' + properties.code +
        '<br>' + '<br>' +
        '<a href="https://www.google.com/maps/dir/?api=1&destination=' + coordinates.lat + ',' + coordinates.lng + '" target="_blank">Go!</a>')
    .openOn(map);



    saveHistory('Search ASCM ' + properties.code)

});


//  LayerControl -------------------------------------------------------------------------------------------------------
L.control.layers({
    'OpenStreetMap': L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map),
    'EsriMap': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'),
}, {
    'ASCM': ascm.addTo(map)
}).addTo(map);


