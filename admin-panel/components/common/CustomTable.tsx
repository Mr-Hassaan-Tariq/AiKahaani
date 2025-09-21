import React from 'react';

interface Column {
  key: string;
  label: string;
}

interface DataRow {
  [key: string]: React.ReactNode;
}

interface CustomTableProps {
  columns: Column[];
  data: DataRow[];
}

const CustomTable: React.FC<CustomTableProps> = ({ columns, data }) => {
  return (
    <div className="overflow-x-auto rounded-lg border border-[#BAFF3812] bg-brand-surface">
      <table className="w-full text-left text-sm text-white">
        <thead className="bg-[#161616] text-xs uppercase text-gray-400">
          <tr>
            {columns.map((column) => (
              <th key={column.key} className="px-6 py-3">
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              className={`border-b border-[#BAFF3812] ${
                rowIndex % 2 === 0 ? 'bg-[#1A1A1A]' : 'bg-[#161616]'
              } hover:bg-[#2B2B2B]`}
            >
              {columns.map((column) => (
                <td key={column.key} className="px-6 py-4">
                  {row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CustomTable;
