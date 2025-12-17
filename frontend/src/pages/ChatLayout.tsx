import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, Plus, MessageSquare, Menu, X, Send, Bot, User as UserIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const ChatLayout = () => {
    const { user, logout } = useAuth();
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [messages, setMessages] = useState<any[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Mock chat history for sidebar
    const history = [
        { id: 1, title: 'Previous Conversation 1', date: 'Today' },
        { id: 2, title: 'Quote for SICK Sensor', date: 'Yesterday' },
    ];

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { role: 'user', content: input };
        setMessages([...messages, userMsg]);
        setInput('');
        setIsLoading(true);

        // TODO: Connect to actual backend API
        setTimeout(() => {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "I'm the AI Assistant. Backend integration is coming next!"
            }]);
            setIsLoading(false);
        }, 1000);
    };

    return (
        <div className="flex h-screen overflow-hidden bg-dark-900">
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
                transition={{ type: "spring", damping: 20 }}
                className={`fixed md:relative z-30 w-72 h-full glass-panel border-r border-white/5 flex flex-col ${!isSidebarOpen && 'hidden md:flex md:w-0 md:opacity-0 md:overflow-hidden'}`}
            >
                <div className="p-4 border-b border-white/10 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                            <Bot className="w-5 h-5 text-white" />
                        </div>
                        <span className="font-bold text-lg tracking-tight">AI Engine</span>
                    </div>
                    <button onClick={() => setIsSidebarOpen(false)} className="md:hidden p-1 hover:bg-white/10 rounded">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="p-4">
                    <button className="w-full btn-primary flex items-center justify-center gap-2 mb-6">
                        <Plus className="w-4 h-4" />
                        New Chat
                    </button>

                    <div className="space-y-2">
                        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">History</h3>
                        {history.map((item) => (
                            <button key={item.id} className="w-full text-left p-3 rounded-lg hover:bg-white/5 transition-colors flex items-center gap-3 text-gray-300 hover:text-white group">
                                <MessageSquare className="w-4 h-4 text-gray-500 group-hover:text-primary transition-colors" />
                                <span className="truncate text-sm">{item.title}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="mt-auto p-4 border-t border-white/10">
                    <div className="flex items-center gap-3 mb-4 px-2">
                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                            {user?.full_name?.charAt(0) || 'U'}
                        </div>
                        <div className="truncate">
                            <p className="text-sm font-medium">{user?.full_name || 'User'}</p>
                            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                        </div>
                    </div>
                    <button onClick={logout} className="w-full flex items-center gap-2 p-2 text-sm text-gray-400 hover:text-white hover:bg-red-500/10 hover:text-red-400 rounded-lg transition-colors">
                        <LogOut className="w-4 h-4" />
                        Sign Out
                    </button>
                </div>
            </motion.aside>

            {/* Main Chat Area */}
            <main className="flex-1 flex flex-col w-full relative">
                {/* Header */}
                <header className="h-16 border-b border-white/5 flex items-center px-4 justify-between bg-dark-900/50 backdrop-blur-sm sticky top-0 z-10">
                    <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                        <Menu className="w-5 h-5" />
                    </button>
                    <span className="text-sm text-gray-500">v1.0.0</span>
                </header>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth">
                    {messages.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-50">
                            <Bot className="w-16 h-16 text-primary mb-4" />
                            <h2 className="text-2xl font-bold mb-2">How can I help you today?</h2>
                            <p className="text-gray-400 max-w-md">
                                I can help you find SICK products, generate quotations, or answer technical questions.
                            </p>
                        </div>
                    ) : (
                        messages.map((msg, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div className={`p-4 rounded-2xl max-w-[80%] ${msg.role === 'user' ? 'bg-primary text-white rounded-br-none' : 'glass-panel rounded-bl-none'}`}>
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
