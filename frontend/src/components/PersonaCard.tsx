import React from 'react';
import { Persona } from '@/lib/api';

interface PersonaCardProps {
  persona: Persona;
  isSelected: boolean;
  onSelect: (id: number) => void;
}

const PersonaCard: React.FC<PersonaCardProps> = ({ persona, isSelected, onSelect }) => {
  return (
    <div
      className={`p-6 border-2 rounded-lg cursor-pointer transition-all duration-200 min-h-[400px] ${
        isSelected
          ? 'border-blue-500 bg-blue-50 shadow-md'
          : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
      }`}
      onClick={() => onSelect(persona.id)}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{persona.name}</h3>
        <div
          className={`w-5 h-5 rounded-full border-2 ${
            isSelected ? 'bg-blue-500 border-blue-500' : 'border-gray-300'
          }`}
        >
          {isSelected && (
            <svg className="w-3 h-3 text-white m-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>
      </div>
      
      <div className="space-y-2 text-sm text-gray-600">
        {/* 主要な情報を表示 */}
        {Object.entries(persona.details)
          .filter(([key, value]) => 
            key !== 'raw_text' && 
            key !== 'ペルソナ名' && 
            value && 
            typeof value === 'string' && 
            value.trim().length > 0
          )
          .slice(0, 6)
          .map(([key, value]) => (
            <div key={key} className="flex">
              <span className="font-medium w-20 text-gray-700 shrink-0">{key}:</span>
              <span className="flex-1 ml-2">{value}</span>
            </div>
          ))}
        
        {/* その他の詳細情報（raw_textから抽出） */}
        {persona.details.raw_text && (
          <div className="mt-4 pt-3 border-t border-gray-200">
            <div className="mb-2">
              <span className="font-medium text-gray-700 text-xs uppercase tracking-wide">その他の詳細</span>
            </div>
            <div className="bg-gray-50 p-3 rounded-md text-xs leading-relaxed max-h-40 overflow-y-auto border border-gray-100">
              <div className="whitespace-pre-wrap text-gray-700">{persona.details.raw_text}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonaCard;
