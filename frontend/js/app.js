// VarshaSetu Core Frontend Application Logic
// Supports Flask API, Chart.js Visualizations, and 7 Official Locales (EN, TE, HI, TA, KN, UR, ML)

const API_BASE = window.location.origin;

// Canonical BCP-47 Speech Synthesis Configuration for 7 Scheduled Languages
const TTS_LANGUAGE_CONFIG = {
  en: { bcp47: 'en-IN', fallbacks: ['en-GB', 'en-US', 'en'], name: 'English' },
  te: { bcp47: 'te-IN', fallbacks: ['te'], name: 'Telugu' },
  hi: { bcp47: 'hi-IN', fallbacks: ['hi'], name: 'Hindi' },
  ta: { bcp47: 'ta-IN', fallbacks: ['ta'], name: 'Tamil' },
  kn: { bcp47: 'kn-IN', fallbacks: ['kn'], name: 'Kannada' },
  ur: { bcp47: 'ur-IN', fallbacks: ['ur-PK', 'ur'], name: 'Urdu' },
  ml: { bcp47: 'ml-IN', fallbacks: ['ml'], name: 'Malayalam' }
};

class SIHMonsoonApp {
  constructor() {
    const savedLang = typeof localStorage !== 'undefined' ? localStorage.getItem('varshasetu_language') : null;
    const supported = ['en', 'te', 'hi', 'ta', 'kn', 'ur', 'ml'];
    this.currentLang = (savedLang && supported.includes(savedLang)) ? savedLang : 'en';
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
    this.lastForecastData = null;
    this.cachedVoices = [];
    this.voicesChangedBound = false;
  }

  async init() {
    this.initSpeechSynthesis();
    this.initMap();
    this.bindDOMEvents();
    await this.loadLocale(this.currentLang);
    await this.loadLocations();
    await this.refreshDashboard(true);
    await this.loadGISLayers();
    await this.loadModelTransparency();
    await this.loadNotificationHistory();
  }

  initSpeechSynthesis() {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
    if (typeof window.speechSynthesis.getVoices !== 'function') return;

    this.cachedVoices = window.speechSynthesis.getVoices() || [];

    if (!this.voicesChangedBound && typeof window.speechSynthesis.addEventListener === 'function') {
      this.voicesChangedBound = true;
      window.speechSynthesis.addEventListener('voiceschanged', () => {
        this.cachedVoices = (typeof window.speechSynthesis.getVoices === 'function')
          ? (window.speechSynthesis.getVoices() || [])
          : [];
      });
    }
  }

  async loadLocale(lang) {
    const supported = ['en', 'te', 'hi', 'ta', 'kn', 'ur', 'ml'];
    if (!supported.includes(lang)) lang = 'en';
    this.currentLang = lang;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('varshasetu_language', lang);
    }

    // Safety: Cancel any active/stale speech utterance when changing languages
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const voiceBtn = document.getElementById('voice-advisory-btn');
      if (voiceBtn) {
        const listenTxt = this.localeDictionary?.btn_listen_audio || 'Listen Audio Advisory';
        voiceBtn.innerHTML = `<span>🔊</span> <span data-i18n="btn_listen_audio">${listenTxt}</span>`;
      }
    }

    // Configure document direction and language code
    const isRtl = (lang === 'ur');
    document.documentElement.setAttribute('dir', isRtl ? 'rtl' : 'ltr');
    document.documentElement.setAttribute('lang', lang);
    document.body.classList.toggle('rtl-layout', isRtl);

    try {
      const res = await fetch(`${API_BASE}/locales/${lang}.json`);
      if (res.ok) {
        this.localeDictionary = await res.json();
      }
    } catch (err) {
      console.warn(`Could not load locales/${lang}.json:`, err);
    }

    this.applyTranslations();

    if (this.mapManager) {
      this.mapManager.setLocale(this.localeDictionary);
    }

    const langSelect = document.getElementById('lang-select');
    if (langSelect && langSelect.value !== lang) {
      langSelect.value = lang;
    }
  }

  applyTranslations() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (this.localeDictionary && this.localeDictionary[key]) {
        el.textContent = this.localeDictionary[key];
      }
    });

    const attrElements = document.querySelectorAll('[data-i18n-attr]');
    attrElements.forEach(el => {
      const mapping = el.getAttribute('data-i18n-attr');
      const pairs = mapping.split(';');
      pairs.forEach(pair => {
        const [attr, key] = pair.split(':').map(s => s.trim());
        if (attr && key && this.localeDictionary && this.localeDictionary[key]) {
          el.setAttribute(attr, this.localeDictionary[key]);
        }
      });
    });
  }

  bindDOMEvents() {
    // Language Switcher
    const langSelect = document.getElementById('lang-select');
    if (langSelect) {
      langSelect.value = this.currentLang;
      langSelect.addEventListener('change', async (e) => {
        const newLang = e.target.value;
        await this.loadLocale(newLang);
        await this.refreshDashboard(false);
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
        if (this.mapManager) {
          this.mapManager.toggleIsochrones(this.isIsochronesActive);
        }
      });
    }

    const toggleRadarBtn = document.getElementById('toggle-radar');
    if (toggleRadarBtn) {
      toggleRadarBtn.addEventListener('click', () => {
        this.isRadarActive = !this.isRadarActive;
        toggleRadarBtn.classList.toggle('active', this.isRadarActive);
        if (this.mapManager) {
          this.mapManager.toggleRadar(this.isRadarActive);
        }
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
        if (!this.isTableModeActive && this.mapManager && this.mapManager.map) {
          setTimeout(() => {
            this.mapManager.map.invalidateSize();
          }, 80);
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
    const recipientSelect = document.getElementById('notify-recipient-type');
    const cropSelect = document.getElementById('notify-crop-select');
    const consentBox = document.getElementById('notify-consent');
    const statusPill = document.getElementById('notify-status-pill');
    const previewBox = document.getElementById('notify-message-preview');
    const d = this.localeDictionary || {};

    if (consentBox && !consentBox.checked) {
      alert(d.notify_consent_alert || 'Recipient opt-in consent is required before alert transmission.');
      return;
    }

    const phone = phoneInput ? phoneInput.value : '+91 98765 43210';
    const channel = channelSelect ? channelSelect.value : 'sms';
    const recipientType = recipientSelect ? recipientSelect.value : 'farmer';
    const selectedCropCode = cropSelect ? cropSelect.value : 'paddy';

    // Extract forecast and location context
    const locationName = (this.lastForecastData && this.lastForecastData.location)
      ? `${this.lastForecastData.location.name} (${this.lastForecastData.location.block_or_mandal})`
      : 'Local Catchment';

    let targetedCrop = null;
    if (this.currentAdvisoryData && this.currentAdvisoryData.advisories) {
      targetedCrop = this.currentAdvisoryData.advisories.find(c => c.crop_code === selectedCropCode) || this.currentAdvisoryData.advisories[0];
    }

    const cropName = targetedCrop ? targetedCrop.crop_name : selectedCropCode.toUpperCase();
    const horizonDays = this.currentHorizon || 14;

    // Determine risk condition
    let riskCondition = 'Normal seasonal progression';
    if (this.lastForecastData && this.lastForecastData.break_spell_outlook) {
      const bRisk = this.lastForecastData.break_spell_outlook.risk_level;
      const bProb = Math.round((this.lastForecastData.break_spell_outlook.probability || 0) * 100);
      if (bRisk === 'CRITICAL' || bRisk === 'HIGH') {
        riskCondition = `Elevated prolonged dry-spell probability (${bProb}%)`;
      } else if (this.lastForecastData.onset_outlook && this.lastForecastData.onset_outlook.status === 'ONSET_DECLARED') {
        riskCondition = 'Active Southwest Monsoon surge established';
      }
    }

    // Determine tailored action based on recipient type
    let actionDirective = '';
    if (recipientType === 'officer') {
      if (riskCondition.includes('dry-spell') || riskCondition.includes('break')) {
        actionDirective = 'Prepare irrigation contingency; advise farmers regarding delayed sowing / crop alteration decision.';
      } else if (this.lastForecastData && this.lastForecastData.heavy_rainfall_risk && this.lastForecastData.heavy_rainfall_risk.heavy_rainfall_risk.includes('HEAVY')) {
        actionDirective = 'Issue waterlogging alert; clear block drainage outlets and maintain flood watch.';
      } else {
        actionDirective = 'Facilitate certified seed supply; monitor block-level nursery emergence.';
      }
    } else {
      actionDirective = targetedCrop
        ? `${targetedCrop.priority_action} ${targetedCrop.irrigation_advice}`
        : (d.tagline || 'Follow local agricultural guidelines.');
    }

    if (statusPill) {
      statusPill.textContent = d.notify_status_transmitting || 'TRANSMITTING...';
      statusPill.style.color = '#d97706';
    }

    try {
      const res = await fetch(`${API_BASE}/api/notifications/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone,
          channel,
          recipient_type: recipientType,
          location_name: locationName,
          crop_name: cropName,
          horizon_days: horizonDays,
          risk_condition: riskCondition,
          action: actionDirective,
          language: this.currentLang
        })
      });
      if (!res.ok) {
        throw new Error(`Carrier simulator error HTTP ${res.status}`);
      }
      const data = await res.json();

      if (statusPill) {
        statusPill.textContent = d.notify_status_delivered_simulated || 'DELIVERED (SIMULATED)';
        statusPill.style.color = '#059669';
      }

      const channelLabel = d.notify_label_channel || 'Channel';
      const recipientLabel = d.notify_label_recipient || 'Recipient';
      const statusLabel = d.notify_label_status || 'Status';
      const contentLabel = d.notify_label_content || 'Message Content';

      const recipientDisplayName = recipientType === 'officer'
        ? (d.recipient_officer || 'Agricultural Extension Officer')
        : (d.recipient_farmer || 'Farmer');

      if (previewBox) {
        previewBox.innerHTML = `
          <strong>${channelLabel}:</strong> ${data.channel.toUpperCase()} | <strong>${recipientLabel}:</strong> ${recipientDisplayName} (${data.recipient_mask})<br/>
          <strong>${statusLabel}:</strong> <span style="color:#059669; font-weight:700;">DELIVERED (SIMULATED)</span> (${data.timestamp.slice(11, 19)} IST)<br/>
          <strong>${contentLabel}:</strong><br/>
          <span style="color:#111827; line-height:1.5;">${data.message}</span>
        `;
      }

      // Prepend to audit history table immediately without page refresh
      this.prependNotificationHistoryRow({
        created_at: data.timestamp,
        recipient_type: recipientType,
        recipient_mask: data.recipient_mask,
        channel: data.channel,
        status: 'DELIVERED (SIMULATED)'
      });

    } catch (err) {
      if (statusPill) {
        statusPill.textContent = d.notify_status_failed || 'FAILED';
        statusPill.style.color = '#dc2626';
      }
      if (previewBox) {
        previewBox.innerHTML = `<span style="color:#dc2626; font-weight:600;">⚠️ Simulation dispatch error: Could not connect to local transmission sandbox. Click 'Dispatch Localized Alert' to retry.</span>`;
      }
      console.error('Dispatch error:', err);
    }
  }

  prependNotificationHistoryRow(item) {
    const tbody = document.getElementById('notify-history-tbody');
    if (!tbody) return;
    const d = this.localeDictionary || {};

    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid #e2e8f0';

    const timeStr = item.created_at ? item.created_at.replace('T', ' ').slice(11, 19) : new Date().toTimeString().slice(0, 8);
    const recType = (item.recipient_type === 'officer')
      ? (d.recipient_officer || 'Extension Officer')
      : (d.recipient_farmer || 'Farmer');
    const badgeColor = (item.recipient_type === 'officer') ? '#7c3aed' : '#0284c7';

    tr.innerHTML = `
      <td style="padding:0.4rem 0.5rem; color:#64748b;">${timeStr}</td>
      <td><span style="color:${badgeColor}; font-weight:600;">${recType}</span></td>
      <td style="color:#111827; font-weight:500;">${item.recipient_mask || 'ANONYMIZED'}</td>
      <td style="text-transform:uppercase; color:#475569; font-weight:600;">${item.channel}</td>
      <td><span style="color:#059669; font-weight:700;">DELIVERED (SIMULATED)</span></td>
    `;
    tbody.insertBefore(tr, tbody.firstChild);

    while (tbody.children.length > 15) {
      tbody.removeChild(tbody.lastChild);
    }
  }

  async loadNotificationHistory() {
    const tbody = document.getElementById('notify-history-tbody');
    if (!tbody) return;
    try {
      const res = await fetch(`${API_BASE}/api/notifications/history`);
      if (!res.ok) return;
      const history = await res.json();
      tbody.innerHTML = '';
      // Reverse so newest appears on top as we prepend
      const reversed = [...history].reverse();
      reversed.forEach(item => {
        this.prependNotificationHistoryRow(item);
      });
    } catch (e) {
      console.warn('Could not load notification history:', e);
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
      const d = this.localeDictionary || {};
      const selectBtnTxt = d.table_btn_select || 'Select';

      if (tableBody) {
        tableBody.innerHTML = '';
        this.locations.forEach(loc => {
          const tr = document.createElement('tr');
          tr.style.borderBottom = '1px solid #e2e8f0';
          tr.innerHTML = `
            <td style="padding:0.6rem 0.4rem; font-weight:600; color:#111827;">${loc.name}<br/><small style="color:var(--text-dim);">${loc.block_or_mandal}</small></td>
            <td style="color:#334155;">${loc.district}</td>
            <td style="color:#334155;">${loc.state}</td>
            <td style="color:#64748b; font-family:monospace; font-size:0.75rem;">${loc.latitude.toFixed(3)}°N, ${loc.longitude.toFixed(3)}°E</td>
            <td style="color:#334155;">${loc.primary_soil}</td>
            <td style="color:#0284c7; font-weight:600;">${loc.normal_onset_date}</td>
            <td>
              <button class="voice-btn" style="padding:0.25rem 0.5rem; font-size:0.7rem;" onclick="window.app.selectLocation('${loc.id}')">${selectBtnTxt}</button>
            </td>
          `;
          tableBody.appendChild(tr);
        });
      }

      if (this.mapManager) {
        this.mapManager.renderLocations(this.locations, this.activeLocationId);
        this.mapManager.fitAllLocations(this.locations);
      }
    } catch (err) {
      console.error('Failed to load locations from API:', err);
      const locSelect = document.getElementById('location-select');
      const d = this.localeDictionary || {};
      if (locSelect) {
        locSelect.innerHTML = `<option value="">⚠️ ${d.error_locations_failed || 'Locations unavailable (Offline)'}</option>`;
      }
      const tableBody = document.getElementById('location-table-body');
      if (tableBody) {
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:1.2rem; color:#dc2626;">⚠️ ${d.error_locations_failed || 'Unable to connect to location database.'} <button class="voice-btn" style="margin-left:0.5rem;" onclick="window.app.loadLocations()">${d.btn_retry || 'Retry'}</button></td></tr>`;
      }
    }
  }

  selectLocation(locId) {
    this.activeLocationId = locId;
    const locSelect = document.getElementById('location-select');
    if (locSelect) locSelect.value = locId;
    this.refreshDashboard(false);
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

  async refreshDashboard(isInitial = false) {
    const locParam = `location_id=${this.activeLocationId}`;
    const scenParam = this.currentScenario ? `&scenario=${this.currentScenario}` : '';
    const horizonParam = `&horizon=${this.currentHorizon}`;
    const langParam = `&lang=${this.currentLang}`;

    try {
      const [forecastRes, advisoryRes] = await Promise.all([
        fetch(`${API_BASE}/api/forecast?${locParam}${horizonParam}${scenParam}`),
        fetch(`${API_BASE}/api/advisories?${locParam}${langParam}${scenParam}`)
      ]);

      if (!forecastRes.ok || !advisoryRes.ok) {
        throw new Error(`API response error: forecast ${forecastRes.status}, advisories ${advisoryRes.status}`);
      }

      const forecastData = await forecastRes.json();
      const advisoryData = await advisoryRes.json();
      this.currentAdvisoryData = advisoryData;
      this.lastForecastData = forecastData;

      this.renderAlertBanner(forecastData, advisoryData);
      this.renderOnsetCard(forecastData);
      this.renderBreakCard(forecastData);
      this.renderTelemetry(forecastData);
      this.renderClimateDrivers(forecastData);
      this.renderChartAndTimeline(forecastData);
      this.renderCrops(advisoryData);

      // Focus map to location coordinates or fit overview
      if (forecastData.location && this.mapManager) {
        this.mapManager.renderLocations(this.locations, this.activeLocationId);
        if (isInitial) {
          this.mapManager.fitAllLocations(this.locations);
        } else {
          this.mapManager.focusLocation(forecastData.location.latitude, forecastData.location.longitude);
        }
      }
    } catch (err) {
      console.error('Error refreshing dashboard:', err);
      const banner = document.getElementById('alert-banner');
      const d = this.localeDictionary || {};
      if (banner) {
        banner.className = 'alert-banner alert-amber';
        const headlineEl = document.getElementById('alert-headline');
        const descEl = document.getElementById('alert-desc');
        const iconEl = document.getElementById('alert-icon');
        if (iconEl) iconEl.textContent = '⚠️';
        if (headlineEl) headlineEl.textContent = d.error_forecast_failed || 'Unable to retrieve meteorological forecast data';
        if (descEl) {
          descEl.innerHTML = `${d.error_forecast_desc || 'Could not connect to the forecasting service. Please verify server connectivity and retry.'} <button class="voice-btn" style="margin-left:0.5rem; padding:0.25rem 0.6rem; font-size:0.75rem;" onclick="window.app.refreshDashboard()">${d.btn_retry || 'Retry Connection'}</button>`;
        }
      }
    }
  }

  renderAlertBanner(forecastData, advisoryData) {
    const banner = document.getElementById('alert-banner');
    if (!banner) return;

    banner.className = 'alert-banner';
    const breakRisk = forecastData.break_spell_outlook.risk_level;
    const isFalseAlarm = forecastData.onset_outlook.is_false_alarm;
    const d = this.localeDictionary || {};

    let alertClass = 'alert-green';
    let icon = '🌱';
    let headline = '';
    let desc = '';

    if (isFalseAlarm) {
      alertClass = 'alert-yellow';
      icon = '⚠️';
      headline = d.alert_false_alarm_headline || 'False Onset Warning: Local Thunderstorm without Synoptic Monsoon Circulation';
      desc = d.alert_false_alarm_desc || 'Surface rain observed without deep tropospheric westerly shear. Premature sowing may result in seed germination failure.';
    } else if (breakRisk === 'CRITICAL' || breakRisk === 'HIGH') {
      alertClass = 'alert-red';
      icon = '🚨';
      const dryDays = forecastData.break_spell_outlook.projected_consecutive_dry_days;
      const dryDaysSuffix = d.consecutive_dry_days_suffix || 'Consecutive Dry Days';
      headline = `${d.alert_break_headline || 'Monsoon Break Alert: Prolonged Dry Spell Projected'} (${dryDays} ${dryDaysSuffix})`;
      desc = d.alert_break_desc || 'Monsoon trough shifted toward Himalayan foothills. Suspend chemical nitrogen top-dressing; apply mulch.';
    } else {
      alertClass = 'alert-green';
      icon = '🌧️';
      headline = d.alert_active_headline || 'Active Southwest Monsoon Current Established across Catchment';
      desc = d.alert_active_desc || 'Soil moisture saturation reached optimal threshold. Favorable window open for Kharif field operations.';
    }

    banner.classList.add(alertClass);
    document.getElementById('alert-icon').textContent = icon;
    document.getElementById('alert-headline').textContent = headline;
    document.getElementById('alert-desc').textContent = desc;
  }

  renderOnsetCard(data) {
    const onset = data.onset_outlook || {};
    const d = this.localeDictionary || {};
    const thresholdBadge = document.getElementById('onset-threshold-status-badge');
    const thresholdText = document.getElementById('onset-threshold-text');

    let statusText = d.onset_threshold_not_met || 'NOT MET';
    let badgeClass = 'badge badge-critical';

    if (onset.threshold_status === 'MET') {
      statusText = d.onset_threshold_met || 'MET';
      badgeClass = 'badge badge-active';
    } else if (onset.threshold_status === 'INSUFFICIENT DATA' || onset.status === 'INSUFFICIENT_OBSERVATION_DAYS') {
      statusText = d.onset_threshold_insufficient || 'INSUFFICIENT DATA';
      badgeClass = 'badge badge-watch';
    }

    if (thresholdBadge) {
      thresholdBadge.textContent = statusText;
      thresholdBadge.className = badgeClass;
    }
    if (thresholdText) {
      thresholdText.textContent = statusText;
      thresholdText.style.color = (onset.threshold_status === 'MET') ? '#059669' : ((onset.threshold_status === 'INSUFFICIENT DATA') ? '#d97706' : '#dc2626');
    }

    const predictedEl = document.getElementById('predicted-onset-date');
    if (predictedEl) {
      let badgeText = d.status_imminent || 'Pending / Pre-Monsoon';
      if (onset.status === 'ONSET_DECLARED') {
        badgeText = d.status_onset_declared || 'Onset Declared';
      } else if (onset.is_false_alarm) {
        badgeText = d.status_false_alarm || 'False Alarm';
      }
      predictedEl.textContent = badgeText;
    }

    const normalOnsetEl = document.getElementById('normal-onset-date');
    if (normalOnsetEl) normalOnsetEl.textContent = onset.normal_onset_date || 'June 08';

    const probVal = onset.onset_probability_pct != null ? onset.onset_probability_pct : Math.round((onset.confidence_score || 0) * 100);
    const onsetConfEl = document.getElementById('onset-confidence');
    if (onsetConfEl) onsetConfEl.textContent = `${probVal}%`;

    const expectedWindowEl = document.getElementById('onset-expected-window-val');
    if (expectedWindowEl) {
      if (onset.threshold_status === 'INSUFFICIENT DATA') {
        expectedWindowEl.textContent = d.onset_insufficient_data_note || 'Insufficient data for threshold assessment';
      } else {
        expectedWindowEl.textContent = onset.expected_onset_window || '7–14 days';
      }
    }

    const ruleUsedEl = document.getElementById('onset-rule-used');
    if (ruleUsedEl) {
      ruleUsedEl.textContent = onset.threshold_rule || 'IMD-referenced monsoon onset criteria adapted within the VarshaSetu hyperlocal forecasting framework: 2 days rain ≥2.5mm + 850hPa wind ≥7.7m/s + OLR ≤200W/m²';
    }

    const tagRain = document.getElementById('tag-rain');
    const tagWind = document.getElementById('tag-wind');
    const tagOlr = document.getElementById('tag-olr');
    const tagDir = document.getElementById('tag-dir');

    const isSatisfied = (onset.status === 'ONSET_DECLARED');
    const passText = `✓ ${d.status_satisfied || 'SATISFIED'}`;
    const failText = `✗ ${d.status_pending || 'PENDING'}`;

    if (tagRain) tagRain.textContent = isSatisfied || onset.is_false_alarm ? passText : failText;
    if (tagWind) tagWind.textContent = isSatisfied ? passText : failText;
    if (tagOlr) tagOlr.textContent = isSatisfied ? passText : failText;
    if (tagDir) tagDir.textContent = isSatisfied ? passText : failText;
  }

  renderBreakCard(data) {
    const brk = data.break_spell_outlook || {};
    const active = data.active_monsoon_outlook || {};
    const d = this.localeDictionary || {};
    const riskBadge = document.getElementById('break-risk-badge');

    if (riskBadge) {
      let riskText = d.risk_low || 'LOW RISK';
      if (brk.risk_level === 'CRITICAL') {
        riskText = d.risk_critical || 'CRITICAL RISK';
        riskBadge.className = 'badge badge-critical';
      } else if (brk.risk_level === 'HIGH') {
        riskText = d.risk_high || 'HIGH RISK';
        riskBadge.className = 'badge badge-critical';
      } else if (brk.risk_level === 'MODERATE') {
        riskText = d.risk_moderate || 'MODERATE RISK';
        riskBadge.className = 'badge badge-watch';
      } else {
        riskBadge.className = 'badge badge-active';
      }
      riskBadge.textContent = riskText;
    }

    // Active Monsoon Period Duration & Probability
    const activeProbEl = document.getElementById('active-prob-val');
    if (activeProbEl) {
      const aProb = active.probability != null ? (active.probability * 100).toFixed(1) : '85.0';
      activeProbEl.textContent = `${aProb}%`;
    }
    const activeDurEl = document.getElementById('active-duration-val');
    if (activeDurEl) {
      if (active.has_duration_estimate === false || active.expected_active_duration_days == null) {
        activeDurEl.textContent = d.duration_unavailable || 'Duration estimate unavailable';
      } else {
        activeDurEl.textContent = `${active.expected_active_duration_days} ${d.timeline_day_prefix || 'Days'}`;
      }
    }
    const activeWinEl = document.getElementById('active-window-val');
    if (activeWinEl) {
      activeWinEl.textContent = active.expected_window || (d.duration_unavailable || 'Duration estimate unavailable');
    }

    // Monsoon Break / Dry Spell Duration & Probability
    const breakProbEl = document.getElementById('break-probability-val');
    if (breakProbEl) {
      breakProbEl.textContent = `${((brk.probability || 0) * 100).toFixed(1)}%`;
    }
    const dryDaysEl = document.getElementById('dry-days-val');
    if (dryDaysEl) {
      if (brk.has_duration_estimate === false || (brk.expected_break_duration_days == null && brk.projected_consecutive_dry_days == null)) {
        dryDaysEl.textContent = d.duration_unavailable || 'Duration estimate unavailable';
      } else {
        const dCount = brk.expected_break_duration_days != null ? brk.expected_break_duration_days : brk.projected_consecutive_dry_days;
        dryDaysEl.textContent = `${dCount} ${d.timeline_day_prefix || 'Days'}`;
      }
    }
    const breakWinEl = document.getElementById('break-window-val');
    if (breakWinEl) {
      breakWinEl.textContent = brk.expected_window || (d.duration_unavailable || 'Duration estimate unavailable');
    }

    const anomaly = data.rainfall_anomaly_outlook;
    const anomalyEl = document.getElementById('anomaly-val');
    if (anomalyEl && anomaly) {
      let catName = anomaly.category;
      if (anomaly.category === 'Normal') catName = d.anomaly_normal || 'Normal';
      else if (anomaly.category === 'Excess') catName = d.anomaly_excess || 'Excess';
      else if (anomaly.category === 'Deficient') catName = d.anomaly_deficit || 'Deficient';
      anomalyEl.textContent = `${anomaly.departure_percentage > 0 ? '+' : ''}${anomaly.departure_percentage}% (${catName})`;
      anomalyEl.style.color = (anomaly.departure_percentage < -20) ? '#dc2626' : '#0284c7';
    }

    const heavyEl = document.getElementById('heavy-rain-val');
    if (heavyEl && data.heavy_rainfall_risk) {
      const hRisk = data.heavy_rainfall_risk.heavy_rainfall_risk;
      let hText = hRisk;
      if (hRisk.includes('GREEN')) {
        hText = d.heavy_rain_green || 'GREEN (No Heavy Rain)';
        heavyEl.style.color = '#059669';
      } else if (hRisk.includes('YELLOW')) {
        hText = d.heavy_rain_yellow || 'YELLOW (Moderate Showers)';
        heavyEl.style.color = '#d97706';
      } else if (hRisk.includes('ORANGE')) {
        hText = d.heavy_rain_orange || 'ORANGE (Heavy Rainfall Alert)';
        heavyEl.style.color = '#ea580c';
      } else if (hRisk.includes('RED')) {
        hText = d.heavy_rain_red || 'RED (Extremely Heavy Rains)';
        heavyEl.style.color = '#dc2626';
      }
      heavyEl.textContent = hText;
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
    const d = this.localeDictionary || {};

    const ensoVal = document.getElementById('tele-enso-val');
    const ensoDesc = document.getElementById('tele-enso-desc');
    const ensoStatus = document.getElementById('tele-enso-status');
    if (ensoVal && cd.enso) {
      const sign = cd.enso.nino34_anomaly_c >= 0 ? '+' : '';
      ensoVal.textContent = `${sign}${cd.enso.nino34_anomaly_c.toFixed(2)} °C (${cd.enso.phase})`;
      if (ensoDesc) ensoDesc.textContent = cd.enso.effect_on_monsoon || 'SST telemetry';
      if (ensoStatus) {
        if (cd.enso.source_status === 'LIVE_VERIFIED_NOAA_CPC') {
          ensoStatus.textContent = d.badge_live_noaa || 'LIVE NOAA CPC';
          ensoStatus.style.background = '#ecfdf5';
          ensoStatus.style.color = '#065f46';
          ensoStatus.style.border = '1px solid #a7f3d0';
        } else {
          ensoStatus.textContent = d.badge_benchmark || 'CONFIGURED BENCHMARK';
          ensoStatus.style.background = '#f1f5f9';
          ensoStatus.style.color = '#64748b';
          ensoStatus.style.border = '1px solid #e2e8f0';
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
        iodStatus.textContent = d.badge_benchmark || 'CONFIGURED BENCHMARK';
        iodStatus.style.background = '#f1f5f9';
        iodStatus.style.color = '#64748b';
        iodStatus.style.border = '1px solid #e2e8f0';
      }
    }

    const mjoVal = document.getElementById('tele-mjo-val');
    const mjoDesc = document.getElementById('tele-mjo-desc');
    const mjoStatus = document.getElementById('tele-mjo-status');
    if (mjoVal && cd.mjo) {
      mjoVal.textContent = `Phase ${cd.mjo.phase} (Amp: ${cd.mjo.amplitude.toFixed(1)})`;
      if (mjoDesc) mjoDesc.textContent = cd.mjo.status || 'MJO Wave State';
      if (mjoStatus) {
        mjoStatus.textContent = d.badge_benchmark || 'CONFIGURED BENCHMARK';
        mjoStatus.style.background = '#f1f5f9';
        mjoStatus.style.color = '#64748b';
        mjoStatus.style.border = '1px solid #e2e8f0';
      }
    }
  }

  renderChartAndTimeline(data) {
    const timeline = data.timeline;
    if (!timeline || timeline.length === 0) return;
    const d = this.localeDictionary || {};

    // Render Timeline List
    const list = document.getElementById('timeline-list');
    if (list) {
      list.innerHTML = '';
      const dayPrefix = d.timeline_day_prefix || 'Day';
      const soilLabel = d.timeline_soil_label || 'Soil Moisture';
      const tempLabel = d.timeline_temp_label || 'Temp';
      const dryDayTxt = d.timeline_dry_day || 'Dry Day';
      const rainDayTxt = d.timeline_rain_day || 'Rain Day';

      timeline.forEach((pt, idx) => {
        const item = document.createElement('div');
        item.className = 'timeline-item';
        item.innerHTML = `
          <div>
            <div class="timeline-date">${dayPrefix} ${pt.day_offset} (${pt.date.slice(5)})</div>
            <div class="timeline-moist">${soilLabel}: ${pt.soil_moisture_pct}% | ${tempLabel}: ${pt.temp_max_c}°C</div>
          </div>
          <div style="text-align: right;">
            <div class="timeline-rain">${pt.rainfall_mm} mm</div>
            <small style="color:${pt.is_dry_day ? '#f43f5e' : '#10b981'}; font-weight:700;">
              ${pt.is_dry_day ? dryDayTxt : rainDayTxt}
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

    const rainLegend = d.chart_legend_rain || 'Daily Rainfall (mm)';
    const moistLegend = d.chart_legend_moist || 'Root-Zone Soil Moisture (%)';
    const rainAxis = d.chart_axis_rain || 'Rain (mm)';
    const moistAxis = d.chart_axis_moist || 'Soil Moisture %';

    if (this.rainfallChart) {
      this.rainfallChart.destroy();
    }

    this.rainfallChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: rainLegend,
            data: rainData,
            backgroundColor: 'rgba(56, 189, 248, 0.65)',
            borderColor: '#0284c7',
            borderWidth: 1,
            yAxisID: 'y'
          },
          {
            label: moistLegend,
            data: soilData,
            type: 'line',
            borderColor: '#059669',
            backgroundColor: 'rgba(5, 150, 105, 0.08)',
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
            grid: { color: 'rgba(226, 232, 240, 0.8)' },
            ticks: { color: '#64748b', font: { size: 10 } }
          },
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: { display: true, text: rainAxis, color: '#0284c7', font: { size: 10, weight: 600 } },
            ticks: { color: '#64748b' },
            grid: { color: 'rgba(226, 232, 240, 0.8)' }
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            title: { display: true, text: moistAxis, color: '#059669', font: { size: 10, weight: 600 } },
            min: 0,
            max: 100,
            ticks: { color: '#64748b' },
            grid: { drawOnChartArea: false }
          }
        },
        plugins: {
          legend: {
            labels: { color: '#111827', font: { size: 11, weight: 500 } }
          }
        }
      }
    });
  }

  renderCrops(advisoryData) {
    const grid = document.getElementById('crops-grid');
    if (!grid) return;
    grid.innerHTML = '';
    const d = this.localeDictionary || {};

    const advisories = advisoryData.advisories || [];
    advisories.forEach(crop => {
      const card = document.createElement('div');
      card.className = 'crop-card';

      let sowClass = 'sow-optimal';
      let statusText = d.crop_status_optimal || 'Optimal Sowing Window';

      if (crop.sowing_status.includes('POSTPONE') || crop.sowing_status.includes('BREAK')) {
        sowClass = 'sow-risk';
        statusText = d.crop_status_postpone || 'Postpone Sowing / High Break Risk';
      } else if (crop.sowing_status.includes('FALSE')) {
        sowClass = 'sow-risk';
        statusText = d.crop_status_false || 'False Onset Detected';
      } else if (crop.sowing_status.includes('AWAIT')) {
        sowClass = 'sow-wait';
        statusText = d.crop_status_await || 'Await Sustained Rains';
      }

      const choice = crop.crop_choice_alteration || {};
      const isAlt = Boolean(choice.is_alteration_recommended);
      const choiceBadgeClass = isAlt ? 'badge-critical' : 'badge-active';
      const choiceBadgeText = isAlt
        ? (d.crop_choice_badge_recommended || 'Alternative Crop Advised')
        : (d.crop_choice_badge_suitable || 'Planned Crop Suitable');
      const varsList = (choice.recommended_short_duration_varieties && choice.recommended_short_duration_varieties.length > 0)
        ? choice.recommended_short_duration_varieties.join(', ')
        : (crop.recommended_varieties_short_duration ? crop.recommended_varieties_short_duration.join(', ') : 'Standard cultivars');

      card.innerHTML = `
        <div>
          <div class="crop-card-top">
            <h3 class="crop-name">${crop.crop_name}</h3>
            <span class="sowing-badge ${sowClass}">${statusText}</span>
          </div>

          <!-- 5 Explicit Advisory Category Badges -->
          <div style="display:flex; gap:0.35rem; flex-wrap:wrap; margin:0.4rem 0;">
            <span class="badge" style="font-size:0.62rem; background:#f0f9ff; color:#0369a1; border:1px solid #bae6fd;">${d.crop_type_sowing || 'SOWING'}</span>
            <span class="badge" style="font-size:0.62rem; background:#f0fdf4; color:#065f46; border:1px solid #bbf7d0;">${d.crop_type_irrigation || 'IRRIGATION'}</span>
            <span class="badge" style="font-size:0.62rem; background:#f8fafc; color:#475569; border:1px solid #e2e8f0;">${d.crop_type_fertilizer || 'FERTILIZER'}</span>
            <span class="badge" style="font-size:0.62rem; background:#fffbeb; color:#92400e; border:1px solid #fde68a;">${d.crop_type_pest || 'PEST/WEATHER RISK'}</span>
            <span class="badge ${choiceBadgeClass}" style="font-size:0.62rem;">${d.crop_type_choice || 'CROP CHOICE'}</span>
          </div>

          <div class="crop-details">
            <div class="detail-row">
              <strong>📅 ${d.crop_sowing_window || 'Sowing Window'}</strong>
              <span style="color:#111827; font-weight:500;">${crop.sowing_window}</span>
            </div>
            <div class="detail-row">
              <strong>💧 ${d.crop_irrigation || 'Irrigation Guidance'}</strong>
              <span>${crop.irrigation_advice}</span>
            </div>
            <div class="detail-row">
              <strong>🧪 ${d.crop_fertilizer || 'Fertilizer Schedule'}</strong>
              <span>${crop.fertilizer_advice}</span>
            </div>
            <div class="detail-row">
              <strong>🐛 ${d.crop_pest || 'Pest & Disease Watch'}</strong>
              <span>${crop.pest_disease_advice}</span>
            </div>

            <!-- Fix 3: CROP CHOICE / VARIETY ALTERNATIVE Section -->
            <div style="background:${isAlt ? '#fff1f2' : '#f8fafc'}; border:1px solid ${isAlt ? '#fecdd3' : '#e2e8f0'}; border-radius:8px; padding:0.65rem; margin-top:0.6rem;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem;">
                <strong style="font-size:0.75rem; color:${isAlt ? '#9f1239' : '#0f766e'};">🌾 ${d.crop_choice_title || 'CROP CHOICE / VARIETY ALTERNATIVE'}</strong>
                <span class="badge ${choiceBadgeClass}" style="font-size:0.63rem;">${choiceBadgeText}</span>
              </div>
              <div style="font-size:0.75rem; color:#475569; line-height:1.45;">
                <div style="margin-bottom:0.2rem;">
                  <span style="color:var(--text-dim);">${d.crop_choice_forecast_condition || 'Forecast Condition'}:</span> <b style="color:#111827;">${choice.forecast_condition || 'Evaluating'}</b>
                </div>
                <div style="margin-bottom:0.2rem;">
                  <span style="color:var(--text-dim);">${d.crop_choice_advisory_label || 'Advisory'}:</span> <span style="color:${isAlt ? '#991b1b' : '#111827'}; font-weight:600;">${choice.crop_choice_advisory || crop.contingency_alternative}</span>
                </div>
                <div style="margin-bottom:0.2rem;">
                  <span style="color:var(--text-dim);">${d.crop_choice_reason_label || 'Reason'}:</span> <span style="color:#64748b;">${choice.reason || 'Agronomic moisture threshold'}</span>
                </div>
                <div>
                  <span style="color:var(--text-dim);">${d.crop_choice_varieties_label || 'Short-Duration Varieties'}:</span> <b style="color:#0284c7;">${varsList}</b>
                </div>
              </div>
            </div>

            <div class="detail-row" style="margin-top:0.45rem; padding-top:0.45rem; border-top:1px dashed #e2e8f0;">
              <small style="color:var(--text-dim);">🔬 <b>${d.crop_reasoning || 'Scientific Reasoning & Rule'}:</b> ${crop.reasoning}</small>
            </div>
          </div>
        </div>

        <div class="action-box">
          <b>⚡ ${d.crop_action || 'Priority Action'}:</b> ${crop.priority_action}
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
      const d = this.localeDictionary || {};

      if (container && data.metrics) {
          container.innerHTML = `
            <div style="background:var(--color-surface); border:1px solid var(--color-border); padding:0.45rem 0.85rem; border-radius:6px;">
              <small style="color:var(--text-dim);">${d.metric_brier_skill || 'Brier Skill Score:'}</small> <b style="color:var(--color-success);">+${data.metrics.brier_skill_score}</b>
            </div>
            <div style="background:var(--color-surface); border:1px solid var(--color-border); padding:0.45rem 0.85rem; border-radius:6px;">
              <small style="color:var(--text-dim);">${d.metric_brier_loss || 'Model Brier Loss:'}</small> <b style="color:var(--color-text);">${data.metrics.brier_score}</b> (${d.metric_climatology || 'Clim'}: ${data.metrics.brier_climatology_baseline})
            </div>
            <div style="background:var(--color-surface); border:1px solid var(--color-border); padding:0.45rem 0.85rem; border-radius:6px;">
              <small style="color:var(--text-dim);">${d.metric_roc_auc || 'ROC-AUC:'}</small> <b style="color:var(--color-primary-dark);">${data.metrics.roc_auc}</b>
            </div>
            <div style="background:var(--color-surface); border:1px solid var(--color-border); padding:0.45rem 0.85rem; border-radius:6px;">
              <small style="color:var(--text-dim);">${d.metric_precision_recall || 'Precision / Recall:'}</small> <b style="color:var(--color-text);">${data.metrics.precision} / ${data.metrics.recall}</b>
            </div>
          `;
      }
    } catch (err) {
      console.error('Error fetching model info:', err);
    }
  }

  getBestSpeechVoice(languageCode) {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return null;

    let voices = window.speechSynthesis.getVoices() || [];
    if (voices.length === 0 && this.cachedVoices && this.cachedVoices.length > 0) {
      voices = this.cachedVoices;
    }
    if (!voices || voices.length === 0) return null;

    const config = TTS_LANGUAGE_CONFIG[languageCode];
    if (!config) return null;

    const primaryCode = config.bcp47.toLowerCase();
    const baseLang = languageCode.toLowerCase();
    const fallbacks = (config.fallbacks || []).map(f => f.toLowerCase());
    const cleanLang = (l) => (l || '').toLowerCase().replace(/_/g, '-');

    // Priority 1: Exact match with primary BCP-47 tag (e.g., 'ml-in', 'ur-in')
    let match = voices.find(v => cleanLang(v.lang) === primaryCode);
    if (match) return match;

    // Priority 2: Configured regional fallbacks in order (e.g., 'ur-pk', 'ml')
    for (const fb of fallbacks) {
      match = voices.find(v => cleanLang(v.lang) === fb);
      if (match) return match;
    }

    // Priority 3: Matches base language prefix (e.g., 'ml-' or 'ur-')
    match = voices.find(v => {
      const vLang = cleanLang(v.lang);
      // Safety: Never match English voices if requested language is not English
      if (baseLang !== 'en' && (vLang.startsWith('en') || vLang === 'en')) return false;
      return vLang.startsWith(`${baseLang}-`) || vLang === baseLang;
    });
    if (match) return match;

    // Priority 4: Check if voice.name explicitly contains the language name
    const langNameLower = config.name.toLowerCase();
    match = voices.find(v => {
      const vName = (v.name || '').toLowerCase();
      const vLang = cleanLang(v.lang);
      if (baseLang !== 'en' && (vLang.startsWith('en') || vName.includes('english'))) {
        return false;
      }
      return vName.includes(langNameLower);
    });
    if (match) return match;

    // CRITICAL: Return null if no voice exists. Never silently fallback to English.
    return null;
  }

  speakAdvisory() {
    const d = this.localeDictionary || {};
    if (!('speechSynthesis' in window)) {
      alert(d.speech_not_supported || 'Speech synthesis is not supported on this device.');
      return;
    }

    // Safety against stale speech
    window.speechSynthesis.cancel();
    if (!this.currentAdvisoryData || !this.currentAdvisoryData.advisories) return;

    const voiceBtn = document.getElementById('voice-advisory-btn');
    const listenTxt = d.btn_listen_audio || 'Listen Audio Advisory';
    const config = TTS_LANGUAGE_CONFIG[this.currentLang] || { bcp47: 'en-IN', name: 'English' };

    // Select suitable voice for active language
    const voice = this.getBestSpeechVoice(this.currentLang);

    if (!voice) {
      console.warn(`[VarshaSetu TTS] ${config.name} voice (${config.bcp47}) is not available on this device/browser. Refusing silent fallback to English.`);
      if (voiceBtn) {
        voiceBtn.innerHTML = `<span>⚠️</span> <span>${d.speech_not_supported || 'Voice Unavailable'}</span>`;
        setTimeout(() => {
          if (voiceBtn) voiceBtn.innerHTML = `<span>🔊</span> <span>${listenTxt}</span>`;
        }, 3500);
      }
      if (typeof window !== 'undefined' && typeof window.alert === 'function') {
        window.alert(d.speech_not_supported || `${config.name} voice is not available on this device/browser.`);
      }
      return;
    }

    const playingTxt = d.btn_playing_audio || 'Playing Audio...';
    if (voiceBtn) voiceBtn.innerHTML = `<span>🔊</span> <span>${playingTxt}</span>`;

    const advisories = this.currentAdvisoryData.advisories;
    let spokenText = d.speech_prefix || 'Ministry of Earth Sciences, VarshaSetu Hyperlocal Monsoon Advisory. ';

    if (advisories.length > 0) {
      const top = advisories[0];
      spokenText += `${top.crop_name}: ${top.priority_action}. ${top.irrigation_advice}`;
    }

    const UtteranceClass = (typeof window !== 'undefined' && window.SpeechSynthesisUtterance) ? window.SpeechSynthesisUtterance : SpeechSynthesisUtterance;
    const utterance = new UtteranceClass(spokenText);
    utterance.lang = config.bcp47;
    utterance.voice = voice;
    utterance.rate = 0.95;

    utterance.onend = () => {
      if (voiceBtn) voiceBtn.innerHTML = `<span>🔊</span> <span>${listenTxt}</span>`;
    };
    utterance.onerror = (e) => {
      console.error('[VarshaSetu TTS] Utterance error:', e);
      if (voiceBtn) voiceBtn.innerHTML = `<span>🔊</span> <span>${listenTxt}</span>`;
    };

    window.speechSynthesis.speak(utterance);
  }

  debugSpeechVoices() {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      console.warn('[VarshaSetu TTS Debug] Web Speech API is not supported on this device.');
      return { supported: false, voices: [] };
    }

    let voices = window.speechSynthesis.getVoices() || [];
    if (voices.length === 0 && this.cachedVoices && this.cachedVoices.length > 0) {
      voices = this.cachedVoices;
    }

    const summary = voices.map(v => ({
      name: v.name,
      lang: v.lang,
      default: v.default,
      localService: v.localService
    }));

    console.log(`[VarshaSetu TTS Debug] Total speech voices detected: ${voices.length}`);
    if (console.table) {
      console.table(summary);
    } else {
      console.log(summary);
    }

    const coverage = {};
    ['en', 'te', 'hi', 'ta', 'kn', 'ur', 'ml'].forEach(code => {
      const v = this.getBestSpeechVoice(code);
      coverage[code] = v ? `${v.name} (${v.lang})` : 'NOT AVAILABLE';
    });

    console.log('[VarshaSetu TTS Debug] Voice availability coverage by language:', coverage);
    console.log(`[VarshaSetu TTS Debug] Malayalam (ml-IN / ml) available: ${Boolean(this.getBestSpeechVoice('ml'))}`);
    console.log(`[VarshaSetu TTS Debug] Urdu (ur-IN / ur) available: ${Boolean(this.getBestSpeechVoice('ur'))}`);

    return {
      supported: true,
      totalVoices: voices.length,
      coverage,
      mlAvailable: Boolean(this.getBestSpeechVoice('ml')),
      urAvailable: Boolean(this.getBestSpeechVoice('ur')),
      voices: summary
    };
  }

  async testSpeechLanguage(langCode) {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      console.warn('[VarshaSetu TTS Test] Speech synthesis not supported on this platform.');
      return { success: false, reason: 'speech_synthesis_unsupported' };
    }

    window.speechSynthesis.cancel();

    let dict = this.localeDictionary;
    if (this.currentLang !== langCode) {
      try {
        const res = await fetch(`${API_BASE}/locales/${langCode}.json`);
        if (res.ok) dict = await res.json();
      } catch (e) {
        console.warn(`[VarshaSetu TTS Test] Could not load ${langCode}.json:`, e);
      }
    }

    const config = TTS_LANGUAGE_CONFIG[langCode] || { bcp47: 'en-IN', name: langCode };
    const voice = this.getBestSpeechVoice(langCode);
    const testText = `${dict.speech_prefix || dict.app_name || 'VarshaSetu'}. ${dict.tagline || ''}`;

    console.log(`[VarshaSetu TTS Test] Language: ${langCode} (${config.bcp47})`);
    console.log(`[VarshaSetu TTS Test] Test sentence: "${testText}"`);

    if (!voice) {
      console.warn(`[VarshaSetu TTS Test] Voice NOT available on this device/browser for ${langCode} (${config.bcp47}). Silent fallback prevented.`);
      return {
        success: false,
        lang: langCode,
        bcp47: config.bcp47,
        voiceAvailable: false,
        reason: 'voice_unavailable_on_device',
        text: testText
      };
    }

    console.log(`[VarshaSetu TTS Test] Selected voice: ${voice.name} (${voice.lang})`);
    const UtteranceClass = (typeof window !== 'undefined' && window.SpeechSynthesisUtterance) ? window.SpeechSynthesisUtterance : SpeechSynthesisUtterance;
    const utterance = new UtteranceClass(testText);
    utterance.lang = config.bcp47;
    utterance.voice = voice;
    utterance.rate = 0.95;

    return new Promise((resolve) => {
      utterance.onstart = () => {
        console.log(`[VarshaSetu TTS Test] Audio started for ${langCode}`);
      };
      utterance.onend = () => {
        console.log(`[VarshaSetu TTS Test] Audio ended for ${langCode}`);
        resolve({ success: true, lang: langCode, bcp47: config.bcp47, voice: voice.name });
      };
      utterance.onerror = (e) => {
        console.error(`[VarshaSetu TTS Test] Audio error for ${langCode}:`, e);
        resolve({ success: false, lang: langCode, bcp47: config.bcp47, error: e.error || 'speech_error' });
      };
      window.speechSynthesis.speak(utterance);
    });
  }
}

if (typeof window !== 'undefined') {
  window.SIHMonsoonApp = SIHMonsoonApp;
  window.TTS_LANGUAGE_CONFIG = TTS_LANGUAGE_CONFIG;
  window.getBestSpeechVoice = (lang) => window.app?.getBestSpeechVoice(lang);
  window.debugSpeechVoices = () => window.app?.debugSpeechVoices();
  window.testSpeechLanguage = (lang) => window.app?.testSpeechLanguage(lang);
}

// Global initialization
window.addEventListener('DOMContentLoaded', () => {
  window.app = new SIHMonsoonApp();
  window.app.init();
});
