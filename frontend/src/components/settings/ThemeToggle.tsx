import { useState, useEffect } from 'react';
import '../../../styles/components/themeToggle.css';

type Theme = 'light' | 'dark';

interface ThemeToogleProps {
    onThemeChange?: (theme: Theme) => void;
}

function ThemeToogle({ onThemeChange }: ThemeToogleProps){
    const [theme, setTheme] = useState<Theme>(() => {
        const savedTheme = localStorage.getItem('theme');
        return (savedTheme === 'light' || savedTheme === 'dark') ? savedTheme as Theme: 'light';
    });

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);

        if(onThemeChange) {
            onThemeChange(theme);
        }
    }, [theme, onThemeChange]);

    const handleThemeChange = (newTheme: Theme) => {
        setTheme(newTheme);
    };

    return (
        <div className="theme-toggle">
            <h4>Appearance</h4>
            <div className="theme-options">
                <div 
                    className={`theme-option ${theme ==='light' ? 'selected' : ''}`}
                    onClick={() => handleThemeChange('light')}
                >
                    <span className="material-icon">light_mode</span>
                    <span className="theme-label">Light</span>
                    {theme === 'light' && <span className="material-icon">check</span>}
                </div>
                <div 
                    className={`theme-option ${theme ==='dark' ? 'selected' : ''}`}
                    onClick={() => handleThemeChange('dark')}
                >
                    <span className="material-icon">dark_mode</span>
                    <span className="theme-label">dark</span>
                    {theme === 'dark' && <span className="material-icon">check</span>}
                </div>
            </div>
        </div>
    );
}

export default ThemeToogle;