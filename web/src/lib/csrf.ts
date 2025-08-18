// CSRF token management for Django backend

let csrfToken: string | null = null;


export async function getCSRFToken() {
    if (csrfToken) {
        return csrfToken;
    }

    try {
        const response = await fetch('http://localhost:8000/api/csrf/', {
            method: 'GET',
            credentials: 'include', // Include cookies to establish session
        });

        if (response.ok) {
            const data = await response.json();
            csrfToken = data.csrfToken;
            return csrfToken || '';
        } else {
            throw new Error('Failed to fetch CSRF token');
        }
    } catch (error) {
        console.error('Error fetching CSRF token:', error);
        throw error;
    }
}

export function getCSRFTokenFromCookie() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


export async function authenticatedFetch(url: string, options: any = {}) {
    const token = await getCSRFToken();
    
    options["headers"]['X-CSRFToken']=token
    options["credentials"] = "include"
    
    console.log(options)

    return fetch(url, options);
}

/**
 * Clears the cached CSRF token (useful after logout)
 */
export function clearCSRFToken() {
    csrfToken = null;
}
