import React from 'react';
import { InterviewResult } from '@/lib/api';

interface InterviewCardProps {
  result: InterviewResult;
  index: number;
}

const InterviewCard: React.FC<InterviewCardProps> = ({ result, index }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-4">
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
          <span className="text-blue-600 font-semibold text-sm">Q{index + 1}</span>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-medium text-gray-900 mb-2">{result.question}</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-800 leading-relaxed">{result.main_answer}</p>
          </div>
        </div>
      </div>

      {result.follow_ups && result.follow_ups.length > 0 && (
        <div className="ml-11 space-y-3">
          {result.follow_ups.map((followUp, followUpIndex) => (
            <div key={followUpIndex} className="border-l-2 border-gray-200 pl-4">
              <div className="text-sm font-medium text-gray-700 mb-1">
                更問 {followUpIndex + 1}: {followUp.question}
              </div>
              <div className="bg-blue-50 rounded p-3">
                <p className="text-gray-800 text-sm leading-relaxed">{followUp.answer}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InterviewCard;
