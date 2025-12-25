import React, { useState } from 'react';

const MessageInput = ({ onSend, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4 bg-gray-50">
      <div className="flex space-x-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Hỏi về địa điểm ở Hà Nội..."
          className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows="1"
          disabled={isLoading}
          style={{
            minHeight: '48px',
            maxHeight: '120px'
          }}
        />
        
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className={`px-6 py-3 rounded-xl font-semibold transition-all ${
            isLoading || !input.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
          }`}
        >
          {isLoading ? (
            <span className="flex items-center">
              <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
          ) : (
            '📤 Gửi'
          )}
        </button>
      </div>
      
      <div className="mt-2 text-xs text-gray-500 text-center">
        Nhấn <kbd className="bg-gray-200 px-2 py-1 rounded">Enter</kbd> để gửi, <kbd className="bg-gray-200 px-2 py-1 rounded">Shift + Enter</kbd> để xuống dòng
      </div>
    </form>
  );
};

export default MessageInput;
