
// Use an environment variable to set the API base URL so it can be easily switched later.
const BASE_URL = process.env.REACT_APP_API_URL || "http://json-server:3001";

/**
 * Fetch tree data from the API.
 * @param {string} path - The endpoint path (e.g., 'Rocket' or 'Rocket/Stage1').
 * @returns {Promise<Object>} - The data returned from the API.
 */
export const fetchTreeData = async (path = "") => {
  try {
    const trimmedPath = path.startsWith('/') ? path.slice(1) : path;
    let encodedPath = encodeURIComponent(trimmedPath);
    let response = await fetch(`${BASE_URL}/${encodedPath}`);
    let data;
    if (!response.ok) {
      // Try with parent path if current path does not work
      const parentPath = trimmedPath.substring(0, trimmedPath.lastIndexOf('/'));
      if (parentPath) {
        data = await fetchTreeData(parentPath);
      } else {
        throw new Error(`No data for query ${path}: ${response.statusText}`);
      }
    } else {
      data = await response.json();
    }
    return data;
  } catch (error) {
    return null;
  }
};
