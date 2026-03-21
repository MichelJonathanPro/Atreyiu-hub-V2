/*!
 * Color mode toggler for Bootstrap's docs (https://getbootstrap.com/)
 * Updated for Atreyiu Hub with Cookie support and Global ThemeManager
 */

(() => {
    'use strict'

    const getCookie = (name) => {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    const setCookie = (name, value, days) => {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/";
    }

    const getStoredTheme = () => localStorage.getItem('theme') || getCookie('theme')
    const setStoredTheme = theme => {
        localStorage.setItem('theme', theme)
        setCookie('theme', theme, 365)
    }

    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme()
        if (storedTheme) {
            return storedTheme
        }

        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }

    const setTheme = theme => {
        if (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.setAttribute('data-bs-theme', 'dark')
        } else {
            document.documentElement.setAttribute('data-bs-theme', theme)
        }
    }

    const showActiveTheme = (theme, focus = false) => {
        const themeSwitcherText = document.querySelector('.bs-theme-text')
        const activeThemeIcon = document.querySelector('.theme-icon-active')
        const btnToActive = document.querySelector(`[data-bs-theme-value="${theme}"]`)

        if (!btnToActive) {
            return
        }

        document.querySelectorAll('[data-bs-theme-value]').forEach(element => {
            element.classList.remove('active')
            element.setAttribute('aria-pressed', 'false')
        })

        btnToActive.classList.add('active')
        btnToActive.setAttribute('aria-pressed', 'true')

        // Update active icon if elements exist
        const iconOfActiveBtn = btnToActive.querySelector('.theme-icon')
        if (activeThemeIcon && iconOfActiveBtn) {
            activeThemeIcon.innerHTML = iconOfActiveBtn.outerHTML
        }

        if (focus) {
            btnToActive.focus()
        }
    }

    // Expose ThemeManager globally
    window.ThemeManager = {
        getStoredTheme,
        setStoredTheme,
        getPreferredTheme,
        setTheme,
        showActiveTheme
    }

    // Initialize theme
    setTheme(getPreferredTheme())

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        const storedTheme = getStoredTheme()
        if (storedTheme !== 'light' && storedTheme !== 'dark') {
            setTheme(getPreferredTheme())
        }
    })

    window.addEventListener('DOMContentLoaded', () => {
        const preferredTheme = getPreferredTheme()
        setTheme(preferredTheme)
        showActiveTheme(preferredTheme)

        document.querySelectorAll('[data-bs-theme-value]')
            .forEach(toggle => {
                toggle.addEventListener('click', () => {
                    const theme = toggle.getAttribute('data-bs-theme-value')
                    setStoredTheme(theme)
                    setTheme(theme)
                    showActiveTheme(theme, true)
                })
            })
    })
})()