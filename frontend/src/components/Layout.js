import React, { useState, useContext } from 'react';
import { signOut } from 'firebase/auth';
import { AuthContext } from '../App';
import Dashboard from './Dashboard';
import PagesList from './PagesList';

const Layout = ({ children }) => {
  const { user, auth } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('dashboard');

  const handleSignOut = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">MCP-CMS</h1>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${activeTab === 'dashboard' ? 'bg-blue-500 text-white' : 'text-gray-700 hover:text-gray-900'}`}
              >
                Dashboard
              </button>

              <button
                onClick={() => setActiveTab('pages')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${activeTab === 'pages' ? 'bg-blue-500 text-white' : 'text-gray-700 hover:text-gray-900'}`}
              >
                Pages
              </button>

              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">{user?.name}</span>
                <button
                  onClick={handleSignOut}
                  className="text-sm text-red-600 hover:text-red-800"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'pages' && <PagesList />}
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
