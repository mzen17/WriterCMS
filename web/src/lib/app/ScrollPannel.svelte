<script lang="ts">
	import { onMount } from 'svelte';

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
	let nextLink: string | null = 'http://localhost:8000/api/buckets';
	let prevLink: string | null = null;
	let scrollContainer: HTMLDivElement;
	let isLoading = false;
	let startX = 0;
	let currentX = 0;
	let isDragging = false;
	let showDialog = false;
	let selectedBucket: Bucket | null = null;
	let isLoadingDetails = false;

	async function fetchBuckets(url: string) {
		if (!url || isLoading) return;
		
		isLoading = true;
		try {
			const response = await fetch(url, {credentials: 'include'});
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const data: BucketResponse = await response.json();
			
			bucketList = data.results;
			nextLink = data.next;
			prevLink = data.previous;
		} catch (error) {
			console.error('Error fetching buckets:', error);
		} finally {
			isLoading = false;
		}
	}

	async function fetchBucketDetails(bucket: Bucket) {
		isLoadingDetails = true;
		showDialog = true;
		selectedBucket = bucket; // Show basic info first
		
		try {
			const response = await fetch(bucket.url, {credentials: 'include'});
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

	function handleCardClick(bucket: Bucket) {
		if (!isDragging) { // Only open dialog if not dragging
			fetchBucketDetails(bucket);
		}
	}

	function closeDialog() {
		showDialog = false;
		selectedBucket = null;
	}

	function getBucketId(url: string): string {
		// Extract bucket ID from URL like "http://localhost:8000/api/buckets/2/"
		const parts = url.split('/');
		return parts[parts.length - 2] || parts[parts.length - 1];
	}

	function navigateToRead(bucketId: string) {
		window.location.href = `/readb/${bucketId}`;
	}

	function navigateToWrite(bucketId: string) {
		window.location.href = `/writeb/${bucketId}`;
	}

	function handleTouchStart(event: TouchEvent) {
		startX = event.touches[0].clientX;
		isDragging = true;
	}

	function handleTouchMove(event: TouchEvent) {
		if (!isDragging) return;
		currentX = event.touches[0].clientX;
	}

	function handleTouchEnd() {
		if (!isDragging) return;
		isDragging = false;
		
		const diffX = startX - currentX;
		const threshold = 50; // Minimum swipe distance
		
		if (Math.abs(diffX) > threshold) {
			if (diffX > 0 && nextLink) {
				// Swiped left (next page)
				fetchBuckets(nextLink);
			} else if (diffX < 0 && prevLink) {
				// Swiped right (previous page)
				fetchBuckets(prevLink);
			}
		}
	}

	function handleMouseDown(event: MouseEvent) {
		startX = event.clientX;
		isDragging = true;
		event.preventDefault();
	}

	function handleMouseMove(event: MouseEvent) {
		if (!isDragging) return;
		currentX = event.clientX;
	}

	function handleMouseUp() {
		if (!isDragging) return;
		isDragging = false;
		
		const diffX = startX - currentX;
		const threshold = 50;
		
		if (Math.abs(diffX) > threshold) {
			if (diffX > 0 && nextLink) {
				fetchBuckets(nextLink);
			} else if (diffX < 0 && prevLink) {
				fetchBuckets(prevLink);
			}
		}
	}

	function handleWheel(event: WheelEvent) {
		if (Math.abs(event.deltaX) > Math.abs(event.deltaY)) {
			event.preventDefault();
			if (event.deltaX > 0 && nextLink) {
				fetchBuckets(nextLink);
			} else if (event.deltaX < 0 && prevLink) {
				fetchBuckets(prevLink);
			}
		}
	}

	onMount(() => {
		fetchBuckets(nextLink!);
	});
</script>

<div 
	class="w-full h-screen overflow-hidden relative cursor-grab select-none active:cursor-grabbing"
	bind:this={scrollContainer}
	on:touchstart={handleTouchStart}
	on:touchmove={handleTouchMove}
	on:touchend={handleTouchEnd}
	on:mousemove={handleMouseMove}
	on:wheel={handleWheel}
	role="region"
>
	{#if isLoading}
		<div class="flex justify-center items-center h-full text-xl text-gray-600 dark:text-gray-300">Loading buckets...</div>
	{:else if bucketList.length > 0}
		<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 p-4 h-full overflow-y-auto">
			{#each bucketList as bucket (bucket.url)}
				<div 
					class="rounded-xl overflow-hidden shadow-lg dark:shadow-gray-800 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:hover:shadow-gray-700 flex flex-col h-64 cursor-pointer"
					style="background-color: {bucket.background}"
					on:click={() => handleCardClick(bucket)}
					role="button"
					tabindex="0"
					on:keydown={(e) => e.key === 'Enter' && handleCardClick(bucket)}
				>
					<div class="flex-1 overflow-hidden">
						<img 
							src={bucket.banner} 
							alt={bucket.name} 
							class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" 
						/>
					</div>
					<div class="p-3 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm">
						<h3 class="text-sm font-semibold text-gray-800 dark:text-gray-200 text-center mb-1 line-clamp-1">{bucket.name}</h3>
						<p class="text-xs text-gray-600 dark:text-gray-400 text-center leading-tight line-clamp-2">{bucket.description}</p>
					</div>
				</div>
			{/each}
		</div>
    	{:else}
		<div class="flex justify-center items-center h-full text-xl text-gray-400 dark:text-gray-500">No buckets found</div>
	{/if}
</div>

<!-- Dialog Modal -->
{#if showDialog && selectedBucket}
	<div class="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50 p-4" on:click={closeDialog} >
		<div 
			class="bg-white dark:bg-gray-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
			on:click|stopPropagation
		>
			<!-- Header with banner -->
			<div class="relative h-48 overflow-hidden rounded-t-2xl" style="background-color: {selectedBucket.background}">
				<img 
					src={selectedBucket.banner} 
					alt={selectedBucket.name} 
					class="w-full h-full object-cover"
				/>
				<button 
					class="absolute top-4 right-4 bg-black/50 hover:bg-black/70 dark:bg-white/20 dark:hover:bg-white/30 text-white rounded-full w-8 h-8 flex items-center justify-center transition-colors"
					on:click={closeDialog}
				>
					✕
				</button>
			</div>
			
			<!-- Content -->
			<div class="p-6">
				{#if isLoadingDetails}
					<div class="flex items-center justify-center py-8">
						<div class="text-lg text-gray-600 dark:text-gray-400">Loading details...</div>
					</div>
				{:else}
					<!-- Title and Action Buttons -->
					<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
						<h2 class="text-2xl font-bold text-gray-800 dark:text-gray-200">{selectedBucket.name}</h2>
						<div class="flex gap-3">
							<!-- Read Button -->
							<button
								class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium"
								on:click={() => navigateToRead(getBucketId(selectedBucket.url))}
							>
								<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
									<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
								</svg>
								Read
							</button>
							
							<!-- Write Button (only if can_edit is true) -->
							{#if selectedBucket.can_edit}
								<button
									class="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors text-sm font-medium"
									on:click={() => navigateToWrite(getBucketId(selectedBucket.url))}
								>
									<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
										<path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>
										<path d="m15 5 4 4"/>
									</svg>
									Write
								</button>
							{/if}
						</div>
					</div>
					
					<!-- Description -->
					<p class="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">{selectedBucket.description}</p>
					
					<!-- Details Grid -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<!-- User Owner -->
						<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
							<h3 class="font-semibold text-gray-700 dark:text-gray-300 mb-2">User Owner</h3>
							<p class="text-gray-600 dark:text-gray-400 text-sm">{selectedBucket.user_owner_name || 'Unknown User'}</p>
						</div>
						
						<!-- Bucket Owner -->
						{#if selectedBucket.bucket_owner}
							<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
								<h3 class="font-semibold text-gray-700 dark:text-gray-300 mb-2">Bucket Owner</h3>
								<p class="text-gray-600 dark:text-gray-400 text-sm">{selectedBucket.bucket_owner_name || 'Unknown Bucket'}</p>
							</div>
						{/if}
						
						<!-- Tags -->
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
					
					<!-- URL -->
					<div class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
						<h3 class="font-semibold text-gray-700 dark:text-gray-300 mb-2">API URL</h3>
						<code class="bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 px-3 py-2 rounded text-sm block break-all">
							{selectedBucket.url}
						</code>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
