import React, { createContext, useState, useContext, useEffect } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en');
  const [translations, setTranslations] = useState({});
  const [isRTL, setIsRTL] = useState(false);
  const [loading, setLoading] = useState(true);

  // Load translations when language changes
  useEffect(() => {
    const loadTranslations = async () => {
      try {
        setLoading(true);
        const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
        const response = await fetch(`${backendUrl}/api/i18n/translations/${language}`);
        const data = await response.json();
        
        if (data.success) {
          setTranslations(data.data.translations);
          setIsRTL(data.data.rtl);
          
          // Update document direction
          document.documentElement.dir = data.data.rtl ? 'rtl' : 'ltr';
          document.documentElement.lang = language;
        }
      } catch (error) {
        console.error('Failed to load translations:', error);
      } finally {
        setLoading(false);
      }
    };

    loadTranslations();
  }, [language]);

  // Load saved language preference on mount
  useEffect(() => {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage && ['en', 'ar'].includes(savedLanguage)) {
      setLanguage(savedLanguage);
    }
  }, []);

  const changeLanguage = (newLanguage) => {
    if (['en', 'ar'].includes(newLanguage)) {
      setLanguage(newLanguage);
      localStorage.setItem('language', newLanguage);
    }
  };

  const t = (key, defaultValue = key) => {
    return translations[key] || defaultValue;
  };

  const value = {
    language,
    changeLanguage,
    t,
    isRTL,
    loading,
    translations
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};
