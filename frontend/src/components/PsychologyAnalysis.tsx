import React from 'react';

interface PsychologyAnalysisProps {
  analysis: string;
  isLoading?: boolean;
}

const PsychologyAnalysis: React.FC<PsychologyAnalysisProps> = ({ 
  analysis, 
  isLoading = false 
}) => {
  if (isLoading) {
    return (
      <div className="my-3 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200 animate-pulse">
        <div className="flex items-center gap-2 text-sm text-purple-600">
          <div className="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
          <span>深層心理を分析中...</span>
        </div>
      </div>
    );
  }

  if (!analysis) return null;

  // 分析結果をパース
  const parseAnalysis = (text: string) => {
    const sections: { icon: string; title: string; content: string }[] = [];
    
    const patterns = [
      { icon: '🧠', title: '本音', key: '本音:' },
      { icon: '💭', title: '感情', key: '感情:' },
      { icon: '🎯', title: '購買影響', key: '購買影響:' },
      { icon: '💡', title: '示唆', key: '示唆:' }
    ];

    patterns.forEach(({ icon, title, key }) => {
      const regex = new RegExp(`${icon}\\s*${key}\\s*([^🧠💭🎯💡]+)`, 'i');
      const match = text.match(regex);
      if (match && match[1]) {
        sections.push({
          icon,
          title,
          content: match[1].trim()
        });
      }
    });

    return sections;
  };

  const sections = parseAnalysis(analysis);

  return (
    <div className="my-3 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <div className="flex items-center justify-center w-8 h-8 bg-purple-600 text-white rounded-full text-sm font-bold">
          🧠
        </div>
        <h4 className="font-semibold text-purple-900 text-sm">深層心理分析</h4>
        <span className="text-xs text-purple-600 bg-purple-100 px-2 py-0.5 rounded-full">
          AI分析
        </span>
      </div>
      
      <div className="space-y-2">
        {sections.length > 0 ? (
          sections.map((section, index) => (
            <div 
              key={index} 
              className="flex gap-2 text-sm bg-white/70 p-2 rounded border border-purple-100"
            >
              <span className="text-lg flex-shrink-0">{section.icon}</span>
              <div className="flex-1">
                <span className="font-medium text-purple-800">{section.title}: </span>
                <span className="text-gray-700">{section.content}</span>
              </div>
            </div>
          ))
        ) : (
          // フォールバック: パースできない場合は全文表示
          <div className="text-sm text-gray-700 whitespace-pre-wrap">
            {analysis}
          </div>
        )}
      </div>
      
      <div className="mt-3 pt-2 border-t border-purple-200">
        <p className="text-xs text-purple-600 italic">
          💡 この分析は、発言の裏にある心理を推測したものです。マーケティング戦略の参考にご活用ください。
        </p>
      </div>
    </div>
  );
};

export default PsychologyAnalysis;

