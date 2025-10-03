<script lang="ts">
    import ScrollPannel from "$lib/app/ScrollPannel.svelte";
    import { user } from '$lib/auth';
    import { authenticatedPost } from '$lib/auth';
    
    // Create bucket dialog state variables
    let showCreateBucketDialog: boolean = $state(false);
    let newBucketName: string = $state('');
    let newBucketVisibility: boolean = $state(false);
    let creatingBucket: boolean = $state(false);
    let createError: string = $state('');
    
    // Function to handle dialogue window opening
    function openCreateBucketDialog() {
        showCreateBucketDialog = true;
        newBucketName = '';
        newBucketVisibility = false;
        createError = '';
    }

    // Function to handle dialogue window closing
    function closeCreateBucketDialog() {
        showCreateBucketDialog = false;
        newBucketName = '';
        newBucketVisibility = false;
        createError = '';
    }

    // Function to handle click outside dialogue
    function handleDialogClick(event: MouseEvent) {
        if (event.target === event.currentTarget) {
            closeCreateBucketDialog();
        }
    }

    // Function to create a new bucket without parent
    async function createNewBucket() {
        if (!newBucketName.trim()) {
            createError = 'Bucket name is required';
            return;
        }

        creatingBucket = true;
        createError = '';

        try {
            let body = {
                name: newBucketName.trim(),
                bucket_owner: null, // No parent for root-level buckets
                visibility: newBucketVisibility,
                tags: [],
                description: '',
                banner: '',
                background: ''
            }

            const response = await authenticatedPost('/api/buckets/', body);

            if (response.ok) {
                const newBucket = await response.json();
                console.log('Bucket created successfully:', newBucket);
                closeCreateBucketDialog();
                // Optionally redirect to the new bucket or refresh the page
                // window.location.href = `/bucket/${newBucket.slug}`;
                window.location.reload(); // Refresh to show the new bucket
            } else {
                const errorData = await response.json().catch(() => ({}));
                createError = errorData.detail || errorData.error || `Failed to create bucket: ${response.status}`;
                console.error('Create bucket error:', errorData);
            }
        } catch (err) {
            createError = 'Network error while creating bucket';
            console.error('Create bucket error:', err);
        } finally {
            creatingBucket = false;
        }
    }
</script>

<div class="flex flex-col items-center">
    <h1 class="text-2xl flex font-bold my-4 text-center text-gray-800 dark:text-white">Content</h1>

    <!-- Create Bucket button for authenticated users -->
    {#if $user}
        <div class="mb-6">
            <button 
                class="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                onclick={openCreateBucketDialog}
            >
                Create Bucket
            </button>
        </div>
    {/if}

    <ScrollPannel />
</div>

<!-- Create Bucket Dialog -->
{#if showCreateBucketDialog}
    <div 
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onclick={handleDialogClick}
    >
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 class="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
                Create New Bucket
            </h2>
            
            <!-- Error message -->
            {#if createError}
                <div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                    {createError}
                </div>
            {/if}
            
            <!-- Bucket name input -->
            <div class="mb-4">
                <label for="bucketName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Bucket Name
                </label>
                <input
                    id="bucketName"
                    type="text"
                    bind:value={newBucketName}
                    placeholder="Enter bucket name"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                    disabled={creatingBucket}
                />
            </div>
            
            <!-- Visibility toggle -->
            <div class="mb-6">
                <label class="flex items-center space-x-3">
                    <button
                        type="button"
                        onclick={() => newBucketVisibility = !newBucketVisibility}
                        class={`relative inline-flex w-12 h-6 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${newBucketVisibility ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'} ${creatingBucket ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                        disabled={creatingBucket}
                    >
                        <span class={`inline-block w-4 h-4 transform transition-transform bg-white rounded-full shadow-md ${newBucketVisibility ? 'translate-x-7' : 'translate-x-1'}`}></span>
                    </button>
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Public visibility
                    </span>
                </label>
            </div>
            
            <!-- Action buttons -->
            <div class="flex justify-end space-x-3">
                <button
                    type="button"
                    onclick={closeCreateBucketDialog}
                    class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 rounded-md transition-colors"
                    disabled={creatingBucket}
                >
                    Cancel
                </button>
                <button
                    type="button"
                    onclick={createNewBucket}
                    class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={creatingBucket || !newBucketName.trim()}
                >
                    {#if creatingBucket}
                        <span class="flex items-center">
                            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Creating...
                        </span>
                    {:else}
                        Create
                    {/if}
                </button>
            </div>
        </div>
    </div>
{/if}
