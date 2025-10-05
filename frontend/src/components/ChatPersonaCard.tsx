import React from 'react';
import { Persona } from '@/lib/api';

interface ChatPersonaCardProps {
  persona: Persona;
  isSelected: boolean;
  onSelect: () => void;
}

const ChatPersonaCard: React.FC<ChatPersonaCardProps> = ({ persona, isSelected, onSelect }) => {
  return (
    <div 
      className={`p-4 border rounded-2xl cursor-pointer transition-all duration-200 ${
        isSelected 
          ? 'border-blue-500 bg-blue-50 shadow-md' 
          : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
      }`}
      onClick={onSelect}
    >
      <div className="flex items-start space-x-4">
        {/* アバター */}
        <div className="flex-shrink-0">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-medium text-lg">
            {persona.name.charAt(0)}
          </div>
          {isSelected && (
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center mt-1 ml-3">
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
          )}
        </div>
        
        {/* ペルソナ情報 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="font-semibold text-gray-900">{persona.name}</h3>
            <span className="text-sm text-gray-500">
              {persona.details?.年齢 || ''}
            </span>
          </div>
          
          <div className="space-y-1">
            <div className="text-sm text-gray-600">
              <span className="font-medium">職業:</span> {persona.details?.職業 || ''}
            </div>
            <div className="text-sm text-gray-600">
              <span className="font-medium">居住地:</span> {persona.details?.居住地 || ''}
            </div>
            <div className="text-sm text-gray-600">
              <span className="font-medium">関心事:</span> {persona.details?.関心事・悩み || ''}
            </div>
          </div>
          
          {/* オンライン状態表示 */}
          <div className="flex items-center mt-3">
            <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
            <span className="text-xs text-gray-500">オンライン</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPersonaCard;
