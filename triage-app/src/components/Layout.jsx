import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, ShieldAlert } from 'lucide-react';
import GooeyNav from './GooeyNav';
import Antigravity from './Antigravity';
import StarBorder from './StarBorder';

const Layout = ({ children }) => {
  const location = useLocation();

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Upload', path: '/upload' },
    { name: 'How It Works', path: '/how-it-works' },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 relative">


      {/* Navbar */}
      <nav className="sticky top-0 z-50 bg-white/70 backdrop-blur-xl border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-20 items-center">
            <Link to="/" className="flex items-center gap-2 group">
              <div className="bg-medical-600 p-2 rounded-lg group-hover:rotate-12 transition-transform">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-slate-900 tracking-tight">
                AI Skin <span className="text-medical-600">Triage</span>
              </span>
            </Link>

            <div className="hidden md:flex">
              <GooeyNav
                items={[
                  { label: "Home", href: "/" },
                  { label: "Upload", href: "/upload" },
                  { label: "How It Works", href: "/how-it-works" },
                ]}
                particleCount={12}
                particleDistances={[60, 5]}
                particleR={80}
                animationTime={500}
                timeVariance={200}
              />
            </div>

            <StarBorder
              as={Link}
              to="/upload"
              color="#ffffff"
              speed="4s"
              thickness={2}
              className="py-0"
            >
              Start Analysis
            </StarBorder>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow relative z-10">
        {children}
      </main>

      {/* Footer Disclaimer */}
      <footer className="sticky bottom-0 z-40 bg-slate-900 text-white py-4 shadow-[0_-4px_20px_rgba(0,0,0,0.1)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-center gap-3">
          <ShieldAlert className="w-5 h-5 text-amber-400 animate-pulse" />
          <p className="text-sm font-medium text-slate-300">
            <span className="text-amber-400 font-bold">⚠️ DISCLAIMER:</span> This tool does NOT provide medical diagnosis. Always consult a professional.
          </p>
        </div>
      </footer>
      
      {/* Real Footer */}
      <footer className="bg-slate-100 border-t border-slate-200 py-12 pb-24 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-12">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-medical-600" />
              <span className="text-lg font-bold text-slate-900">AI Skin Triage Assistant</span>
            </div>
            <p className="text-slate-500 text-sm leading-relaxed">
              Empowering individuals with AI-driven skin risk assessment. Our mission is to facilitate early detection through advanced technology.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">Quick Links</h4>
            <ul className="space-y-2">
              {navLinks.map(link => (
                <li key={link.path}>
                  <Link to={link.path} className="text-slate-500 hover:text-medical-600 text-sm">{link.name}</Link>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">Legal</h4>
            <ul className="space-y-2">
              <li><span className="text-slate-500 text-sm">Privacy Policy</span></li>
              <li><span className="text-slate-500 text-sm">Terms of Service</span></li>
              <li><span className="text-slate-500 text-sm">Medical Disclaimer</span></li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 pt-8 border-t border-slate-200 text-center">
          <p className="text-slate-400 text-xs">© 2024 AI Skin Triage Assistant. All rights reserved.</p>
        </div>
      </footer>

      {/* Foreground Cursor Effect */}
      <div className="fixed inset-0 pointer-events-none z-[9999]">
        <Antigravity
          count={250}
          magnetRadius={8}
          ringRadius={5}
          waveSpeed={0.6}
          waveAmplitude={1.0}
          particleSize={0.8}
          lerpSpeed={0.15}
          color={'#0ea5e9'}
          autoAnimate={true}
          particleVariance={0.5}
          fieldStrength={12}
        />
      </div>
    </div>
  );
};

export default Layout;
