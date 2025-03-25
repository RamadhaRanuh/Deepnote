import { useNavigate } from 'react-router-dom';
import { useState, useRef, useEffect, use } from 'react';
import '../../../styles/components/button.css';

interface ButtonProps {
    variant: 'back' | 'settings' | 'send' | 'upload';
    onClick?: () => void;
    disabled?: boolean;
    children?: React.ReactNode;
    className?: string;
    dropdownContent?: React.ReactNode;
}

function Button({ 
    variant, 
    onClick, 
    disabled = false, 
    children, className = '',
    dropdownContent
    }: ButtonProps) 
{
    const navigate = useNavigate();

    // Settings Variable
    const [showDropdown, setShowDropdown] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const buttonRef = useRef<HTMLButtonElement>(null);
    
    // handler
    const defaultHandler = {
        back: () => navigate('/'),
        settings: () => {
            if(dropdownContent) {
                setShowDropdown(!showDropdown);
            } 
        },
        send: () => {},
        upload: () => {},
    };
    
    const handleClick = () => {
        if(onClick) {
            onClick();
        } else if (defaultHandler[variant]) {
            defaultHandler[variant]();
        }
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (
                dropdownRef.current &&
                buttonRef.current &&
                !dropdownRef.current.contains(event.target as Node) &&
                !buttonRef.current.contains(event.target as Node)
            ) {
                setShowDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        }
    }, []);
    
    const renderButtonContent = () => {
        switch (variant) {
            case 'back':
                return <span className="material-icon">arrow_back</span>;
            case 'settings':
                return <span className="material-icon">settings</span>;
            case 'send':
                return <span className="material-icon">send</span>;
            case 'upload':
                return (
                    <>
                      <span className="material-icon">upload_file</span>
                      {children || 'Upload PDF'}
                    </>
                  );
            default:
                return children;
        }
    }

    const getButtonClass = () => {
    switch (variant) {
        case 'back':
            return 'back-button';
        case 'settings':
            return 'settings-button';
        case 'send':
            return 'send-button';
        case 'upload':
            return 'upload-button';
        default:
            return '';
        }
    }

    return (
        <div className="button-container">
            <button 
                ref={buttonRef}
                className = {`${getButtonClass()}`}
                onClick={handleClick}
                disabled={disabled}

            >
                {renderButtonContent()}
            </button>

            {showDropdown && dropdownContent && (
                <div className="dropdown-menu" ref={dropdownRef}>
                    {dropdownContent}
                </div>
            )}
        </div>
    )
}

export default Button;