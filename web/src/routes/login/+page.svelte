<script>
    let username = '';
    let password = '';
    let loading = false;
    let error = '';

    async function handleSubmit() {
        loading = true;
        error = '';
        
        try {
            const response = await fetch('http://localhost:8000/api/login/', {
                method: 'POST',
                credentials: 'include', // Important: include cookies
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            if (response.ok) {
                // No need to manually store anything - browser handles the session cookie
                window.location.href = '/';
            } else {
                error = 'Failed to Login';
            }
        } catch (err) {
            console.error('Login failed:', err);
            error = 'Failed to Login';
        } finally {
            loading = false;
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
            <label for="username" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Username</label>
            <input
                type="username"
                id="username"
                bind:value={username}
                required
                placeholder="Enter your username"
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
            disabled={loading}
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
    
    <div class="mt-6 text-center">
        <p class="text-sm text-gray-600 dark:text-white">
            Don't have an account? 
            <a href="/register" class="text-blue-600 dark:text-blue-300 hover:text-blue-500 font-medium">Sign up</a>
        </p>
    </div>
</div>
