class MonsoonMapManager {
  constructor(containerId, onLocationSelectCallback) {
    this.containerId = containerId;
    this.onLocationSelect = onLocationSelectCallback;
    this.map = null;
    this.isochronesLayer = null;
    this.radarLayer = null;
    this.markersLayer = null;
    this.selectedMarker = null;
  }

  init() {
    if (this.map) return;

    // Centered on India
    this.map = L.map(this.containerId, {
      zoomControl: true,
      minZoom: 4,
      maxZoom: 12
    }).setView([20.0, 78.9], 5);

    // CartoDB Dark Matter / Positron tiles for high-contrast presentation
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://carto.com/">CARTO</a> | IMD MoES Open Data',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(this.map);

    this.isochronesLayer = L.layerGroup().addTo(this.map);
    this.radarLayer = L.layerGroup().addTo(this.map);
    this.markersLayer = L.layerGroup().addTo(this.map);

    // Click on map to request nearest block
    this.map.on('click', (e) => {
      if (this.onLocationSelect) {
        this.onLocationSelect(null, e.latlng.lat, e.latlng.lng);
      }
    });
  }

  renderIsochrones(geojson) {
    if (!this.map || !geojson) return;
    this.isochronesLayer.clearLayers();

    L.geoJSON(geojson, {
      style: (feature) => ({
        color: feature.properties.color || '#3b82f6',
        weight: feature.properties.stroke_width || 3,
        opacity: 0.9,
        dashArray: '6, 6'
      }),
      onEachFeature: (feature, layer) => {
        layer.bindTooltip(
          `<strong>${feature.properties.date}</strong>: ${feature.properties.label}`,
          { permanent: false, direction: 'top', className: 'map-tooltip' }
        );
      }
    }).addTo(this.isochronesLayer);
  }

  renderRadarGrid(radarPoints) {
    if (!this.map || !radarPoints) return;
    this.radarLayer.clearLayers();

    radarPoints.forEach((pt) => {
      let color = '#38bdf8';
      let radius = 18000;
      if (pt.intensity_mm_hr > 15) {
        color = '#ef4444'; // Heavy rain
        radius = 32000;
      } else if (pt.intensity_mm_hr > 5) {
        color = '#f59e0b'; // Moderate rain
        radius = 24000;
      } else if (pt.intensity_mm_hr > 0.5) {
        color = '#10b981'; // Light shower
        radius = 16000;
      } else {
        color = '#64748b'; // Dry
        radius = 10000;
      }

      const circle = L.circle([pt.lat, pt.lon], {
        color: color,
        fillColor: color,
        fillOpacity: 0.45,
        radius: radius,
        weight: 1.5
      });

      circle.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; color: #1e293b;">
          <strong>Doppler Radar Grid Point</strong><br/>
          Intensity: <b>${pt.intensity_mm_hr} mm/hr</b><br/>
          Cloud Top: <b>${pt.cloud_top_km} km</b><br/>
          Lat: ${pt.lat.toFixed(2)}, Lon: ${pt.lon.toFixed(2)}
        </div>
      `);
      circle.addTo(this.radarLayer);
    });
  }

  renderLocations(locations, activeLocationId) {
    if (!this.map || !locations) return;
    this.markersLayer.clearLayers();

    locations.forEach((loc) => {
      const isSelected = (loc.id === activeLocationId);

      const customIcon = L.divIcon({
        className: 'custom-map-pin',
        html: `
          <div style="
            width: ${isSelected ? '24px' : '16px'};
            height: ${isSelected ? '24px' : '16px'};
            background: ${isSelected ? '#10b981' : '#3b82f6'};
            border: 2px solid #ffffff;
            border-radius: 50%;
            box-shadow: 0 0 12px ${isSelected ? 'rgba(16,185,129,0.8)' : 'rgba(59,130,246,0.5)'};
            transition: all 0.2s ease;
            cursor: pointer;
          "></div>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      });

      const lat = loc.latitude !== undefined ? loc.latitude : loc.lat;
      const lon = loc.longitude !== undefined ? loc.longitude : loc.lon;
      const blockName = loc.block_or_mandal || loc.block || '';

      const marker = L.marker([lat, lon], { icon: customIcon });
      marker.bindTooltip(`<b>${loc.name}</b><br/>${blockName}, ${loc.district}`, {
        direction: 'top',
        className: 'map-tooltip'
      });

      marker.on('click', (e) => {
        L.DomEvent.stopPropagation(e);
        if (this.onLocationSelect) {
          this.onLocationSelect(loc.id);
        }
      });

      marker.addTo(this.markersLayer);
    });
  }

  focusLocation(lat, lon) {
    if (this.map) {
      this.map.flyTo([lat, lon], 9, { duration: 1.2 });
    }
  }

  toggleIsochrones(visible) {
    if (!this.map) return;
    if (visible) {
      this.map.addLayer(this.isochronesLayer);
    } else {
      this.map.removeLayer(this.isochronesLayer);
    }
  }

  toggleRadar(visible) {
    if (!this.map) return;
    if (visible) {
      this.map.addLayer(this.radarLayer);
    } else {
      this.map.removeLayer(this.radarLayer);
    }
  }
}
