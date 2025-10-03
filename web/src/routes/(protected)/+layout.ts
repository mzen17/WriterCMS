import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ url }) => {
    // This will be handled client-side by the auth store
    // Server-side route protection can be added here if needed
    return {};
};
