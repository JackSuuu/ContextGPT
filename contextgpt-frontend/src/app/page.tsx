"use client";

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import { FiGithub } from 'react-icons/fi';
import { FaFileUpload } from "react-icons/fa";
import { IoSend } from "react-icons/io5";
import { IoMdCloseCircle } from "react-icons/io";
import { FaHeart } from "react-icons/fa";
import { FaFilePdf } from "react-icons/fa";
import { FaRocketchat } from "react-icons/fa";
import { FaHistory } from "react-icons/fa";
import { IoIosSettings } from "react-icons/io";
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Message {
  content: string;
  type: 'user' | 'bot';
}

export default function Home() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const simulationTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [hasSummary, setHasSummary] = useState(false); // New state for summary check

  // Check for summary on client side
  useEffect(() => {
    const summary = localStorage.getItem('latestSummary');
    setHasSummary(!!summary);
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Cleanup timeouts on unmount
  useEffect(() => () => {
    if (simulationTimeoutRef.current) {
      clearTimeout(simulationTimeoutRef.current);
    }
  }, []);

  // Toggle sidebar
  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

  const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const userQuery = query.trim();
    if (!userQuery) return;

    setMessages(prev => [
      ...prev,
      { content: userQuery, type: 'user' },
      { content: '', type: 'bot' }
    ]);
    
    setQuery('');

    try {
        if (simulationTimeoutRef.current) {
            clearTimeout(simulationTimeoutRef.current);
        }

      const response = await axios.post(
        'https://unigpt-backend-git-79205187327.europe-west2.run.app/api/generate_output/',
        { query: userQuery, use_groq: true },
        { headers: { 'Content-Type': 'application/json' } }
      );

      simulateStreamingResponse(response.data.response);
    } catch (error) {
      handleApiError(error);
    }
  };

  const simulateStreamingResponse = (botResponse: string) => {
    let i = 0;
    const updateMessage = () => {
      if (i < botResponse.length) {
        setMessages(prev => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          return lastMessage?.type === 'bot' 
            ? [...prev.slice(0, -1), { ...lastMessage, content: botResponse.substring(0, i + 1) }]
            : prev;
        });
        i++;
        simulationTimeoutRef.current = setTimeout(updateMessage, 20);
      }
    };
    updateMessage();
  };

  const handleApiError = (error: unknown) => {
    console.error('Error:', error);
    setMessages(prev => {
      const newMessages = [...prev];
      const lastMessage = newMessages[newMessages.length - 1];
      return lastMessage?.type === 'bot'
        ? [...prev.slice(0, -1), { ...lastMessage, content: '⚠️ Error processing request. Please try again.' }]
        : prev;
    });
  };

  const handleFileUpload = async (selectedFile: File) => {
    if (!selectedFile) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(
        'https://unigpt-backend-git-79205187327.europe-west2.run.app/api/upload_pdf/',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      localStorage.setItem('latestSummary', JSON.stringify({
        content: response.data.summary,
        filename: selectedFile.name
      }));
      setHasSummary(true);

      setMessages(prev => [
        ...prev,
        { 
          content: `✅ File "${selectedFile.name}" processed successfully!\n${response.data.summary}`,
          type: 'bot' 
        }
      ]);
    } catch (error) {
      console.error('Upload failed:', error);
      setMessages(prev => [
        ...prev,
        { 
          content: '❌ Failed to process PDF. Please ensure:\n- It\'s a valid PDF file\n- Contains extractable text\n- File size < 10MB',
          type: 'bot' 
        }
      ]);
    } finally {
      setIsUploading(false);
      setFile(null);
    }
  };

  return (
    <div className="container">
      <div className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <nav>
          <button className="close-button" onClick={toggleSidebar}>
            <IoMdCloseCircle />
          </button>
          <ul>
            <li>
              <button
                onClick={() => router.push('/summary')}
                disabled={!hasSummary}
                className="summary-button"
              >
                <FaFilePdf /> PDF Summary
              </button>
            </li>
            <li>
              <button onClick={() => router.push('/')}>
                <FaRocketchat /> New Chat
              </button>
            </li>
            <li><button><FaHistory /> History</button></li>
            <li><button><IoIosSettings /> Settings</button></li>
          </ul>
          <p className='love-message'>Made with <FaHeart /> by context-gpt team</p>
          <Link href="https://github.com/JackSuuu/ContextGPT" target="_blank" className="github-icon-menu">
            <FiGithub size={24} />
          </Link>
        </nav>
      </div>

      <header>
        <button className="menu-button" onClick={toggleSidebar}>
          ☰
        </button>
        <h1>ContextGPT</h1>
        <p id="heading-description" ><b>context-based AI agent</b></p>
        <Link href="https://github.com/JackSuuu/ContextGPT" target="_blank" className="github-icon">
          <FiGithub size={24} />
        </Link>
      </header>

      <div className="chatbox">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}-message`}>
            {msg.type === 'bot' ? (
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
                {msg.content}
              </ReactMarkdown>
            ) : (
              msg.content
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className='input-container'>
        <form onSubmit={handleSendMessage}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Message ContextGPT..."
            disabled={isUploading}
          />
          <button type="submit" disabled={isUploading}>
            <IoSend style={{ position: "absolute", right: "12px", top: "16px"}} />
          </button>
        </form>

        <div className="file-upload">
          <input 
            type="file" 
            id="file-upload"
            onChange={(e) => {
              const selectedFile = e.target.files?.[0];
              if (selectedFile?.type === 'application/pdf') {
                handleFileUpload(selectedFile);
              } else {
                setMessages(prev => [...prev, {
                  content: '❌ Invalid file type. Please upload a PDF document.',
                  type: 'bot'
                }]);
              }
            }}
            accept="application/pdf"
            disabled={isUploading}
          />
          <label htmlFor="file-upload" className={isUploading ? 'disabled' : ''}>
            <FaFileUpload />
            {isUploading ? (
              <div className="upload-status">
                Processing PDF...
                <div className="loading-spinner"></div>
              </div>
            ) : (
              `${file ? file.name : "Upload PDF document"}`
            )}
          </label>
        </div>
      </div>
    </div>
  );
}