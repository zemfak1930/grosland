//  Coordinates of plots -----------------------------------------------------------------------------------------------
var coordinates = new Map();


//  Create style -------------------------------------------------------------------------------------------------------
function createStyle(desiredFillColor='#87CEEB', desiredOpacity=0.4) {
    return {
        stroke: true,
        color: '#000000',
        weight: 0.5,
        fill: true,
        fillColor: desiredFillColor,
        fillOpacity: desiredOpacity,
    }
};


//  Map of Leaflet -----------------------------------------------------------------------------------------------------
var map = L.map('map', {
    center: [48.5, 31.5],
    zoom: 6,
    minZoom: 6,
    maxZoom: 18,
})
map.doubleClickZoom.disable();


//  Cadastre Map -------------------------------------------------------------------------------------------------------
var cadastreMap = L.vectorGrid.protobuf(
    'https://grosland.fun/geoserver/gwc/service/tms/1.0.0/grosland:cadastre@EPSG%3A900913@pbf/{z}/{x}/{-y}.pbf', {
        minZoom: 14,
        maxZoom: 18,
        interactive: true,
        getFeatureId: function(feature) { return feature.properties.cadnum },
        vectorTileLayerStyles: {
            cadastre: createStyle(),
        },
    }
)


//  Set cadastre style
.on('click', function(event) {
    //  Get properties of cadastre
    if (event.layer.feature) {
        var properties = event.layer.feature.properties;
    } else {
        var properties = event.layer.properties;
    };


    //  Set default cadastre style
    if (properties != 0) {
        cadastreMap.setFeatureStyle(cadnum, createStyle())
    };


    //  Override ID
    cadnum = properties.cadnum;


    //  Set style for selected cadastre
    cadastreMap.setFeatureStyle(cadnum, createStyle(desiredFillColor='#87CEEB', desiredOpacity=0.8));


    let tooltip = L.tooltip()
    .setLatLng(event.latlng)
    .setContent('<p>Кадастровий номер: ' + cadnum + '</p>', { className: "tooltip" })
    .addTo(map);
})
.on('dblclick', function() { window.open('https://e.land.gov.ua/back/cadaster/?cad_num=' + cadnum, '_blank') })


//  Archive Map --------------------------------------------------------------------------------------------------------
var archiveMap = L.vectorGrid.protobuf(
    'https://grosland.fun/geoserver/gwc/service/tms/1.0.0/grosland:archive@EPSG%3A900913@pbf/{z}/{x}/{-y}.pbf', {
        minZoom: 14,
        maxZoom: 18,
        interactive: true,
        getFeatureId: function(feature) { return feature.properties.cadnum },
        vectorTileLayerStyles: {
            archive: createStyle(desiredFillColor='#CD5C5C', desiredOpacity=0.4),
        },
    }
)


//  Set archive style
.on('click', function(event) {
    //  Get properties of archive
    if (event.layer.feature) {
        var properties = event.layer.feature.properties;
    } else {
        var properties = event.layer.properties;
    };


    //  Set default archive style
    if (properties != 0) {
        archiveMap.setFeatureStyle(cadnum, createStyle(desiredFillColor='#CD5C5C', desiredOpacity=0.4))
    };


    //  Override ID
    cadnum = properties.cadnum;


    //  Set style for selected archive
    archiveMap.setFeatureStyle(cadnum, createStyle(desiredFillColor='#CD5C5C', desiredOpacity=0.8));


    let tooltip = L.tooltip()
    .setLatLng(event.latlng)
    .setContent('<p>Кадастровий номер: ' + cadnum + '</p>', { className: "tooltip" })
    .addTo(map);
})


//  LayerControl -------------------------------------------------------------------------------------------------------
L.control.layers({
    // baseMaps
    'OpenStreetMap': L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map),
    'EsriMap': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'),
}, {
    // overlayMaps
    'Кадастр': cadastreMap.addTo(map),
    'Архів': archiveMap,
}).addTo(map);


//  Search cadnum in .db -----------------------------------------------------------------------------------------------
$(document).ready(function() {
    //
    $('#input').on('submit', function(event){
        //
        let cadnum = $('#cadnum').val();

        //
        if (coordinates.has(cadnum) === false) {
            //  The request itself
            $.ajax({
                data: {
                    cadnum: cadnum,
                },
                type: 'POST',
                url: '/',
                async:false,
            })

            //  Actions after
            .done(function(data){
                coordinates.set(cadnum, data.coordinates);
            });
        }

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
        }

        // Reset browser settings
        event.preventDefault();
    });
});
