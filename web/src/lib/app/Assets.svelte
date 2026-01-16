<script lang="ts">
  import { authenticatedFetch, get_backend_url } from '$lib/auth';
  import { goto } from '$app/navigation';

  // Props
  export let value: string = '';
  export let placeholder: string = 'Enter URL or select an asset...';

  interface Asset {
    url: string;
    file_name: string;
    size: number;
    owner: string;
    can_share: boolean;
  }

  interface PaginatedResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: Asset[];
  }

  let showDialog = false;
  let assets: Asset[] = [];
  let loading = false;
  let error: string | null = null;
  
  // Pagination state
  let currentPage = 1;
  let totalCount = 0;
  let hasNext = false;
  let hasPrevious = false;
  const pageSize = 5;

  // Create asset form state
  let showCreateForm = false;
  let uploadFile: File | null = null;
  let newAssetCanShare = false;
  let creating = false;

  function getAssetUrl(fileName: string): string {
    return `${get_backend_url()}/api/file/${fileName}/`;
  }

  async function loadAssets(page: number = 1) {
    loading = true;
    error = null;

    try {
      const response = await authenticatedFetch(`/api/assets/?pageno=${page}&size=${pageSize}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: PaginatedResponse = await response.json();
      assets = data.results || [];
      totalCount = data.count || 0;
      hasNext = !!data.next;
      hasPrevious = !!data.previous;
      currentPage = page;
    } catch (err: any) {
      error = err.message || 'Failed to load assets';
      console.error('Error loading assets:', err);
    } finally {
      loading = false;
    }
  }

  function openDialog() {
    showDialog = true;
    showCreateForm = false;
    loadAssets(1);
  }

  function closeDialog() {
    showDialog = false;
    showCreateForm = false;
    error = null;
  }

  function selectAsset(asset: Asset) {
    value = getAssetUrl(asset.file_name);
    closeDialog();
  }

  function nextPage() {
    if (hasNext) {
      loadAssets(currentPage + 1);
    }
  }

  function prevPage() {
    if (hasPrevious) {
      loadAssets(currentPage - 1);
    }
  }

  function handleFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      uploadFile = input.files[0];
    }
  }

  function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  async function createAsset() {
    if (!uploadFile) {
      error = 'Please select a file to upload';
      return;
    }

    creating = true;
    error = null;

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('can_share', String(newAssetCanShare));

      const response = await authenticatedFetch('/api/assets/', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.file?.[0] || `HTTP error! status: ${response.status}`);
      }

      // Reset form and reload assets
      uploadFile = null;
      newAssetCanShare = false;
      showCreateForm = false;
      const fileInput = document.getElementById('asset_file_upload') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      await loadAssets(1);
    } catch (err: any) {
      error = err.message || 'Failed to create asset';
      console.error('Error creating asset:', err);
    } finally {
      creating = false;
    }
  }

  function goToManage() {
    goto('/assets');
  }

  function isImageFile(fileName: string): boolean {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'];
    return imageExtensions.some(ext => fileName.toLowerCase().endsWith(ext));
  }
</script>

<div class="flex gap-2">
  <input
    type="text"
    bind:value
    {placeholder}
    class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
  />
  <button
    type="button"
    on:click={openDialog}
    class="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-600"
    title="Select from assets"
  >
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
    </svg>
  </button>
</div>

<!-- Asset Selection Dialog -->
{#if showDialog}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={closeDialog}>
    <div 
      class="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden flex flex-col"
      on:click|stopPropagation
    >
      <!-- Header -->
      <div class="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-bold text-gray-800 dark:text-white">Select Asset</h2>
        <div class="flex gap-2">
          <button
            type="button"
            on:click={() => showCreateForm = !showCreateForm}
            class="px-3 py-1.5 text-sm font-medium rounded-md {showCreateForm ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'} text-white"
          >
            {showCreateForm ? 'Cancel' : 'Create'}
          </button>
          <button
            type="button"
            on:click={goToManage}
            class="px-3 py-1.5 text-sm font-medium rounded-md bg-gray-600 hover:bg-gray-700 text-white"
          >
            Manage
          </button>
          <button
            type="button"
            on:click={closeDialog}
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Create Form -->
      {#if showCreateForm}
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <div class="space-y-3">
            <div>
              <label for="asset_file_upload" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Select File</label>
              <input
                type="file"
                id="asset_file_upload"
                on:change={handleFileSelect}
                class="mt-1 block w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 dark:file:bg-green-900 dark:file:text-green-300"
              />
              {#if uploadFile}
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{uploadFile.name} ({formatFileSize(uploadFile.size)})</p>
              {/if}
            </div>
            <div class="flex items-center gap-4">
              <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                <input
                  type="checkbox"
                  bind:checked={newAssetCanShare}
                  class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                />
                Can Share
              </label>
              <button
                type="button"
                on:click={createAsset}
                disabled={creating || !uploadFile}
                class="px-4 py-1.5 text-sm font-medium rounded-md bg-green-600 hover:bg-green-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {creating ? 'Uploading...' : 'Upload'}
              </button>
            </div>
          </div>
        </div>
      {/if}

      <!-- Error Message -->
      {#if error}
        <div class="p-3 bg-red-100 border-b border-red-200 text-red-700 text-sm">
          {error}
        </div>
      {/if}

      <!-- Assets Grid -->
      <div class="flex-1 overflow-y-auto p-4">
        {#if loading}
          <div class="flex items-center justify-center h-40">
            <p class="text-gray-500 dark:text-gray-400">Loading assets...</p>
          </div>
        {:else if assets.length === 0}
          <div class="flex items-center justify-center h-40">
            <p class="text-gray-500 dark:text-gray-400">No assets found</p>
          </div>
        {:else}
          <div class="grid grid-cols-5 gap-3">
            {#each assets as asset}
              <button
                type="button"
                on:click={() => selectAsset(asset)}
                class="aspect-square rounded-lg border-2 border-gray-200 dark:border-gray-700 hover:border-indigo-500 dark:hover:border-indigo-400 overflow-hidden focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                title={asset.file_name}
              >
                {#if isImageFile(asset.file_name)}
                  <img
                    src={getAssetUrl(asset.file_name)}
                    alt={asset.file_name}
                    class="w-full h-full object-cover"
                  />
                {:else}
                  <div class="w-full h-full flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-800 p-2">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <span class="text-xs text-gray-500 dark:text-gray-400 truncate w-full text-center mt-1">
                      {asset.file_name}
                    </span>
                  </div>
                {/if}
              </button>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Pagination Footer -->
      <div class="flex justify-between items-center p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <button
          type="button"
          on:click={prevPage}
          disabled={!hasPrevious || loading}
          class="px-4 py-2 text-sm font-medium rounded-md bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ← Previous
        </button>
        <span class="text-sm text-gray-500 dark:text-gray-400">
          Page {currentPage} of {Math.ceil(totalCount / pageSize) || 1} ({totalCount} total)
        </span>
        <button
          type="button"
          on:click={nextPage}
          disabled={!hasNext || loading}
          class="px-4 py-2 text-sm font-medium rounded-md bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
{/if}
