import React, { useState } from 'react';

interface InsightAnalysisProps {
  analysis: string;
  title?: string;
}

const InsightAnalysis: React.FC<InsightAnalysisProps> = ({ 
  analysis, 
  title = "インサイト分析結果" 
}) => {
  const [activeSection, setActiveSection] = useState<string | null>(null);

  // Markdownの見出しを解析してセクション分けする
  const parseAnalysis = (text: string) => {
    const sections: { title: string; content: string; id: string }[] = [];
    const lines = text.split('\n');
    let currentSection: { title: string; content: string; id: string } | null = null;

    lines.forEach((line) => {
      // ## で始まる見出しを検出
      if (line.startsWith('## ')) {
        if (currentSection) {
          sections.push(currentSection);
        }
        const title = line.replace('## ', '').trim();
        const id = title.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '-');
        currentSection = { title, content: '', id };
      } else if (currentSection) {
        currentSection.content += line + '\n';
      } else if (line.trim()) {
        // 最初のセクション（見出しなし）
        if (!currentSection) {
          currentSection = { title: '概要', content: line + '\n', id: 'overview' };
        } else {
          currentSection.content += line + '\n';
        }
      }
    });

    if (currentSection) {
      sections.push(currentSection);
    }

    return sections;
  };

  const sections = parseAnalysis(analysis);

  const getSectionIcon = (title: string) => {
    if (title.includes('ベネフィット') || title.includes('共感')) return '💝';
    if (title.includes('購買') || title.includes('購入')) return '🛒';
    if (title.includes('理由') || title.includes('阻害')) return '⚠️';
    if (title.includes('インサイト') || title.includes('裏側')) return '🔍';
    if (title.includes('競合') || title.includes('比較')) return '⚖️';
    if (title.includes('ターゲット') || title.includes('顧客')) return '🎯';
    if (title.includes('価格')) return '💰';
    if (title.includes('ヒートマップ') || title.includes('四象限')) return '📊';
    if (title.includes('戦略') || title.includes('示唆')) return '💡';
    return '📋';
  };

  const getSectionColor = (index: number) => {
    const colors = [
      'border-blue-200 bg-blue-50',
      'border-green-200 bg-green-50',
      'border-yellow-200 bg-yellow-50',
      'border-red-200 bg-red-50',
      'border-purple-200 bg-purple-50',
      'border-indigo-200 bg-indigo-50',
      'border-pink-200 bg-pink-50',
      'border-gray-200 bg-gray-50',
      'border-orange-200 bg-orange-50'
    ];
    return colors[index % colors.length];
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
        <p className="text-gray-600">各項目をクリックして詳細を確認できます</p>
      </div>

      {sections.length === 0 ? (
        <div className="bg-white p-6 rounded-lg border">
          <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
            {analysis}
          </div>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sections.map((section, index) => (
            <div
              key={section.id}
              className={`border-2 rounded-xl p-4 cursor-pointer transition-all duration-200 hover:shadow-md ${
                getSectionColor(index)
              } ${
                activeSection === section.id ? 'ring-2 ring-blue-400' : ''
              }`}
              onClick={() => setActiveSection(activeSection === section.id ? null : section.id)}
            >
              <div className="flex items-center space-x-3 mb-3">
                <span className="text-2xl">{getSectionIcon(section.title)}</span>
                <h3 className="font-semibold text-gray-900 text-sm">
                  {section.title}
                </h3>
                <svg
                  className={`w-4 h-4 text-gray-400 transition-transform ${
                    activeSection === section.id ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
              
              {activeSection === section.id ? (
                <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {section.content.trim()}
                </div>
              ) : (
                <div className="text-xs text-gray-500">
                  クリックして詳細を表示
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {sections.length > 0 && (
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-blue-600">💡</span>
            <h4 className="font-semibold text-blue-900">使い方</h4>
          </div>
          <p className="text-sm text-blue-700">
            各カードをクリックすると詳細な分析内容を確認できます。
            複数のカードを同時に開いて比較することも可能です。
          </p>
        </div>
      )}
    </div>
  );
};

export default InsightAnalysis;
