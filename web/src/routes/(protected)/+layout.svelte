<script>
    import { user, loading } from '$lib/auth';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    let { children } = $props();

    // Redirect to login if not authenticated
    $effect(() => {
        if (!$loading && !$user) {
            goto('/login');
        }
    });
</script>

<!-- Only render children if user is authenticated -->
{#if $loading}
    <div class="flex justify-center items-center min-h-screen">
        <div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
    </div>
{:else if $user}
    {@render children()}
{:else}
    <!-- User will be redirected to login -->
{/if}
