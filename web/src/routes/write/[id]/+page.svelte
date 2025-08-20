<script lang="ts">

    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { getCSRFToken } from '$lib/csrf';

    // TypeScript declarations for TinyMCE
    declare global {
        interface Window {
            tinymce: any;
        }
    }

    // Reactive state variables for page data
    let pageData: any = $state(null);
    let loading: boolean = $state(true);
    let error: string = $state('');
    let isSaving: boolean = $state(false);
    let isDirty: boolean = $state(false);
    let editor: any = null;
    
    // Get the ID from the route parameters
    let pageID = $derived($page.params.id);
    
    // Reactive effect to handle route changes
    $effect(() => {
        if (pageID) {
            // Clean up existing editor first
            if (window.tinymce && editor) {
                window.tinymce.remove('#pg_content');
                editor = null;
            }
            
            // Fetch new page data and reinitialize
            fetchPageData(pageID).then(() => {
                if (pageData) {
                    const decodedContent = pageData.description?.replace(/\[\@\@\#%\]/g, '"') || '';
                    setTimeout(() => {
                        initializeTinyMCE(decodedContent);
                    }, 100);
                }
            });
        }
    });
    
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
            const response = await fetch(`http://localhost:8000/api/pages/${id}/`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
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
    }
    

    // TinyMCE configuration
    const TINYMCE_URL = 'http://lib.starlitex.com/tinymce/tinymce.min.js';

    // Add beforeunload handler function
    function handleBeforeUnload(event: BeforeUnloadEvent) {
        if (isDirty) {
            event.preventDefault();
            event.returnValue = '';
        }
    }

    onMount(async () => {
        // Clean up any existing TinyMCE instances first
        if (window.tinymce) {
            window.tinymce.remove('#pg_content');
        }

        // Load TinyMCE first
        await loadTinyMCE();
        
        // Then fetch page data
        if (pageID) {
            await fetchPageData(pageID);
            
            // Initialize TinyMCE after page data is loaded
            if (pageData) {
                const decodedContent = pageData.description?.replace(/\[\@\@\#%\]/g, '"') || '';
                // Add a small delay to ensure DOM is ready
                setTimeout(() => {
                    initializeTinyMCE(decodedContent);
                }, 100);
            }
        }

        // Add beforeunload listener
        window.addEventListener('beforeunload', handleBeforeUnload);

        // Cleanup function
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
            // Proper cleanup of TinyMCE
            if (window.tinymce) {
                window.tinymce.remove('#pg_content');
            }
            if (editor) {
                try {
                    editor.destroy();
                } catch (e) {
                    console.log('Editor already destroyed');
                }
                editor = null;
            }
        };
    });

    async function loadTinyMCE() {
        return new Promise((resolve, reject) => {
            if (window.tinymce) {
                resolve(window.tinymce);
                return;
            }

            const script = document.createElement('script');
            script.src = TINYMCE_URL;
            script.onload = () => resolve(window.tinymce);
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    function initializeTinyMCE(content: string) {
        // Ensure any existing instance is removed
        if (window.tinymce) {
            window.tinymce.remove('#pg_content');
        }

        // Check if the textarea element exists
        const textarea = document.getElementById('pg_content');
        if (!textarea) {
            console.error('TinyMCE textarea not found');
            return;
        }

        window.tinymce.init({
            selector: '#pg_content',
            height: 850,
            width: '100%',
            branding: false,
            promotion: false,
            skin: window.matchMedia("(prefers-color-scheme: dark)").matches ? "oxide-dark" : "",
            content_css: window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "",
            content_style: "@import url('https://fonts.googleapis.com/css?family=Open+Sans&display=swap');p { margin: 0; }",
            menu: {
                file: { title: 'File', items: 'save delete back' },
                edit: { title: 'Edit', items: 'undo redo | cut copy paste pastetext | selectall | searchreplace' },
                view: { title: 'View', items: 'code revisionhistory | visualaid visualchars visualblocks | spellchecker | preview fullscreen | showcomments' },
                insert: { title: 'Insert', items: 'image link media addcomment pageembed codesample inserttable | math | charmap emoticons hr | pagebreak nonbreaking anchor tableofcontents | insertdatetime' },
                format: { title: 'Format', items: 'bold italic underline strikethrough superscript subscript codeformat | styles blocks fontfamily fontsize align lineheight | forecolor backcolor | language | removeformat' },
                tools: { title: 'Tools', items: ' enable-spell-check disable-spell-check add-word | image wordcount | code ' },
                table: { title: 'Table', items: 'inserttable | cell row column | advtablesort | tableprops deletetable' },
                help: { title: 'Help', items: 'help' }
            },
            toolbar: "undo redo | blocks fontfamily fontsize | bold italic underline forecolor backcolor | link image | checklist bullist numlist",
            font_family_formats: "Andale Mono=andale mono,times;\
                                 Arial=arial,helvetica,sans-serif;\
                                 Arial Black=arial black,avant garde;\
                                 Book Antiqua=book antiqua,palatino;\
                                 Comic Sans MS=comic sans ms,sans-serif;\
                                 Courier New=courier new,courier;\
                                 Georgia=georgia,palatino;\
                                 Helvetica=helvetica;\
                                 Impact=impact,chicago;\
                                 Open Sans=open sans;\
                                 Symbol=symbol;\
                                 Tahoma=tahoma,arial,helvetica,sans-serif;\
                                 Terminal=terminal,monaco;\
                                 Times New Roman=times new roman,times;\
                                 Trebuchet MS=trebuchet ms,geneva;\
                                 Verdana=verdana,geneva;\
                                 Webdings=webdings;\
                                 Wingdings=wingdings,zapf dingbats",
            plugins: 'wordcount code spellchecker image',
            setup: function (editorInstance: any) {
                editor = editorInstance;

                // Add custom menu items
                editor.ui.registry.addMenuItem('save', {
                    text: 'Save',
                    onAction: () => save()
                });

                editor.ui.registry.addMenuItem('delete', {
                    text: 'Delete',
                    onAction: () => deletePage()
                });

                editor.ui.registry.addMenuItem('back', {
                    text: 'Back to Bucket',
                    onAction: () => goBack()
                });

                // Add spell checker menu items
                editor.ui.registry.addMenuItem('enable-spell-check', {
                    text: 'Enable Spell Check',
                    onAction: () => enableSpellCheck()
                });

                editor.ui.registry.addMenuItem('disable-spell-check', {
                    text: 'Disable Spell Check',
                    onAction: () => disableSpellCheck()
                });

                editor.on('init', function () {
                    console.log('TinyMCE initialized successfully');
                    editor.setContent(content);
                    // Set initial dirty state to false after content is loaded
                    isDirty = false;
                });

                // Use a debounced change handler to prevent excessive dirty state updates
                let changeTimeout: any;
                editor.on('change keyup', function () {
                    clearTimeout(changeTimeout);
                    changeTimeout = setTimeout(() => {
                        isDirty = true;
                    }, 250);
                });
            }
        });

        // Register the spellchecker plugin only once
        if (!window.tinymce.PluginManager.get('spellchecker')) {
            window.tinymce.PluginManager.add('spellchecker', (editorInstance: any, url: string) => {
                // Only register spellchecker items, not save/delete/back
                return {
                    getMetadata: () => ({
                        name: 'OSS Spellchecker for TinyMCE via browser.',
                        url: 'https://mzen.dev'
                    })
                };
            });
        }
    }

    async function save() {
        if (isSaving || !editor || !pageData) {
            console.log('Save already in progress or missing data, skipping...');
            return;
        }

        isSaving = true;
        console.log('Starting save operation...');

        try {
            const content = editor.getContent({ format: 'raw' });
            const encodedContent = content.replace(/"/g, '[@@#%]');

            const updateData = {
                title: pageData.title?.trim() || '',
                description: encodedContent,
                visibility: pageData.visibility || false,
                porder: pageData.porder === null || pageData.porder === undefined || String(pageData.porder).trim() === '' ? -1 : pageData.porder,
                bucket: pageData.bucket
            };

            console.log('Saving with data:', updateData);
            
            const csrfToken = await getCSRFToken();

            const response = await fetch(`http://localhost:8000/api/pages/${pageID}/`, {
                method: 'PUT',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken

                },
                body: JSON.stringify(updateData)
            });

            const result = await response.json();
            console.log('Save result:', result);

            if (result.resp === true || response.ok) {
                isDirty = false;
                window.removeEventListener('beforeunload', handleBeforeUnload);
                goto(`/bucket/${pageData.bucket_slug}`);
            } else {
                alert("An error occurred. Please save your content somewhere else and try again later.");
            }
        } catch (error) {
            console.error('Save error:', error);
            alert("An error occurred. Please save your content somewhere else and try again later.");
        } finally {
            // Add a small delay before allowing another save
            setTimeout(() => {
                isSaving = false;
                console.log('Save operation completed, ready for next save');
            }, 500);
        }
    }

    async function deletePage() {
        if (!pageData) return;
        
        const confirmDelete = confirm("Deleting this page is irreversible! Do you still want to delete?");

        if (!confirmDelete) return;

        try {
            const response = await fetch(`http://localhost:8000/api/pages/${pageID}/`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();

            if (result.resp === true || response.ok) {
                window.removeEventListener('beforeunload', handleBeforeUnload);
                goto(`/bucket/${pageData.bucket_slug}`);
            } else {
                alert("Failed to delete page.");
            }
        } catch (error) {
            console.error('Delete error:', error);
            alert("Failed to delete page.");
        }
    }

    function goBack() {
        if (pageData?.bucket_slug) {
            goto(`/bucket/${pageData.bucket_slug}`);
        } else {
            goto('/');
        }
    }

    function enableSpellCheck() {
        const iframe = document.getElementById('pg_content_ifr') as HTMLIFrameElement;
        if (iframe?.contentDocument) {
            const tinymceBox = iframe.contentDocument.getElementById('tinymce');
            if (tinymceBox) {
                (tinymceBox as any).spellcheck = true;
            }
        }
    }

    function disableSpellCheck() {
        const iframe = document.getElementById('pg_content_ifr') as HTMLIFrameElement;
        if (iframe?.contentDocument) {
            const tinymceBox = iframe.contentDocument.getElementById('tinymce');
            if (tinymceBox) {
                (tinymceBox as any).spellcheck = false;
            }
        }
    }

</script>

<svelte:head>
    <title>{pageData?.title || 'Edit Page'}</title>
</svelte:head>

{#if loading}
    <div class="flex justify-center items-center min-h-[50vh]">
        <p class="text-lg">Loading page editor...</p>
    </div>
{:else if error}
    <div class="flex justify-center items-center min-h-[50vh]">
        <div class="text-center">
            <p class="text-red-600 text-lg mb-4">Error: {error}</p>
            <button 
                onclick={() => fetchPageData(pageID)} 
                class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
            >
                Retry
            </button>
        </div>
    </div>
{:else if pageData}
    <div class="flex flex-col items-center max-w-6xl mx-auto p-5">
        <div class="flex flex-col lg:flex-row items-center w-full max-w-4xl mb-5 gap-5">
            <div class="flex-1 w-full">
                <input
                    type="text"
                    bind:value={pageData.title}
                    placeholder="Page title"
                    class="w-full h-10 text-lg px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white focus:border-transparent"
                    spellcheck="true"
                />
            </div>
            <div class="flex flex-col lg:flex-row gap-2 w-full lg:w-auto">
                <div class="flex items-center gap-3">
                    <label for="order" class="dark:text-white font-medium min-w-[50px]">Order</label>
                    <input
                        type="number"
                        id="order"
                        bind:value={pageData.porder}
                        class="w-20 px-2 dark:text-white py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>
                <div class="flex items-center gap-3">
                    <label for="vis" class="font-medium dark:text-white">Public</label>
                    <input
                        type="checkbox"
                        id="vis"
                        bind:checked={pageData.visibility}
                        class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                </div>
            </div>
        </div>

        <div class="w-full max-w-4xl mb-5">
            <textarea id="pg_content" class="w-full"></textarea>
        </div>

    </div>
{/if}

