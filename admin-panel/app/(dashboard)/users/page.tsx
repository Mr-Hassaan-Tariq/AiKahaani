import Card from 'components/ui/Card';
import Text from 'components/ui/Text';
import CustomTable from 'components/common/CustomTable';

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'signupDate', label: 'Signup Date' },
  { key: 'status', label: 'Status' },
  { key: 'role', label: 'Role' },
  { key: 'actions', label: 'Actions' },
];

const data = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john.doe@example.com',
    signupDate: '2025-01-15',
    status: 'Active',
    role: 'Admin',
    actions: (
      <div className="flex items-center gap-2">
        <button className="text-blue-500 hover:underline">View</button>
        <button className="text-yellow-500 hover:underline">Deactivate</button>
        <button className="text-red-500 hover:underline">Delete</button>
      </div>
    ),
  },
  {
    id: 2,
    name: 'Jane Smith',
    email: 'jane.smith@example.com',
    signupDate: '2025-02-20',
    status: 'Inactive',
    role: 'Editor',
    actions: (
      <div className="flex items-center gap-2">
        <button className="text-blue-500 hover:underline">View</button>
        <button className="text-green-500 hover:underline">Activate</button>
        <button className="text-red-500 hover:underline">Delete</button>
      </div>
    ),
  },
  {
    id: 3,
    name: 'Alice Johnson',
    email: 'alice.johnson@example.com',
    signupDate: '2025-03-10',
    status: 'Active',
    role: 'Viewer',
    actions: (
      <div className="flex items-center gap-2">
        <button className="text-blue-500 hover:underline">View</button>
        <button className="text-yellow-500 hover:underline">Deactivate</button>
        <button className="text-red-500 hover:underline">Delete</button>
      </div>
    ),
  },
];

export default function UserManagement() {
  return (
    <Card className="text-white">
      <Text className="mb-4 text-2xl font-bold">Users</Text>
      <CustomTable columns={columns} data={data} />
    </Card>
  );
}
