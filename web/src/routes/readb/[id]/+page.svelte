<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    
    // Reactive state variables for bucket data
    let bucketData: any = $state(null);
    let loading: boolean = $state(true);
    let error: string = $state('');
    
    // Get the ID from the route parameters
    let bucketId = $derived($page.params.id);
    
    // Function to fetch bucket data
    async function fetchBucketData(id: string) {
        loading = true;
        error = '';
        
        try {
            const response = await fetch(`http://localhost:8000/api/buckets/${id}/`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                bucketData = await response.json();
                console.log("Bucket data fetched successfully:", bucketData);
            } else {
                const errorData = await response.json().catch(() => ({}));
                error = `Failed to fetch bucket data: ${response.status} ${response.statusText}`;
                console.error(error, errorData);
            }
        } catch (err) {
            error = 'Network error while fetching bucket data';
            console.error(error, err);
        } finally {
            loading = false;
        }
    }
    
    // Fetch data when component mounts or ID changes
    // Fetch data when component mounts or ID changes
    $effect(() => {
        if (bucketId) {
            fetchBucketData(bucketId);
        }
    });
</script>

<!-- Loading state -->
{#if loading}
    <div class="flex justify-center items-center min-h-screen">
        <div class="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>
{/if}

<!-- Error state -->
{#if error}
    <div class="max-w-4xl mx-auto p-6">
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <strong class="font-bold">Error!</strong>
            <span class="block sm:inline">{error}</span>
        </div>
    </div>
{/if}

<!-- Bucket content -->
{#if bucketData && !loading}
    <div class="max-w-6xl mx-auto">
        <!-- Header with banner image -->
        <div class="relative h-64 md:h-80 lg:h-96 overflow-hidden rounded-lg shadow-lg mb-8">
            <img 
                src={bucketData.banner} 
                alt={bucketData.name} 
                class="w-full h-full object-cover"
            />
            <!-- Overlay with bucket info -->
            <div class="absolute inset-0 bg-black bg-opacity-40 flex items-end">
                <div class="p-6 text-white">
                    <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-2">
                        {bucketData.name}
                    </h1>
                    <p class="text-lg md:text-xl opacity-90">
                        by {bucketData.user_owner_name}
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Content area -->
        <div class="px-6 pb-8">
            <!-- Tags -->
            {#if bucketData.tag_names && bucketData.tag_names.length > 0}
                <div class="mb-6">
                    <div class="flex flex-wrap gap-2">
                        {#each bucketData.tag_names as tag}
                            <span class="inline-block bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full dark:bg-blue-900 dark:text-blue-200">
                                #{tag}
                            </span>
                        {/each}
                    </div>
                </div>
            {/if}
            
            <!-- Description -->
            {#if bucketData.description}
                <div class="mb-8">
                    <h2 class="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
                        About
                    </h2>

                    <p class="text-gray-600 dark:text-gray-300 text-lg leading-relaxed">
                        {bucketData.description}
                    </p>
                </div>
            {/if}

            <!-- Children Buckets -->
            {#if bucketData.children_buckets && bucketData.children_buckets.length > 0}
                <div class="mb-8">
                    <h2 class="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
                        Sub-Buckets
                    </h2>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                        {#each bucketData.children_buckets as childBucket}
                            <a 
                                href="/readb/{childBucket.id}" 
                                class="group block bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden"
                            >
                                <div class="aspect-[4/3] relative overflow-hidden">
                                    <img 
                                        src={childBucket.banner} 
                                        alt={childBucket.name}
                                        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                                    />
                                </div>
                                <div class="p-3">
                                    <h3 class="text-sm font-medium text-gray-800 dark:text-white truncate">
                                        {childBucket.name}
                                    </h3>
                                </div>
                            </a>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- Pages -->
            {#if bucketData.pages && bucketData.pages.length > 0}
                <div class="mb-8">
                    <h2 class="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
                        Pages
                    </h2>
                    <div class="space-y-2">
                        {#each bucketData.pages as page}
                            <a 
                                href="/readp/{page.id}" 
                                class="block p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-all group"
                            >
                                <h3 class="text-lg font-medium text-gray-800 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                    {page.title}
                                </h3>
                            </a>
                        {/each}
                    </div>
                </div>
            {/if}
                        
            <!-- Action buttons -->
            <div class="flex flex-wrap gap-4">
                {#if bucketData.can_edit}
                    <button 
                        class="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                        style="background-color: {bucketData.background || '#3B82F6'}"
                    >
                        Edit Bucket
                    </button>
                {/if}
                <button class="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-6 rounded-lg transition-colors">
                    Share
                </button>
            </div>
        </div>
    </div>
{/if}
