'use client';

import { useRef, useState } from 'react';
import Image from 'next/image';

import { postClientDataAction } from 'lib/utils/clientDataActions';

interface NicheType {
  id: number;
  title: string;
  tagline: string;
  thumbnail_url?: string;
}

export default function NicheThumbnailUploader({
  niche,
  setNiche,
}: {
  niche: NicheType;
  setNiche: React.Dispatch<React.SetStateAction<NicheType | null>>;
}) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);

      const formData = new FormData();
      formData.append('thumbnail', file);

      const response = await postClientDataAction<NicheType, FormData>(
        `v1/admin/niches/${niche.id}/upload-thumbnail/`,
        formData,
      );

      setNiche((prev) =>
        prev ? { ...prev, thumbnail_url: response.thumbnail_url || prev.thumbnail_url } : prev,
      );
    } catch (error) {
      console.error('Thumbnail upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-3">
      {/* Thumbnail Preview */}
      {niche.thumbnail_url ? (
        <Image
          src={niche.thumbnail_url}
          alt={niche.title}
          width={200}
          height={120}
          className="rounded-lg object-cover"
        />
      ) : (
        <div className="flex h-[120px] w-[200px] items-center justify-center rounded-lg border text-gray-400">
          No Thumbnail
        </div>
      )}

      {/* Hidden File Input */}
      <input
        type="file"
        accept="image/*"
        ref={fileInputRef}
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Upload Button */}
      <button
        type="button"
        onClick={handleUploadClick}
        disabled={uploading}
        className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
      >
        {uploading ? 'Uploading...' : 'Upload Thumbnail'}
      </button>
    </div>
  );
}
