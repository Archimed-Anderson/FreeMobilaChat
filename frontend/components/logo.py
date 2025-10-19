"""
FreeMobilaChat Logo Component
Professional logo and branding elements
"""

import streamlit as st


def render_logo(size="large", style="default"):
    """
    Render FreeMobilaChat logo
    
    Args:
        size: "small", "medium", "large", "xlarge"
        style: "default", "white", "minimal"
    """
    
    size_configs = {
        "small": {"font_size": "1.5rem", "icon_size": "1.2rem"},
        "medium": {"font_size": "2rem", "icon_size": "1.6rem"},
        "large": {"font_size": "3.5rem", "icon_size": "3rem"},
        "xlarge": {"font_size": "4.5rem", "icon_size": "4rem"}
    }
    
    style_configs = {
        "default": {"color": "#DC143C", "text_shadow": "2px 2px 4px rgba(0,0,0,0.3)"},
        "white": {"color": "white", "text_shadow": "2px 2px 4px rgba(0,0,0,0.5)"},
        "minimal": {"color": "#DC143C", "text_shadow": "none"}
    }
    
    config = size_configs.get(size, size_configs["large"])
    style_config = style_configs.get(style, style_configs["default"])
    
    logo_html = f"""
    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
        <span style="
            font-size: {config['font_size']};
            font-weight: 800;
            font-family: 'Inter', sans-serif;
            color: {style_config['color']};
            text-shadow: {style_config['text_shadow']};
        ">FreeMobilaChat</span>
    </div>
    """
    
    return logo_html


def render_brand_badge():
    """Render a small brand badge"""
    return """
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: linear-gradient(135deg, #DC143C 0%, #FF6B6B 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(220, 20, 60, 0.3);
    ">
        <span>FreeMobilaChat</span>
    </div>
    """


def render_favicon_svg():
    """Generate SVG favicon for FreeMobilaChat"""
    return """
    <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#DC143C;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#FF6B6B;stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="32" height="32" rx="8" fill="url(#grad1)"/>
        <text x="16" y="22" font-family="Arial, sans-serif" font-size="14"
              font-weight="bold" text-anchor="middle" fill="white">FMC</text>
    </svg>
    """


def render_loading_animation():
    """Render a loading animation with FreeMobilaChat branding"""
    return """
    <div style="text-align: center; padding: 2rem;">
        <div style="
            font-size: 3rem;
            animation: pulse 2s infinite;
            margin-bottom: 1rem;
            font-weight: bold;
            color: #DC143C;
        ">FMC</div>
        <div style="
            font-size: 1.5rem;
            font-weight: 600;
            color: #DC143C;
            margin-bottom: 0.5rem;
        ">FreeMobilaChat</div>
        <div style="color: #666;">Loading your AI-powered analytics...</div>
        
        <style>
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }
        </style>
    </div>
    """


def render_error_state():
    """Render error state with branding"""
    return """
    <div style="text-align: center; padding: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem; color: #DC143C; font-weight: bold;">ERROR</div>
        <div style="
            font-size: 1.5rem;
            font-weight: 600;
            color: #DC143C;
            margin-bottom: 0.5rem;
        ">FreeMobilaChat</div>
        <div style="color: #666;">Something went wrong. Please try again.</div>
    </div>
    """


def render_success_state(message="Success!"):
    """Render success state with branding"""
    return f"""
    <div style="text-align: center; padding: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem; color: #28a745; font-weight: bold;">SUCCESS</div>
        <div style="
            font-size: 1.5rem;
            font-weight: 600;
            color: #DC143C;
            margin-bottom: 0.5rem;
        ">FreeMobilaChat</div>
        <div style="color: #666;">{message}</div>
    </div>
    """
