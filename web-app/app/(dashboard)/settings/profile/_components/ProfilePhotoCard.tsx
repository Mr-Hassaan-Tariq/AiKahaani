'use client';

import { Camera, Trash2 } from 'lucide-react';

import ChangePhotoModal from './ChangePhotoModal';
import DeletePhotoModal from './DeletePhotoModal';
import { Button } from 'components/ui/Button';
import ClientImage from 'components/ui/ClientImage';

export default function ProfilePhotoCard({
  profileImage,
  fullName,
}: {
  profileImage?: string;
  fullName?: string;
}) {
  const getInitials = (name?: string) => {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0][0].toUpperCase();
    return (parts[0][0] + parts[1][0]).toUpperCase();
  };

  return (
    <div className="rounded-xl border border-border bg-card p-4 sm:p-8">
      <h3 className="mb-6 border-b border-border pb-6 text-[18px] font-semibold text-foreground">
        Personal Information
      </h3>

      <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:gap-6">
        {/* Avatar */}
        {profileImage ? (
          <ClientImage
            src={profileImage}
            alt="Profile"
            width={80}
            height={80}
            priority
            className="h-20 w-20 shrink-0 rounded-full object-cover ring-2 ring-border"
          />
        ) : (
          <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xl font-bold text-primary ring-2 ring-border">
            {getInitials(fullName)}
          </div>
        )}

        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-3">
            <ChangePhotoModal
              trigger={
                <Button variant="outline" size="sm">
                  <Camera className="h-4 w-4" /> Change Photo
                </Button>
              }
            />
            {profileImage && (
              <DeletePhotoModal
                trigger={
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" /> Remove
                  </Button>
                }
              />
            )}
          </div>
          <p className="text-[13px] text-muted-foreground">JPG, GIF or PNG. Max size of 5MB.</p>
        </div>
      </div>
    </div>
  );
}
