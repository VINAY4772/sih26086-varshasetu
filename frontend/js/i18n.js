// VarshaSetu Multilingual Internationalization (i18n) Engine
// Supports 7 Scheduled Languages: English (en), Telugu (te), Hindi (hi), Tamil (ta), Kannada (kn), Urdu (ur), Malayalam (ml)

const VARSHASETU_LANGUAGES = [
  { code: 'en', label: 'English', native: 'English', dir: 'ltr' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు', dir: 'ltr' },
  { code: 'hi', label: 'Hindi', native: 'हिन्दी', dir: 'ltr' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்', dir: 'ltr' },
  { code: 'kn', label: 'Kannada', native: 'ಕನ್ನಡ', dir: 'ltr' },
  { code: 'ur', label: 'Urdu', native: 'اردو', dir: 'rtl' },
  { code: 'ml', label: 'Malayalam', native: 'മലയാളം', dir: 'ltr' }
];

class VarshaSetuI18n {
  constructor() {
    this.currentLang = 'en';
    this.dictionary = {};
    this.listeners = [];
  }

  getAvailableLanguages() {
    return VARSHASETU_LANGUAGES;
  }

  isRTL(lang = this.currentLang) {
    const meta = VARSHASETU_LANGUAGES.find(l => l.code === lang);
    return meta ? meta.dir === 'rtl' : false;
  }

  async loadLanguage(lang) {
    const validLang = VARSHASETU_LANGUAGES.some(l => l.code === lang) ? lang : 'en';
    this.currentLang = validLang;

    try {
      const res = await fetch(`/locales/${validLang}.json`);
      if (res.ok) {
        this.dictionary = await res.json();
      } else {
        console.warn(`Could not load /locales/${validLang}.json, status: ${res.status}`);
      }
    } catch (err) {
      console.warn(`Failed to fetch /locales/${validLang}.json:`, err);
    }

    this.applyDOMTranslations();
    this.notifyListeners(this.currentLang, this.dictionary);
    return this.dictionary;
  }

  t(key, fallback = '') {
    return this.dictionary[key] || fallback || key;
  }

  applyDOMTranslations() {
    const isRtl = this.isRTL(this.currentLang);
    document.documentElement.setAttribute('dir', isRtl ? 'rtl' : 'ltr');
    document.documentElement.setAttribute('lang', this.currentLang);

    if (document.body) {
      if (isRtl) {
        document.body.classList.add('rtl-layout');
      } else {
        document.body.classList.remove('rtl-layout');
      }
    }

    // 1. Text Content replacements
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (this.dictionary[key]) {
        el.textContent = this.dictionary[key];
      }
    });

    // 2. Attribute replacements (title, placeholder, aria-label)
    const attrElements = document.querySelectorAll('[data-i18n-attr]');
    attrElements.forEach(el => {
      const mapping = el.getAttribute('data-i18n-attr').split(';');
      mapping.forEach(pair => {
        const [attr, key] = pair.split(':').map(s => s.trim());
        if (attr && key && this.dictionary[key]) {
          el.setAttribute(attr, this.dictionary[key]);
        }
      });
    });

    // 3. Document Title
    if (this.dictionary['app_title']) {
      document.title = this.dictionary['app_title'];
    }
  }

  onLanguageChange(callback) {
    this.listeners.push(callback);
  }

  notifyListeners(lang, dict) {
    this.listeners.forEach(cb => {
      try { cb(lang, dict); } catch (e) { console.error('i18n listener error:', e); }
    });
  }
}

if (typeof window !== 'undefined') {
  window.VARSHASETU_LANGUAGES = VARSHASETU_LANGUAGES;
  window.VarshaSetuI18n = VarshaSetuI18n;
  window.i18n = new VarshaSetuI18n();
}
