import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, Plus, MessageSquare, Menu, X, Send, Bot, User as UserIcon, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { RequestQuoteModal } from '../components/RequestQuoteModal';

export const ChatLayout = () => {
    const { user, logout } = useAuth();
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [isQuoteModalOpen, setIsQuoteModalOpen] = useState(false);
    const [messages, setMessages] = useState<any[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const [sessions, setSessions] = useState<any[]>([]);
    const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);

    // Initial load: Fetch sessions
    React.useEffect(() => {
        fetchSessions();
    }, []);

    // Load messages when session changes
    React.useEffect(() => {
        if (currentSessionId) {
            fetchMessages(currentSessionId);
        } else {
            setMessages([]);
        }
    }, [currentSessionId]);

    const fetchSessions = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/chat/sessions', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setSessions(data);
            }
        } catch (err) {
            console.error("Failed to fetch sessions", err);
        }
    };

    const fetchMessages = async (sessionId: number) => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/v1/chat/sessions/${sessionId}/messages`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setMessages(data);
            }
        } catch (err) {
            console.error("Failed to fetch messages", err);
        }
    };

    const createNewSession = async (firstMessage: string) => {
        try {
            const token = localStorage.getItem('token');
            // Create session with first message as title (truncated)
            const title = firstMessage.substring(0, 30) + (firstMessage.length > 30 ? '...' : '');
            const res = await fetch('/api/v1/chat/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ title })
            });
            if (res.ok) {
                const newSession = await res.json();
                setSessions([newSession, ...sessions]);
                setCurrentSessionId(newSession.id);
                return newSession.id;
            }
        } catch (err) {
            console.error("Failed to create session", err);
        }
        return null;
    };

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const messageContent = input;
        setInput('');
        setIsLoading(true);

        // Optimistic update
        const userMsg = { role: 'user', content: messageContent, timestamp: new Date().toISOString() };
        setMessages(prev => [...prev, userMsg]);

        try {
            let sessionId = currentSessionId;
            if (!sessionId) {
                sessionId = await createNewSession(messageContent);
            }

            if (sessionId) {
                const token = localStorage.getItem('token');
                const res = await fetch(`/api/v1/chat/sessions/${sessionId}/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        role: 'user',
                        content: messageContent,
                        timestamp: new Date().toISOString()
                    })
                });

                if (res.ok) {
                    const data = await res.json();
                    // Add AI response
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: data.response,
                        timestamp: new Date().toISOString()
                    }]);
                    // Refresh sessions to update "Last Updated" order if needed
                    fetchSessions();
                }
            }
        } catch (error) {
            console.error("Chat error:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex h-screen overflow-hidden bg-dark-900">
            <RequestQuoteModal isOpen={isQuoteModalOpen} onClose={() => setIsQuoteModalOpen(false)} />

            {/* Mobile Sidebar Overlay */}
            <AnimatePresence>
                {isSidebarOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setIsSidebarOpen(false)}
                        className="md:hidden fixed inset-0 bg-black/50 z-20"
                    />
                )}
            </AnimatePresence>

            {/* Sidebar */}
            <motion.aside
                initial={{ x: -300 }}
                animate={{ x: isSidebarOpen ? 0 : -300 }}
                transition={{ type: "spring", damping: 25, stiffness: 200 }}
                className={`fixed md:relative z-30 w-72 h-full glass-panel border-r border-white/5 flex flex-col ${!isSidebarOpen && 'hidden md:flex md:w-0 md:opacity-0 md:overflow-hidden'}`}
            >
                <div className="p-6 border-b border-white/5 flex items-center justify-between bg-white/0">
                    <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-blue-600 shadow-lg shadow-primary/20 flex items-center justify-center">
                            <Bot className="w-6 h-6 text-white" />
                        </div>
                        <span className="font-bold text-xl tracking-tight text-gradient-primary">AI Engine</span>
                    </div>
                    <button onClick={() => setIsSidebarOpen(false)} className="md:hidden p-1 hover:bg-white/10 rounded-lg">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="p-4 flex-1 overflow-y-auto custom-scrollbar">
                    <button
                        onClick={() => { setCurrentSessionId(null); setMessages([]); }}
                        className="w-full btn-primary flex items-center justify-center gap-2 mb-8 py-3 text-sm tracking-wide uppercase font-bold"
                    >
                        <Plus className="w-4 h-4" />
                        New Chat
                    </button>

                    <div className="space-y-1">
                        <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-4 pl-2">History</h3>
                        {sessions.map((session) => (
                            <button
                                key={session.id}
                                onClick={() => setCurrentSessionId(session.id)}
                                className={`w-full text-left p-3 rounded-xl transition-all duration-200 flex items-center gap-3 group border border-transparent ${currentSessionId === session.id
                                        ? 'bg-white/10 text-white border-white/10 shadow-lg'
                                        : 'text-gray-400 hover:text-white glass-panel-hover'
                                    }`}
                            >
                                <MessageSquare className={`w-4 h-4 transition-colors ${currentSessionId === session.id ? 'text-primary' : 'text-gray-600 group-hover:text-primary'}`} />
                                <span className="truncate text-sm font-medium">{session.title}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="p-4 border-t border-white/5 bg-black/20">
                    <div className="flex items-center gap-3 mb-4 p-2 rounded-xl hover:bg-white/5 transition-colors cursor-pointer">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-gray-700 to-gray-600 border border-white/10 flex items-center justify-center text-white font-bold shadow-inner">
                            {user?.full_name?.charAt(0) || 'U'}
                        </div>
                        <div className="truncate flex-1">
                            <p className="text-sm font-semibold text-white">{user?.full_name || 'User'}</p>
                            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                        </div>
                    </div>
                    <button onClick={logout} className="w-full flex items-center gap-2 p-2.5 text-sm font-medium text-gray-400 hover:text-white hover:bg-red-500/10 hover:text-red-400 rounded-lg transition-all">
                        <LogOut className="w-4 h-4" />
                        Sign Out
                    </button>
                </div>
            </motion.aside>

            {/* Main Chat Area */}
            <main className="flex-1 flex flex-col w-full relative bg-radial-gradient">
                {/* Header */}
                <header className="h-20 border-b border-white/5 flex items-center px-6 justify-between bg-dark-900/80 backdrop-blur-md sticky top-0 z-10 transition-all">
                    <div className="flex items-center gap-4">
                        <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-white/5 rounded-xl transition-colors text-gray-400 hover:text-white">
                            <Menu className="w-6 h-6" />
                        </button>
                    </div>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setIsQuoteModalOpen(true)}
                            className="btn-secondary text-sm flex items-center gap-2 px-4 py-2 hover:border-primary/50 hover:text-primary transition-all group"
                        >
                            <FileText className="w-4 h-4 group-hover:scale-110 transition-transform" />
                            Request Quote
                        </button>
                    </div>
                </header>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 scroll-smooth custom-scrollbar">
                    {messages.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-0 animate-fade-in" style={{ animationFillMode: 'forwards' }}>
                            <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-primary/20 to-transparent flex items-center justify-center mb-8 animate-float">
                                <Bot className="w-12 h-12 text-primary" />
                            </div>
                            <h2 className="text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-500">
                                Global Industrial AI
                            </h2>
                            <p className="text-gray-400 max-w-lg text-lg leading-relaxed">
                                I am your SICK sensor expert. Ask me about products, technical specifications, or request a formal quotation.
                            </p>
                        </div>
                    ) : (
                        messages.map((msg, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4, delay: idx * 0.1 }}
                                className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div className={`p-5 rounded-3xl max-w-[85%] md:max-w-[75%] shadow-xl backdrop-blur-sm border border-white/5 leading-relaxed ${msg.role === 'user'
                                        ? 'bg-gradient-to-br from-primary to-blue-600 text-white rounded-br-none'
                                        : 'glass-panel rounded-bl-none text-gray-100'
                                    }`}>
                                    {msg.content}
                                </div>
                            </motion.div>
                        ))
                    )}
                    {isLoading && (
                        <div className="flex justify-start">
                            <div className="glass-panel p-4 rounded-2xl rounded-bl-none flex gap-2 items-center">
                                <span className="w-2 h-2 bg-primary rounded-full animate-bounce"></span>
                                <span className="w-2 h-2 bg-primary rounded-full animate-bounce delay-75"></span>
                                <span className="w-2 h-2 bg-primary rounded-full animate-bounce delay-150"></span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-white/5 bg-dark-900/50 backdrop-blur-sm">
                    <form onSubmit={handleSend} className="max-w-4xl mx-auto relative flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type a message..."
                            className="flex-1 input-field pr-12"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="absolute right-2 top-1.5 p-1.5 bg-primary/20 text-primary hover:bg-primary hover:text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </form>
                    <div className="text-center mt-2 text-xs text-gray-500">
                        AI can make mistakes. Please verify important information.
                    </div>
                </div>
            </main>
        </div>
    );
};
