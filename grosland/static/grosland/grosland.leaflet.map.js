// Base Variable -------------------------------------------------------------------------------------------------------
var coordinates = new Map();

var defaultCenter = [48.5, 31.5];

var defaultZoom = 6;

var layers = {
    archive: {
        code: 'archive',
        color: '#CD5C5C',
    },
    cadastre: {
        code: 'cadastre',
        color: '#87CEEB',
    },
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
    fetch('/history', {
        method: 'POST',
        body: message,
    });
};

//  Map of Leaflet -----------------------------------------------------------------------------------------------------
var map = L.map('map', {
    center: defaultCenter,
    zoom: defaultZoom,
    minZoom: defaultZoom,
    maxZoom: 18,
});
map.doubleClickZoom.disable();

//  Leaflet Plugins ----------------------------------------------------------------------------------------------------
//  Restore View
if (!map.restoreView()) {
    map.setView(defaultCenter, defaultZoom);
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

//  Layers -------------------------------------------------------------------------------------------------------------
for (var key in layers) {
    layers[key].overlay = L.vectorGrid.protobuf(
        'https://grosland.fun/geoserver/gwc/service/tms/1.0.0/grosland:' + layers[key].code + '@EPSG%3A900913@pbf/{z}/{x}/{-y}.pbf', {
            minZoom: 14,
            maxZoom: 18,
            interactive: true,
            getFeatureId: function(feature) { return feature.properties.cadnum },
            vectorTileLayerStyles: {
                cadastre: createStyle(desiredFillColor=layers[key].color, desiredOpacity=0.4),
                archive: createStyle(desiredFillColor=layers[key].color, desiredOpacity=0.4),
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
            layers[key].overlay.setFeatureStyle(cadnum, createStyle(desiredFillColor=layers[key].color, desiredOpacity=0.4))
        };

        //  Override ID
        cadnum = properties.cadnum;
        area = properties.area;

        //  Set style for selected cadastre
        layers[key].overlay.setFeatureStyle(cadnum, createStyle(desiredFillColor=layers[key].color, desiredOpacity=0.8));

        let tooltip = L.tooltip()
        .setLatLng(event.latlng)
        .setContent('Кадастровий номер: ' + cadnum + '<br>' + 'Площа: ' + area + ' га', { className: 'tooltip' } )
        .addTo(map);
    });

    if (layers[key].code === 'cadastre') {
        layers[key].overlay.on('dblclick', function() {
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
    'Кадастр': layers.cadastre.overlay.addTo(map),
    'Архів': layers.archive.overlay,
}).addTo(map);

//  ATU ----------------------------------------------------------------------------------------------------------------
['village', 'council', 'district', 'state'].forEach(function(item, i, arr) {
    L.tileLayer.wms('https://grosland.fun/geoserver/wms', {
        layers: 'grosland:' + item,
        format: 'image/png',
        transparent: true,
        version: '1.1.0',
    }).addTo(map);
});

//  Search cadnum in .db -----------------------------------------------------------------------------------------------
$(document).ready(function() {
    saveHistory('Вхід у сервіс');

    $('#input').on('submit', function(event){
        let cadnum = $('#cadnum').val();

        if (coordinates.has(cadnum) === false) {
            $.ajax({
                data: {
                    cadnum: cadnum,
                },
                type: 'POST',
                url: '/get_coordinates',
                async:false,
            })
            .done(function(data){
                coordinates.set(cadnum, data.coordinates);
            });
        };

        if (coordinates.get(cadnum) !== undefined) {
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
