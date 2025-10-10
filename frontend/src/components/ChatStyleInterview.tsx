import React from 'react';
import { InterviewResult } from '@/lib/api';

interface ChatStyleInterviewProps {
  personaName: string;
  allInterviews: InterviewResult[];
  personaDetails?: Record<string, string>;
}

const ChatStyleInterview: React.FC<ChatStyleInterviewProps> = ({
  personaName,
  allInterviews,
  personaDetails
}) => {
  // ペルソナの性別に基づいたアバター生成
  const getAvatarUrl = (name: string, gender?: string) => {
    const seed = encodeURIComponent(name);
    const genderLower = (gender || '').toLowerCase();
    const isFemale = genderLower.includes('女');
    const isMale = genderLower.includes('男');
    
    if (isFemale) {
      return `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,d1d4f9&skinColor=fdbcb4,edb98a,f0d5be&hairColor=2c1b18,724133,a55728,4a312c&eyesColor=6b4423,3e2723,896c56&clothingColor=262e33,3c4f5c,65c9ff,5199e4,929598&facialHairProbability=0&accessoriesProbability=30&hatProbability=0&eyebrowProbability=100&mouthProbability=100&mouth=smile,default,serious&eyes=default,happy,wink`;
    } else if (isMale) {
      return `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,d1d4f9&skinColor=fdbcb4,edb98a,f0d5be,ae5d29&hairColor=2c1b18,724133,a55728,4a312c,b58143&eyesColor=6b4423,3e2723,896c56&clothingColor=262e33,3c4f5c,65c9ff,5199e4,929598&facialHairProbability=40&accessoriesProbability=20&hatProbability=0&eyebrowProbability=100&mouthProbability=100&mouth=smile,default,serious&eyes=default,happy`;
    } else {
      return `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,d1d4f9&skinColor=fdbcb4,edb98a,f0d5be&hairColor=2c1b18,724133,a55728,4a312c&eyesColor=6b4423,3e2723,896c56&clothingColor=262e33,3c4f5c,65c9ff,5199e4,929598&facialHairProbability=0&accessoriesProbability=20&hatProbability=0&eyebrowProbability=100&mouthProbability=100&mouth=smile,default&eyes=default,happy`;
    }
  };

  const avatarUrl = getAvatarUrl(personaName, personaDetails?.性別);

  return (
    <div className="bg-gray-50 rounded-lg p-6 h-full overflow-y-auto">
      <div className="flex items-center space-x-3 mb-6 sticky top-0 bg-gray-50 pb-3 border-b border-gray-200">
        <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-gray-200">
          <img 
            src={avatarUrl} 
            alt={personaName}
            className="w-full h-full object-cover"
          />
        </div>
        <div>
          <h4 className="font-semibold text-gray-900 text-lg">{personaName}</h4>
          <p className="text-sm text-gray-500">
            {personaDetails?.年齢}歳 • {personaDetails?.職業}
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {allInterviews.map((interview, idx) => (
          <div key={idx} className="space-y-4">
            {/* インタビュアー（AI）の質問 */}
            <div className="flex justify-start items-end space-x-3">
              <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  <circle cx="9" cy="9" r="2"/>
                  <circle cx="15" cy="9" r="2"/>
                  <path d="M12 17.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
                </svg>
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-5 py-3 max-w-md shadow-sm">
                <p className="text-sm text-gray-800 leading-relaxed">{interview.question}</p>
              </div>
            </div>

            {/* ペルソナの回答 */}
            <div className="flex justify-end items-end space-x-3">
              <div className="bg-blue-500 text-white rounded-2xl rounded-br-md px-5 py-3 max-w-md shadow-sm">
                <p className="text-sm leading-relaxed">{interview.main_answer}</p>
              </div>
              <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-gray-200 flex-shrink-0">
                <img 
                  src={avatarUrl} 
                  alt={personaName}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            {/* フォローアップ質問と回答 */}
            {interview.follow_ups && interview.follow_ups.map((followUp, fuIdx) => (
              <div key={fuIdx} className="space-y-4 ml-6">
                {/* フォローアップ質問 */}
                <div className="flex justify-start items-end space-x-3">
                  <div className="w-8 h-8 rounded-full bg-blue-400 flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                      <circle cx="9" cy="9" r="2"/>
                      <circle cx="15" cy="9" r="2"/>
                      <path d="M12 17.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
                    </svg>
                  </div>
                  <div className="bg-gray-100 border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 max-w-sm shadow-sm">
                    <p className="text-sm text-gray-800 leading-relaxed">{followUp.question}</p>
                  </div>
                </div>

                {/* フォローアップ回答 */}
                <div className="flex justify-end items-end space-x-3">
                  <div className="bg-blue-400 text-white rounded-2xl rounded-br-md px-4 py-3 max-w-sm shadow-sm">
                    <p className="text-sm leading-relaxed">{followUp.answer}</p>
                  </div>
                  <div className="w-8 h-8 rounded-full overflow-hidden border-2 border-gray-200 flex-shrink-0">
                    <img 
                      src={avatarUrl} 
                      alt={personaName}
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatStyleInterview;
