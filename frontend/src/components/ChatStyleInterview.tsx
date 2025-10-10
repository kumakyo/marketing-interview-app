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
    <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
      <div className="flex items-center space-x-3 mb-4 sticky top-0 bg-gray-50 pb-2">
        <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-gray-200">
          <img 
            src={avatarUrl} 
            alt={personaName}
            className="w-full h-full object-cover"
          />
        </div>
        <div>
          <h4 className="font-semibold text-gray-900">{personaName}</h4>
          <p className="text-sm text-gray-500">
            {personaDetails?.年齢}歳 • {personaDetails?.職業}
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {allInterviews.map((interview, idx) => (
          <div key={idx} className="space-y-3">
            {/* インタビュアーの質問 */}
            <div className="flex justify-end">
              <div className="bg-blue-500 text-white rounded-2xl rounded-br-md px-4 py-2 max-w-xs shadow-sm">
                <p className="text-sm">{interview.question}</p>
              </div>
            </div>

            {/* ペルソナの回答 */}
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-2 max-w-xs shadow-sm">
                <p className="text-sm text-gray-800">{interview.main_answer}</p>
              </div>
            </div>

            {/* フォローアップ質問と回答 */}
            {interview.follow_ups && interview.follow_ups.map((followUp, fuIdx) => (
              <div key={fuIdx} className="space-y-2 ml-4">
                {/* フォローアップ質問 */}
                <div className="flex justify-end">
                  <div className="bg-blue-400 text-white rounded-2xl rounded-br-md px-4 py-2 max-w-xs shadow-sm">
                    <p className="text-sm">{followUp.question}</p>
                  </div>
                </div>

                {/* フォローアップ回答 */}
                <div className="flex justify-start">
                  <div className="bg-gray-100 border border-gray-200 rounded-2xl rounded-bl-md px-4 py-2 max-w-xs shadow-sm">
                    <p className="text-sm text-gray-800">{followUp.answer}</p>
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
