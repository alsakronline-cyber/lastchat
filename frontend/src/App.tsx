import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './pages/Login'; // Make sure this path exists
// import { ChatLayout } from './pages/ChatLayout'; // Placeholder

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        return <div className="min-h-screen flex items-center justify-center"><div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div></div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
};

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<div className="flex items-center justify-center min-h-screen">Signup Coming Soon</div>} />

                    <Route path="/" element={
                        <ProtectedRoute>
                            {/* <ChatLayout /> */}
                            <div className="p-10 text-center">
                                <h1 className="text-4xl font-bold mb-4">Chat Interface Here</h1>
                                <p className="text-gray-400">Under construction...</p>
                                <button onClick={() => { localStorage.removeItem('token'); window.location.reload(); }} className="mt-8 btn-primary">Logout</button>
                            </div>
                        </ProtectedRoute>
                    } />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
