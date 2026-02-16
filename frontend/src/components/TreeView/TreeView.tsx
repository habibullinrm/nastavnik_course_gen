'use client';
export default function TreeView({ trackData }: { trackData: Record<string, unknown> }) {
  return <div className="p-4 bg-gray-50 rounded"><p className="text-gray-500">TreeView — в разработке</p><pre className="text-xs mt-2 overflow-auto max-h-96">{JSON.stringify(trackData, null, 2)}</pre></div>;
}
