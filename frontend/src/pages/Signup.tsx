import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { Lock, Mail, User, Loader2, ArrowRight } from 'lucide-react';

export const Signup = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();
    const API_URL = '/api/v1';

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Register
            await axios.post(`${API_URL}/auth/register`, {
                email,
                password,
                full_name: fullName
            });

            // Auto login after register
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const loginResponse = await axios.post(`${API_URL}/auth/token`, formData);
            login(loginResponse.data.access_token);
            navigate('/');
        } catch (err: any) {
            console.error(err);
            if (err.response && err.response.data && err.response.data.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Registration failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="glass-panel w-full max-w-md p-8 animate-fade-in relative overflow-hidden">
                {/* Decorative background blur */}
                <div className="absolute -top-20 -left-20 w-40 h-40 bg-accent/20 rounded-full blur-3xl"></div>
                <div className="absolute -bottom-20 -right-20 w-40 h-40 bg-primary/20 rounded-full blur-3xl"></div>

                <div className="text-center mb-8 relative z-10">
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                        Create Account
                    </h1>
                    <p className="text-gray-400 mt-2">Join the Industrial AI Engine</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6 relative z-10">
                    {error && (
                        <div className="p-3 rounded bg-red-500/20 border border-red-500/50 text-red-200 text-sm">
                            {error}
                        </div>
                    )}

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300 ml-1">Full Name</label>
                        <div className="relative">
                            <User className="absolute left-3 top-3.5 h-5 w-5 text-gray-500" />
                            <input
                                type="text"
                                required
                                className="input-field pl-10"
                                placeholder="John Doe"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300 ml-1">Email</label>
                        <div className="relative">
                            <Mail className="absolute left-3 top-3.5 h-5 w-5 text-gray-500" />
                            <input
                                type="email"
                                required
                                className="input-field pl-10"
                                placeholder="name@company.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300 ml-1">Password</label>
                        <div className="relative">
                            <Lock className="absolute left-3 top-3.5 h-5 w-5 text-gray-500" />
                            <input
                                type="password"
                                required
                                className="input-field pl-10"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full btn-primary flex items-center justify-center py-3 group"
                    >
                        {loading ? (
                            <Loader2 className="h-5 w-5 animate-spin" />
                        ) : (
                            <>
                                Create Account
                                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                            </>
                        )}
                    </button>

                    <div className="text-center text-sm text-gray-400">
                        Already have an account?{' '}
                        <Link to="/login" className="text-primary hover:text-sky-400 transition-colors">
                            Sign In
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
};
