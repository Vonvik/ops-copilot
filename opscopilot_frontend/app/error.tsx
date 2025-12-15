"use client";

export default function Error({ error }: { error: Error }) {
  return (
    <div className="m-6 border border-red-300 bg-red-50 text-red-700 rounded p-4">
      <div className="font-semibold mb-1">Error</div>
      <div className="text-sm whitespace-pre-wrap">{error.message}</div>
    </div>
  );
}
