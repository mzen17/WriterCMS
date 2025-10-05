<script lang="ts">
    import { authenticatedFetch, get_backend_url } from '$lib/auth';
	import { onMount, tick } from 'svelte';

	// Interfaces remain the same
	interface Bucket {
		url: string;
		name: string;
		user_owner: string;
		user_owner_name: string;
		bucket_owner: string;
		bucket_owner_name: string;
		visibility: boolean;
		tags: string[];
		tag_names: string[];
		description: string;
		banner: string;
		background: string;
		can_edit: boolean;
	}

	interface BucketResponse {
		count: number;
		next: string | null;
		previous: string | null;
		results: Bucket[];
	}

	let bucketList: Bucket[] = [];
	let nextLink: string | null = get_backend_url() + "/api/buckets";
	let gridContainer: HTMLDivElement;
	let isLoading = false;
	let isInitialLoading = true; // For the initial full-screen loader

	// Dialog state remains the same
	let showDialog = false;
	let selectedBucket: Bucket | null = null;
	let isLoadingDetails = false;

	/**
	 * Checks if the content fills the viewport and loads more if it doesn't.
	 */
	async function checkAndLoadMore() {
		await tick(); // Wait for DOM to update
		if (gridContainer && gridContainer.scrollHeight <= gridContainer.clientHeight && nextLink) {
			// If no scrollbar and there are more pages, fetch next page
			await fetchBuckets(nextLink);
		}
	}

	async function fetchBuckets(url: string | null) {
		if (!url || isLoading) return;

		isLoading = true;
		try {
			const response = await authenticatedFetch(url);
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const data: BucketResponse = await response.json();

			// Append new results instead of replacing the list
			bucketList = [...bucketList, ...data.results];
			nextLink = data.next;
		}  finally {
		   isLoading = false;
		    if (isInitialLoading) {
				isInitialLoading = false;
		   }
			await checkAndLoadMore();
		}
	}

	async function fetchBucketDetails(bucket: Bucket) {
		isLoadingDetails = true;
		showDialog = true;
		selectedBucket = bucket;

		try {
			const response = await authenticatedFetch(bucket.url);
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const detailedData: Bucket = await response.json();
			selectedBucket = detailedData;
		} catch (error) {
			console.error('Error fetching bucket details:', error);
		} finally {
			isLoadingDetails = false;
		}
	}

	// Simplified card click handler
	function handleCardClick(bucket: Bucket) {
		fetchBucketDetails(bucket);
	}

	function closeDialog() {
		showDialog = false;
		selectedBucket = null;
	}

	function getBucketId(url: string): string {
		const parts = url.split('/');
		return parts[parts.length - 2] || parts[parts.length - 1];
	}

	function navigateToRead(bucketId: string) {
		window.location.href = `/bucket/${bucketId}`;
	}

	// New scroll handler for infinite loading
	function handleScroll() {
		if (!gridContainer) return;
		const { scrollTop, scrollHeight, clientHeight } = gridContainer;
		const threshold = 300; // Trigger fetch when 300px from the bottom

		if (scrollTop + clientHeight >= scrollHeight - threshold) {
			fetchBuckets(nextLink);
		}
	}

	onMount(() => {
		fetchBuckets(nextLink);
	});
</script>

<div class="w-full h-screen overflow-hidden relative">
	{#if isInitialLoading}
		<div class="flex justify-center items-center h-full text-xl text-gray-600 dark:text-gray-300">
			Loading buckets...
		</div>
	{:else if bucketList.length > 0}
		<div
			class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 h-full overflow-y-auto"
			bind:this={gridContainer}
			on:scroll={handleScroll}
		>
			{#each bucketList as bucket (bucket.url)}
				<div
					class="rounded-xl overflow-hidden my-4 shadow-lg dark:shadow-gray-800 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:hover:shadow-gray-700 flex flex-col h-64 md:h-96 cursor-pointer"
					style="background-color: {bucket.background}"
					on:click={() => handleCardClick(bucket)}
					role="button"
					tabindex="0"
					on:keydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							handleCardClick(bucket);
						}
					}}
				>
					<div class="flex-1 overflow-hidden">
						<img
							src={bucket.banner}
							alt={bucket.name}
							class="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
						/>
					</div>
					<div class="p-3 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm">
						<h3 class="text-sm font-semibold text-gray-800 dark:text-gray-200 text-center mb-1 line-clamp-1">
							{bucket.name}
						</h3>
						<p class="text-xs text-gray-600 dark:text-gray-400 text-center leading-tight line-clamp-2">
							{bucket.description}
						</p>
					</div>
				</div>
			{/each}

			{#if isLoading}
				<div class="col-span-full flex justify-center items-center p-4">
					<div class="text-lg text-gray-600 dark:text-gray-400">Loading more...</div>
				</div>
			{/if}
		</div>
	{:else}
		<div class="flex justify-center items-center h-full text-xl text-gray-400 dark:text-gray-500">
			No buckets found
		</div>
	{/if}
</div>

{#if showDialog && selectedBucket}
	<div
		class="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50 p-4"
		on:click={closeDialog}
		role="button"
		tabindex="0"
		on:keydown={(e) => {
			if (e.key === 'Escape') {
				e.preventDefault();
				closeDialog();
			}
		}}
	>
		<div
			class="bg-white dark:bg-gray-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
			on:click|stopPropagation
			on:keydown|stopPropagation
			role="dialog"
			aria-modal="true"
			tabindex="-1"
		>
			<div
				class="relative h-48 overflow-hidden rounded-t-2xl"
				style="background-color: {selectedBucket.background}"
			>
				<img src={selectedBucket.banner} alt={selectedBucket.name} class="w-full h-full object-cover" />
				<button
					class="absolute top-4 right-4 bg-black/50 hover:bg-black/70 dark:bg-white/20 dark:hover:bg-white/30 text-white rounded-full w-8 h-8 flex items-center justify-center transition-colors"
					on:click={closeDialog}
				>
					✕
				</button>
			</div>

			<div class="p-6">
				{#if isLoadingDetails}
					<div class="flex items-center justify-center py-4">
						<div class="text-lg text-gray-600 dark:text-gray-400">Loading details...</div>
					</div>
				{:else}
					<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
						<h2 class="text-2xl font-bold text-gray-800 dark:text-gray-200">
							{selectedBucket.name}
						</h2>
						<div class="flex gap-3">
							<button
								class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium"
								on:click={() => navigateToRead(getBucketId(selectedBucket!.url))}
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
								</svg>
								Read
							</button>

				
						</div>
					</div>

					<p class="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
						{selectedBucket.description}
					</p>

					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
							<h3 class="font-semibold text-gray-700 dark:text-gray-300 mb-2">User Owner</h3>
							<p class="text-gray-600 dark:text-gray-400 text-sm">
								{selectedBucket.user_owner_name || 'Unknown User'}
							</p>
						</div>

						{#if selectedBucket.bucket_owner}
							<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
								<h3 class="font-semibold text-gray-700 dark:text-gray-300 mb-2">Bucket Owner</h3>
								<p class="text-gray-600 dark:text-gray-400 text-sm">
									{selectedBucket.bucket_owner_name || 'Unknown Bucket'}
								</p>
							</div>
						{/if}

						{#if selectedBucket.tag_names && selectedBucket.tag_names.length > 0}
							<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
								<h3 class="font-semibold text-gray-700 dark:text-gray-300 mb-2">Tags</h3>
								<div class="flex flex-wrap gap-2">
									{#each selectedBucket.tag_names as tagName}
										<span class="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded-md text-sm">
											{tagName}
										</span>
									{/each}
								</div>
							</div>
						{/if}
					</div>

				{/if}
			</div>
		</div>
	</div>
{/if}