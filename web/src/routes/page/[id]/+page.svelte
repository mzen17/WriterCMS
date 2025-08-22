<script lang="ts">

    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { authenticatedFetch, authenticatedPost } from '$lib/auth';
    

    // Reactive state variables for page data
    let pageData: any = $state(null);
    let loading: boolean = $state(true);
    let error: string = $state('');
    let backgroundImageLoaded: boolean = $state(false);
    let backgroundImageError: boolean = $state(false);
    
    // Get the ID from the route parameters
    let pageID = $derived($page.params.id);
    
    // Derived URLs for navigation
    let previousUrl = $derived(
        pageData?.before?.slug ? `/page/${pageData.before.slug}` : null
    );
    let nextUrl = $derived(
        pageData?.next?.slug ? `/page/${pageData.next.slug}` : null
    );
    let tableOfContentsUrl = $derived(
        pageData?.bucket_slug ? `/bucket/${pageData.bucket_slug}` : '/'
    );
    
    // Function to fetch page data
    async function fetchPageData(id: string) {
        loading = true;
        error = '';
        
        try {
            const response = await authenticatedFetch(`http://localhost:8000/api/pages/${id}/`);
            
            if (response.ok) {
                pageData = await response.json();
            } else {
                const errorData = await response.json().catch(() => ({}));
                error = `Failed to fetch page data: ${response.status} ${response.statusText}`;
                console.error(error, errorData);
            }
        } catch (err) {
            error = 'Network error while fetching page data';
            console.error(error, err);
        } finally {
            loading = false;
        }
        // Decode the description content
        const decodedContent = pageData.description?.replace(/\[\@\@\#%\]/g, '"') || '';
        pageData.description = decodedContent;
    }
    
    // Fetch data when component mounts or ID changes
    $effect(() => {
        if (pageID) {
            fetchPageData(pageID);
        }
    });
</script>

<svelte:head>
    {#if pageData}
        <title>{pageData.title}</title>
        <meta name="description" content={pageData.description} />
    {/if}
    <link href="https://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet">
</svelte:head>

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

<!-- Page content -->
{#if pageData && !loading}
    <div class="fixed inset-0 z-0" id="renderer">
        {#if pageData.bucket_bg}
            <div id="bg"
                class="w-full h-full bg-cover bg-center bg-fixed bg-no-repeat"
                style="background-image: url('{pageData.bucket_bg}')"
            ></div>
        {/if}
    </div>

    <main class="flex justify-center min-h-screen relative">        
        <article id="page_content" class="md:w-[600px] md:p-4 flex flex-col min-h-screen relative z-10 backdrop-blur-sm bg-white bg-opacity-90 dark:bg-gray-900 dark:bg-opacity-90 rounded-lg shadow-lg m-0.5 p-4">
            <header class="mb-1.5 mt-5">
                <div class="flex items-center gap-3 mb-1.5">
                    <h2 
                        id="pg_title"
                        class="text-2xl md:text-3xl font-normal mt-0 border-0 w-full dark:text-white"
                    >
                        {pageData.title}
                    </h2>
                    {#if pageData.can_edit}
                        <a 
                            href="/write/{pageData.slug}"
                            class="inline-flex items-center justify-center w-8 h-8 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors duration-200"
                            title="Edit page"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                            </svg>
                        </a>
                    {/if}
                </div>
                <div class="backfront mb-2.5">
                    {#if previousUrl}
                        <a href={previousUrl} title={pageData.before?.title} class="mr-5 text-blue-600 hover:text-blue-800">
                            Previous
                        </a>
                    {/if}
                    <a href={tableOfContentsUrl} class="mr-5 text-blue-600 hover:text-blue-800">Table of Content</a>
                    {#if nextUrl}
                        <a href={nextUrl} title={pageData.next?.title} class="text-blue-600 hover:text-blue-800">
                            Next
                        </a>
                    {/if}
                </div>
                <hr class="border-gray-300">
            </header>
            
            <div 
                id="pg_content" 
                class="pt-2.5 flex-grow min-h-vh"
            >
                <div class="text-gray-800 leading-relaxed dark:text-white">

                    {@html pageData.description}
                </div>
                
            </div>
            
            <hr class="border-gray-300">
            
            <!-- Bottom Navigation -->
            <div class="backfront mt-5">
                <div class="flex flex-wrap justify-between items-center gap-4">
                <div class="backfront">
                    {#if previousUrl}
                        <a href={previousUrl} title={pageData.before?.title} class="mr-5 text-blue-600 hover:text-blue-800">
                            Previous
                        </a>
                    {/if}
                    <a href={tableOfContentsUrl} class="mr-5 text-blue-600 hover:text-blue-800">Table of Content</a>
                    {#if nextUrl}
                        <a href={nextUrl} title={pageData.next?.title} class="text-blue-600 hover:text-blue-800">
                            Next
                        </a>
                    {/if}
                </div>
                <hr class="border-gray-300">

 
                </div>
            </div>
        </article>
        
    </main>
    
{/if}
