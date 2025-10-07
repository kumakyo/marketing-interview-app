import React from 'react';

interface ChatMessageProps {
  message: string;
  isUser?: boolean;
  personaName?: string;
  personaImage?: string;
  timestamp?: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ 
  message, 
  isUser = false, 
  personaName, 
  personaImage,
  timestamp 
}) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      {!isUser && (
        <div className="flex-shrink-0 mr-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-medium text-sm">
            {personaImage ? (
              <img src={personaImage} alt={personaName} className="w-10 h-10 rounded-full" />
            ) : (
              personaName?.charAt(0) || 'P'
            )}
          </div>
        </div>
      )}
      
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
        isUser 
          ? 'bg-blue-500 text-white rounded-br-md' 
          : 'bg-gray-100 text-gray-800 rounded-bl-md'
      }`}>
        {!isUser && personaName && (
          <div className="text-xs text-gray-500 mb-1 font-medium">
            {personaName}
          </div>
        )}
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {message}
        </div>
        {timestamp && (
          <div className={`text-xs mt-1 ${
            isUser ? 'text-blue-100' : 'text-gray-400'
          }`}>
            {timestamp}
          </div>
        )}
      </div>
      
      {isUser && (
        <div className="flex-shrink-0 ml-3">
          <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium text-sm">
            👤
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;


