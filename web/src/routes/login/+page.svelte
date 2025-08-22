<script>
    import { signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
    import { auth } from '$lib/firebase';
    import { goto } from '$app/navigation';

    let email = '';
    let password = '';
    let loading = false;
    let googleLoading = false;
    let error = '';

    async function handleSubmit() {
        loading = true;
        error = '';
        
        try {
            await signInWithEmailAndPassword(auth, email, password);
            // Firebase automatically handles the authentication state
            goto('/');
        } catch (err) {
            console.error('Login failed:', err);
            // Handle specific Firebase auth errors
            switch (err.code) {
                case 'auth/user-not-found':
                    error = 'No account found with this email address';
                    break;
                case 'auth/wrong-password':
                    error = 'Incorrect password';
                    break;
                case 'auth/invalid-email':
                    error = 'Invalid email address';
                    break;
                case 'auth/user-disabled':
                    error = 'This account has been disabled';
                    break;
                case 'auth/too-many-requests':
                    error = 'Too many failed login attempts. Please try again later';
                    break;
                default:
                    error = 'Failed to login. Please try again';
            }
        } finally {
            loading = false;
        }
    }

    async function handleGoogleSignIn() {
        googleLoading = true;
        error = '';

        try {
            const provider = new GoogleAuthProvider();
            await signInWithPopup(auth, provider);
            // Firebase automatically handles the authentication state
            goto('/');
        } catch (err) {
            console.error('Google sign-in failed:', err);
            // Handle specific Firebase auth errors
            switch (err.code) {
                case 'auth/popup-closed-by-user':
                    error = 'Sign-in cancelled';
                    break;
                case 'auth/popup-blocked':
                    error = 'Pop-up blocked by browser. Please allow pop-ups and try again';
                    break;
                case 'auth/cancelled-popup-request':
                    error = 'Sign-in cancelled';
                    break;
                case 'auth/account-exists-with-different-credential':
                    error = 'An account already exists with this email using a different sign-in method';
                    break;
                default:
                    error = 'Failed to sign in with Google. Please try again';
            }
        } finally {
            googleLoading = false;
        }
    }
</script>

<svelte:head>
    <title>Login</title>
</svelte:head>

<div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
    <h1 class="text-2xl font-bold text-center mb-6 text-gray-800 dark:text-white">Login</h1>
    
    {#if error}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"> 
            {error}
        </div>
    {/if}
    
    <form on:submit|preventDefault={handleSubmit}>
        <div class="mb-4">
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email</label>
            <input
                type="email"
                id="email"
                bind:value={email}
                required
                placeholder="Enter your email"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:text-gray-400"
            />
        </div>
        
        <div class="mb-6">
            <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Password</label>
            <input
                type="password"
                id="password"
                bind:value={password}
                required
                placeholder="Enter your password"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:text-gray-400"
            />
        </div>
        
        <button
            type="submit"
            disabled={loading || googleLoading}
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2 px-4 rounded-md transition duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
            {#if loading}
                <span class="flex items-center justify-center">
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Logging in...
                </span>
            {:else}
                Login
            {/if}
        </button>
    </form>
    
    <!-- Divider -->
    <div class="mt-6 mb-6">
        <div class="relative">
            <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-gray-300"></div>
            </div>
            <div class="relative flex justify-center text-sm">
                <span class="px-2 bg-white dark:bg-gray-800 text-gray-500">or</span>
            </div>
        </div>
    </div>
    
    <!-- Google Sign-in Button -->
    <button
        type="button"
        on:click={handleGoogleSignIn}
        disabled={loading || googleLoading}
        class="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-600 transition duration-200 ease-in-out"
    >
        {#if googleLoading}
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Signing in...
        {:else}
            <svg class="w-5 h-5 mr-3" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
        {/if}
    </button>
    
    <div class="mt-6 text-center">
        <p class="text-sm text-gray-600 dark:text-white">
            Don't have an account? 
            <a href="/register" class="text-blue-600 dark:text-blue-300 hover:text-blue-500 font-medium">Sign up</a>
        </p>
        <p class="text-sm text-gray-600 dark:text-white mt-2">
            Forgot your password? 
            <a href="/reset-password" class="text-blue-600 dark:text-blue-300 hover:text-blue-500 font-medium">Reset it here</a>
        </p>
    </div>
</div>
