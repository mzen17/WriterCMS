<script lang="ts">
	import '../app.css';
	import Navbar from '$lib/app/Navbar.svelte';
    import { onMount } from 'svelte';
    // Reactive state variables to hold user data
    let username: string = $state('Loading...');
    let pfp: string = $state(''); // Profile picture URL or base64
    let auth: boolean = $state(false);
	let darkmode: boolean = $state(false);

    // Function to fetch user data
    async function fetchUserData() {

        try {
            const response = await fetch('http://localhost:8000/api/users/me/', {
                method: 'GET',
				credentials: 'include', // Important: include cookies
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const userData = await response.json();
                console.log("User data fetched successfully:", userData);
                username = userData.username || 'User'; // Fallback username
                pfp = userData.pfp || 'https://placehold.co/40x40/cccccc/000000?text=PFP'; // Fallback PFP
				darkmode = userData.theme //;
                auth = true;
            } else {
                const errorData = await response.json().catch(() => ({}));
                console.error(`Failed to fetch user data: ${response.status} ${response.statusText}`, errorData);
                username = 'Login';
				darkmode = false;
                pfp = '';
                auth = false;
            }
        } catch (error) {
            console.error('Network error while fetching user data:', error);
            username = 'Oh Dear, Network got Fked.';
            pfp = '';
            auth = false;
        }
    }

    // Call fetchUserData when the component mounts
    onMount(() => {
        fetchUserData();
    });

    // The children slot will render the content passed to this layout component
    let { children } = $props();
</script>

<Navbar username={username} auth={auth} pfp={pfp}/>
<div class="pt-16 flex justify-center items-center min-h-screen p-4 bg-white dark:bg-gray-900">
{@render children()}
</div>