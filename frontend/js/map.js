class MonsoonMapManager {
  constructor(containerId, onLocationSelectCallback) {
    this.containerId = containerId;
    this.onLocationSelect = onLocationSelectCallback;
    this.map = null;
    this.isochronesLayer = null;
    this.radarLayer = null;
    this.polygonsLayer = null;
    this.markersLayer = null;
    this.blockGeojsonData = null;
    this.activeRiskLayerType = 'break_risk'; // 'break_risk' or 'onset_status'
  }

  init() {
    if (this.map) return;

    // Centered on central/southern India agricultural belt
    this.map = L.map(this.containerId, {
      zoomControl: true,
      minZoom: 4,
      maxZoom: 14
    }).setView([18.5, 78.5], 6);

    // CartoDB Dark Matter tiles for clean high-contrast presentation
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://carto.com/">CARTO</a> | NCMRWF-MoES Open Data',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(this.map);

    this.polygonsLayer = L.layerGroup().addTo(this.map);
    this.isochronesLayer = L.layerGroup().addTo(this.map);
    this.radarLayer = L.layerGroup().addTo(this.map);
    this.markersLayer = L.layerGroup().addTo(this.map);

    this.addMapLegend();

    // Map click handler
    this.map.on('click', (e) => {
      if (this.onLocationSelect) {
        this.onLocationSelect(null, e.latlng.lat, e.latlng.lng);
      }
    });
  }

  addMapLegend() {
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = () => {
      const div = L.DomUtil.create('div', 'info legend');
      div.style.background = 'rgba(10, 15, 29, 0.85)';
      div.style.padding = '8px 12px';
      div.style.borderRadius = '8px';
      div.style.border = '1px solid rgba(59, 130, 246, 0.3)';
      div.style.color = '#f8fafc';
      div.style.fontSize = '11px';
      div.style.lineHeight = '1.5';
      div.innerHTML = `
        <strong style="color:#38bdf8;">Block Dry-Spell Risk</strong><br/>
        <span style="display:inline-block; width:10px; height:10px; background:#10b981; border-radius:2px; margin-right:4px;"></span> Low (&lt;30%)<br/>
        <span style="display:inline-block; width:10px; height:10px; background:#f59e0b; border-radius:2px; margin-right:4px;"></span> Moderate (30-50%)<br/>
        <span style="display:inline-block; width:10px; height:10px; background:#f97316; border-radius:2px; margin-right:4px;"></span> High (50-75%)<br/>
        <span style="display:inline-block; width:10px; height:10px; background:#f43f5e; border-radius:2px; margin-right:4px;"></span> Critical (&gt;75%)
      `;
      return div;
    };
    legend.addTo(this.map);
  }

  renderBlockPolygons(geojson) {
    if (!this.map || !geojson) return;
    this.blockGeojsonData = geojson;
    this.polygonsLayer.clearLayers();

    L.geoJSON(geojson, {
      style: (feature) => {
        const risk = feature.properties.break_risk_level;
        let color = '#10b981';
        let fillColor = '#10b981';

        if (risk === 'CRITICAL') {
          color = '#f43f5e';
          fillColor = '#f43f5e';
        } else if (risk === 'HIGH') {
          color = '#f97316';
          fillColor = '#f97316';
        } else if (risk === 'MODERATE') {
          color = '#f59e0b';
          fillColor = '#f59e0b';
        } else {
          color = '#10b981';
          fillColor = '#10b981';
        }

        return {
          color: color,
          weight: 2,
          fillColor: fillColor,
          fillOpacity: 0.35,
          dashArray: '3'
        };
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        layer.bindTooltip(
          `<strong>${p.name}</strong><br/>Break Risk: <b>${p.break_risk_level} (${p.break_probability_pct}%)</b><br/>Onset: ${p.onset_status}<br/><span style="color:#f59e0b; font-size:10px;">Approximate Demo Polygon</span>`,
          { direction: 'top', className: 'map-tooltip' }
        );

        layer.bindPopup(`
          <div style="font-family:inherit; font-size:12px; color:#0f172a; min-width:180px;">
            <strong style="font-size:13px; color:#1e293b;">${p.name}</strong><br/>
            <span>${p.block_or_mandal}, ${p.district}</span><br/>
            <div style="font-size:10px; color:#b45309; background:#fef3c7; padding:2px 5px; border-radius:3px; margin:4px 0;">
              ⚠️ Approximate Demonstration Geometry (Not official administrative boundary)
            </div>
            <hr style="margin:4px 0; border:0; border-top:1px solid #cbd5e1;"/>
            <b>Monsoon Onset:</b> ${p.onset_status}<br/>
            <b>Dry Spell Risk:</b> <span style="font-weight:700; color:${p.break_risk_level === 'CRITICAL' ? '#e11d48' : '#059669'};">${p.break_risk_level} (${p.break_probability_pct}%)</span><br/>
            <b>Heavy Rain Risk:</b> ${p.heavy_rain_risk}<br/>
            <b>Soil:</b> ${p.primary_soil}<br/>
            <small style="color:#64748b;">Source: ${p.data_provenance}</small><br/>
            <button onclick="window.app.selectLocation('${p.id}')" style="margin-top:6px; background:#2563eb; color:#fff; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; width:100%;">
              Select This Block
            </button>
          </div>
        `);

        layer.on('click', () => {
          if (this.onLocationSelect) {
            this.onLocationSelect(p.id);
          }
        });
      }
    }).addTo(this.polygonsLayer);
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
    if (this.map && lat && lon) {
      this.map.flyTo([lat, lon], 9, { duration: 1.2 });
    }
  }

  toggleIsochrones(visible) {
    if (!this.map) return;
    if (visible) this.map.addLayer(this.isochronesLayer);
    else this.map.removeLayer(this.isochronesLayer);
  }

  toggleRadar(visible) {
    if (!this.map) return;
    if (visible) this.map.addLayer(this.radarLayer);
    else this.map.removeLayer(this.radarLayer);
  }

  togglePolygons(visible) {
    if (!this.map) return;
    if (visible) this.map.addLayer(this.polygonsLayer);
    else this.map.removeLayer(this.polygonsLayer);
  }
}
