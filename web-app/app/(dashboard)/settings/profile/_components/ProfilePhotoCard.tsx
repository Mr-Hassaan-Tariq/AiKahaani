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
    <div className="rounded-xl border border-border bg-card p-6">
      <h3 className="mb-5 text-sm font-semibold text-foreground">Profile Photo</h3>

      <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
        {/* Avatar */}
        {profileImage ? (
          <ClientImage
            src={profileImage}
            alt="Profile"
            width={96}
            height={96}
            priority
            className="h-24 w-24 shrink-0 rounded-full object-cover ring-2 ring-border"
          />
        ) : (
          <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-full bg-accent text-xl font-bold text-accent-foreground ring-2 ring-border">
            {getInitials(fullName)}
          </div>
        )}

        <div className="flex flex-col gap-3">
          <div className="space-y-1 text-xs text-muted-foreground">
            <p>Recommended size: <span className="font-medium text-foreground">400×400 px</span></p>
            <p>Accepted formats: <span className="font-medium text-foreground">JPG, PNG · Max 5 MB</span></p>
          </div>

          <div className="flex items-center gap-2">
            <ChangePhotoModal
              trigger={
                <Button variant="outline" size="sm">
                  <Camera className="h-4 w-4" /> Change photo
                </Button>
              }
            />
            {profileImage && (
              <DeletePhotoModal
                trigger={
                  <Button variant="outline" size="sm" className="text-destructive hover:text-destructive">
                    <Trash2 className="h-4 w-4" /> Remove
                  </Button>
                }
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
