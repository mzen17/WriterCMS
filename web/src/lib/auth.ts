// src/lib/auth.ts
import { writable, get } from 'svelte/store';
import { onAuthStateChanged, type User } from 'firebase/auth';
import { auth } from './firebase'; // Your firebase.ts initialization
import { browser } from '$app/environment';

// Writable stores for user and loading state
export const user = writable<User | null>(null);
export const loading = writable(true);

/**
 * A promise that resolves when the initial Firebase auth check is complete.
 * This is useful for functions that need to wait for auth state before executing.
 */
let authReady: Promise<void>;
let resolveAuthReady: (() => void) | null;

// Only create the promise and initialize auth in the browser
if (browser) {
  authReady = new Promise(resolve => {
    resolveAuthReady = resolve;
  });
  
  // Automatically initialize the auth listener
  onAuthStateChanged(auth, (firebaseUser) => {
    user.set(firebaseUser);
    loading.set(false);
    // Resolve the authReady promise on first auth state change
    if (resolveAuthReady) {
      resolveAuthReady();
      resolveAuthReady = null; // Prevent multiple calls
    }
  });
} else {
  // In SSR, create a resolved promise
  authReady = Promise.resolve();
}

/**
 * Gets the current user's Firebase ID token.
 * It waits for the initial auth check to complete.
 * @returns {Promise<string | null>} The ID token or null if not authenticated.
 */
export async function getIdToken(): Promise<string | null> {

  // Wait for the initial auth state to be determined
  await authReady;
  
  const currentUser = get(user);
  if (!currentUser) {
    return null;
  }

  try {
    return await currentUser.getIdToken();
  } catch (error) {
    console.error('Error getting ID token:', error);
    return null;
  }
}

/**
 * A wrapper for the native fetch API that automatically includes the
 * Firebase Authentication token in the request headers.
 * @param {string} url The URL to fetch.
 * @param {RequestInit} options The fetch options.
 * @returns {Promise<Response>} The fetch response.
 */
export async function authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = await getIdToken();
  if (!token) {
    // For GET requests without credentials, proceed without token
    if (!options.method || options.method.toUpperCase() === 'GET') {
        console.log(options)
      return fetch(url, options);
    }
    
    // For non-GET requests, authentication is required
    throw new Error('User is not authenticated. Cannot make authenticated fetch call.');
  }

  const headers = new Headers(options.headers);
  headers.set('Authorization', `Bearer ${token}`);
  
  return fetch(url, { ...options, headers });
}

/**
 * A convenience function for making authenticated POST requests.
 * @param {string} url The URL to post to.
 * @param {any} body The request body, which will be JSON stringified.
 * @param {RequestInit} options Additional fetch options.
 * @returns {Promise<Response>} The fetch response.
 */
export async function authenticatedPost(url:string, body: any, method="POST", options: RequestInit = {}): Promise<Response> {
    console.log(options)
    const postOptions = {
        ...options,
        method: method,
        headers: {
            ...options.headers,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    }
    return authenticatedFetch(url, postOptions);
}