import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MCPToolTester = () => {
  const [toolName, setToolName] = useState('createPage');
  const [toolArgs, setToolArgs] = useState('{"title": "Test Page", "content": "This is a test page"}');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const testTool = async () => {
    setLoading(true);
    try {
      const args = JSON.parse(toolArgs);
      const response = await axios.post(`${API}/mcp/dispatch`, {
        tool: toolName,
        args,
      });
      setResult(response.data);
    } catch (error) {
      setResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Tool Name</label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
          value={toolName}
          onChange={(e) => setToolName(e.target.value)}
        >
          <option value="createPage">Create Page</option>
          <option value="createArticle">Create Article</option>
          <option value="updatePage">Update Page</option>
          <option value="createUser">Create User</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Tool Arguments (JSON)</label>
        <textarea
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
          rows="4"
          value={toolArgs}
          onChange={(e) => setToolArgs(e.target.value)}
          placeholder='{"title": "Test Page", "content": "This is a test page"}'
        />
      </div>

      <button
        onClick={testTool}
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test Tool'}
      </button>

      {result && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold mb-2">Result:</h4>
          <pre className="text-sm overflow-x-auto">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default MCPToolTester;
