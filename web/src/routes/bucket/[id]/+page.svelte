<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { getCSRFToken } from '$lib/csrf';
    
    // Reactive state variables for bucket data
    let bucketData: any = $state(null);
    let loading: boolean = $state(true);
    let error: string = $state('');
    
    // Dialogue state variables
    let showCreateBucketDialog: boolean = $state(false);
    let newBucketName: string = $state('');
    let newBucketVisibility: boolean = $state(false);
    let creatingBucket: boolean = $state(false);
    let createError: string = $state('');
    
    // Edit dialog state variables
    let showEditBucketDialog: boolean = $state(false);
    let editBucketName: string = $state('');
    let editBucketDescription: string = $state('');
    let editBucketVisibility: boolean = $state(false);
    let editBucketBanner: string = $state('');
    let editBucketBackground: string = $state('');
    let editBucketTags: string[] = $state([]); // Store as array of tag URLs
    let savingBucket: boolean = $state(false);
    let editError: string = $state('');

    // Tag management state variables
    let availableTags: any[] = $state([]);
    let loadingTags: boolean = $state(false);
    let newTagName: string = $state('');
    let showTagInput: boolean = $state(false);
    let creatingTag: boolean = $state(false);
    let tagError: string = $state('');

    // Create page dialog state variables
    let showCreatePageDialog: boolean = $state(false);
    let newPageTitle: string = $state('');
    let newPagePublic: boolean = $state(false);
    let creatingPage: boolean = $state(false);
    let createPageError: string = $state('');
    
    // Get the ID from the route parameters
    let bucketId = $derived($page.params.id);
    
    // Function to fetch available tags
    async function fetchAvailableTags() {
        loadingTags = true;
        try {
            const response = await fetch('http://localhost:8000/api/tags/', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                availableTags = data.results;
            } else {
                console.error('Failed to fetch tags:', response.status);
            }
        } catch (err) {
            console.error('Network error while fetching tags:', err);
        } finally {
            loadingTags = false;
        }
    }

    // Function to create a new tag
    async function createNewTag() {
        if (!newTagName.trim()) {
            tagError = 'Tag name is required';
            return;
        }

        // Validate tag name
        const tagNameRegex = /^[a-zA-Z\-_\/]+$/;
        if (!tagNameRegex.test(newTagName) || newTagName.length > 20) {
            tagError = 'Tag name can only contain letters, hyphens, underscores, and slashes, and must be 20 characters or less';
            return;
        }

        creatingTag = true;
        tagError = '';

        try {
            const csrfToken = await getCSRFToken();
            const response = await fetch('http://localhost:8000/api/tags/', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    tag_name: newTagName.trim(),
                    tag_description: ''
                })
            });

            if (response.ok) {
                const newTag = await response.json();
                availableTags = [...availableTags, newTag];
                editBucketTags = [...editBucketTags, newTag.url];
                newTagName = '';
                showTagInput = false;
            } else {
                const errorData = await response.json().catch(() => ({}));
                tagError = errorData.detail || errorData.error || `Failed to create tag: ${response.status}`;
            }
        } catch (err) {
            tagError = 'Network error while creating tag';
            console.error('Create tag error:', err);
        } finally {
            creatingTag = false;
        }
    }

    // Function to toggle tag selection
    function toggleTag(tagUrl: string) {
        if (editBucketTags.includes(tagUrl)) {
            editBucketTags = editBucketTags.filter(url => url !== tagUrl);
        } else {
            editBucketTags = [...editBucketTags, tagUrl];
        }
    }

    // Function to remove tag from selection
    function removeTag(tagUrl: string) {
        editBucketTags = editBucketTags.filter(url => url !== tagUrl);
    }

    // Function to get tag name by URL
    function getTagNameByUrl(tagUrl: string): string {
        const tag = availableTags.find(t => t.url === tagUrl);
        return tag ? tag.tag_name : '';
    }

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
            closeCreatePageDialog();
            closeEditBucketDialog();
        }
    }

    // Function to handle edit dialogue window opening
    function openEditBucketDialog() {
        if (bucketData) {
            showEditBucketDialog = true;
            editBucketName = bucketData.name || '';
            editBucketDescription = bucketData.description || '';
            editBucketVisibility = bucketData.visibility || false;
            editBucketBanner = bucketData.banner || '';
            editBucketBackground = bucketData.background || '';
            editBucketTags = bucketData.tags || [];
            editError = '';
            fetchAvailableTags(); // Load available tags when opening dialog
        }
    }

    // Function to handle edit dialogue window closing
    function closeEditBucketDialog() {
        showEditBucketDialog = false;
        editBucketName = '';
        editBucketDescription = '';
        editBucketVisibility = false;
        editBucketBanner = '';
        editBucketBackground = '';
        editBucketTags = [];
        editError = '';
        newTagName = '';
        showTagInput = false;
        tagError = '';
    }

    // Function to save bucket edits
    async function saveEditedBucket() {
        if (!editBucketName.trim()) {
            editError = 'Bucket name is required';
            return;
        }

        savingBucket = true;
        editError = '';

        try {
            const csrfToken = await getCSRFToken();
            
            const response = await fetch(`http://localhost:8000/api/buckets/${bucketId}/`, {
                method: 'PUT',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    name: editBucketName.trim(),
                    description: editBucketDescription.trim(),
                    visibility: editBucketVisibility,
                    banner: editBucketBanner.trim(),
                    background: editBucketBackground.trim(),
                    tags: editBucketTags
                })
            });

            if (response.ok) {
                const updatedBucket = await response.json();
                console.log('Bucket updated successfully:', updatedBucket);
                closeEditBucketDialog();
                await fetchBucketData(bucketId);
                window.location.href = "/bucket/" + bucketData.bucket_owner_slug
            } else {
                const errorData = await response.json().catch(() => ({}));
                editError = errorData.detail || errorData.error || `Failed to update bucket: ${response.status}`;
                console.error('Update bucket error:', errorData);
            }
        } catch (err) {
            editError = 'Network error while updating bucket';
            console.error('Update bucket error:', err);
        } finally {
            savingBucket = false;
        }
    }

    // Function to create a new bucket
    async function createNewBucket() {
        if (!newBucketName.trim()) {
            createError = 'Bucket name is required';
            return;
        }

        creatingBucket = true;
        createError = '';

        try {
            const csrfToken = await getCSRFToken();
            const response = await fetch('http://localhost:8000/api/buckets/', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    name: newBucketName.trim(),
                    bucket_owner: bucketData.url,
                    visibility: newBucketVisibility,
                    tags: [],
                    description: '',
                    banner: '',
                    background: ''
                })
            });

            if (response.ok) {
                const newBucket = await response.json();
                console.log('Bucket created successfully:', newBucket);
                closeCreateBucketDialog();
                // Refresh the bucket data to show the new sub-bucket
                await fetchBucketData(bucketId);
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

    // Function to handle create page dialogue window opening
    function openCreatePageDialog() {
        showCreatePageDialog = true;
        newPageTitle = '';
        newPagePublic = false;
        createPageError = '';
    }

    // Function to handle create page dialogue window closing
    function closeCreatePageDialog() {
        showCreatePageDialog = false;
        newPageTitle = '';
        newPagePublic = false;
        createPageError = '';
    }

    // Function to create a new page
    async function createNewPage() {
        if (!newPageTitle.trim()) {
            createPageError = 'Page title is required';
            return;
        }

        creatingPage = true;
        createPageError = '';

        try {
            const csrfToken = await getCSRFToken();
            const response = await fetch('http://localhost:8000/api/pages/', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    title: newPageTitle.trim(),
                    description: '',
                    porder: 1,
                    public: newPagePublic,
                    bucket: bucketData.url
                })
            });
            console.log(JSON.stringify({
                    title: newPageTitle.trim(),
                    description: '',
                    porder: 1,
                    public: newPagePublic,
                    bucket: bucketData.url
                }))

            if (response.ok) {
                const newPage = await response.json();
                console.log('Page created successfully:', newPage);
                closeCreatePageDialog();
                // Refresh the bucket data to show the new page
                await fetchBucketData(bucketId);
            } else {
                const errorData = await response.json().catch(() => ({}));
                createPageError = errorData.detail || errorData.error || `Failed to create page: ${response.status}`;
                console.error('Create page error:', errorData);
            }
        } catch (err) {
            createPageError = 'Network error while creating page';
            console.error('Create page error:', err);
        } finally {
            creatingPage = false;
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
            <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent flex items-end">
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
                                href="/bucket/{childBucket.slug}" 
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
                                href="/page/{page.slug}" 
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
            <div class="flex flex-col justify-center items-center">
            <div class="flex flex-wrap gap-4 justify-center mb-8">
                {#if bucketData.can_edit}
                    <button 
                        class="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                        onclick={openCreateBucketDialog}
                    >
                        New Bucket
                    </button>
                    <button 
                        class="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                        onclick={openCreatePageDialog}
                    >
                        New Page
                    </button>
                    <button 
                        class="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                        onclick={openEditBucketDialog}
                    >
                        Edit
                    </button>

                {/if}
            </div>
            <button class=" hover:bg-orange-600 text-white font-medium py-2 px-6 rounded-lg transition-colors bg-orange-400 w-32" onclick={() => window.location.href = bucketData.bucket_owner ? '/bucket/' + bucketData.bucket_owner_slug : '/'}>
                Return
            </button>
        </div>

        </div>
    </div>
{/if}

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

<!-- Create Page Dialog -->
{#if showCreatePageDialog}
    <div 
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onclick={handleDialogClick}
    >
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 class="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
                Create New Page
            </h2>
            
            <!-- Error message -->
            {#if createPageError}
                <div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                    {createPageError}
                </div>
            {/if}
            
            <!-- Page title input -->
            <div class="mb-4">
                <label for="pageTitle" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Page Title
                </label>
                <input
                    id="pageTitle"
                    type="text"
                    bind:value={newPageTitle}
                    placeholder="Enter page title"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                    disabled={creatingPage}
                />
            </div>
            
            <!-- Public toggle -->
            <div class="mb-6">
                <label class="flex items-center space-x-3">
                    <button
                        type="button"
                        onclick={() => newPagePublic = !newPagePublic}
                        class={`relative inline-flex w-12 h-6 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${newPagePublic ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'} ${creatingPage ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                        disabled={creatingPage}
                    >
                        <span class={`inline-block w-4 h-4 transform transition-transform bg-white rounded-full shadow-md ${newPagePublic ? 'translate-x-7' : 'translate-x-1'}`}></span>
                    </button>
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Public page
                    </span>
                </label>
            </div>
            
            <!-- Action buttons -->
            <div class="flex justify-end space-x-3">
                <button
                    type="button"
                    onclick={closeCreatePageDialog}
                    class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 rounded-md transition-colors"
                    disabled={creatingPage}
                >
                    Cancel
                </button>
                <button
                    type="button"
                    onclick={createNewPage}
                    class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={creatingPage || !newPageTitle.trim()}
                >
                    {#if creatingPage}
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

<!-- Edit Bucket Dialog -->
{#if showEditBucketDialog}
    <div 
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onclick={handleDialogClick}
    >
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <h2 class="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
                Edit Bucket
            </h2>
            
            <!-- Error message -->
            {#if editError}
                <div class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                    {editError}
                </div>
            {/if}
            
            <!-- Bucket name input -->
            <div class="mb-4">
                <label for="editBucketName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Bucket Name *
                </label>
                <input
                    id="editBucketName"
                    type="text"
                    bind:value={editBucketName}
                    placeholder="Enter bucket name"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                    disabled={savingBucket}
                />
            </div>
            
            <!-- Description input -->
            <div class="mb-4">
                <label for="editBucketDescription" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description
                </label>
                <textarea
                    id="editBucketDescription"
                    bind:value={editBucketDescription}
                    placeholder="Enter bucket description"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                    disabled={savingBucket}
                ></textarea>
            </div>
            
            <!-- Banner URL input -->
            <div class="mb-4">
                <label for="editBucketBanner" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Banner Image URL
                </label>
                <input
                    id="editBucketBanner"
                    type="url"
                    bind:value={editBucketBanner}
                    placeholder="Enter banner image URL"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                    disabled={savingBucket}
                />
            </div>
            
            <!-- Background URL input -->
            <div class="mb-4">
                <label for="editBucketBackground" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Background Image URL
                </label>
                <input
                    id="editBucketBackground"
                    type="url"
                    bind:value={editBucketBackground}
                    placeholder="Enter background image URL"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                    disabled={savingBucket}
                />
            </div>
            
            <!-- Tags input -->
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Tags
                </label>
                
                <!-- Selected tags display -->
                {#if editBucketTags.length > 0}
                    <div class="mb-3">
                        <div class="flex flex-wrap gap-2">
                            {#each editBucketTags as tagUrl}
                                <span class="inline-flex items-center gap-1 bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full dark:bg-blue-900 dark:text-blue-200">
                                    #{getTagNameByUrl(tagUrl)}
                                    <button 
                                        type="button"
                                        onclick={() => removeTag(tagUrl)}
                                        class="ml-1 text-blue-600 hover:text-blue-800 dark:text-blue-300 dark:hover:text-blue-100"
                                        disabled={savingBucket}
                                    >
                                        ×
                                    </button>
                                </span>
                            {/each}
                        </div>
                    </div>
                {/if}
                
                <!-- Available tags dropdown -->
                {#if !loadingTags && availableTags.length > 0}
                    <div class="mb-3">
                        <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                            Select from existing tags:
                        </label>
                        <div class="max-h-32 overflow-y-auto border border-gray-300 dark:border-gray-600 rounded-md p-2 bg-white dark:bg-gray-700">
                            {#each availableTags as tag}
                                <label class="flex items-center space-x-2 p-1 hover:bg-gray-50 dark:hover:bg-gray-600 rounded cursor-pointer">
                                    <button
                                        type="button"
                                        onclick={() => toggleTag(tag.url)}
                                        class={`relative inline-flex w-10 h-5 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${editBucketTags.includes(tag.url) ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'} ${savingBucket ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                                        disabled={savingBucket}
                                    >
                                        <span class={`inline-block w-3 h-3 transform transition-transform bg-white rounded-full shadow-sm ${editBucketTags.includes(tag.url) ? 'translate-x-6' : 'translate-x-1'}`}></span>
                                    </button>
                                    <span class="text-sm text-gray-700 dark:text-gray-300">
                                        {tag.tag_name}
                                        {#if tag.tag_description}
                                            <span class="text-xs text-gray-500 dark:text-gray-400">
                                                - {tag.tag_description}
                                            </span>
                                        {/if}
                                    </span>
                                </label>
                            {/each}
                        </div>
                    </div>
                {:else if loadingTags}
                    <div class="mb-3 text-sm text-gray-500 dark:text-gray-400">
                        Loading tags...
                    </div>
                {/if}
                
                <!-- Create new tag section -->
                <div class="mb-3">
                    {#if !showTagInput}
                        <button
                            type="button"
                            onclick={() => { showTagInput = true; tagError = ''; }}
                            class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 transition-colors"
                            disabled={savingBucket}
                        >
                            + Create new tag
                        </button>
                    {:else}
                        <div class="space-y-2">
                            <label class="block text-sm text-gray-600 dark:text-gray-400">
                                Create new tag:
                            </label>
                            <div class="flex gap-2">
                                <input
                                    type="text"
                                    bind:value={newTagName}
                                    placeholder="Tag name (letters, -, _, / only)"
                                    maxlength="20"
                                    class="flex-1 px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                                    disabled={creatingTag || savingBucket}
                                />
                                <button
                                    type="button"
                                    onclick={createNewTag}
                                    class="px-3 py-1 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    disabled={creatingTag || savingBucket || !newTagName.trim()}
                                >
                                    {#if creatingTag}
                                        Creating...
                                    {:else}
                                        Add
                                    {/if}
                                </button>
                                <button
                                    type="button"
                                    onclick={() => { showTagInput = false; newTagName = ''; tagError = ''; }}
                                    class="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 rounded-md transition-colors"
                                    disabled={creatingTag || savingBucket}
                                >
                                    Cancel
                                </button>
                            </div>
                            {#if tagError}
                                <div class="text-sm text-red-600 dark:text-red-400">
                                    {tagError}
                                </div>
                            {/if}
                        </div>
                    {/if}
                </div>
            </div>
            
            <!-- Visibility toggle -->
            <div class="mb-6">
                <label class="flex items-center space-x-3">
                    <button
                        type="button"
                        onclick={() => editBucketVisibility = !editBucketVisibility}
                        class={`relative inline-flex w-12 h-6 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${editBucketVisibility ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'} ${savingBucket ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                        disabled={savingBucket}
                    >
                        <span class={`inline-block w-4 h-4 transform transition-transform bg-white rounded-full shadow-md ${editBucketVisibility ? 'translate-x-7' : 'translate-x-1'}`}></span>
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
                    onclick={closeEditBucketDialog}
                    class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 rounded-md transition-colors"
                    disabled={savingBucket}
                >
                    Cancel
                </button>
                <button
                    type="button"
                    onclick={saveEditedBucket}
                    class="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={savingBucket || !editBucketName.trim()}
                >
                    {#if savingBucket}
                        <span class="flex items-center">
                            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Saving...
                        </span>
                    {:else}
                        Save
                    {/if}
                </button>
            </div>
        </div>
    </div>
{/if}
