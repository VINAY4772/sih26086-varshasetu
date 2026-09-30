// SIH26086 Core Frontend Application Logic
// Supports Flask API, Chart.js Visualizations, English & Telugu Locales

const API_BASE = window.location.origin;

class SIHMonsoonApp {
  constructor() {
    this.currentLang = 'en';
    this.activeLocationId = 'tel_wgl_dharmasagar';
    this.currentHorizon = 14;
    this.currentScenario = null;
    this.locations = [];
    this.mapManager = null;
    this.isIsochronesActive = true;
    this.isRadarActive = true;
    this.isTableModeActive = false;
    this.rainfallChart = null;
    this.localeDictionary = {};
    this.currentAdvisoryData = null;
  }

  async init() {
    await this.loadLocale(this.currentLang);
    this.bindDOMEvents();
    this.initMap();
    await this.loadLocations();
    await this.refreshDashboard();
    await this.loadGISLayers();
    await this.loadModelTransparency();
  }

  async loadLocale(lang) {
    try {
      const res = await fetch(`${API_BASE}/locales/${lang}.json`);
      if (res.ok) {
        this.localeDictionary = await res.json();
      }
    } catch (err) {
      console.warn(`Could not load locales/${lang}.json:`, err);
    }
    this.applyTranslations();
  }

  applyTranslations() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (this.localeDictionary[key]) {
        el.textContent = this.localeDictionary[key];
      }
    });
  }

  bindDOMEvents() {
    // Language Switcher
    const langSelect = document.getElementById('lang-select');
    if (langSelect) {
      langSelect.addEventListener('change', async (e) => {
        this.currentLang = e.target.value;
        await this.loadLocale(this.currentLang);
        await this.refreshDashboard();
      });
    }

    // Location Selector
    const locSelect = document.getElementById('location-select');
    if (locSelect) {
      locSelect.addEventListener('change', async (e) => {
        this.activeLocationId = e.target.value;
        await this.refreshDashboard();
      });
    }

    // Horizon Selector (7, 14, 21, 30 days)
    const horizonSelect = document.getElementById('horizon-select');
    if (horizonSelect) {
      horizonSelect.addEventListener('change', async (e) => {
        this.currentHorizon = parseInt(e.target.value, 10);
        await this.refreshDashboard();
      });
    }

    // Scenario Simulator Buttons
    const scenarioBtns = document.querySelectorAll('.scenario-btn');
    scenarioBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        scenarioBtns.forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        const scenario = e.currentTarget.getAttribute('data-scenario');
        this.currentScenario = scenario === 'default' ? null : scenario;
        this.refreshDashboard();
      });
    });

    // Voice Readout Button (Web Speech TTS)
    const voiceBtn = document.getElementById('voice-advisory-btn');
    if (voiceBtn) {
      voiceBtn.addEventListener('click', () => this.speakAdvisory());
    }

    // Map Layer Toggles
    const toggleIsoBtn = document.getElementById('toggle-isochrones');
    if (toggleIsoBtn) {
      toggleIsoBtn.addEventListener('click', () => {
        this.isIsochronesActive = !this.isIsochronesActive;
        toggleIsoBtn.classList.toggle('active', this.isIsochronesActive);
        this.mapManager.toggleIsochrones(this.isIsochronesActive);
      });
    }

    const toggleRadarBtn = document.getElementById('toggle-radar');
    if (toggleRadarBtn) {
      toggleRadarBtn.addEventListener('click', () => {
        this.isRadarActive = !this.isRadarActive;
        toggleRadarBtn.classList.toggle('active', this.isRadarActive);
        this.mapManager.toggleRadar(this.isRadarActive);
      });
    }

    // Accessible Location Table Alternative Toggle
    const toggleTableBtn = document.getElementById('toggle-table-fallback');
    if (toggleTableBtn) {
      toggleTableBtn.addEventListener('click', () => {
        this.isTableModeActive = !this.isTableModeActive;
        toggleTableBtn.classList.toggle('active', this.isTableModeActive);
        const mapContainer = document.getElementById('map-container');
        const tableContainer = document.getElementById('location-table-container');
        if (mapContainer && tableContainer) {
          mapContainer.style.display = this.isTableModeActive ? 'none' : 'block';
          tableContainer.style.display = this.isTableModeActive ? 'block' : 'none';
        }
      });
    }

    // Messaging Gateway Sandbox Dispatch Handler
    const dispatchBtn = document.getElementById('dispatch-notify-btn');
    if (dispatchBtn) {
      dispatchBtn.addEventListener('click', () => this.handleSimulatedDispatch());
    }

    // Model Info Refresh
    const refreshModelBtn = document.getElementById('refresh-model-info-btn');
    if (refreshModelBtn) {
      refreshModelBtn.addEventListener('click', () => this.loadModelTransparency());
    }
  }

  async handleSimulatedDispatch() {
    const phoneInput = document.getElementById('notify-phone');
    const channelSelect = document.getElementById('notify-channel');
    const consentBox = document.getElementById('notify-consent');
    const statusPill = document.getElementById('notify-status-pill');
    const previewBox = document.getElementById('notify-message-preview');

    if (!consentBox.checked) {
      alert('Farmer opt-in consent is required before alert transmission.');
      return;
    }

    const phone = phoneInput ? phoneInput.value : '+91-9876543210';
    const channel = channelSelect ? channelSelect.value : 'sms';

    // Format localized message body
    let msgBody = '';
    if (this.currentAdvisoryData && this.currentAdvisoryData.advisories && this.currentAdvisoryData.advisories.length > 0) {
      const topCrop = this.currentAdvisoryData.advisories[0];
      if (this.currentLang === 'te') {
        msgBody = `[MoES-NCMRWF] ${topCrop.crop_name}: ${topCrop.priority_action} ${topCrop.irrigation_advice}`;
      } else {
        msgBody = `[MoES-NCMRWF] ${topCrop.crop_name}: ${topCrop.priority_action} ${topCrop.irrigation_advice}`;
      }
    } else {
      msgBody = `[MoES-NCMRWF] Local Monsoon Advisory update for your village.`;
    }

    statusPill.textContent = 'TRANSMITTING...';
    statusPill.style.color = '#f59e0b';

    try {
      const res = await fetch(`${API_BASE}/api/notifications/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, channel, message: msgBody })
      });
      const data = await res.json();

      statusPill.textContent = 'DELIVERED (SIMULATED)';
      statusPill.style.color = '#10b981';
      previewBox.innerHTML = `
        <strong>Channel:</strong> ${data.channel.toUpperCase()} | <strong>Recipient:</strong> ${data.recipient_mask}<br/>
        <strong>Status:</strong> ${data.status} (${data.timestamp.slice(11, 19)} IST)<br/>
        <strong>Message Content:</strong><br/>
        <span style="color:#f8fafc;">${msgBody}</span>
      `;
    } catch (err) {
      statusPill.textContent = 'FAILED';
      statusPill.style.color = '#f43f5e';
      console.error('Dispatch error:', err);
    }
  }

  initMap() {
    this.mapManager = new MonsoonMapManager('map-container', (locId, lat, lon) => {
      if (locId) {
        this.activeLocationId = locId;
        const locSelect = document.getElementById('location-select');
        if (locSelect) locSelect.value = locId;
        this.refreshDashboard();
      }
    });
    this.mapManager.init();
  }

  async loadLocations() {
    try {
      const res = await fetch(`${API_BASE}/api/locations`);
      this.locations = await res.json();

      // Populate Select Dropdown
      const locSelect = document.getElementById('location-select');
      if (locSelect) {
        locSelect.innerHTML = '';
        this.locations.forEach(loc => {
          const opt = document.createElement('option');
          opt.value = loc.id;
          opt.textContent = `${loc.name} (${loc.block_or_mandal}, ${loc.district}, ${loc.state})`;
          if (loc.id === this.activeLocationId) opt.selected = true;
          locSelect.appendChild(opt);
        });
      }

      // Populate Accessible Non-Map Table
      const tableBody = document.getElementById('location-table-body');
      if (tableBody) {
        tableBody.innerHTML = '';
        this.locations.forEach(loc => {
          const tr = document.createElement('tr');
          tr.style.borderBottom = '1px solid rgba(255,255,255,0.05)';
          tr.innerHTML = `
            <td style="padding:0.6rem 0.4rem; font-weight:600; color:#fff;">${loc.name}<br/><small style="color:var(--text-dim);">${loc.block_or_mandal}</small></td>
            <td>${loc.district}</td>
            <td>${loc.state}</td>
            <td>${loc.latitude.toFixed(3)}°N, ${loc.longitude.toFixed(3)}°E</td>
            <td>${loc.primary_soil}</td>
            <td>${loc.normal_onset_date}</td>
            <td>
              <button class="voice-btn" style="padding:0.25rem 0.5rem; font-size:0.7rem;" onclick="window.app.selectLocation('${loc.id}')">Select</button>
            </td>
          `;
          tableBody.appendChild(tr);
        });
      }

      this.mapManager.renderLocations(this.locations, this.activeLocationId);
    } catch (err) {
      console.error('Failed to load locations from API:', err);
    }
  }

  selectLocation(locId) {
    this.activeLocationId = locId;
    const locSelect = document.getElementById('location-select');
    if (locSelect) locSelect.value = locId;
    this.refreshDashboard();
  }

  async loadGISLayers() {
    try {
      const res = await fetch(`${API_BASE}/api/risk-map`);
      const data = await res.json();
      if (data.block_polygons) this.mapManager.renderBlockPolygons(data.block_polygons);
      if (data.isochrones) this.mapManager.renderIsochrones(data.isochrones);
      if (data.radar_grid) this.mapManager.renderRadarGrid(data.radar_grid);
    } catch (err) {
      console.error('Failed to load GIS layers:', err);
    }
  }

  async refreshDashboard() {
    const locParam = `location_id=${this.activeLocationId}`;
    const scenParam = this.currentScenario ? `&scenario=${this.currentScenario}` : '';
    const horizonParam = `&horizon=${this.currentHorizon}`;
    const langParam = `&lang=${this.currentLang}`;

    try {
      const [forecastRes, advisoryRes] = await Promise.all([
        fetch(`${API_BASE}/api/forecast?${locParam}${horizonParam}${scenParam}`),
        fetch(`${API_BASE}/api/advisories?${locParam}${langParam}${scenParam}`)
      ]);

      const forecastData = await forecastRes.json();
      const advisoryData = await advisoryRes.json();
      this.currentAdvisoryData = advisoryData;

      this.renderAlertBanner(forecastData, advisoryData);
      this.renderOnsetCard(forecastData);
      this.renderBreakCard(forecastData);
      this.renderTelemetry(forecastData);
      this.renderClimateDrivers(forecastData);
      this.renderChartAndTimeline(forecastData);
      this.renderCrops(advisoryData);

      // Focus map to location coordinates
      if (forecastData.location) {
        this.mapManager.focusLocation(forecastData.location.latitude, forecastData.location.longitude);
        this.mapManager.renderLocations(this.locations, this.activeLocationId);
      }
    } catch (err) {
      console.error('Error refreshing dashboard:', err);
    }
  }

  renderAlertBanner(forecastData, advisoryData) {
    const banner = document.getElementById('alert-banner');
    if (!banner) return;

    banner.className = 'alert-banner';
    const breakRisk = forecastData.break_spell_outlook.risk_level;
    const isFalseAlarm = forecastData.onset_outlook.is_false_alarm;

    let alertClass = 'alert-green';
    let icon = '🌱';
    let headline = '';
    let desc = '';

    if (isFalseAlarm) {
      alertClass = 'alert-yellow';
      icon = '⚠️';
      headline = (this.currentLang === 'te')
        ? 'నకిలీ రుతుపవన హెచ్చరిక: పొడి దుక్కిలో విత్తనాలు వేయకండి'
        : 'False Onset Warning: Local Thunderstorm without Synoptic Monsoon Circulation';
      desc = (this.currentLang === 'te')
        ? 'ఉపరితల పశ్చిమ గాలుల తీవ్రత లోపించింది. విత్తనం మాడిపోయే ప్రమాదం ఉన్నందున వర్షాలు స్థిరపడే వరకు వేచి చూడండి.'
        : 'Surface rain observed without deep tropospheric westerly shear. Premature sowing may result in seed germination failure.';
    } else if (breakRisk === 'CRITICAL' || breakRisk === 'HIGH') {
      alertClass = 'alert-red';
      icon = '🚨';
      headline = (this.currentLang === 'te')
        ? `తీవ్ర బెట్ట / వర్షాభావ హెచ్చరిక (${forecastData.break_spell_outlook.projected_consecutive_dry_days} రోజులు వర్షాభావం)`
        : `Monsoon Break Alert: Prolonged Dry Spell Projected (${forecastData.break_spell_outlook.projected_consecutive_dry_days} Consecutive Dry Days)`;
      desc = (this.currentLang === 'te')
        ? 'యూరియా పైపాటు వేయకండి. జీవనాధార రక్షక తడి ఇవ్వండి మరియు నేల తేమను కాపాడటానికి మల్చింగ్ చేయండి.'
        : 'Monsoon trough shifted toward Himalayan foothills. Suspend chemical nitrogen top-dressing; apply mulch.';
    } else {
      alertClass = 'alert-green';
      icon = '🌧️';
      headline = (this.currentLang === 'te')
        ? 'నైరుతి రుతుపవనాలు చురుకుగా ఉన్నాయి: ఖరీఫ్ విత్తుకోవడానికి అనుకూలం'
        : 'Active Southwest Monsoon Current Established across Catchment';
      desc = (this.currentLang === 'te')
        ? 'నేలలో తగినంత తేమ లభ్యత ఉంది. సిఫార్సు చేసిన విత్తన శుద్ధి పూర్తి చేసుకుని విత్తుకోండి.'
        : 'Soil moisture saturation reached optimal threshold. Favorable window open for Kharif field operations.';
    }

    banner.classList.add(alertClass);
    document.getElementById('alert-icon').textContent = icon;
    document.getElementById('alert-headline').textContent = headline;
    document.getElementById('alert-desc').textContent = desc;
  }

  renderOnsetCard(data) {
    const onset = data.onset_outlook;
    const phaseBadge = document.getElementById('onset-phase-badge');
    if (phaseBadge) {
      phaseBadge.textContent = onset.status.replace(/_/g, ' ');
      phaseBadge.className = 'badge ' + (onset.status === 'ONSET_DECLARED' ? 'badge-active' : (onset.is_false_alarm ? 'badge-critical' : 'badge-watch'));
    }

    document.getElementById('predicted-onset-date').textContent = onset.status === 'ONSET_DECLARED' ? 'Onset Declared' : (onset.is_false_alarm ? 'False Alarm' : 'Imminent (3-5d)');
    document.getElementById('normal-onset-date').textContent = onset.normal_onset_date;
    document.getElementById('onset-confidence').textContent = `${Math.round(onset.confidence_score * 100)}%`;

    const tagRain = document.getElementById('tag-rain');
    const tagWind = document.getElementById('tag-wind');
    const tagOlr = document.getElementById('tag-olr');
    const tagDir = document.getElementById('tag-dir');

    const isSatisfied = (onset.status === 'ONSET_DECLARED');
    const passText = (this.currentLang === 'te') ? '✓ నిబంధన నెరవేరింది' : '✓ SATISFIED';
    const failText = (this.currentLang === 'te') ? '✗ పెండింగ్‌లో ఉంది' : '✗ PENDING';

    if (tagRain) tagRain.textContent = isSatisfied || onset.is_false_alarm ? passText : failText;
    if (tagWind) tagWind.textContent = isSatisfied ? passText : failText;
    if (tagOlr) tagOlr.textContent = isSatisfied ? passText : failText;
    if (tagDir) tagDir.textContent = isSatisfied ? passText : failText;
  }

  renderBreakCard(data) {
    const brk = data.break_spell_outlook;
    const riskBadge = document.getElementById('break-risk-badge');
    if (riskBadge) {
      riskBadge.textContent = `${brk.risk_level} RISK`;
      if (brk.risk_level === 'CRITICAL' || brk.risk_level === 'HIGH') {
        riskBadge.className = 'badge badge-critical';
      } else if (brk.risk_level === 'MODERATE') {
        riskBadge.className = 'badge badge-watch';
      } else {
        riskBadge.className = 'badge badge-active';
      }
    }

    document.getElementById('break-probability-val').textContent = `${(brk.probability * 100).toFixed(1)}%`;
    document.getElementById('dry-days-val').textContent = `${brk.projected_consecutive_dry_days} Days`;

    const anomaly = data.rainfall_anomaly_outlook;
    const anomalyEl = document.getElementById('anomaly-val');
    if (anomalyEl) {
      anomalyEl.textContent = `${anomaly.departure_percentage > 0 ? '+' : ''}${anomaly.departure_percentage}% (${anomaly.category})`;
      anomalyEl.style.color = (anomaly.departure_percentage < -20) ? '#f43f5e' : '#38bdf8';
    }

    const heavyEl = document.getElementById('heavy-rain-val');
    if (heavyEl) {
      heavyEl.textContent = data.heavy_rainfall_risk.heavy_rainfall_risk.replace(/_/g, ' ');
    }
  }

  renderTelemetry(data) {
    const timeline = data.timeline;
    if (!timeline || timeline.length === 0) return;
    const current = timeline[0];

    document.getElementById('metric-rain-val').textContent = `${current.rainfall_mm} mm`;
    document.getElementById('metric-temp-val').textContent = `${current.temp_max_c} °C`;
    document.getElementById('metric-moist-val').textContent = `${current.soil_moisture_pct} %`;
    document.getElementById('metric-humidity-val').textContent = `${current.humidity_pct} %`;
  }

  renderClimateDrivers(data) {
    const cd = data.climate_drivers;
    if (!cd) return;

    const ensoVal = document.getElementById('tele-enso-val');
    const ensoDesc = document.getElementById('tele-enso-desc');
    const ensoStatus = document.getElementById('tele-enso-status');
    if (ensoVal && cd.enso) {
      const sign = cd.enso.nino34_anomaly_c >= 0 ? '+' : '';
      ensoVal.textContent = `${sign}${cd.enso.nino34_anomaly_c.toFixed(2)} °C (${cd.enso.phase})`;
      if (ensoDesc) ensoDesc.textContent = cd.enso.effect_on_monsoon || 'SST telemetry';
      if (ensoStatus) {
        if (cd.enso.source_status === 'LIVE_VERIFIED_NOAA_CPC') {
          ensoStatus.textContent = 'LIVE NOAA CPC';
          ensoStatus.style.background = 'rgba(16,185,129,0.2)';
          ensoStatus.style.color = '#34d399';
        } else {
          ensoStatus.textContent = 'CONFIGURED BENCHMARK';
          ensoStatus.style.background = 'rgba(255,255,255,0.08)';
          ensoStatus.style.color = '#94a3b8';
        }
      }
    }

    const iodVal = document.getElementById('tele-iod-val');
    const iodDesc = document.getElementById('tele-iod-desc');
    const iodStatus = document.getElementById('tele-iod-status');
    if (iodVal && cd.iod) {
      const sign = cd.iod.dipole_mode_index_c >= 0 ? '+' : '';
      iodVal.textContent = `${sign}${cd.iod.dipole_mode_index_c.toFixed(2)} °C (${cd.iod.phase})`;
      if (iodDesc) iodDesc.textContent = cd.iod.effect_on_monsoon || 'Thermal gradient';
      if (iodStatus) {
        iodStatus.textContent = 'CONFIGURED BENCHMARK';
        iodStatus.style.background = 'rgba(255,255,255,0.08)';
        iodStatus.style.color = '#94a3b8';
      }
    }

    const mjoVal = document.getElementById('tele-mjo-val');
    const mjoDesc = document.getElementById('tele-mjo-desc');
    const mjoStatus = document.getElementById('tele-mjo-status');
    if (mjoVal && cd.mjo) {
      mjoVal.textContent = `Phase ${cd.mjo.phase} (Amp: ${cd.mjo.amplitude.toFixed(1)})`;
      if (mjoDesc) mjoDesc.textContent = cd.mjo.status || 'MJO Wave State';
      if (mjoStatus) {
        mjoStatus.textContent = 'CONFIGURED BENCHMARK';
        mjoStatus.style.background = 'rgba(255,255,255,0.08)';
        mjoStatus.style.color = '#94a3b8';
      }
    }
  }

  renderChartAndTimeline(data) {
    const timeline = data.timeline;
    if (!timeline || timeline.length === 0) return;

    // Render Timeline List
    const list = document.getElementById('timeline-list');
    if (list) {
      list.innerHTML = '';
      timeline.forEach((pt, idx) => {
        const item = document.createElement('div');
        item.className = 'timeline-item';
        item.innerHTML = `
          <div>
            <div class="timeline-date">Day ${pt.day_offset} (${pt.date.slice(5)})</div>
            <div class="timeline-moist">Soil Moisture: ${pt.soil_moisture_pct}% | Temp: ${pt.temp_max_c}°C</div>
          </div>
          <div style="text-align: right;">
            <div class="timeline-rain">${pt.rainfall_mm} mm</div>
            <small style="color:${pt.is_dry_day ? '#f43f5e' : '#10b981'}; font-weight:700;">
              ${pt.is_dry_day ? 'Dry Day' : 'Rain Day'}
            </small>
          </div>
        `;
        list.appendChild(item);
      });
    }

    // Render Chart.js Chart
    const ctx = document.getElementById('rainfall-chart');
    if (!ctx) return;

    const labels = timeline.map(pt => `D+${pt.day_offset}`);
    const rainData = timeline.map(pt => pt.rainfall_mm);
    const soilData = timeline.map(pt => pt.soil_moisture_pct);

    if (this.rainfallChart) {
      this.rainfallChart.destroy();
    }

    this.rainfallChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Daily Rainfall (mm)',
            data: rainData,
            backgroundColor: 'rgba(56, 189, 248, 0.75)',
            borderColor: '#38bdf8',
            borderWidth: 1,
            yAxisID: 'y'
          },
          {
            label: 'Root Soil Moisture (%)',
            data: soilData,
            type: 'line',
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: true,
            tension: 0.35,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8', font: { size: 10 } }
          },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: { display: true, text: 'Rain (mm)', color: '#38bdf8', font: { size: 10 } },
            ticks: { color: '#94a3b8' },
            grid: { color: 'rgba(255, 255, 255, 0.05)' }
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            title: { display: true, text: 'Soil Moisture %', color: '#10b981', font: { size: 10 } },
            min: 0,
            max: 100,
            ticks: { color: '#94a3b8' },
            grid: { drawOnChartArea: false }
          }
        },
        plugins: {
          legend: {
            labels: { color: '#f8fafc', font: { size: 11 } }
          }
        }
      }
    });
  }

  renderCrops(advisoryData) {
    const grid = document.getElementById('crops-grid');
    if (!grid) return;
    grid.innerHTML = '';

    const advisories = advisoryData.advisories || [];
    advisories.forEach(crop => {
      const card = document.createElement('div');
      card.className = 'crop-card';

      let sowClass = 'sow-optimal';
      if (crop.sowing_status.includes('POSTPONE') || crop.sowing_status.includes('FALSE')) {
        sowClass = 'sow-risk';
      } else if (crop.sowing_status.includes('AWAIT')) {
        sowClass = 'sow-wait';
      }

      card.innerHTML = `
        <div>
          <div class="crop-card-top">
            <h3 class="crop-name">${crop.crop_name}</h3>
            <span class="sowing-badge ${sowClass}">${crop.sowing_status.replace(/_/g, ' ')}</span>
          </div>

          <div class="crop-details">
            <div class="detail-row">
              <strong>📅 ${this.localeDictionary.crop_sowing_window || 'Sowing Window'}</strong>
              <span>${crop.sowing_window}</span>
            </div>
            <div class="detail-row">
              <strong>💧 ${this.localeDictionary.crop_irrigation || 'Irrigation'}</strong>
              <span>${crop.irrigation_advice}</span>
            </div>
            <div class="detail-row">
              <strong>🧪 ${this.localeDictionary.crop_fertilizer || 'Fertilizer'}</strong>
              <span>${crop.fertilizer_advice}</span>
            </div>
            <div class="detail-row">
              <strong>🐛 ${this.localeDictionary.crop_pest || 'Pest & Disease Watch'}</strong>
              <span>${crop.pest_disease_advice}</span>
            </div>
            <div class="detail-row" style="margin-top:0.4rem; padding-top:0.4rem; border-top:1px dashed rgba(255,255,255,0.08);">
              <small style="color:var(--text-dim);">🔬 <b>${this.localeDictionary.crop_reasoning || 'Reasoning'}:</b> ${crop.reasoning}</small>
            </div>
          </div>
        </div>

        <div class="action-box">
          <b>⚡ ${this.localeDictionary.crop_action || 'Priority Action'}:</b> ${crop.priority_action}
        </div>
      `;
      grid.appendChild(card);
    });
  }

  async loadModelTransparency() {
    try {
      const res = await fetch(`${API_BASE}/api/model-info`);
      const data = await res.json();
      const container = document.getElementById('model-metrics-pills');
      if (container && data.metrics) {
        container.innerHTML = `
          <div style="background:rgba(255,255,255,0.05); padding:0.4rem 0.8rem; border-radius:6px;">
            <small style="color:var(--text-dim);">Brier Skill Score:</small> <b style="color:var(--accent-emerald);">+${data.metrics.brier_skill_score}</b>
          </div>
          <div style="background:rgba(255,255,255,0.05); padding:0.4rem 0.8rem; border-radius:6px;">
            <small style="color:var(--text-dim);">Model Brier Loss:</small> <b style="color:#fff;">${data.metrics.brier_score}</b> (Clim: ${data.metrics.brier_climatology_baseline})
          </div>
          <div style="background:rgba(255,255,255,0.05); padding:0.4rem 0.8rem; border-radius:6px;">
            <small style="color:var(--text-dim);">ROC-AUC:</small> <b style="color:var(--accent-cyan);">${data.metrics.roc_auc}</b>
          </div>
          <div style="background:rgba(255,255,255,0.05); padding:0.4rem 0.8rem; border-radius:6px;">
            <small style="color:var(--text-dim);">Precision / Recall:</small> <b style="color:#fff;">${data.metrics.precision} / ${data.metrics.recall}</b>
          </div>
        `;
      }
    } catch (err) {
      console.error('Error fetching model info:', err);
    }
  }

  speakAdvisory() {
    if (!('speechSynthesis' in window)) {
      alert('Speech synthesis is not supported on this device.');
      return;
    }

    window.speechSynthesis.cancel();
    if (!this.currentAdvisoryData || !this.currentAdvisoryData.advisories) return;

    const voiceBtn = document.getElementById('voice-advisory-btn');
    const playingTxt = this.localeDictionary.btn_playing_audio || 'Playing Audio...';
    if (voiceBtn) voiceBtn.innerHTML = `<span>🔊</span> ${playingTxt}`;

    const advisories = this.currentAdvisoryData.advisories;
    let spokenText = (this.currentLang === 'te')
      ? 'భారత ప్రభుత్వ భూ శాస్త్రాల మంత్రిత్వ శాఖ వ్యవసాయ వాతావరణ సమాచారం. '
      : 'Ministry of Earth Sciences Hyperlocal Monsoon Advisory. ';

    if (advisories.length > 0) {
      const top = advisories[0];
      spokenText += `${top.crop_name}: ${top.priority_action}. ${top.irrigation_advice}`;
    }

    const utterance = new SpeechSynthesisUtterance(spokenText);
    utterance.lang = (this.currentLang === 'te') ? 'te-IN' : 'en-IN';
    utterance.rate = 0.95;

    utterance.onend = () => {
      const listenTxt = this.localeDictionary.btn_listen_audio || 'Listen Audio Advisory';
      if (voiceBtn) voiceBtn.innerHTML = `<span>🔊</span> ${listenTxt}`;
    };
    utterance.onerror = () => {
      const listenTxt = this.localeDictionary.btn_listen_audio || 'Listen Audio Advisory';
      if (voiceBtn) voiceBtn.innerHTML = `<span>🔊</span> ${listenTxt}`;
    };

    window.speechSynthesis.speak(utterance);
  }
}

if (typeof window !== 'undefined') {
  window.SIHMonsoonApp = SIHMonsoonApp;
}

// Global initialization
window.addEventListener('DOMContentLoaded', () => {
  window.app = new SIHMonsoonApp();
  window.app.init();
});
