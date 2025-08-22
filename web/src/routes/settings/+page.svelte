<script lang="ts">
  import { onMount } from 'svelte';
  import { authenticatedFetch, user as authUser, loading as authLoading } from '$lib/auth';
  import { goto } from '$app/navigation';

  // Define the User interface based on your provided response structure
  interface User {
    url: string;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    pfp: string | null;
    bio: string;
    dictionary: string | null;
    theme: boolean;
  }

  let user: User = {
    url: '',
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    pfp: null,
    bio: '',
    dictionary: null,
    theme: false,
  };

  let error: string | null = null;
  let loading: boolean = true;
  let successMessage: string | null = null;

  onMount(async () => {
    // Wait for Firebase auth to initialize
    if ($authLoading) {
      const unsubscribe = authLoading.subscribe((isLoading) => {
        if (!isLoading) {
          unsubscribe();
          loadUserData();
        }
      });
    } else {
      await loadUserData();
    }
  });

  async function loadUserData() {
    // Check if user is authenticated
    if (!$authUser) {
      goto('/login');
      return;
    }

    try {
      const response = await authenticatedFetch('http://localhost:8000/api/users/me/');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.  status}`);
      }
      user = await response.json();
    } catch (err: any) {
      error = err.message || 'Failed to load user data';
      console.error('Error loading user data:', err);
    } finally {
      loading = false;
    }
  }

  async function handleSubmit() {
    error = null;
    successMessage = null;
    
    if (!$authUser) {
      error = 'You must be logged in to update your profile';
      return;
    }

    try {
      const response = await authenticatedFetch(user.url, {
        method: 'PUT',
        body: JSON.stringify(user),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      successMessage = 'Profile updated successfully!';
      // Redirect to homepage after successful update
      setTimeout(() => goto('/'), 1500);
    } catch (err: any) {
      error = err.message || 'Failed to update profile';
      console.error('Error updating profile:', err);
    }
  }

  function toggleTheme() {
    user.theme = !user.theme;
  }
</script>


<svelte:head>
    <title>Settings</title>
</svelte:head>

  <div class="flex flex-col bg-white dark:bg-gray-900 rounded-lg shadow-md w-2xl ">

    {#if loading}
      <p class="text-center text-gray-600 dark:text-gray-300">Loading profile data...</p>
    {:else if error}
      <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
        <strong class="font-bold">Error!</strong>
        <span class="block sm:inline"> {error}</span>
      </div>
    {:else if successMessage}
      <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
        <strong class="font-bold">Success!</strong>
        <span class="block sm:inline"> {successMessage}</span>
      </div>
    {/if}

    <form on:submit|preventDefault={handleSubmit} class="space-y-4">
            <h1 class="text-2xl flex font-bold my-4 text-center text-gray-800 dark:text-white">User Settings</h1>

      <!-- Firebase-managed identity fields (read-only) -->
      <div class="bg-gray-50 dark:bg-gray-800 p-4 rounded-md border">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Account Information (managed by Firebase)</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span class="block text-sm font-medium text-gray-500 dark:text-gray-400">Username</span>
            <div class="mt-1 text-sm text-gray-900 dark:text-white">{user.username}</div>
          </div>
          
          <div>
            <span class="block text-sm font-medium text-gray-500 dark:text-gray-400">Email</span>
            <div class="mt-1 text-sm text-gray-900 dark:text-white">{user.email}</div>
          </div>
        </div>
        
        <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
          To change your email or username, please update them in your Firebase authentication settings.
        </p>
      </div>

      <!-- Editable profile fields -->

      <div>
        <label for="first_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">First Name</label>
        <input
          type="text"
          id="first_name"
          bind:value={user.first_name}
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        />
      </div>

      <div>
        <label for="last_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Last Name</label>
        <input
          type="text"
          id="last_name"
          bind:value={user.last_name}
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        />
      </div>

      <div>
        <label for="pfp" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Profile Picture URL</label>
        <input
          type="text"
          id="pfp"
          bind:value={user.pfp}
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          placeholder="Enter image URL"
        />
      </div>

      <div>
        <label for="bio" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Bio</label>
        <textarea
          id="bio"
          bind:value={user.bio}
          rows="3"
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        ></textarea>
      </div>

      <div>
        <label for="dictionary" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Dictionary</label>
        <input
          type="text"
          id="dictionary"
          bind:value={user.dictionary}
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          placeholder="Enter dictionary value"
        />
      </div>

      <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Theme</span>
        <button
          type="button"
          on:click={toggleTheme}
          class="p-2 rounded-full bg-gray-200 dark:bg-gray-700 text-2xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors duration-200"
        >
          {#if user.theme}
            <span role="img" aria-label="Dark mode">🌙</span>
          {:else}
            <span role="img" aria-label="Light mode">☀️</span>
          {/if}
        </button>
      </div>

      <button
        type="submit"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-600"
      >
        Save Changes
      </button>
    </form>
  </div>