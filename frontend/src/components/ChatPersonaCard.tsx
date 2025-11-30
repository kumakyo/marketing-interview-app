import React, { useState } from 'react';
import { Persona } from '@/lib/api';

interface ChatPersonaCardProps {
  persona: Persona;
  isSelected: boolean;
  onSelect: () => void;
}

const ChatPersonaCard: React.FC<ChatPersonaCardProps> = ({ persona, isSelected, onSelect }) => {
  const [isFavorite, setIsFavorite] = useState(false);

  // ペルソナの顔画像生成（性別に基づいた適切なアイコン）
  const getAvatarUrl = (name: string, gender?: string) => {
    const seed = encodeURIComponent(name);
    
    // 性別情報を取得（detailsから）
    const genderLower = (gender || persona.details?.性別 || '').toLowerCase();
    const isFemale = genderLower.includes('女') || genderLower.includes('female');
    const isMale = genderLower.includes('男') || genderLower.includes('male');
    
    // 性別に応じてアバタースタイルを設定
    if (isFemale) {
      // 女性用のアバター設定
      return `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,d1d4f9&skinColor=fdbcb4,edb98a,f0d5be&hairColor=2c1b18,724133,a55728,4a312c&eyesColor=6b4423,3e2723,896c56&clothingColor=262e33,3c4f5c,65c9ff,5199e4,929598&facialHairProbability=0&accessoriesProbability=30&hatProbability=0&eyebrowProbability=100&mouthProbability=100&mouth=smile,default,serious&eyes=default,happy,wink`;
    } else if (isMale) {
      // 男性用のアバター設定
      return `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,d1d4f9&skinColor=fdbcb4,edb98a,f0d5be,ae5d29&hairColor=2c1b18,724133,a55728,4a312c,b58143&eyesColor=6b4423,3e2723,896c56&clothingColor=262e33,3c4f5c,65c9ff,5199e4,929598&facialHairProbability=40&accessoriesProbability=20&hatProbability=0&eyebrowProbability=100&mouthProbability=100&mouth=smile,default,serious&eyes=default,happy`;
    } else {
      // 性別不明の場合は中性的なアバター
      return `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,d1d4f9&skinColor=fdbcb4,edb98a,f0d5be&hairColor=2c1b18,724133,a55728,4a312c&eyesColor=6b4423,3e2723,896c56&clothingColor=262e33,3c4f5c,65c9ff,5199e4,929598&facialHairProbability=0&accessoriesProbability=20&hatProbability=0&eyebrowProbability=100&mouthProbability=100&mouth=smile,default&eyes=default,happy`;
    }
  };

  // キャッチーなタイトルを生成
  const generateTitle = () => {
    const job = persona.details?.職業 || '';
    const age = persona.details?.年齢 || '';
    const hobbies = persona.details?.['趣味・余暇'] || '';
    const concerns = persona.details?.['関心事・悩み'] || '';
    const family = persona.details?.家族構成 || '';
    
    // 職業と特徴からタイトルを生成
    let title = '';
    
    if (family.includes('子') && job) {
      title = `${job}×子育て世代`;
    } else if (family.includes('独身')) {
      if (hobbies && concerns) {
        const hobbyKey = hobbies.split('、')[0];
        title = `${hobbyKey}を楽しむ${job}`;
      } else {
        title = `キャリアを追求する${job}`;
      }
    } else if (family.includes('夫') || family.includes('妻')) {
      title = `家族と共に歩む${job}`;
    } else {
      title = persona.details?.ペルソナ名 || persona.name;
    }
    
    return title;
  };

  // 説明文を生成
  const generateDescription = () => {
    const location = persona.details?.居住地 || '';
    const age = persona.details?.年齢 || '';
    const gender = persona.details?.性別 || '';
    const job = persona.details?.職業 || '';
    const family = persona.details?.家族構成 || '';
    const hobbies = persona.details?.['趣味・余暇'] || '';
    const concerns = persona.details?.['関心事・悩み'] || '';
    
    let description = '';
    
    // 基本情報
    if (location && age && gender) {
      description += `${location}在住の${age}${gender}。`;
    }
    
    // 職業と家族
    if (job && family) {
      description += `${job}として働きながら、${family}。`;
    } else if (job) {
      description += `${job}として働いている。`;
    }
    
    // 趣味
    if (hobbies) {
      const hobbyList = hobbies.split('、').slice(0, 2).join('、');
      description += `${hobbyList}が好き。`;
    }
    
    // 関心事
    if (concerns) {
      const concernList = concerns.split('、').slice(0, 2).join('、');
      description += `${concernList}に関心がある。`;
    }
    
    return description || persona.raw_text?.substring(0, 120) + '...' || '';
  };

  return (
    <div 
      className={`relative bg-white rounded-2xl overflow-hidden cursor-pointer transition-all duration-300 ${
        isSelected 
          ? 'ring-4 ring-cyan-400 shadow-xl transform scale-105' 
          : 'shadow-md hover:shadow-xl hover:transform hover:scale-102'
      }`}
      onClick={onSelect}
    >
      {/* お気に入りボタン */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          setIsFavorite(!isFavorite);
        }}
        className="absolute top-4 left-4 z-10 bg-white rounded-full p-2 shadow-md hover:bg-gray-50 transition"
      >
        <svg 
          className={`w-6 h-6 ${isFavorite ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
          fill={isFavorite ? 'currentColor' : 'none'}
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" 
          />
        </svg>
      </button>

      {/* 選択インジケーター */}
      {isSelected && (
        <div className="absolute top-4 right-4 z-10 bg-cyan-500 rounded-full p-2 shadow-lg">
          <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        </div>
      )}

      {/* カードコンテンツ */}
      <div className="p-6">
        {/* アバター画像 */}
        <div className="flex justify-center mb-4">
          <div className="w-24 h-24 rounded-full overflow-hidden border-4 border-gray-100 shadow-lg">
            <img 
              src={getAvatarUrl(persona.name)} 
              alt={persona.name}
              className="w-full h-full object-cover"
            />
          </div>
        </div>

        {/* タイトル */}
        <h3 className="text-lg font-bold text-center text-gray-900 mb-3 min-h-[56px] flex items-center justify-center">
          {generateTitle()}
        </h3>

        {/* 基本情報バッジ */}
        <div className="flex justify-center gap-2 mb-4 flex-wrap">
          {persona.details?.年齢 && (
            <span className="px-3 py-1 bg-cyan-50 text-cyan-700 text-sm rounded-full">
              {persona.details.年齢}
            </span>
          )}
          {persona.details?.性別 && (
            <span className="px-3 py-1 bg-cyan-50 text-cyan-700 text-sm rounded-full">
              {persona.details.性別}
            </span>
          )}
        </div>

        {/* 職業 */}
        {persona.details?.職業 && (
          <div className="text-center mb-4">
            <p className="text-cyan-600 font-medium">
              {persona.details.職業}
            </p>
          </div>
        )}

        {/* 説明文 */}
        <div className="text-sm text-gray-600 leading-relaxed min-h-[80px]">
          {generateDescription()}
        </div>

        {/* 詳細情報の折りたたみ */}
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
            {persona.details?.年収帯 && (
              <div>
                <span className="font-medium">年収:</span> {persona.details.年収帯}
              </div>
            )}
            {persona.details?.居住地 && (
              <div>
                <span className="font-medium">居住地:</span> {persona.details.居住地}
              </div>
            )}
            {persona.details?.家族構成 && (
              <div className="col-span-2">
                <span className="font-medium">家族:</span> {persona.details.家族構成}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPersonaCard;
