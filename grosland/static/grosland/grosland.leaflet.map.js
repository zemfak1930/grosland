// Base Variable -------------------------------------------------------------------------------------------------------
const coordinates = new Map();
const minZoom = 9;
const maxZoom = 18;
const baseUrl = 'https://grosland.fun';

const mainLayers = {
    archive: { color: '#CD5C5C' },
    cadastre: { color: '#87CEEB' },
    land: { color: '#FF69B4' },
};

var paramsFilter = createParamsFilter(testParams);


//  Base functions -----------------------------------------------------------------------------------------------------
const createStyle = (desiredFillColor, desiredOpacity) => ({
    stroke: true,
    color: '#000000',
    weight: 0.5,
    fill: true,
    fillColor: desiredFillColor,
    fillOpacity: desiredOpacity,
});

const saveHistory = (message) => {
    fetch('/journal/search_history/', {
        method: 'POST',
        body: message,
    }).catch(error => console.error('Error saving history:', error));
};

const polygonAction = async (data, method) => {
    try {
        const response = await fetch('/api/lands', {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: data,
        });
        if (response.ok) {
            map.removeLayer(mainLayers.land.overlay);
            map.addLayer(mainLayers.land.overlay);
        } else {
            console.error('Failed to perform polygon action:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('Error performing polygon action:', error);
    }
};

function createCheckbox(testList1) {
    result = [];

    for (testConst1 in testList1) {
        result.push({
            name: testList1[testConst1].code + " " + testList1[testConst1].desc.slice(0, 20) + "...",
            layer: new L.Layer(),
            id: testConst1 + "Checkbox" })
    }

    return result
};

function createParamsFilter(testList1) {
    result = {}

    for (item in testList1) {
        for (let item2 in testList1[item]) {
            result[item2] = testList1[item][item2].code
        }
    }

    return result
}

function createFilter(testList1) {
    for (let filter in testList1) {

        $('body').on('change', 'input[id="' + filter + 'Checkbox"]', function() {
            if ($(this).is(':checked')) {
                paramsFilter[filter] = testList1[filter].code;
            } else {
                paramsFilter[filter] = null;
            }

            mainLayers.cadastre.overlay.redraw();
        })
    }
}

function filterByParameters(properties, testList1) {
    const ownershipCodes = [];
    const purposeCodes = [];

    for (let key in testList1) {
        if (key.includes("Ownership")) {
            ownershipCodes.push(testList1[key]);
        }
    }

    for (let m in testList1) {
        if (m.includes("Purpose")) {
            purposeCodes.push(testList1[m]);
        }
    }


    let ownershipMatch = false;
    for (let code1 of ownershipCodes) {
        if (properties.ownership_code.indexOf(code1) === 0) {
            ownershipMatch = true;
            break;
        }
    }

    let purposeMatch = false;
    for (let code2 of purposeCodes) {
        if (properties.purpose_code.indexOf(code2) === 0) {
            purposeMatch = true;
            break;
        }
    }

    return purposeMatch && ownershipMatch;
}


//  Map initialization -------------------------------------------------------------------------------------------------
const map = L.map('map', {
    minZoom: minZoom,
    maxZoom: maxZoom,
    maxBounds: L.latLngBounds(
        L.latLng(46, 29.1), L.latLng(48, 31)
    ),
});
map.doubleClickZoom.disable();

// Measurement ---------------------------------------------------------------------------------------------------------
const drawnItems = new L.FeatureGroup().addTo(map);

const drawControl = new L.Control.Draw({
    draw: {
        polygon: {
            shapeOptions: {
                color: '#000000',
                weight: 1,
                fillOpacity: 0.4,
                fillColor: '#FF69B4'
            }
        },
        polyline: false,
        rectangle: false,
        circle: false,
        marker: false,
        circlemarker: false
    }
});

map.addControl(drawControl);

map.on('draw:created', (e) => {
    const layer = e.layer;
    drawnItems.addLayer(layer);

    if (layer instanceof L.Polygon) {
        const areaHectares = (L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]) / 10000).toFixed(4);
        const myGeojson = layer.toGeoJSON();

        const landTooltip = L.tooltip()
            .setLatLng(layer.getBounds().getCenter())
            .setContent(`Площа: ${areaHectares} га`);

        layer.on('click', (e) => {
            landTooltip.setLatLng(e.latlng).openOn(map);
        });

        drawnItems.addLayer(layer);
        polygonAction(JSON.stringify({ geojson: JSON.stringify(myGeojson), area: areaHectares }), 'POST');
    }
});

//  Restore View -------------------------------------------------------------------------------------------------------
if (!map.restoreView()) {
    map.setView([47.07, 29.9], minZoom);
};

//  EasyPrint ----------------------------------------------------------------------------------------------------------
L.easyPrint({
    sizeModes: ['A4Landscape', 'A4Portrait'],
    filename: 'grosland',
    exportOnly: true,
    hideControlContainer: true,
}).addTo(map);

//  LocateControl ------------------------------------------------------------------------------------------------------
L.control.locate({
    enableHighAccuracy: true,
    showPopup: false,
}).addTo(map);

//  Main Layers --------------------------------------------------------------------------------------------------------
for (const key in mainLayers) {
    if (Object.prototype.hasOwnProperty.call(mainLayers, key)) {
        const layerConfig = mainLayers[key];
        layerConfig.overlay = L.vectorGrid.protobuf(
            `${baseUrl}/geoserver/gwc/service/tms/1.0.0/grosland:${key}@EPSG%3A900913@pbf/{z}/{x}/{-y}.pbf`, {
                minZoom: (minZoom + maxZoom) / 2,
                maxZoom: maxZoom,
                interactive: true,
                getFeatureId: (feature) => feature.properties.cadnum,
                vectorTileLayerStyles: {
                    cadastre: (properties, zoom) => {
                        if (filterByParameters(properties, paramsFilter)) {
                            return createStyle(layerConfig.color, 0.4);
                        } else {
                            return [];
                        }
                    },
                    archive: createStyle(layerConfig.color, 0.4),
                    land: (properties, zoom) => {
                        if (properties.address.indexOf(myVariable) === 0) {
                            return createStyle(layerConfig.color, 0.4);
                        } else {
                            return [];
                        }
                    }
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
        address = properties.address;

        if (address && address.includes('область')) {
            address = address.slice(0, address.indexOf('район') + 6)
            + '<br>'
            + '&emsp;&emsp;&emsp;&ensp;&nbsp;'
            + address.slice(address.indexOf('район') + 6)
        } else {
            address = 'Не визначено'
        }

        //  Set style for selected cadastre
        mainLayers[key].overlay.setFeatureStyle(cadnum, createStyle(desiredFillColor=mainLayers[key].color, desiredOpacity=0.8));

        let tooltip = L.tooltip()
        .setLatLng(event.latlng)
        .setContent(
            ((key === 'land') ? 'ID: ' : 'Кадастровий номер: ') + cadnum
            + '<br>'
            + 'Площа: ' + area + ' га'
            + '<br>'
            + 'Адреса: ' + address,
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

    if (key === 'land') {
        mainLayers[key].overlay.on('contextmenu', function(e) {
            e.originalEvent.preventDefault();

            let properties;
            if (e.layer.feature) {
                properties = e.layer.feature.properties;
            } else {
                properties = e.layer.properties;
            };

            polygonAction(JSON.stringify({ cadnum: properties.cadnum, note: properties.note }), 'DELETE')
        })
    }};
};

//  Panel Layers -------------------------------------------------------------------------------------------------------
var baseLayers = [
    {
        name: "OpenStreetMap",
        layer: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map),
    },
    {
        name: "EsriMap",
        layer: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'),
    }
]

var overLayers = [
    {
        group: "Слої",
        collapsed: true,
        layers: [
            { name: "Кадастр",  layer: mainLayers.cadastre.overlay.addTo(map) },
            { name: "Архів",    layer: mainLayers.archive.overlay },
            { name: "Мої слої", layer: mainLayers.land.overlay.addTo(map) }
        ]
    },
    {
        group: "Форма власності",
        collapsed: true,
        layers: createCheckbox(testParams.ownership)
    },
    {
        group: "Цільове призначення",
        collapsed: true,
        layers: createCheckbox(testParams.purpose)
    }
]

var panelLayers = new L.Control.PanelLayers(baseLayers, overLayers, {
    compact: true,
    collapsibleGroups: true,
});

map.addControl(panelLayers);

// ATU Layers ----------------------------------------------------------------------------------------------------------
['village', 'council', 'district'].forEach((item) => {
    const minZoomLevel = item === 'village' ? 13 : minZoom;
    L.tileLayer.wms(`${baseUrl}/geoserver/wms`, {
        layers: `grosland:${item}`,
        format: 'image/png',
        minZoom: minZoomLevel,
        transparent: true,
        version: '1.1.0',
        zIndex: 3,
    }).addTo(map);
});

//  Create Filter ------------------------------------------------------------------------------------------------------
createFilter(testParams.ownership)
createFilter(testParams.purpose)

//  OwnershipCheckbox checked ------------------------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', function() {
    let elements = document.querySelectorAll('[id$="CustomParameterCheckbox"]');

    elements.forEach(function(element) {
        element.checked = true;
    });
});

//  Search cadnum in .db -----------------------------------------------------------------------------------------------
$(document).ready(function() {
    $('#input').on('submit', async function(event) {
        event.preventDefault();

        let cadnum = $('#cadnum').val();

        try {
            if (!coordinates.has(cadnum)) {
                const response = await fetch('/api/parcels/' + cadnum);
                if (response.ok) {
                    const data = await response.json();
                    coordinates.set(cadnum, data.features[0].geometry.coordinates);
                } else {
                    throw new Error('Failed to fetch parcel data');
                }
            }

            if (coordinates.get(cadnum)) {
                map.fitBounds(L.geoJSON({
                    "type": "FeatureCollection",
                    "features": [{
                        "type": "Feature",
                        "geometry": {
                            "type": "MultiPolygon",
                            "coordinates": coordinates.get(cadnum),
                        }
                    }],
                }).getBounds());
            } else {
                window.alert('Земельна ділянка з кадастровим номером ' + cadnum + ' відсутня.');
            }

            saveHistory(cadnum);
        } catch (error) {
            console.error('Error fetching parcel data:', error);
        }
    });
});
