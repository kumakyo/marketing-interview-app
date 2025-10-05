import React from 'react';

interface InterviewResultsProps {
  results: { [key: string]: string[] };
  personas: any[];
}

const InterviewResults: React.FC<InterviewResultsProps> = ({ results, personas }) => {
  // ロボットアイコンのSVG
  const RobotIcon = () => (
    <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H9C7.89 1 7 1.89 7 3V7C5.89 7 5 7.89 5 9V16C5 17.11 5.89 18 7 18H9L9.83 21.17C9.96 21.69 10.43 22 11 22H13C13.57 22 14.04 21.69 14.17 21.17L15 18H17C18.11 18 19 17.11 19 16V9C19 7.89 18.11 7 17 7V3C17 1.89 16.11 1 15 1L21 7V9ZM7.5 13.5C7.5 12.67 8.17 12 9 12S10.5 12.67 10.5 13.5 9.83 15 9 15 7.5 14.33 7.5 13.5ZM13.5 13.5C13.5 12.67 14.17 12 15 12S16.5 12.67 16.5 13.5 15.83 15 15 15 13.5 14.33 13.5 13.5Z"/>
      </svg>
    </div>
  );

  // ペルソナのアバター取得（一般的な日本人風）
  const getAvatarUrl = (name: string) => {
    const seed = encodeURIComponent(name);
    return `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,d1d4f9&skinColor=fdbcb4,edb98a&hairColor=2c1b18,724133,a55728&eyesColor=6b4423,3e2723&clothingColor=262e33,65c9ff,5199e4&facialHairProbability=0&accessoriesProbability=0&hatProbability=0&eyebrowProbability=100&mouthProbability=100`;
  };

  return (
    <div className="space-y-6">
      {Object.entries(results).length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">インタビュー結果がありません</p>
        </div>
      ) : (
        Object.entries(results).map(([personaName, answers]) => {
          console.log('Processing persona:', personaName, 'answers:', answers);
          const persona = personas.find(p => p.name === personaName);
          
          return (
            <div key={personaName} className="bg-white border rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-gray-200">
                  <img 
                    src={getAvatarUrl(personaName)} 
                    alt={personaName}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{personaName}</h3>
                  <p className="text-sm text-gray-500">との会話</p>
                </div>
              </div>

              <div className="space-y-4">
                {!answers || answers.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">回答がありません</p>
                ) : (
                  Array.isArray(answers) ? answers.map((answer, index) => {
                    console.log(`Answer ${index}:`, answer, typeof answer);
                    
                    // 新しいデータ構造に対応
                    if (typeof answer === 'object' && answer !== null) {
                      // 新しい形式: {question, main_answer, follow_ups}
                      if (answer.question && answer.main_answer) {
                        return (
                          <div key={index} className="space-y-3">
                            {/* メイン質問（ロボット） */}
                            <div className="flex items-start space-x-3">
                              <RobotIcon />
                              <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[80%]">
                                <p className="text-gray-800">{answer.question}</p>
                              </div>
                            </div>

                            {/* メイン回答（ペルソナ） */}
                            <div className="flex items-start space-x-3 justify-end">
                              <div className="bg-blue-500 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-[80%]">
                                <p>{answer.main_answer}</p>
                              </div>
                              <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-gray-200">
                                <img 
                                  src={getAvatarUrl(personaName)} 
                                  alt={personaName}
                                  className="w-full h-full object-cover"
                                />
                              </div>
                            </div>

                            {/* フォローアップ質問と回答 */}
                            {answer.follow_ups && answer.follow_ups.map((followUp: any, followIndex: number) => (
                              <div key={`follow-${followIndex}`} className="space-y-3 ml-4">
                                {/* フォローアップ質問（ロボット） */}
                                <div className="flex items-start space-x-3">
                                  <RobotIcon />
                                  <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[80%]">
                                    <p className="text-gray-800">{followUp.question}</p>
                                  </div>
                                </div>

                                {/* フォローアップ回答（ペルソナ） */}
                                <div className="flex items-start space-x-3 justify-end">
                                  <div className="bg-blue-500 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-[80%]">
                                    <p>{followUp.answer}</p>
                                  </div>
                                  <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-gray-200">
                                    <img 
                                      src={getAvatarUrl(personaName)} 
                                      alt={personaName}
                                      className="w-full h-full object-cover"
                                    />
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        );
                      }
                      // 古い形式: {question, response}
                      else if (answer.question && answer.response) {
                        return (
                          <div key={index} className="space-y-3">
                            {/* 質問（ロボット） */}
                            <div className="flex items-start space-x-3">
                              <RobotIcon />
                              <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[80%]">
                                <p className="text-gray-800">{answer.question}</p>
                              </div>
                            </div>

                            {/* 回答（ペルソナ） */}
                            <div className="flex items-start space-x-3 justify-end">
                              <div className="bg-blue-500 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-[80%]">
                                <p>{answer.response}</p>
                              </div>
                              <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-gray-200">
                                <img 
                                  src={getAvatarUrl(personaName)} 
                                  alt={personaName}
                                  className="w-full h-full object-cover"
                                />
                              </div>
                            </div>
                          </div>
                        );
                      }
                      // オブジェクトだが既知の形式でない場合
                      else {
                        return (
                          <div key={index} className="bg-yellow-50 border border-yellow-200 rounded p-3">
                            <p className="text-yellow-800 text-sm">未対応のデータ形式:</p>
                            <pre className="text-xs text-yellow-700 mt-1">{JSON.stringify(answer, null, 2)}</pre>
                          </div>
                        );
                      }
                    }
                    // 文字列形式（従来形式）
                    else if (typeof answer === 'string') {
                      const parts = answer.split('\n回答: ');
                      const question = parts[0].replace(/^\d+\.\s*/, ''); // 番号を削除
                      const response = parts[1] || '';

                      return (
                        <div key={index} className="space-y-3">
                          {/* 質問（ロボット） */}
                          <div className="flex items-start space-x-3">
                            <RobotIcon />
                            <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[80%]">
                              <p className="text-gray-800">{question}</p>
                            </div>
                          </div>

                          {/* 回答（ペルソナ） */}
                          <div className="flex items-start space-x-3 justify-end">
                            <div className="bg-blue-500 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-[80%]">
                              <p>{response}</p>
                            </div>
                            <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-gray-200">
                              <img 
                                src={getAvatarUrl(personaName)} 
                                alt={personaName}
                                className="w-full h-full object-cover"
                              />
                            </div>
                          </div>
                        </div>
                      );
                    }
                    // その他の型
                    else {
                      return (
                        <div key={index} className="bg-red-50 border border-red-200 rounded p-3">
                          <p className="text-red-800 text-sm">不明なデータ型: {typeof answer}</p>
                          <pre className="text-xs text-red-700 mt-1">{String(answer)}</pre>
                        </div>
                      );
                    }
                  }) : <p className="text-red-500">Answers is not an array: {typeof answers}</p>
                )}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};

export default InterviewResults;
