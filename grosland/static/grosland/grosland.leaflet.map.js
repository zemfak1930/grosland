// Base Variable -------------------------------------------------------------------------------------------------------
var coordinates = new Map();
var minZoom = 9;
var maxZoom = 18;

var mainLayers = {
    archive:    { color: '#CD5C5C' },
    cadastre:   { color: '#87CEEB' },
};

//  Base functions -----------------------------------------------------------------------------------------------------
function createStyle(desiredFillColor, desiredOpacity) {
    return {
        stroke: true,
        color: '#000000',
        weight: 0.5,
        fill: true,
        fillColor: desiredFillColor,
        fillOpacity: desiredOpacity,
    }
};

function saveHistory(message) {
    fetch('/journal/search_history/', {
        method: 'POST',
        body: message,
    });
};

//  Map of Leaflet -----------------------------------------------------------------------------------------------------
var map = L.map('map', {
    minZoom: minZoom,
    maxZoom: maxZoom,
    maxBounds: L.latLngBounds(
        L.latLng(46, 29.1), L.latLng(48, 31),
    ),
});
map.doubleClickZoom.disable();

//  Leaflet Plugins ----------------------------------------------------------------------------------------------------
//  Restore View
if (!map.restoreView()) {
    map.setView([47.07, 29.9], minZoom);
};

//  EasyPrint
L.easyPrint({
    sizeModes: ['A4Landscape', 'A4Portrait'],
    filename: 'grosland',
    exportOnly: true,
    hideControlContainer: true,
}).addTo(map);

//  LocateControl
L.control.locate({
    enableHighAccuracy: true,
    showPopup: false,
}).addTo(map);

//  Main Layers --------------------------------------------------------------------------------------------------------
for (let key in mainLayers) {
    mainLayers[key].overlay = L.vectorGrid.protobuf(
        'https://grosland.fun/geoserver/gwc/service/tms/1.0.0/grosland:' + key + '@EPSG%3A900913@pbf/{z}/{x}/{-y}.pbf', {
            minZoom: (minZoom + maxZoom) / 2,
            maxZoom: maxZoom,
            interactive: true,
            getFeatureId: function(feature) { return feature.properties.cadnum },
            vectorTileLayerStyles: {
                cadastre:   createStyle(desiredFillColor=mainLayers[key].color, desiredOpacity=0.4),
                archive:    createStyle(desiredFillColor=mainLayers[key].color, desiredOpacity=0.4),
            },
        }
    )
    .on('click', function(event) {
        //  Get properties of cadastre
        if (event.layer.feature) {
            var properties = event.layer.feature.properties;
        } else {
            var properties = event.layer.properties;
        };

        //  Set default cadastre style
        if (properties != 0) {
            mainLayers[key].overlay.setFeatureStyle(cadnum, createStyle(desiredFillColor=mainLayers[key].color, desiredOpacity=0.4))
        };

        //  Override ID
        cadnum = properties.cadnum;
        area = properties.area;

        //  Set style for selected cadastre
        mainLayers[key].overlay.setFeatureStyle(cadnum, createStyle(desiredFillColor=mainLayers[key].color, desiredOpacity=0.8));

        let tooltip = L.tooltip()
        .setLatLng(event.latlng)
        .setContent(
            'Кадастровий номер: ' + cadnum
            + '<br>'
            + 'Площа: ' + area + ' га',
            { className: 'tooltip' }
        )
        .addTo(map);

	saveHistory(cadnum);
    });

    if (key === 'cadastre') {
        mainLayers[key].overlay.on('dblclick', function() {
            window.open('https://e.land.gov.ua/back/cadaster/?cad_num=' + cadnum, '_blank');
            saveHistory(cadnum);
        })
    };
};

//  LayerControl -------------------------------------------------------------------------------------------------------
L.control.layers({
    // baseMaps
    'OpenStreetMap': L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map),
    'EsriMap': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'),
}, {
    // overlayMaps
    'Кадастр': mainLayers.cadastre.overlay.addTo(map),
    'Архів': mainLayers.archive.overlay,
}).addTo(map);

//  ATU Layers ---------------------------------------------------------------------------------------------------------
['village', 'council', 'district'].forEach(function(item, i, arr) {
    L.tileLayer.wms('https://grosland.fun/geoserver/wms', {
        layers: 'grosland:' + item,
        format: 'image/png',
        minZoom: (item === 'village') ? 13 : minZoom,
        transparent: true,
        version: '1.1.0',
    }).addTo(map);
});

//  Search cadnum in .db -----------------------------------------------------------------------------------------------
$(document).ready(function() {
    $('#input').on('submit', function(event){
        let cadnum = $('#cadnum').val();

        if (coordinates.has(cadnum) === false) {
            let xhr = new XMLHttpRequest();
            xhr.open('GET', '/api/parcels/' + cadnum, false);
            xhr.send();

            if (xhr.status >= 200 && xhr.status < 300) {
                //  Can receive an entire object and remember/output it? Wouldn't it catch more memory?
                coordinates.set(cadnum, JSON.parse(xhr.responseText).features[0].geometry.coordinates);
            };
        };

        if (coordinates.get(cadnum) !== undefined) {
            //  Can receive an entire object and remember/output it? Wouldn't it catch more memory?
            map.fitBounds(L.geoJSON({
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": coordinates.get(cadnum),
                    }
                }],
            })
            .getBounds());
        } else {
            window.alert('Земельна ділянка з кадастровим номером ' + cadnum + ' відсутня.')
        };

        saveHistory(cadnum);
        event.preventDefault();
    });
});
