<script lang="ts">
	import '../app.css';
	import Navbar from '$lib/app/Navbar.svelte';
    import { user, loading, authenticatedFetch } from '$lib/auth';
    import { onMount } from 'svelte';

    // Reactive state variables to hold user data
    let username: string = $state('Loading...');
    let pfp: string = $state(''); // Profile picture URL or base64
    let auth: boolean = $state(false);
	let darkmode: boolean = $state(false);

    // Function to update user data based on Firebase auth state
    async function updateUserData(firebaseUser: any) {
        if (firebaseUser) {
            auth = true;
            
            // Optionally sync with Django backend to get additional user data
            try {
                const response = await authenticatedFetch('/api/users/me/');

                if (response.ok) {
                    const userData = await response.json();
                    if (userData.first_name) console.log("Data: " + userData.first_name)
                    // Update with backend data if available
                    username = userData.email.substring(0, 10) + "..."
                    if (userData.first_name) username = userData.first_name
                    if (userData.pfp) pfp = userData.pfp;
                    if (userData.theme !== undefined) darkmode = userData.theme;
                }
            } catch (error) {
                console.log('Could not fetch additional user data from backend:', error);
            }
        } else {
            username = 'Login';
            pfp = '';
            auth = false;
            darkmode = false;
        }
    }

    // Subscribe to Firebase auth state changes
    $effect(() => {
        if (!$loading) {
            updateUserData($user);
        }
    });

    // The children slot will render the content passed to this layout component
    let { children } = $props();
</script>

<svelte:head>
        <title>WCMS</title>
</svelte:head>


<Navbar username={username} auth={auth} pfp={pfp}/>
<div class="pt-16 flex justify-center items-center min-h-screen p-4 bg-white dark:bg-gray-900">
{@render children()}
</div>