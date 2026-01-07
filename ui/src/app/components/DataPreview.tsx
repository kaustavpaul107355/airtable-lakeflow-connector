import { useState, useEffect } from "react";
import {
  Download,
  RefreshCw,
  ListFilter,
  Table as TableIcon,
} from "lucide-react";

interface DataPreviewProps {
  selectedTable: string | null;
  isSourceConnected: boolean;
}

// Mock data for preview
const generateMockData = (tableName: string) => {
  const dataTemplates: Record<string, any[]> = {
    Contacts: [
      {
        id: 1,
        name: "John Smith",
        email: "john.smith@example.com",
        phone: "(555) 123-4567",
        company: "Acme Corp",
        status: "Active",
      },
      {
        id: 2,
        name: "Sarah Johnson",
        email: "sarah.j@example.com",
        phone: "(555) 234-5678",
        company: "TechStart Inc",
        status: "Active",
      },
      {
        id: 3,
        name: "Mike Davis",
        email: "mike.d@example.com",
        phone: "(555) 345-6789",
        company: "Global Solutions",
        status: "Pending",
      },
      {
        id: 4,
        name: "Emily Brown",
        email: "emily.b@example.com",
        phone: "(555) 456-7890",
        company: "Innovation Labs",
        status: "Active",
      },
      {
        id: 5,
        name: "David Wilson",
        email: "david.w@example.com",
        phone: "(555) 567-8901",
        company: "Future Tech",
        status: "Inactive",
      },
    ],
    Projects: [
      {
        id: 1,
        projectName: "Website Redesign",
        status: "In Progress",
        owner: "John Smith",
        startDate: "2024-01-15",
        endDate: "2024-03-30",
        budget: "$50,000",
      },
      {
        id: 2,
        projectName: "Mobile App Development",
        status: "Planning",
        owner: "Sarah Johnson",
        startDate: "2024-02-01",
        endDate: "2024-06-15",
        budget: "$120,000",
      },
      {
        id: 3,
        projectName: "Data Migration",
        status: "Completed",
        owner: "Mike Davis",
        startDate: "2023-11-01",
        endDate: "2024-01-10",
        budget: "$35,000",
      },
      {
        id: 4,
        projectName: "CRM Integration",
        status: "In Progress",
        owner: "Emily Brown",
        startDate: "2024-01-20",
        endDate: "2024-04-15",
        budget: "$75,000",
      },
    ],
    Tasks: [
      {
        id: 1,
        taskName: "Design mockups",
        assignee: "John Smith",
        priority: "High",
        dueDate: "2024-02-20",
        status: "In Progress",
      },
      {
        id: 2,
        taskName: "Backend API development",
        assignee: "Sarah Johnson",
        priority: "High",
        dueDate: "2024-02-25",
        status: "Not Started",
      },
      {
        id: 3,
        taskName: "Write documentation",
        assignee: "Mike Davis",
        priority: "Medium",
        dueDate: "2024-03-01",
        status: "In Progress",
      },
      {
        id: 4,
        taskName: "User testing",
        assignee: "Emily Brown",
        priority: "Low",
        dueDate: "2024-03-10",
        status: "Not Started",
      },
      {
        id: 5,
        taskName: "Deploy to production",
        assignee: "David Wilson",
        priority: "High",
        dueDate: "2024-03-15",
        status: "Not Started",
      },
    ],
    Companies: [
      {
        id: 1,
        companyName: "Acme Corp",
        industry: "Technology",
        location: "San Francisco",
        size: "500-1000",
        website: "acmecorp.com",
      },
      {
        id: 2,
        companyName: "TechStart Inc",
        industry: "Software",
        location: "New York",
        size: "50-100",
        website: "techstart.com",
      },
      {
        id: 3,
        companyName: "Global Solutions",
        industry: "Consulting",
        location: "London",
        size: "1000+",
        website: "globalsolutions.com",
      },
      {
        id: 4,
        companyName: "Innovation Labs",
        industry: "Research",
        location: "Boston",
        size: "100-500",
        website: "innovationlabs.com",
      },
    ],
    Products: [
      {
        id: 1,
        productName: "Pro Plan Subscription",
        sku: "PROD-001",
        price: "$99.99",
        category: "Software",
        stock: "Unlimited",
      },
      {
        id: 2,
        productName: "Enterprise License",
        sku: "PROD-002",
        price: "$499.99",
        category: "Software",
        stock: "Unlimited",
      },
      {
        id: 3,
        productName: "Hardware Kit",
        sku: "PROD-003",
        price: "$299.99",
        category: "Hardware",
        stock: "47",
      },
      {
        id: 4,
        productName: "Training Package",
        sku: "PROD-004",
        price: "$1,999.99",
        category: "Services",
        stock: "12",
      },
    ],
  };

  return dataTemplates[tableName] || [];
};

export function DataPreview({
  selectedTable,
  isSourceConnected,
}: DataPreviewProps) {
  const [data, setData] = useState<any[]>([]);

  // Update data when table changes
  useEffect(() => {
    if (selectedTable) {
      setData(generateMockData(selectedTable));
    }
  }, [selectedTable]);

  const handleRefresh = () => {
    if (selectedTable) {
      setData(generateMockData(selectedTable));
    }
  };

  if (!selectedTable) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <TableIcon className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-slate-900 mb-2">No Table Selected</h3>
          <p className="text-slate-600">
            Please select a table from the Browse Tables tab to preview data.
          </p>
        </div>
      </div>
    );
  }

  if (!isSourceConnected) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center max-w-md">
          <TableIcon className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-slate-900 mb-2">Source Not Connected</h3>
          <p className="text-slate-600">
            Please configure and connect to your Airtable source to preview data.
          </p>
        </div>
      </div>
    );
  }

  const columns = data.length > 0 ? Object.keys(data[0]) : [];

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl text-slate-900 mb-2">Data Preview</h2>
        <p className="text-slate-600">
          Preview data from {selectedTable} before configuring sync settings.
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-xs text-blue-700 mb-1">Total Records</p>
          <p className="text-2xl text-blue-900">{data.length}</p>
        </div>
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <p className="text-xs text-purple-700 mb-1">Total Fields</p>
          <p className="text-2xl text-purple-900">{columns.length}</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-xs text-green-700 mb-1">Source Table</p>
          <p className="text-lg text-green-900">{selectedTable}</p>
        </div>
      </div>

      {/* Data Preview Table */}
      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <h3 className="text-slate-900">Table Data</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={handleRefresh}
              className="flex items-center gap-2 px-3 py-1.5 border border-slate-300 rounded-md hover:bg-white transition-colors text-sm"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 border border-slate-300 rounded-md hover:bg-white transition-colors text-sm">
              <ListFilter className="w-4 h-4" />
              Filter
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 border border-slate-300 rounded-md hover:bg-white transition-colors text-sm">
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        <div className="overflow-x-auto max-h-[600px]">
          <table className="w-full">
            <thead className="sticky top-0 bg-slate-50">
              <tr className="border-b border-slate-200">
                {columns.map((column) => (
                  <th
                    key={column}
                    className="px-4 py-3 text-left text-xs text-slate-700 uppercase tracking-wider"
                  >
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {data.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  className="hover:bg-slate-50 transition-colors"
                >
                  {columns.map((column) => (
                    <td
                      key={column}
                      className="px-4 py-3 text-sm text-slate-700"
                    >
                      {row[column]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}