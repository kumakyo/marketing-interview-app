import React, { useState, useRef, useEffect } from 'react';
import { InterviewResult } from '@/lib/api';
import ChatMessage from './ChatMessage';

interface ChatInterviewProps {
  personaName: string;
  results: InterviewResult[];
  onNewResult: (result: InterviewResult) => void;
}

const ChatInterview: React.FC<ChatInterviewProps> = ({ 
  personaName, 
  results, 
  onNewResult 
}) => {
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [results, isTyping]);

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString('ja-JP', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMessages = () => {
    const messages: JSX.Element[] = [];
    
    results.forEach((result, index) => {
      // 質問メッセージ
      messages.push(
        <ChatMessage
          key={`q-${index}`}
          message={result.question}
          isUser={true}
          timestamp={formatTimestamp(new Date())}
        />
      );
      
      // 回答メッセージ
      messages.push(
        <ChatMessage
          key={`a-${index}`}
          message={result.main_answer}
          isUser={false}
          personaName={personaName}
          timestamp={formatTimestamp(new Date())}
        />
      );
      
      // フォローアップ質問と回答
      result.follow_ups?.forEach((followUp, fIndex) => {
        messages.push(
          <ChatMessage
            key={`fq-${index}-${fIndex}`}
            message={followUp.question}
            isUser={true}
            timestamp={formatTimestamp(new Date())}
          />
        );
        
        messages.push(
          <ChatMessage
            key={`fa-${index}-${fIndex}`}
            message={followUp.answer}
            isUser={false}
            personaName={personaName}
            timestamp={formatTimestamp(new Date())}
          />
        );
      });
    });
    
    return messages;
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
      {/* チャットヘッダー */}
      <div className="bg-gray-50 px-4 py-3 border-b">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-medium text-sm">
            {personaName.charAt(0)}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{personaName}</h3>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span className="text-xs text-gray-500">オンライン</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* チャットメッセージエリア */}
      <div className="h-96 overflow-y-auto p-4 bg-gray-50">
        {results.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <div className="text-4xl mb-2">💬</div>
              <p>インタビューを開始してください</p>
            </div>
          </div>
        ) : (
          <>
            {renderMessages()}
            {isTyping && (
              <div className="flex justify-start mb-4">
                <div className="flex-shrink-0 mr-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-medium text-sm">
                    {personaName.charAt(0)}
                  </div>
                </div>
                <div className="bg-gray-100 px-4 py-2 rounded-2xl rounded-bl-md">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
    </div>
  );
};

export default ChatInterview;
