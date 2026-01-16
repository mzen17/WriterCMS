<script lang="ts">
  import { onMount } from 'svelte';
  import { authenticatedFetch, authenticatedPost, user as authUser, loading as authLoading, get_backend_url } from '$lib/auth';
  import { goto } from '$app/navigation';

  interface Asset {
    url: string;
    file_name: string;
    size: number;
    owner: string;
    can_share: boolean;
  }

  let assets: Asset[] = [];
  let error: string | null = null;
  let loading: boolean = true;

  // Create asset form state
  let showCreateForm: boolean = false;
  let newAssetCanShare: boolean = false;
  let creating: boolean = false;
  let uploadFile: File | null = null;

  // Edit dialog state
  let selectedAsset: Asset | null = null;
  let showEditDialog: boolean = false;
  let editCanShare: boolean = false;
  let previewUrl: string | null = null;
  let loadingPreview: boolean = false;
  let updating: boolean = false;
  let deleting: boolean = false;

  onMount(async () => {
    // Wait for Firebase auth to initialize
    if ($authLoading) {
      const unsubscribe = authLoading.subscribe((isLoading) => {
        if (!isLoading) {
          unsubscribe();
          loadAssets();
        }
      });
    } else {
      await loadAssets();
    }
  });

  async function loadAssets() {
    // Check if user is authenticated
    if (!$authUser) {
      goto('/login');
      return;
    }

    try {
      const response = await authenticatedFetch(`/api/assets/?owner=me`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // Filter to show only assets owned by current user
      assets = data.results || data;
    } catch (err: any) {
      error = err.message || 'Failed to load assets';
      console.error('Error loading assets:', err);
    } finally {
      loading = false;
    }
  }

  function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  function getAssetApiUrl(fileName: string): string {
    return `${get_backend_url()}/api/file/${fileName}/`;
  }

  function handleFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      uploadFile = input.files[0];
    }
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
      // Reset file input
      const fileInput = document.getElementById('file_upload') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      await loadAssets();
    } catch (err: any) {
      error = err.message || 'Failed to create asset';
      console.error('Error creating asset:', err);
    } finally {
      creating = false;
    }
  }

  async function openEditDialog(asset: Asset) {
    selectedAsset = asset;
    editCanShare = asset.can_share;
    showEditDialog = true;
    previewUrl = getAssetApiUrl(asset.file_name);
    console.log(previewUrl)
    loadingPreview = false;
  }

  function closeEditDialog() {
    showEditDialog = false;
    selectedAsset = null;
    previewUrl = null;
    editCanShare = false;
  }

  async function updateAsset() {
    if (!selectedAsset) return;

    updating = true;
    error = null;

    try {
      const response = await authenticatedPost(
        `/api/assets/${selectedAsset.file_name}/`,
        { can_share: editCanShare },
        'PATCH'
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      // Update local state
      assets = assets.map(a => 
        a.file_name === selectedAsset!.file_name 
          ? { ...a, can_share: editCanShare } 
          : a
      );
      closeEditDialog();
    } catch (err: any) {
      error = err.message || 'Failed to update asset';
      console.error('Error updating asset:', err);
    } finally {
      updating = false;
    }
  }

  async function deleteAsset() {
    if (!selectedAsset) return;
    
    if (!confirm('Are you sure you want to delete this asset? This action cannot be undone.')) {
      return;
    }

    deleting = true;
    error = null;

    try {
      const response = await authenticatedFetch(`/api/assets/${selectedAsset.file_name}/`, {
        method: 'DELETE'
      });

      if (!response.ok && response.status !== 204) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      // Remove from local state
      assets = assets.filter(a => a.file_name !== selectedAsset!.file_name);
      closeEditDialog();
    } catch (err: any) {
      error = err.message || 'Failed to delete asset';
      console.error('Error deleting asset:', err);
    } finally {
      deleting = false;
    }
  }

  function isImageFile(fileName: string): boolean {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'];
    return imageExtensions.some(ext => fileName.toLowerCase().endsWith(ext));
  }
</script>

<svelte:head>
  <title>My Assets</title>
</svelte:head>

<div class="flex flex-col bg-white dark:bg-gray-900 rounded-lg shadow-md w-full max-w-4xl">
  <div class="flex justify-between items-center px-4 my-4">
    <h1 class="text-2xl font-bold text-gray-800 dark:text-white">My Assets</h1>
    <button
      on:click={() => showCreateForm = !showCreateForm}
      class={"px-4 py-2 text-white font-medium rounded-md shadow-sm focus:outline-none " + (showCreateForm ? "bg-red-600 hover:bg-red-700": "bg-green-600 hover:bg-green-700")}
    >
      {showCreateForm ? 'Cancel' : 'Create Asset'}
    </button>
  </div>

  {#if showCreateForm}
    <div class="bg-gray-50 dark:bg-gray-800 p-4 mx-4 mb-4 rounded-md border border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-4">Upload New Asset</h3>
      <div class="space-y-4">
        <div>
          <label for="file_upload" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Select File</label>
          <input
            type="file"
            id="file_upload"
            on:change={handleFileSelect}
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 dark:file:bg-green-900 dark:file:text-green-300"
          />
          {#if uploadFile}
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Selected: {uploadFile.name} ({formatFileSize(uploadFile.size)})</p>
          {/if}
        </div>
        <div class="flex items-center">
          <input
            type="checkbox"
            id="can_share"
            bind:checked={newAssetCanShare}
            class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded dark:border-gray-600"
          />
          <label for="can_share" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">Can Share</label>
        </div>
        <button
          on:click={createAsset}
          disabled={creating || !uploadFile}
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 dark:bg-green-500 dark:hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {creating ? 'Uploading...' : 'Upload Asset'}
        </button>
      </div>
    </div>
  {/if}

  {#if loading}
    <p class="text-center text-gray-600 dark:text-gray-300 p-4">Loading assets...</p>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4 mx-4" role="alert">
      <strong class="font-bold">Error!</strong>
      <span class="block sm:inline"> {error}</span>
    </div>
  {:else if assets.length === 0}
    <p class="text-center text-gray-600 dark:text-gray-300 p-4">No assets found.</p>
  {:else}
    <div class="overflow-x-auto p-4">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Asset URL
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              File Size
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Can Share
            </th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          {#each assets as asset}
            <tr 
              class="hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
              on:click={() => openEditDialog(asset)}
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-indigo-600 dark:text-indigo-400 truncate block max-w-xs">
                  {asset.file_name}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {formatFileSize(asset.size)}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {#if asset.can_share}
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                    Yes
                  </span>
                {:else}
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100">
                    No
                  </span>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<!-- Edit Dialog Modal -->
{#if showEditDialog && selectedAsset}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={closeEditDialog}>
    <div 
      class="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
      on:click|stopPropagation
    >
      <div class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-800 dark:text-white">Edit Asset</h2>
          <button 
            on:click={closeEditDialog}
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- File Preview -->
        <div class="mb-6">
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Preview</h3>
          <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-800 min-h-[200px] flex items-center justify-center">
            {#if loadingPreview}
              <p class="text-gray-500 dark:text-gray-400">Loading preview...</p>
            {:else if previewUrl}
              {#if isImageFile(selectedAsset.file_name)}
                <img 
                  src={previewUrl} 
                  alt={selectedAsset.file_name}
                  class="max-w-full max-h-[300px] object-contain rounded"
                />
              {:else}
                <div class="text-center">
                  <svg class="w-16 h-16 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">File preview not available</p>
                  <a 
                    href={previewUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    class="mt-2 inline-block text-indigo-600 dark:text-indigo-400 hover:underline text-sm"
                  >
                    Open file in new tab
                  </a>
                </div>
              {/if}
            {:else}
              <p class="text-gray-500 dark:text-gray-400">Preview not available</p>
            {/if}
          </div>
        </div>

        <!-- File Info -->
        <div class="mb-6 space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-500 dark:text-gray-400">File Name:</span>
            <span class="text-gray-900 dark:text-white font-mono">{selectedAsset.file_name}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500 dark:text-gray-400">Size:</span>
            <span class="text-gray-900 dark:text-white">{formatFileSize(selectedAsset.size)}</span>
          </div>
          {#if previewUrl}
            <div class="text-sm">
              <span class="text-gray-500 dark:text-gray-400">Direct URL:</span>
              <input 
                type="text" 
                readonly 
                value={previewUrl}
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 dark:bg-gray-700 dark:border-gray-600 dark:text-white text-xs font-mono"
                on:click={(e) => e.currentTarget.select()}
              />
            </div>
          {/if}
        </div>

        <!-- Can Share Toggle -->
        <div class="mb-6">
          <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div>
              <label for="edit_can_share" class="text-sm font-medium text-gray-700 dark:text-gray-300">Can Share</label>
              <p class="text-xs text-gray-500 dark:text-gray-400">Allow others to view this asset</p>
            </div>
            <input
              type="checkbox"
              id="edit_can_share"
              bind:checked={editCanShare}
              class="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded dark:border-gray-600"
            />
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3">
          <button
            on:click={updateAsset}
            disabled={updating}
            class="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {updating ? 'Saving...' : 'Save Changes'}
          </button>
          <button
            on:click={deleteAsset}
            disabled={deleting}
            class="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {deleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
