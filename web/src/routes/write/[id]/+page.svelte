<script lang="ts">

    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { authenticatedFetch, authenticatedPost } from '$lib/auth';

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
    let originalContent: string = $state(''); // Store original content for diff calculation
    let isDirty: boolean = $state(false);
    let editor: any = null;
    
    // Get the ID from the route parameters
    let pageID = $derived($page.params.id);
    
    // Reactive effect to update save status in TinyMCE toolbar
    $effect(() => {
        if ((window as any).updateSaveStatus) {
            (window as any).updateSaveStatus();
        }
    });
    
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
                    originalContent = decodedContent; // Store original content
                    setTimeout(() => {
                        initializeTinyMCE(decodedContent);
                        // Enable spell check automatically after reinitializing
                        setTimeout(() => {
                            enableSpellCheck();
                        }, 500);
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
            const response = await authenticatedFetch(`/api/pages/${id}/`);
            
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
            console.log(pageData.bucket_bg)
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
                originalContent = decodedContent; // Store original content
                // Add a small delay to ensure DOM is ready
                setTimeout(() => {
                    initializeTinyMCE(decodedContent);
                    // Enable spell check automatically after TinyMCE is initialized
                    setTimeout(() => {
                        enableSpellCheck();
                    }, 500);
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
            height: window.innerWidth < 768 ? 650 : 750,
            width: '100%',
            branding: false,
            promotion: false,
            skin: window.matchMedia("(prefers-color-scheme: dark)").matches ? "oxide-dark" : "",
            content_css: window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "",
            content_style: "@import url('https://fonts.googleapis.com/css?family=Open+Sans&display=swap');p { margin: 0; }",
            mobile: {
                theme: 'silver',
                menubar: true,
                plugins: 'autosave lists autolink',
                toolbar: 'savestatus | undo redo | bold italic | bullist numlist'
            },
            toolbar_mode: 'sliding',
            menu: {
                file: { title: 'File', items: 'save delete back' },
                edit: { title: 'Edit', items: 'undo redo | cut copy paste pastetext | selectall | searchreplace' },
                view: { title: 'View', items: 'code revisionhistory | visualaid visualchars visualblocks | spellchecker | preview fullscreen | showcomments' },
                insert: { title: 'Insert', items: 'image link media addcomment pageembed codesample inserttable | math | charmap emoticons hr | pagebreak nonbreaking anchor tableofcontents | insertdatetime' },
                format: { title: 'Format', items: 'bold italic underline strikethrough superscript subscript codeformat | styles blocks fontfamily fontsize align lineheight | forecolor backcolor | language | removeformat' },
                tools: { title: 'Tools', items: 'revisions | add-word | image wordcount | code ' },
                table: { title: 'Table', items: 'inserttable | cell row column | advtablesort | tableprops deletetable' },
                help: { title: 'Help', items: 'help' }
            },
            toolbar: "savestatus | undo redo | blocks fontfamily fontsize | bold italic underline forecolor backcolor | link image | checklist bullist numlist",
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
            plugins: 'wordcount code image revisions',
            setup: function (editorInstance: any) {
                editor = editorInstance;

                // Add save status indicator to toolbar
                editor.ui.registry.addButton('savestatus', {
                    text: 'All changes saved',
                    onAction: function () {
                        // Do nothing - this is just a status indicator
                    },
                    onSetup: function (api: any) {
                        // Update the button text based on isDirty state
                        const updateStatus = () => {
                            if (isDirty) {
                                api.setText('You have unsaved changes');
                                api.setEnabled(false);
                            } else {
                                api.setText('All changes saved');
                                api.setEnabled(false);
                            }
                        };

                        // Initial update
                        updateStatus();

                        // We'll need to manually update this when isDirty changes
                        // Store reference to update function for later use
                        (window as any).updateSaveStatus = updateStatus;

                        return function () {
                            // Cleanup
                            delete (window as any).updateSaveStatus;
                        };
                    }
                });

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

                editor.ui.registry.addMenuItem('revisions', {
                    text: 'Revisions',
                    onAction: () => openRevisionsDialog()
                });

                // Add spell checker menu item
                editor.ui.registry.addMenuItem('enable-spell-check', {
                    text: 'Enable Spell Check',
                    onAction: () => enableSpellCheck()
                });

                editor.on('init', function () {
                    console.log('TinyMCE initialized successfully');
                    editor.setContent(content);
                    originalContent = content; // Store original content for diff calculation
                    // Set initial dirty state to false after content is loaded
                    isDirty = false;
                    
                    // Update save status in toolbar after initialization
                    setTimeout(() => {
                        if ((window as any).updateSaveStatus) {
                            (window as any).updateSaveStatus();
                        }
                    }, 100);
                    
                    // Enable spell check automatically after editor is fully initialized
                    setTimeout(() => {
                        enableSpellCheck();
                    }, 100);
                });

                // Use a debounced change handler to prevent excessive dirty state updates
                let changeTimeout: any;
                editor.on('change keyup', function () {
                    clearTimeout(changeTimeout);
                    changeTimeout = setTimeout(() => {
                        isDirty = true;
                        // Update save status in toolbar
                        if ((window as any).updateSaveStatus) {
                            (window as any).updateSaveStatus();
                        }
                    }, 250);
                });
            }
        });

        // Register the revisions plugin
        if (!window.tinymce.PluginManager.get('revisions')) {
            window.tinymce.PluginManager.add('revisions', (editorInstance: any) => {
                return {
                    getMetadata: () => ({
                        name: 'Page Revisions',
                        url: 'https://mzen.dev'
                    })
                };
            });
        }

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

    // Revisions dialog functionality
    let selectedRevision: any = null;
    
    async function fetchRevisions() {
        if (!pageData?.slug) return [];
        
        try {
            const response = await authenticatedFetch(`/api/pages/${pageData.slug}/revisions/list/`);
            
            if (response.ok) {
                const revisions = await response.json();
                return revisions.sort((a: any, b: any) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
            } else {
                console.error('Failed to fetch revisions:', response.status);
                return [];
            }
        } catch (error) {
            console.error('Error fetching revisions:', error);
            return [];
        }
    }
    
    function formatDate(timestamp: string) {
        const date = new Date(timestamp);
        return date.toISOString().split('T')[0]; // Returns YYYY-MM-DD format
    }
    
    function decodeRevisionContent(content: string) {
        return content.replace(/\[\@\@\#%\]/g, '"');
    }
    
    async function openRevisionsDialog() {
        const revisions = await fetchRevisions();
        
        if (revisions.length === 0) {
            editor.windowManager.alert('No revisions found for this page.');
            return;
        }
        
        const dialogConfig = {
            title: 'Page Revisions',
            size: 'large',
            body: {
                type: 'panel',
                items: [
                    {
                        type: 'htmlpanel',
                        html: `
                            <style>
                                .revisions-container {
                                    display: flex; 
                                    height: 500px; 
                                    gap: 20px;
                                    position: relative;
                                }
                                
                                @media (max-width: 900px) {
                                    .revisions-container {
                                        flex-direction: column;
                                        height: 650px;
                                        gap: 15px;
                                    }
                                    
                                    .revisions-sidebar {
                                        flex: 0 0 200px !important;
                                        max-height: 200px !important;
                                        border-right: none !important;
                                        border-bottom: 1px solid #ddd !important;
                                        padding-right: 0 !important;
                                        padding-bottom: 15px !important;
                                    }
                                    
                                    .revisions-list {
                                        max-height: 160px !important;
                                    }
                                    
                                    .revisions-preview-container {
                                        flex: 1 !important;
                                        padding-left: 0 !important;
                                        padding-top: 15px !important;
                                    }
                                    
                                    .revisions-preview {
                                        height: 410px !important;
                                    }
                                }
                                
                                .revisions-sidebar {
                                    flex: 0 0 240px; 
                                    border-right: 1px solid #e5e5e5; 
                                    padding-right: 20px;
                                }
                                
                                .revisions-list {
                                    max-height: 430px; 
                                    overflow-y: auto;
                                    overflow-x: hidden;
                                    scrollbar-width: thin;
                                    scrollbar-color: #c1c1c1 #f8f9fa;
                                    padding-right: 8px;
                                }
                                
                                .revisions-list::-webkit-scrollbar {
                                    width: 6px;
                                }
                                
                                .revisions-list::-webkit-scrollbar-track {
                                    background: #f8f9fa;
                                    border-radius: 6px;
                                }
                                
                                .revisions-list::-webkit-scrollbar-thumb {
                                    background: #c1c1c1;
                                    border-radius: 6px;
                                }
                                
                                .revisions-list::-webkit-scrollbar-thumb:hover {
                                    background: #a1a1a1;
                                }
                                
                                .revision-item {
                                    padding: 16px 18px; 
                                    cursor: pointer; 
                                    font-size: 14px;
                                    transition: all 0.2s ease;
                                    border-radius: 12px;
                                    margin: 0 0 8px 0;
                                    background-color: #f9fafb;
                                    border: 1px solid transparent;
                                    user-select: none;
                                    position: relative;
                                }
                                
                                .revision-item:hover {
                                    background-color: #f3f4f6 !important;
                                    border-color: #e5e7eb;
                                    transform: translateY(-1px);
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                                }
                                
                                .revision-item.selected {
                                    background-color: #1976d2 !important;
                                    color: white !important;
                                    border-color: #1565c0;
                                    box-shadow: 0 4px 8px rgba(25,118,210,0.3);
                                    transform: translateY(-1px);
                                }
                                
                                .revision-item.selected .revision-date {
                                    color: #bbdefb !important;
                                }
                                
                                .revision-number {
                                    font-weight: normal;
                                    color: #6b7280;
                                    font-size: 14px;
                                    margin-bottom: 4px;
                                }
                                
                                .revision-item.selected .revision-number {
                                    color: #e3f2fd;
                                }
                                
                                .revision-date {
                                    color: #9ca3af;
                                    font-size: 12px;
                                }
                                
                                .revisions-preview-container {
                                    flex: 1; 
                                    padding-left: 20px;
                                    display: flex;
                                    flex-direction: column;
                                }
                                
                                .revisions-preview {
                                    height: 430px; 
                                    overflow-y: auto; 
                                    overflow-x: hidden;
                                    border: 1px solid #e5e5e5; 
                                    padding: 20px; 
                                    background: white;
                                    border-radius: 8px;
                                    scrollbar-width: thin;
                                    scrollbar-color: #c1c1c1 #f8f9fa;
                                    flex: 1;
                                }
                                
                                .revisions-preview::-webkit-scrollbar {
                                    width: 6px;
                                }
                                
                                .revisions-preview::-webkit-scrollbar-track {
                                    background: #f8f9fa;
                                    border-radius: 6px;
                                }
                                
                                .revisions-preview::-webkit-scrollbar-thumb {
                                    background: #c1c1c1;
                                    border-radius: 6px;
                                }
                                
                                .revisions-preview::-webkit-scrollbar-thumb:hover {
                                    background: #a1a1a1;
                                }
                                
                                .section-title {
                                    margin: 0 0 16px 0; 
                                    font-size: 16px; 
                                    font-weight: 500; 
                                    color: white;
                                    background: transparent;
                                }
                                
                                .preview-title {
                                    margin: 0 0 20px 0; 
                                    font-size: 16px; 
                                    font-weight: 500; 
                                    color: white;
                                    background: transparent;
                                }
                                
                                .preview-placeholder {
                                    color: #9ca3af; 
                                    font-style: italic; 
                                    text-align: center; 
                                    padding: 60px 20px;
                                    font-size: 14px;
                                }
                                
                                /* Ensure the dialog doesn't move */
                                .tox-dialog {
                                    position: fixed !important;
                                    top: 50% !important;
                                    left: 50% !important;
                                    transform: translate(-50%, -50%) !important;
                                }
                                
                                .tox-dialog__content-js {
                                    overflow: hidden !important;
                                }
                                
                                .tox-dialog__body-content {
                                    overflow: hidden !important;
                                }
                            </style>
                            <div class="revisions-container">
                                <div class="revisions-sidebar">
                                    <h3 class="section-title">Revisions</h3>
                                    <div id="revisions-list" class="revisions-list">
                                        ${revisions.map((rev: any, index: number) => `
                                            <div class="revision-item" data-revision-id="${rev.id}" data-revision='${JSON.stringify(rev).replace(/'/g, '&#39;')}'>
                                                <div class="revision-number">Rev ${rev.revision_number}</div>
                                                <div class="revision-date">${formatDate(rev.timestamp)}</div>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                                <div class="revisions-preview-container">
                                    <h3 class="preview-title">Preview</h3>
                                    <div id="revision-preview" class="revisions-preview">
                                        <div class="preview-placeholder">Select a revision to preview</div>
                                    </div>
                                </div>
                            </div>
                        `
                    }
                ]
            },
            buttons: [
                {
                    type: 'cancel',
                    text: 'Close'
                },
                {
                    type: 'custom',
                    text: 'Restore',
                    name: 'restore',
                    primary: true
                }
            ],
            onAction: (api: any, details: any) => {
                if (details.name === 'restore') {
                    if (selectedRevision) {
                        const decodedContent = decodeRevisionContent(selectedRevision.diff);
                        editor.setContent(decodedContent);
                        isDirty = true;
                        if ((window as any).updateSaveStatus) {
                            (window as any).updateSaveStatus();
                        }
                        api.close();
                    }
                }
            },
            onCancel: () => {
                selectedRevision = null;
            }
        };
        
        const dialog = editor.windowManager.open(dialogConfig);
        
        // Add event listeners after dialog opens
        setTimeout(() => {
            const revisionItems = document.querySelectorAll('.revision-item');
            const previewDiv = document.getElementById('revision-preview');
            const dialogButtons = document.querySelectorAll('.tox-dialog__footer button');
            let restoreButton: HTMLButtonElement | null = null;
            
            // Find the restore button (it should be the primary button)
            dialogButtons.forEach((btn: any) => {
                if (btn.textContent?.includes('Restore') || btn.classList.contains('tox-button--primary')) {
                    restoreButton = btn as HTMLButtonElement;
                }
            });
            
            // Initially disable restore button
            if (restoreButton) {
                restoreButton.disabled = true;
                restoreButton.style.opacity = '0.5';
                restoreButton.style.cursor = 'not-allowed';
            }
            
            revisionItems.forEach((item) => {
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    
                    // Prevent any default behavior that might move the dialog
                    if (e.target) {
                        (e.target as HTMLElement).focus = () => {}; // Disable focus
                    }
                    
                    // Remove previous selection from all items
                    revisionItems.forEach(i => {
                        i.classList.remove('selected');
                    });
                    
                    // Add selection to clicked item
                    item.classList.add('selected');
                    
                    // Get revision data - fix JSON parsing
                    try {
                        const revisionDataAttr = (item as HTMLElement).getAttribute('data-revision');
                        if (revisionDataAttr) {
                            const revisionData = JSON.parse(revisionDataAttr.replace(/&#39;/g, "'"));
                            selectedRevision = revisionData;
                            
                            // Update preview with decoded content
                            if (previewDiv) {
                                const decodedContent = decodeRevisionContent(revisionData.diff);
                                previewDiv.innerHTML = decodedContent || '<div class="preview-placeholder">No content available</div>';
                            }
                            
                            // Enable restore button
                            if (restoreButton) {
                                restoreButton.disabled = false;
                                restoreButton.style.opacity = '1';
                                restoreButton.style.cursor = 'pointer';
                            }
                        }
                    } catch (error) {
                        console.error('Error parsing revision data:', error);
                        if (previewDiv) {
                            previewDiv.innerHTML = '<div class="preview-placeholder">Error loading revision</div>';
                        }
                    }
                }, { passive: false });
            });
        }, 200);
    }

    async function save() {
        if (isSaving || !editor || !pageData) {
            console.log('Save already in progress or missing data, skipping...');
            return;
        }

        isSaving = true;
        console.log('Starting save operation...');

        try {
            const currentContent = editor.getContent({ format: 'raw' });

            // First, update page metadata if it has changed
            const metadataUpdateData = {
                title: pageData.title?.trim() || '',
                public: pageData.public || false,
                porder: pageData.porder === null || pageData.porder === undefined || String(pageData.porder).trim() === '' ? -1 : pageData.porder,
                bucket: pageData.bucket
            };

            const metadataResponse = await authenticatedPost(`/api/pages/${pageID}/`, metadataUpdateData, 'PUT');

            if (!metadataResponse.ok) {
                const errorData = await metadataResponse.json().catch(() => ({}));
                console.error('Metadata update failed:', errorData);
                alert("Failed to update page metadata. Please try again.");
                return;
            }

            console.log('Metadata updated successfully');

            // Check if content has changed
            const encodedOriginalContent = originalContent.replace(/"/g, '[@@#%]');
            const encodedCurrentContent = currentContent.replace(/"/g, '[@@#%]');
            
            if (encodedOriginalContent !== encodedCurrentContent) {
                console.log('Content changed, creating revision...');
                
                // Create a revision for content changes
                const revisionData = {
                    content: encodedCurrentContent
                };

                const revisionResponse = await authenticatedPost(`/api/pages/${pageID}/revisions/`, revisionData);

                if (!revisionResponse.ok) {
                    const errorData = await revisionResponse.json().catch(() => ({}));
                    console.error('Revision creation failed:', errorData);
                    alert("Failed to save content changes. Please try again.");
                    return;
                }

                console.log('Revision created successfully');
                // Update original content for future comparisons
                originalContent = currentContent;
            }

            isDirty = false;
            window.removeEventListener('beforeunload', handleBeforeUnload);
            
            // Update save status in toolbar
            if ((window as any).updateSaveStatus) {
                (window as any).updateSaveStatus();
            }
            
            console.log('Save completed successfully');

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
            const response = await authenticatedFetch(`/api/pages/${pageID}/`,
                {
                    method: 'DELETE',
                    credentials: 'include'
                } 
            )

            // Check if response is ok first
            if (response.ok) {
                window.removeEventListener('beforeunload', handleBeforeUnload);
                goto(`/bucket/${pageData.bucket_slug}`);
            } else {
                // Try to parse error response if it exists
                let errorMessage = "Failed to delete page.";
                try {
                    const errorData = await response.json();
                    if (errorData.message) {
                        errorMessage = errorData.message;
                    }
                } catch (parseError) {
                    // If JSON parsing fails, use default message
                    console.log('No JSON error response available');
                }
                alert(errorMessage);
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

</script>

<svelte:head>
    <title>{pageData?.title || 'Edit Page'}</title>
</svelte:head>

{#if loading}
    <div class="min-h-screen flex justify-center items-center px-2">
        <p class="text-lg">Loading page editor...</p>
    </div>
{:else if error}
    <div class="min-h-screen flex justify-center items-center px-2">
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
    <!-- Add background styling based on bucket_bg -->
     
    <div class="min-h-screen">
        {#if pageData.bucket_bg}
            <div id="bg"
                class="fixed inset-0 w-full h-full bg-cover bg-center bg-no-repeat z-10"
                style="background-image: url('{pageData.bucket_bg}')"
            ></div>
        {/if}

        <div class="flex flex-col items-center max-w-6xl mx-auto px-2 sm:px-5 py-5 relative backdrop-blur-sm dark:bg-gray-900 bg-opacity-50 z-10">
            <div class="flex flex-col lg:flex-row items-center w-full max-w-4xl mb-5 gap-3 sm:gap-5">
                <div class="flex-1 w-full">
                    <input
                        type="text"
                        bind:value={pageData.title}
                        placeholder="Page title"
                        class="w-full h-10 text-lg px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white focus:border-transparent"
                        spellcheck="true"
                    />
                </div>
                <div class="flex flex-col sm:flex-row lg:flex-row gap-2 w-full lg:w-auto">
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
                            bind:checked={pageData.public}
                            class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                    </div>
                </div>
            </div>

            <div class="w-full max-w-4xl mb-5">
                <textarea id="pg_content" class="w-full"></textarea>
            </div>
        </div>
    </div>
{/if}
