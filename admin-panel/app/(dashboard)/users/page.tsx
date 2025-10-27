'use client';

import type { AdminUser } from 'lib/api/user';
import { useEffect, useState } from 'react';
import { Eye, Trash2, UserCheck, UserX } from 'lucide-react';
import { toast } from 'sonner';

import Pagination from '../_components/Pagination';
import { useAdminUsers } from 'lib/api/hooks';
import Card from 'components/ui/Card';
import Text from 'components/ui/Text';
import CustomTable from 'components/common/CustomTable';

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'fullname', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'date_joined', label: 'Signup Date' },
  { key: 'is_active', label: 'Status' },
  { key: 'role', label: 'Role' },
  { key: 'actions', label: 'Actions' },
];

export default function UserManagement() {
  const {
    users,
    loading,
    error,
    pagination,
    getUsers,
    activateUser,
    deactivateUser,
    deleteUser,
    grantAdminPrivileges,
    revokeAdminPrivileges,
  } = useAdminUsers();

  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    getUsers(1, 10);
  }, [getUsers]);

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    getUsers(1, pagination.limit, term);
  };

  const handlePageChange = (page: number) => {
    getUsers(page, pagination.limit, searchTerm);
  };

  const handleActivateUser = async (userId: string) => {
    try {
      await activateUser(userId);
      toast.success('User activated successfully');
    } catch (error) {
      console.error('Failed to activate user:', error);
      toast.error('Failed to activate user');
    }
  };

  const handleDeactivateUser = async (userId: string) => {
    try {
      await deactivateUser(userId);
      toast.success('User deactivated successfully');
    } catch (error) {
      console.error('Failed to deactivate user:', error);
      toast.error('Failed to deactivate user');
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await deleteUser(userId);
        toast.success('User deleted successfully');
      } catch (error) {
        console.error('Failed to delete user:', error);
        toast.error('Failed to delete user');
      }
    }
  };

  const handleGrantAdmin = async (userId: string) => {
    try {
      await grantAdminPrivileges(userId);
      toast.success('Admin privileges granted');
    } catch (error) {
      console.error('Failed to grant admin privileges:', error);
      toast.error('Failed to grant admin privileges');
    }
  };

  const handleRevokeAdmin = async (userId: string) => {
    try {
      await revokeAdminPrivileges(userId);
      toast.success('Admin privileges revoked');
    } catch (error) {
      console.error('Failed to revoke admin privileges:', error);
      toast.error('Failed to revoke admin privileges');
    }
  };

  const tableData = users.map((user: AdminUser) => ({
    id: user?.id,
    fullname: user?.fullname || 'N/A',
    email: user?.email,
    date_joined: new Date(user?.date_joined).toLocaleDateString(),
    is_active: user?.is_active ? 'Active' : 'Inactive',
    role: user?.is_admin ? 'Admin' : user?.roles_display?.join(', ') || 'User',
    actions: (
      <div className="flex items-center gap-3">
        <button
          className="text-blue-500 hover:text-blue-400"
          onClick={() => console.log('View user:', user?.id)}
          title="View"
        >
          <Eye size={18} />
        </button>

        {user?.is_active ? (
          <button
            className="text-yellow-500 hover:text-yellow-400"
            onClick={() => handleDeactivateUser(user?.id)}
            title="Deactivate"
          >
            <UserX size={18} />
          </button>
        ) : (
          <button
            className="text-green-500 hover:text-green-400"
            onClick={() => handleActivateUser(user?.id)}
            title="Activate"
          >
            <UserCheck size={18} />
          </button>
        )}

        <button
          className="text-red-500 hover:text-red-400"
          onClick={() => handleDeleteUser(user?.id)}
          title="Delete"
        >
          <Trash2 size={18} />
        </button>
      </div>
    ),
  }));

  if (loading && users.length === 0) {
    return (
      <Card className="text-white">
        <Text className="mb-4 text-2xl font-bold">Users</Text>
        <div className="flex items-center justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
          <span className="ml-2">Loading users...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="text-white">
        <Text className="mb-4 text-2xl font-bold">Users</Text>
        <div className="rounded border border-red-500 bg-red-900/20 p-4">
          <Text className="text-red-400">Error: {error}</Text>
        </div>
      </Card>
    );
  }

  return (
    <Card className="text-white">
      <div className="mb-4 flex items-center justify-between">
        <Text className="text-2xl font-bold">Users</Text>
        <div className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            className="rounded-xl border border-gray-500 bg-transparent px-4 py-2 text-white placeholder-gray-400 focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-400"
          />

          <Text className="text-sm text-gray-400">Total: {pagination.total} users</Text>
        </div>
      </div>

      <CustomTable columns={columns} data={tableData} />

      <div className="mt-4">
        <Pagination
          currentPage={pagination.page}
          totalCount={pagination.total}
          pageSize={pagination.limit}
          onPageChange={handlePageChange}
        />
      </div>
    </Card>
  );
}
