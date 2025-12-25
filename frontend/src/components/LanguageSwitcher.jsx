import React, { useState } from 'react';
import { Globe } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

const LanguageSwitcher = () => {
  const { language, changeLanguage, isRTL } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);

  const languages = [
    { code: 'en', name: 'English', nativeName: 'English', flag: '🇬🇧' },
    { code: 'ar', name: 'Arabic', nativeName: 'العربية', flag: '🇦🇪' }
  ];

  const currentLang = languages.find(lang => lang.code === language);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg border border-green-500/30 
                   bg-black/40 hover:bg-green-500/10 transition-all duration-300
                   text-green-400 hover:text-green-300"
      >
        <Globe className="w-4 h-4" />
        <span className="hidden sm:inline text-sm font-mono">
          {currentLang?.flag} {currentLang?.nativeName}
        </span>
        <span className="sm:hidden text-sm font-mono">
          {currentLang?.flag}
        </span>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div 
            className={`absolute ${isRTL ? 'left-0' : 'right-0'} mt-2 w-48 z-50
                       bg-black/95 backdrop-blur-xl border border-green-500/30 
                       rounded-lg shadow-lg shadow-green-500/20 overflow-hidden`}
          >
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => {
                  changeLanguage(lang.code);
                  setIsOpen(false);
                }}
                className={`w-full px-4 py-3 text-left flex items-center gap-3
                           transition-all duration-200 font-mono text-sm
                           ${language === lang.code 
                             ? 'bg-green-500/20 text-green-400 border-l-2 border-green-500' 
                             : 'text-green-300/70 hover:bg-green-500/10 hover:text-green-300'
                           }`}
              >
                <span className="text-xl">{lang.flag}</span>
                <div className="flex-1">
                  <div className="font-semibold">{lang.nativeName}</div>
                  <div className="text-xs opacity-60">{lang.name}</div>
                </div>
                {language === lang.code && (
                  <span className="text-green-400">✓</span>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default LanguageSwitcher;
