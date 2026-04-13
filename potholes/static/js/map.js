/*
 * Pothole Pilot - Leaflet Map Implementation
 * Replaces Google Maps for a free, reliable OpenStreetMap experience.
 */

const PotholeMap = {
    map: null,
    markers: L.layerGroup(),
    
    // Colors for different severity levels
    colors: {
        'High': '#dc3545',   // Red
        'Medium': '#ffc107', // Yellow/Orange
        'Low': '#28a745'     // Green
    },

    init: function() {
        // Initialize the map on the #map div
        this.map = L.map('map').setView([40.7128, -74.0060], 13);
        
        // Add OpenStreetMap tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(this.map);
        
        this.markers.addTo(this.map);
        this.addLegend();
        this.loadPotholes();
    },

    loadPotholes: function() {
        console.log("Loading potholes from API...");
        fetch('/api/potholes/')
            .then(response => response.json())
            .then(potholes => {
                console.log(`Loaded ${potholes.length} potholes.`);
                potholes.forEach(p => this.addMarker(p));
                
                if (potholes.length > 0) {
                    this.fitBounds(potholes);
                }
            })
            .catch(error => console.error('Error loading potholes:', error));
    },

    addMarker: function(pothole) {
        const color = this.colors[pothole.severity] || '#6c757d';
        
        // Use circle markers for a clean look
        const marker = L.circleMarker([pothole.latitude, pothole.longitude], {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });

        const popupContent = this.getInfoWindowContent(pothole, color);
        marker.bindPopup(popupContent);
        
        this.markers.addLayer(marker);
    },

    getInfoWindowContent: function(pothole, color) {
        // Handle image path
        const imageUrl = pothole.image ? 
            (pothole.image.startsWith('http') ? pothole.image : `/media/${pothole.image}`) : 
            null;

        return `
            <div style="width: 200px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                <h6 style="margin: 0 0 8px 0; font-weight: bold;">${pothole.severity} Severity Pothole</h6>
                ${imageUrl ? `<img src="${imageUrl}" style="width: 100%; height: auto; border-radius: 4px; margin-bottom: 8px;">` : ''}
                <p style="margin: 0 0 5px 0; font-size: 0.9rem;">${pothole.description}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
                    <span style="font-size: 0.8rem; color: #666;">Status: ${pothole.status}</span>
                    <a href="/pothole/${pothole.id}/" style="font-size: 0.8rem; font-weight: bold; text-decoration: none; color: #0d6efd;">Details →</a>
                </div>
            </div>
        `;
    },

    fitBounds: function(potholes) {
        const latLngs = potholes.map(p => [p.latitude, p.longitude]);
        const bounds = L.latLngBounds(latLngs);
        this.map.fitBounds(bounds, { padding: [50, 50] });
    },

    addLegend: function() {
        const legend = L.control({ position: 'bottomright' });

        legend.onAdd = function(map) {
            const div = L.DomUtil.create('div', 'legend');
            const grades = ['High', 'Medium', 'Low'];
            const colors = {
                'High': '#dc3545',
                'Medium': '#ffc107',
                'Low': '#28a745'
            };

            div.innerHTML = '<strong>Severity</strong><br>';
            for (let i = 0; i < grades.length; i++) {
                div.innerHTML +=
                    '<i style="background:' + colors[grades[i]] + '"></i> ' +
                    grades[i] + '<br>';
            }
            return div;
        };

        legend.addTo(this.map);
    }
};

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('map')) {
        PotholeMap.init();
    }
});
