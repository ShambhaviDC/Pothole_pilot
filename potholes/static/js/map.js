/*
 * Pothole Pilot - Map JavaScript
 */

// Map initialization and marker management
const PotholeMap = {
    map: null,
    markers: [],
    
    init: function() {
        const defaultCenter = { lat: 40.7128, lng: -74.0060 };
        this.map = new google.maps.Map(document.getElementById('map'), {
            zoom: 12,
            center: defaultCenter,
            mapTypeControl: true,
            fullscreenControl: true,
        });
        this.loadPotholes();
    },
    
    loadPotholes: function() {
        fetch('/api/potholes/')
            .then(response => response.json())
            .then(potholes => {
                potholes.forEach(pothole => this.addMarker(pothole));
                if(potholes.length > 0) this.fitBounds(potholes);
            })
            .catch(error => console.error('Error loading potholes:', error));
    },
    
    addMarker: function(pothole) {
        const colors = {
            'High': '#dc3545',
            'Medium': '#ffc107',
            'Low': '#28a745'
        };
        
        const marker = new google.maps.Marker({
            position: { lat: parseFloat(pothole.latitude), lng: parseFloat(pothole.longitude) },
            map: this.map,
            title: pothole.description,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                fillColor: colors[pothole.severity] || '#6c757d',
                fillOpacity: 0.8,
                strokeWeight: 1,
                strokeColor: '#fff',
                scale: 10
            }
        });
        
        const infoWindow = new google.maps.InfoWindow({
            content: this.getInfoWindowContent(pothole, colors[pothole.severity])
        });
        
        marker.addListener('click', () => {
            this.markers.forEach(m => {
                if(m.infoWindow) m.infoWindow.close();
            });
            infoWindow.open(this.map, marker);
        });
        
        marker.infoWindow = infoWindow;
        this.markers.push(marker);
    },
    
    getInfoWindowContent: function(pothole, color) {
        return `
            <div style="width: 250px; font-family: Arial, sans-serif;">
                <h6 style="margin: 0 0 10px 0; color: #333;">${pothole.description}</h6>
                ${pothole.image ? `<img src="${pothole.image}" style="width: 100%; height: auto; border-radius: 4px; margin-bottom: 10px;">` : ''}
                <p style="margin: 5px 0;"><small><strong>Severity:</strong> <span style="color: ${color}; font-weight: bold;">${pothole.severity}</span></small></p>
                <p style="margin: 5px 0;"><small><strong>Status:</strong> ${pothole.status}</small></p>
                <p style="margin: 10px 0;"><small><strong>Location:</strong><br>Lat: ${pothole.latitude.toFixed(6)}<br>Lon: ${pothole.longitude.toFixed(6)}</small></p>
                <a href="/pothole/${pothole.id}/" style="display: inline-block; padding: 5px 10px; background-color: #0d6efd; color: white; text-decoration: none; border-radius: 4px; font-size: 12px;">View Details</a>
            </div>
        `;
    },
    
    fitBounds: function(potholes) {
        const bounds = new google.maps.LatLngBounds();
        potholes.forEach(pothole => {
            bounds.extend(new google.maps.LatLng(pothole.latitude, pothole.longitude));
        });
        this.map.fitBounds(bounds);
    }
};

// Initialize map when page loads
if(document.getElementById('map')) {
    window.addEventListener('load', () => PotholeMap.init());
}
