import React from 'react';
import { Competitor } from '@/lib/api';

interface CompetitorFormProps {
  competitor: Competitor;
  index: number;
  onUpdate: (index: number, field: keyof Competitor, value: string) => void;
  onRemove: (index: number) => void;
}

export default function CompetitorForm({ 
  competitor, 
  index, 
  onUpdate, 
  onRemove 
}: CompetitorFormProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-medium text-gray-900">競合 {index + 1}</h4>
        <button
          onClick={() => onRemove(index)}
          className="text-red-600 hover:text-red-800 text-sm flex items-center space-x-1"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
          <span>削除</span>
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label className="block">
          <span className="text-sm font-medium text-gray-700">競合名</span>
          <input
            type="text"
            value={competitor.name}
            onChange={(e) => onUpdate(index, 'name', e.target.value)}
            placeholder="例: JOYSOUNDアプリ"
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </label>
        
        <label className="block">
          <span className="text-sm font-medium text-gray-700">価格</span>
          <input
            type="text"
            value={competitor.price || ''}
            onChange={(e) => onUpdate(index, 'price', e.target.value)}
            placeholder="例: 月額500円"
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </label>
      </div>
      
      <label className="block">
        <span className="text-sm font-medium text-gray-700">説明</span>
        <textarea
          value={competitor.description}
          onChange={(e) => onUpdate(index, 'description', e.target.value)}
          placeholder="例: 大手カラオケチェーンが提供するアプリサービス"
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={2}
        />
      </label>
      
      <label className="block">
        <span className="text-sm font-medium text-gray-700">特徴</span>
        <textarea
          value={competitor.features || ''}
          onChange={(e) => onUpdate(index, 'features', e.target.value)}
          placeholder="例: 豊富な楽曲数、採点機能、店舗との連携"
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={2}
        />
      </label>
    </div>
  );
}
