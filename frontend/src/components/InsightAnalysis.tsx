import React, { useState } from 'react';

interface InsightAnalysisProps {
  analysis: string;
  title?: string;
}

const InsightAnalysis: React.FC<InsightAnalysisProps> = ({ 
  analysis, 
  title = "インサイト分析結果" 
}) => {
  // Markdownの見出しを解析してセクション分けする
  const parseAnalysis = (text: string) => {
    // 「*」を削除
    const cleanText = text.replace(/\*/g, '');
    
    const sections: { title: string; content: string; id: string }[] = [];
    const lines = cleanText.split('\n');
    let currentSection: { title: string; content: string; id: string } | null = null;

    lines.forEach((line) => {
      // ### で始まる見出し（3つのハッシュ）を優先的に検出
      const markdownHeading3 = line.match(/^###\s+(.+)$/);
      const markdownHeading2 = line.match(/^##\s+(.+)$/);
      
      if (markdownHeading3 || markdownHeading2) {
        if (currentSection && currentSection.content.trim()) {
          sections.push(currentSection);
        }
        
        let title = '';
        if (markdownHeading3) {
          title = markdownHeading3[1].trim();
        } else if (markdownHeading2) {
          title = markdownHeading2[1].trim();
        }
        
        const id = title.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '-');
        currentSection = { title, content: '', id };
      } else if (currentSection) {
        currentSection.content += line + '\n';
      } else if (line.trim() && !line.includes('詳細インサイト分析レポート')) {
        // 最初のセクション（見出しなし、ただし「詳細インサイト分析レポート」は除外）
        if (!currentSection) {
          currentSection = { title: '概要', content: line + '\n', id: 'overview' };
        } else {
          currentSection.content += line + '\n';
        }
      }
    });

    if (currentSection && currentSection.content.trim()) {
      sections.push(currentSection);
    }

    return sections.filter(section => 
      section.content.trim().length > 0 && 
      !section.title.includes('詳細インサイト分析レポート')
    );
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
    if (title.includes('ヒートマップ') || title.includes('四象限') || title.includes('象限')) return '📊';
    if (title.includes('戦略') || title.includes('示唆')) return '💡';
    return '📋';
  };

  // コンテンツをレンダリングする関数（コードブロックやリストを適切に処理）
  const renderContent = (content: string) => {
    const lines = content.split('\n');
    const elements: JSX.Element[] = [];
    let inCodeBlock = false;
    let codeBlockLines: string[] = [];
    let currentIndex = 0;

    lines.forEach((line, index) => {
      // コードブロックの開始・終了を検出
      if (line.trim().startsWith('```')) {
        if (inCodeBlock) {
          // コードブロックの終了
          elements.push(
            <pre key={`code-${currentIndex}`} className="bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto my-4">
              <code>{codeBlockLines.join('\n')}</code>
            </pre>
          );
          codeBlockLines = [];
          inCodeBlock = false;
          currentIndex++;
        } else {
          // コードブロックの開始
          inCodeBlock = true;
        }
        return;
      }

      if (inCodeBlock) {
        codeBlockLines.push(line);
      } else if (line.trim().startsWith('■ ')) {
        // リスト項目（■で始まる行）
        elements.push(
          <div key={`list-${currentIndex}-${index}`} className="flex items-start space-x-2 mb-2">
            <span className="text-blue-600 font-bold">■</span>
            <span>{line.trim().substring(2)}</span>
          </div>
        );
        currentIndex++;
      } else if (line.trim().startsWith('- ')) {
        // リスト項目（-で始まる行）
        elements.push(
          <div key={`list-${currentIndex}-${index}`} className="flex items-start space-x-2 mb-2 pl-4">
            <span className="text-gray-600">•</span>
            <span>{line.trim().substring(2)}</span>
          </div>
        );
        currentIndex++;
      } else if (line.trim()) {
        // 通常のテキスト行
        elements.push(
          <p key={`text-${currentIndex}-${index}`} className="mb-2">
            {line}
          </p>
        );
        currentIndex++;
      }
    });

    // コードブロックが閉じられていない場合の処理
    if (inCodeBlock && codeBlockLines.length > 0) {
      elements.push(
        <pre key={`code-${currentIndex}`} className="bg-gray-800 text-gray-100 p-4 rounded-lg overflow-x-auto my-4">
          <code>{codeBlockLines.join('\n')}</code>
        </pre>
      );
    }

    return <div className="space-y-2">{elements}</div>;
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
        <div className="space-y-4">
          {sections.map((section, index) => (
            <div
              key={section.id}
              className={`border-2 rounded-xl p-6 ${getSectionColor(index)}`}
            >
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-2xl">{getSectionIcon(section.title)}</span>
                <h3 className="font-semibold text-gray-900 text-lg">
                  {section.title}
                </h3>
              </div>
              
              <div className="text-sm text-gray-700 leading-relaxed">
                {renderContent(section.content.trim())}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InsightAnalysis;
