<script>
    import { sendPasswordResetEmail } from 'firebase/auth';
    import { auth } from '$lib/firebase';

    let email = '';
    let loading = false;
    let error = '';
    let success = '';

    async function handleSubmit() {
        loading = true;
        error = '';
        success = '';
        
        try {
            await sendPasswordResetEmail(auth, email);
            success = 'Password reset email sent! Check your inbox.';
        } catch (err) {
            console.error('Password reset failed:', err);
            switch (err.code) {
                case 'auth/user-not-found':
                    error = 'No account found with this email address';
                    break;
                case 'auth/invalid-email':
                    error = 'Invalid email address';
                    break;
                case 'auth/too-many-requests':
                    error = 'Too many requests. Please wait before trying again';
                    break;
                default:
                    error = 'Failed to send reset email. Please try again';
            }
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Reset Password</title>
</svelte:head>

<div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
    <h1 class="text-2xl font-bold text-center mb-6 text-gray-800 dark:text-white">Reset Password</h1>
    
    {#if error}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"> 
            {error}
        </div>
    {/if}

    {#if success}
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4"> 
            {success}
        </div>
    {/if}
    
    <form on:submit|preventDefault={handleSubmit}>
        <div class="mb-6">
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email</label>
            <input
                type="email"
                id="email"
                bind:value={email}
                required
                placeholder="Enter your email address"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:text-gray-400"
            />
        </div>
        
        <button
            type="submit"
            disabled={loading}
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2 px-4 rounded-md transition duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
            {#if loading}
                <span class="flex items-center justify-center">
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Sending...
                </span>
            {:else}
                Send Reset Email
            {/if}
        </button>
    </form>
    
    <div class="mt-6 text-center">
        <p class="text-sm text-gray-600 dark:text-white">
            Remember your password? 
            <a href="/login" class="text-blue-600 dark:text-blue-300 hover:text-blue-500 font-medium">Sign in</a>
        </p>
    </div>
</div>
