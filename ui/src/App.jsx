import React from 'react';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🗺️ Map Assistant
          </h1>
          <p className="text-gray-600">
            AI Travel Guide - Khám phá Hà Nội cùng trợ lý thông minh
          </p>
        </header>
        
        <ChatInterface />
      </div>
    </div>
  );
}

export default App;
