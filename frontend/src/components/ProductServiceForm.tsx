import React from 'react';
import { ProductService } from '@/lib/api';

interface ProductServiceFormProps {
  product: ProductService;
  index: number;
  onUpdate: (id: string, field: keyof ProductService, value: string) => void;
  onRemove: (id: string) => void;
  canRemove: boolean;
}

export default function ProductServiceForm({ 
  product, 
  index, 
  onUpdate, 
  onRemove, 
  canRemove 
}: ProductServiceFormProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-medium text-gray-900">商品・サービス {index + 1}</h4>
        {canRemove && (
          <button
            onClick={() => onRemove(product.id)}
            className="text-red-600 hover:text-red-800 text-sm flex items-center space-x-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span>削除</span>
          </button>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label className="block">
          <span className="text-sm font-medium text-gray-700">
            商品・サービス名 *
          </span>
          <input
            type="text"
            value={product.name}
            onChange={(e) => onUpdate(product.id, 'name', e.target.value)}
            placeholder="例: 個人向けオンライン英会話サービス"
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </label>
        
        <label className="block">
          <span className="text-sm font-medium text-gray-700">
            価格などの基本情報 *
          </span>
          <input
            type="text"
            value={product.basic_info}
            onChange={(e) => onUpdate(product.id, 'basic_info', e.target.value)}
            placeholder="例: 月額980円、初回30日無料"
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </label>
      </div>
      
      <label className="block">
        <span className="text-sm font-medium text-gray-700">
          ①どういった人に向けた商品・サービスか *
        </span>
        <textarea
          value={product.target_audience}
          onChange={(e) => onUpdate(product.id, 'target_audience', e.target.value)}
          placeholder="例: 20-30代のビジネスパーソンで、キャリアアップや海外展開を目指す社会人。英語でのコミュニケーション能力向上を求める人。"
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
        />
      </label>
      
      <label className="block">
        <span className="text-sm font-medium text-gray-700">
          ②その人たちにとってどういう良いこと（ベネフィット）があるか *
        </span>
        <textarea
          value={product.benefits}
          onChange={(e) => onUpdate(product.id, 'benefits', e.target.value)}
          placeholder="例: ネイティブ講師との1対1レッスン、24時間予約可能、個別カリキュラム作成、発音矯正AI機能、実践的な会話練習、短期間での英語力向上。"
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
        />
      </label>
      
      <label className="block">
        <span className="text-sm font-medium text-gray-700">
          ③そのベネフィットはなぜ実現・体現できるか？（ベネフィットを信じられる理由） *
        </span>
        <textarea
          value={product.benefit_reason}
          onChange={(e) => onUpdate(product.id, 'benefit_reason', e.target.value)}
          placeholder="例: 英語教育専門の資格を持つネイティブ講師陣、独自開発の学習進捗管理システム、TESOL認定カリキュラム、24時間対応可能な専用プラットフォーム。"
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
        />
      </label>
    </div>
  );
}






