import React, { useState } from 'react';
import { Persona } from '@/lib/api';

interface ChatPersonaCardProps {
  persona: Persona;
  isSelected: boolean;
  onSelect: () => void;
}

const ChatPersonaCard: React.FC<ChatPersonaCardProps> = ({ persona, isSelected, onSelect }) => {
  const [showDetails, setShowDetails] = useState(false);

  // ペルソナの顔画像生成（簡単なアバター）
  const getAvatarUrl = (name: string) => {
    // DiceBear APIを使用してアバター生成
    const seed = encodeURIComponent(name);
    return `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,d1d4f9`;
  };

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
          <div className="w-16 h-16 rounded-full overflow-hidden border-2 border-gray-200">
            <img 
              src={getAvatarUrl(persona.name)} 
              alt={persona.name}
              className="w-full h-full object-cover"
            />
          </div>
          {isSelected && (
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center mt-1 ml-5">
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
          )}
        </div>
        
        {/* ペルソナ情報 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <h3 className="font-semibold text-gray-900">{persona.name}</h3>
              <span className="text-sm text-gray-500">
                {persona.details?.年齢 || ''}
              </span>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowDetails(!showDetails);
              }}
              className="text-blue-500 hover:text-blue-700 text-sm"
            >
              {showDetails ? '▲' : '▼'}
            </button>
          </div>
          
          {/* 基本情報 */}
          <div className="space-y-1 text-sm text-gray-600">
            <div>
              <span className="font-medium">職業:</span> {persona.details?.職業 || ''}
            </div>
            <div>
              <span className="font-medium">年収:</span> {persona.details?.年収帯 || ''}
            </div>
            <div>
              <span className="font-medium">居住地:</span> {persona.details?.居住地 || ''}
            </div>
          </div>
          
          {/* 詳細情報（展開可能） */}
          {showDetails && (
            <div className="mt-3 pt-3 border-t border-gray-200 space-y-2 text-sm text-gray-600 max-h-32 overflow-y-auto">
              <div>
                <span className="font-medium">家族構成:</span> {persona.details?.家族構成 || ''}
              </div>
              <div>
                <span className="font-medium">趣味・余暇:</span> {persona.details?.['趣味・余暇'] || ''}
              </div>
              <div>
                <span className="font-medium">関心事・悩み:</span> {persona.details?.['関心事・悩み'] || ''}
              </div>
              {persona.details?.性格 && (
                <div>
                  <span className="font-medium">性格:</span> {persona.details.性格}
                </div>
              )}
              {persona.details?.価値観 && (
                <div>
                  <span className="font-medium">価値観:</span> {persona.details.価値観}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPersonaCard;
