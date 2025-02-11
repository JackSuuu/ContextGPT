'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import { FiArrowLeft } from 'react-icons/fi';

export default function SummaryPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<{ content: string; filename: string } | null>(null);

  useEffect(() => {
    const storedSummary = localStorage.getItem('latestSummary');
    if (!storedSummary) {
      router.push('/');
      return;
    }
    setSummary(JSON.parse(storedSummary));
  }, [router]);

  return (
    <div className="summary-container">
      <button 
        onClick={() => {
          localStorage.removeItem('latestSummary');
          router.push('/');
        }}
        className="back-button"
      >
        <FiArrowLeft /> Back to Chat
      </button>

      {summary && (
        <div className="summary-content">
          <h2>{summary.filename} Summary</h2>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight]}
            components={{
              code({ className, children, ...props }) {
                return (
                  <code className={className} {...props}>
                    {children}
                  </code>
                )
              }
            }}
          >
            {summary.content}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
}