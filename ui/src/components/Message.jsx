import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const Message = ({ message }) => {
  const isUser = message.role === 'user';

  // Custom components for react-markdown
  const markdownComponents = {
    // Images
    img: ({ node, ...props }) => (
      <img 
        {...props} 
        className="max-w-full h-auto rounded-lg my-4 shadow-md"
        loading="lazy"
        alt={props.alt || 'Image'}
      />
    ),
    // Links
    a: ({ node, ...props }) => (
      <a 
        {...props} 
        className="text-blue-600 hover:text-blue-800 underline"
        target="_blank"
        rel="noopener noreferrer"
      />
    ),
    // Code blocks
    code: ({ node, inline, ...props }) => 
      inline ? (
        <code className="bg-gray-200 px-2 py-1 rounded text-sm font-mono" {...props} />
      ) : (
        <code className="block bg-gray-900 text-gray-100 p-4 rounded-lg my-4 overflow-x-auto text-sm font-mono" {...props} />
      ),
    // Tables
    table: ({ node, ...props }) => (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full border-collapse border border-gray-300" {...props} />
      </div>
    ),
    th: ({ node, ...props }) => (
      <th className="border border-gray-300 bg-gray-100 px-4 py-2 text-left font-semibold" {...props} />
    ),
    td: ({ node, ...props }) => (
      <td className="border border-gray-300 px-4 py-2" {...props} />
    ),
    // Lists
    ul: ({ node, ...props }) => (
      <ul className="list-disc list-inside my-2 space-y-1" {...props} />
    ),
    ol: ({ node, ...props }) => (
      <ol className="list-decimal list-inside my-2 space-y-1" {...props} />
    ),
    // Headings
    h1: ({ node, ...props }) => (
      <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />
    ),
    h2: ({ node, ...props }) => (
      <h2 className="text-xl font-bold mt-3 mb-2" {...props} />
    ),
    h3: ({ node, ...props }) => (
      <h3 className="text-lg font-bold mt-2 mb-1" {...props} />
    ),
    // Blockquotes
    blockquote: ({ node, ...props }) => (
      <blockquote className="border-l-4 border-blue-500 pl-4 italic my-4 text-gray-700" {...props} />
    ),
    // Paragraphs
    p: ({ node, ...props }) => (
      <p className="my-2" {...props} />
    ),
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-[80%] rounded-2xl px-6 py-4 ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-gray-100 text-gray-800'
        }`}
      >
        {/* Intent Badge (for assistant messages) */}
        {!isUser && message.intent && (
          <div className="mb-2">
            <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              🎯 {message.intent}
            </span>
          </div>
        )}
        
        {/* Message Content with Markdown */}
        <div className={`prose prose-sm max-w-none ${isUser ? 'prose-invert' : ''}`}>
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={markdownComponents}
          >
            {message.content}
          </ReactMarkdown>
        </div>
        
        {/* Timestamp */}
        <div className={`text-xs mt-2 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
          {message.timestamp.toLocaleTimeString('vi-VN', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  );
};

export default Message;
