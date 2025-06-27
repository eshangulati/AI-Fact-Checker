// src/app/page.tsx
'use client';

import { useState } from 'react';

export default function HomePage() {
  const [url, setUrl] = useState<string>('');
  const [thumbnail, setThumbnail] = useState<string | null>(null);
  const [claims, setClaims] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!url) {
      setError('Please enter a YouTube URL');
      return;
    }

    setLoading(true);
    setError(null);
    setThumbnail(null);
    setClaims([]);

    try {
      // Fetch video metadata
      const infoRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/video-info`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url }),
        }
      );
      if (!infoRes.ok) throw new Error(`Error fetching video info: ${infoRes.status}`);
      const { thumbnail_url } = await infoRes.json();
      setThumbnail(thumbnail_url || null);

      // Fetch claims (and transcript if needed)
      const claimsRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/extract-claims`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url }),
        }
      );
      if (!claimsRes.ok) throw new Error(`Error fetching claims: ${claimsRes.status}`);
      const { claims: extracted } = await claimsRes.json();
      setClaims(Array.isArray(extracted) ? extracted : []);
    } catch (err) {
      console.error(err);
      setError('Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-4 bg-gray-50 flex items-center justify-center">
      <div className="w-full max-w-xl bg-white p-6 rounded-lg shadow">
        <h1 className="text-3xl font-bold mb-6 text-center text-black">YouTube Fact-Checker</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700">
              YouTube URL
            </label>
            <input
              id="url"
              type="url"
              placeholder="https://youtu.be/..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none text-black"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-black text-white rounded-md hover:bg-gray-800 disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Extract Claims'}
          </button>
        </form>
        {error && <p className="mt-4 text-center text-red-600">{error}</p>}
        {thumbnail && (
          <div className="mt-6 flex justify-center">
            <img
              src={thumbnail}
              alt="Video thumbnail"
              className="w-64 h-auto rounded-md"
            />
          </div>
        )}
        {claims.length > 0 && (
          <div className="mt-6">
            <h2 className="text-2xl font-semibold mb-2 text-black">Extracted Claims</h2>
            <ul className="space-y-2 list-disc list-inside text-gray-800">
              {claims.map((claim, idx) => (
                <li key={idx}>{claim}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </main>
  );
}
