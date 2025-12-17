import React, { useState } from 'react';
import { X, FileText, Send, Plus, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface RequestQuoteModalProps {
    isOpen: boolean;
    onClose: () => void;
}

interface QuoteItem {
    name: string;
    description?: string;
    quantity: number;
}

export const RequestQuoteModal: React.FC<RequestQuoteModalProps> = ({ isOpen, onClose }) => {
    // Customer Details
    const [customer, setCustomer] = useState({
        name: '',
        company: '',
        email: '',
        phone: ''
    });

    // Items List
    const [items, setItems] = useState<QuoteItem[]>([
        { name: '', description: '', quantity: 1 }
    ]);

    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    // --- Item Handlers ---
    const addItem = () => {
        setItems([...items, { name: '', description: '', quantity: 1 }]);
    };

    const removeItem = (index: number) => {
        if (items.length > 1) {
            setItems(items.filter((_, i) => i !== index));
        }
    };

    const updateItem = (index: number, field: keyof QuoteItem, value: any) => {
        const newItems = [...items];
        newItems[index] = { ...newItems[index], [field]: value };
        setItems(newItems);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const token = localStorage.getItem('token');

            // Construct payload matching backend
            const payload = {
                quotation_id: `Q-${Date.now()}`,
                bill_to: {
                    name: customer.name,
                    company_name: customer.company,
                    address: "Address Placeholder",
                    email: customer.email,
                    phone: customer.phone
                },
                items: items.map(item => ({
                    name: item.name || "Product Item",
                    description: item.description,
                    quantity: Number(item.quantity)
                }))
            };

            const res = await fetch('/api/v1/quotations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Quotation_${payload.quotation_id}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                setSuccess(true);
                setTimeout(() => {
                    setSuccess(false);
                    onClose();
                    // Reset Form
                    setItems([{ name: '', description: '', quantity: 1 }]);
                }, 2000);
            } else {
                console.error("Failed to generate quote");
            }
        } catch (error) {
            console.error("Error submitting quote:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="relative w-full max-w-2xl bg-[#0f1115] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
                    >
                        {/* Header */}
                        <div className="p-6 border-b border-white/10 flex items-center justify-between bg-white/5 shrink-0">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-gradient-to-br from-primary/20 to-blue-500/20 rounded-lg text-primary">
                                    <FileText className="w-5 h-5" />
                                </div>
                                <h2 className="text-xl font-bold text-white">Request Quotation</h2>
                            </div>
                            <button onClick={onClose} className="p-1 text-gray-400 hover:text-white transition-colors">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Body */}
                        <div className="p-6 overflow-y-auto custom-scrollbar">
                            {success ? (
                                <div className="text-center py-12">
                                    <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-500/20 text-green-500 mb-6 animate-float">
                                        <Send className="w-10 h-10" />
                                    </div>
                                    <h3 className="text-2xl font-bold text-white mb-2">Quote Generated!</h3>
                                    <p className="text-gray-400">Your PDF interpretation has been downloaded.</p>
                                </div>
                            ) : (
                                <form onSubmit={handleSubmit} className="space-y-8">
                                    {/* Customer Section */}
                                    <div className="space-y-4">
                                        <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider">Customer Details</h3>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="space-y-2">
                                                <label className="text-xs font-medium text-gray-400">Contact Name</label>
                                                <input
                                                    required
                                                    type="text"
                                                    value={customer.name}
                                                    onChange={e => setCustomer({ ...customer, name: e.target.value })}
                                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-primary/50"
                                                    placeholder="John Doe"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-medium text-gray-400">Company</label>
                                                <input
                                                    required
                                                    type="text"
                                                    value={customer.company}
                                                    onChange={e => setCustomer({ ...customer, company: e.target.value })}
                                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-primary/50"
                                                    placeholder="Acme Inc."
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-medium text-gray-400">Email</label>
                                                <input
                                                    required
                                                    type="email"
                                                    value={customer.email}
                                                    onChange={e => setCustomer({ ...customer, email: e.target.value })}
                                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-primary/50"
                                                    placeholder="john@example.com"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-xs font-medium text-gray-400">Phone</label>
                                                <input
                                                    type="tel"
                                                    value={customer.phone}
                                                    onChange={e => setCustomer({ ...customer, phone: e.target.value })}
                                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-primary/50"
                                                    placeholder="+1 234 567 890"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Items Section */}
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider">Line Items</h3>
                                            <button
                                                type="button"
                                                onClick={addItem}
                                                className="text-xs flex items-center gap-1 text-primary hover:text-primary/80 font-medium transition-colors"
                                            >
                                                <Plus className="w-3 h-3" /> Add Item
                                            </button>
                                        </div>

                                        <div className="space-y-3">
                                            {items.map((item, index) => (
                                                <div key={index} className="flex gap-3 items-start animate-slide-up">
                                                    <div className="flex-1 space-y-2">
                                                        <input
                                                            required
                                                            type="text"
                                                            value={item.name}
                                                            onChange={e => updateItem(index, 'name', e.target.value)}
                                                            className="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary/50 placeholder-gray-600"
                                                            placeholder="Product Name / SKU"
                                                        />
                                                        <input
                                                            type="text"
                                                            value={item.description || ''}
                                                            onChange={e => updateItem(index, 'description', e.target.value)}
                                                            className="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary/50 placeholder-gray-600"
                                                            placeholder="Additional Specs / Description (Optional)"
                                                        />
                                                    </div>
                                                    <div className="w-20">
                                                        <input
                                                            required
                                                            type="number"
                                                            min="1"
                                                            value={item.quantity}
                                                            onChange={e => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                                                            className="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white text-sm text-center focus:outline-none focus:border-primary/50"
                                                        />
                                                    </div>
                                                    <button
                                                        type="button"
                                                        onClick={() => removeItem(index)}
                                                        className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors mt-[1px]"
                                                        title="Remove Item"
                                                        disabled={items.length === 1}
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="w-full btn-primary py-3 rounded-xl flex items-center justify-center gap-2 mt-8 transition-all hover:scale-[1.02]"
                                    >
                                        {loading ? (
                                            <>
                                                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                                Generating Quote...
                                            </>
                                        ) : (
                                            <>
                                                <FileText className="w-4 h-4" />
                                                Generate PDF Quote
                                            </>
                                        )}
                                    </button>
                                </form>
                            )}
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
