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
    this.lastLocations = null;
    this.lastActiveLocationId = null;
    this.lastRadarPoints = null;
    this.legendControl = null;
    this.localeDict = {};
    this.activeRiskLayerType = 'break_risk'; // 'break_risk' or 'onset_status'
  }

  setLocale(dict) {
    this.localeDict = dict || {};
    this.updateLegend();
    if (this.lastLocations) {
      this.renderLocations(this.lastLocations, this.lastActiveLocationId);
    }
    if (this.blockGeojsonData) {
      this.renderBlockPolygons(this.blockGeojsonData);
    }
    if (this.lastRadarPoints) {
      this.renderRadarGrid(this.lastRadarPoints);
    }
  }

  init() {
    if (this.map) return;

    // Centered on central/southern India agricultural belt
    this.map = L.map(this.containerId, {
      zoomControl: true,
      minZoom: 4,
      maxZoom: 14
    }).setView([18.5, 78.5], 6);

    // Standard OpenStreetMap raster tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors | NCMRWF-MoES Open Data',
      subdomains: 'abc',
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
    this.legendControl = L.control({ position: 'bottomright' });
    this.legendControl.onAdd = () => {
      const div = L.DomUtil.create('div', 'info legend');
      div.id = 'map-legend-box';
      div.style.background = 'rgba(255, 255, 255, 0.95)';
      div.style.padding = '8px 12px';
      div.style.borderRadius = '8px';
      div.style.border = '1px solid #e2e8f0';
      div.style.color = '#111827';
      div.style.boxShadow = '0 1px 4px rgba(15, 23, 42, 0.1)';
      div.style.fontSize = '11px';
      div.style.lineHeight = '1.5';
      this.populateLegendContent(div);
      return div;
    };
    this.legendControl.addTo(this.map);
  }

  updateLegend() {
    const div = document.getElementById('map-legend-box');
    if (div) {
      this.populateLegendContent(div);
    }
  }

  populateLegendContent(div) {
    const d = this.localeDict || {};
    const title = d.map_legend_title || 'Block Dry-Spell Risk';
    const low = d.map_legend_low || 'Low (<30%)';
    const mod = d.map_legend_moderate || 'Moderate (30-50%)';
    const high = d.map_legend_high || 'High (50-75%)';
    const crit = d.map_legend_critical || 'Critical (>75%)';

    div.innerHTML = `
      <strong style="color:#0284c7;">${title}</strong><br/>
      <span style="display:inline-block; width:10px; height:10px; background:#10b981; border-radius:2px; margin-right:4px;"></span> ${low}<br/>
      <span style="display:inline-block; width:10px; height:10px; background:#f59e0b; border-radius:2px; margin-right:4px;"></span> ${mod}<br/>
      <span style="display:inline-block; width:10px; height:10px; background:#f97316; border-radius:2px; margin-right:4px;"></span> ${high}<br/>
      <span style="display:inline-block; width:10px; height:10px; background:#f43f5e; border-radius:2px; margin-right:4px;"></span> ${crit}
    `;
  }

  renderBlockPolygons(geojson) {
    if (!this.map || !geojson) return;
    this.blockGeojsonData = geojson;
    this.polygonsLayer.clearLayers();
    const d = this.localeDict || {};

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
        const approxGeo = d.map_popup_approx_geo || 'Approximate Demonstration Geometry (Not official administrative boundary)';
        const monsoonOnsetLabel = d.map_popup_monsoon_onset || 'Monsoon Onset';
        const drySpellRiskLabel = d.map_popup_dry_spell_risk || 'Dry Spell Risk';
        const heavyRainRiskLabel = d.map_popup_heavy_rain_risk || 'Heavy Rain Risk';
        const soilLabel = d.map_popup_soil || 'Soil';
        const sourceLabel = d.map_popup_source || 'Source';
        const selectBlockLabel = d.map_popup_block_select || 'Select This Block';

        layer.bindTooltip(
          `<strong>${p.name}</strong><br/>${drySpellRiskLabel}: <b>${p.break_risk_level} (${p.break_probability_pct}%)</b><br/>${monsoonOnsetLabel}: ${p.onset_status}<br/><span style="color:#f59e0b; font-size:10px;">${approxGeo}</span>`,
          { direction: 'top', className: 'map-tooltip' }
        );

        layer.bindPopup(`
          <div style="font-family:inherit; font-size:12px; color:#0f172a; min-width:180px;">
            <strong style="font-size:13px; color:#1e293b;">${p.name}</strong><br/>
            <span>${p.block_or_mandal}, ${p.district}</span><br/>
            <div style="font-size:10px; color:#b45309; background:#fef3c7; padding:2px 5px; border-radius:3px; margin:4px 0;">
              ⚠️ ${approxGeo}
            </div>
            <hr style="margin:4px 0; border:0; border-top:1px solid #cbd5e1;"/>
            <b>${monsoonOnsetLabel}:</b> ${p.onset_status}<br/>
            <b>${drySpellRiskLabel}:</b> <span style="font-weight:700; color:${p.break_risk_level === 'CRITICAL' ? '#e11d48' : '#059669'};">${p.break_risk_level} (${p.break_probability_pct}%)</span><br/>
            <b>${heavyRainRiskLabel}:</b> ${p.heavy_rain_risk}<br/>
            <b>${soilLabel}:</b> ${p.primary_soil}<br/>
            <small style="color:#64748b;">${sourceLabel}: ${p.data_provenance}</small><br/>
            <button onclick="window.app.selectLocation('${p.id}')" style="margin-top:6px; background:#2563eb; color:#fff; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; width:100%;">
              ${selectBlockLabel}
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
      const lat = loc.latitude !== undefined ? loc.latitude : loc.lat;
      const lon = loc.longitude !== undefined ? loc.longitude : loc.lon;
      const blockName = loc.block_or_mandal || loc.block || '';
      const pinColor = isSelected ? '#10b981' : '#2563eb';

      const customIcon = L.divIcon({
        className: `custom-map-pin ${isSelected ? 'active-pin' : ''}`,
        html: `
          <div style="position:relative; width:28px; height:36px;">
            <svg width="28" height="36" viewBox="0 0 28 36" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 0C6.268 0 0 6.268 0 14C0 24.5 14 36 14 36C14 36 28 24.5 28 14C28 6.268 21.732 0 14 0Z" fill="${pinColor}" stroke="#ffffff" stroke-width="2"/>
              <circle cx="14" cy="13" r="5.5" fill="#ffffff"/>
              <circle cx="14" cy="13" r="3" fill="${pinColor}"/>
            </svg>
            ${isSelected ? '<span style="position:absolute; top:-2px; left:-2px; width:32px; height:32px; border-radius:50%; border:2px solid #10b981; animation:leaflet-pulse 1.8s infinite; pointer-events:none;"></span>' : ''}
          </div>
        `,
        iconSize: [28, 36],
        iconAnchor: [14, 36],
        popupAnchor: [0, -36]
      });

      const marker = L.marker([lat, lon], {
        icon: customIcon,
        zIndexOffset: isSelected ? 3000 : 1500,
        title: `${loc.name} (${blockName})`
      });

      marker.bindTooltip(`<b>${loc.name}</b><br/>${blockName}, ${loc.district}`, {
        direction: 'top',
        offset: [0, -34],
        className: 'map-tooltip'
      });

      marker.bindPopup(`
        <div style="font-family:inherit; font-size:12px; color:#0f172a; min-width:210px; line-height:1.4;">
          <strong style="font-size:13px; color:#1e293b;">📍 ${loc.name}</strong><br/>
          <span style="color:#64748b; font-size:11px;">${blockName}, ${loc.district}, ${loc.state}</span>
          <hr style="margin:5px 0; border:0; border-top:1px solid #e2e8f0;"/>
          <div style="font-size:11px; margin-bottom:6px;">
            <b>Coordinates:</b> ${Number(lat).toFixed(4)}°N, ${Number(lon).toFixed(4)}°E<br/>
            <b>IMD Normal Onset:</b> ${loc.normal_onset_date || 'N/A'}<br/>
            <b>Primary Soil:</b> ${loc.primary_soil || 'N/A'}<br/>
            <b>Agro-Zone:</b> ${loc.agro_climatic_zone || 'N/A'}
          </div>
          <button onclick="window.app.selectLocation('${loc.id}')" style="background:#2563eb; color:#fff; border:none; padding:5px 10px; border-radius:4px; cursor:pointer; width:100%; font-size:11px; font-weight:600;">
            ${isSelected ? '✓ Currently Selected' : 'Select This Location'}
          </button>
        </div>
      `);

      marker.on('click', () => {
        if (this.onLocationSelect && !isSelected) {
          this.onLocationSelect(loc.id);
        }
      });

      marker.addTo(this.markersLayer);
    });
  }

  fitAllLocations(locations) {
    if (!this.map || !locations || locations.length === 0) return;
    const latLngs = locations
      .map(loc => {
        const lat = loc.latitude !== undefined ? loc.latitude : loc.lat;
        const lon = loc.longitude !== undefined ? loc.longitude : loc.lon;
        return (lat && lon) ? [lat, lon] : null;
      })
      .filter(Boolean);
    if (latLngs.length > 0) {
      this.map.fitBounds(latLngs, { padding: [40, 40], maxZoom: 7 });
    }
  }

  focusLocation(lat, lon, zoom = 8) {
    if (this.map && lat && lon) {
      this.map.flyTo([lat, lon], zoom, { duration: 1.0 });
    }
  }

  toggleIsochrones(visible) {
    if (!this.map || !this.isochronesLayer) return;
    if (visible) {
      if (!this.map.hasLayer(this.isochronesLayer)) this.map.addLayer(this.isochronesLayer);
    } else {
      if (this.map.hasLayer(this.isochronesLayer)) this.map.removeLayer(this.isochronesLayer);
    }
  }

  toggleRadar(visible) {
    if (!this.map || !this.radarLayer) return;
    if (visible) {
      if (!this.map.hasLayer(this.radarLayer)) this.map.addLayer(this.radarLayer);
    } else {
      if (this.map.hasLayer(this.radarLayer)) this.map.removeLayer(this.radarLayer);
    }
  }

  togglePolygons(visible) {
    if (!this.map || !this.polygonsLayer) return;
    if (visible) {
      if (!this.map.hasLayer(this.polygonsLayer)) this.map.addLayer(this.polygonsLayer);
    } else {
      if (this.map.hasLayer(this.polygonsLayer)) this.map.removeLayer(this.polygonsLayer);
    }
  }
}

if (typeof window !== 'undefined') {
  window.MonsoonMapManager = MonsoonMapManager;
}
