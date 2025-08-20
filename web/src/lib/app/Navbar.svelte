<script lang="ts">
    import { authenticatedFetch, clearCSRFToken } from '$lib/csrf';
    
    export let pfp = "";
    export let auth = false;
    export let username = "";
    let showMenu = false;

    async function handleLogout() {
        try {
            // Call the backend logout endpoint
            const response = await authenticatedFetch('http://localhost:8000/api/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                // Clear CSRF token
                clearCSRFToken();
                
                // Clear all authentication cookies
                document.cookie = 'sessionid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=localhost;';
                document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=localhost;';
                document.cookie = 'username=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=localhost;';
                document.cookie = 'session_ck=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=localhost;';
                
                // Redirect to login page or home page
                window.location.href = '/login';
            } else {
                console.error('Logout failed:', response.statusText);
            }
        } catch (error) {
            console.error('Error during logout:', error);
            // Even if the backend call fails, clear the cookies locally
            clearCSRFToken();
            document.cookie = 'sessionid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=localhost;';
            document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=localhost;';
            document.cookie = 'username=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=localhost;';
            document.cookie = 'session_ck=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=localhost;';
            window.location.href = '/login';
        }
    }
</script>

<nav class="bg-white z-20 dark:bg-gray-800 shadow-lg w-screen border-b border-gray-200 fixed">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <div class="flex-shrink-0">
                <h1 class="text-xl font-bold text-gray-900 dark:text-white"><a href="/">WCMS</a></h1>
            </div>

            <div
                class="relative"
                on:mouseenter={() => (showMenu = true)}
                on:mouseleave={() => (showMenu = false)}
                role="menu"
                tabindex="-1"

            >
                <button
                    on:click={() => showMenu = !showMenu}
                    class="w-8 h-8 rounded-full overflow-hidden border-2 border-gray-300 hover:border-gray-400 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                    <img src={pfp} alt="pfp" class="w-full h-full object-cover" />
                </button>

                {#if showMenu}
                    <div
                        class="absolute right-0 mt-0 w-36 bg-white dark:bg-gray-700 rounded-md shadow-lg py-1 z-50 border border-gray-200 dark:border-black"
                    >
                        {#if auth}
                            <div class="px-4 py-2 text-sm text-gray-700 border-b border-gray-200 dark:border-white dark:text-white">
                                {username}
                            </div>
                            <a href="/settings" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark: dark:text-white dark:hover:bg-gray-800">
                                Settings
                            </a>
                            <button 
                                on:click={handleLogout}
                                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-800 hover:text-white transition-colors dark:text-white"
                            >
                                Logout
                            </button>
                        {:else}
                            <div class="px-4 py-2 text-sm text-gray-700 border-b border-gray-200 dark:text-white">
                                Guest
                            </div>
                            <a href="/login" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-800 hover:text-white transition-colors dark:text-white">
                                Login
                            </a>
                        {/if}
                    </div>
                {/if}
            </div>
        </div>
    </div>
</nav>