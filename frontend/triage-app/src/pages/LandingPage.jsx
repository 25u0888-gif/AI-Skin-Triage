import React from 'react';
import { Link } from 'react-router-dom';
import { Brain, Flame, ShieldAlert, ShieldCheck, ArrowRight, Upload, Cpu, BarChart3, Stethoscope } from 'lucide-react';
import { motion } from 'framer-motion';
import GradientBlinds from '../components/GradientBlinds';
import LogoLoop from '../components/LogoLoop';
import StarBorder from '../components/StarBorder';
import ScrollReveal from '../components/ScrollReveal';
import ElectricBorder from '../components/ElectricBorder';
import { SiReact, SiTailwindcss, SiVite, SiFramer, SiThreedotjs, SiLucide } from 'react-icons/si';

const FeatureCard = ({ icon: Icon, title, description, delay }) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
    viewport={{ once: true }}
  >
    <ElectricBorder
      color="#0ea5e9"
      speed={1.5}
      chaos={0.15}
      borderRadius={24}
    >
      <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm hover:shadow-xl transition-all group h-full">
        <div className="w-14 h-14 bg-medical-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-medical-600 transition-colors">
          <Icon className="w-7 h-7 text-medical-600 group-hover:text-white transition-colors" />
        </div>
        <h3 className="text-xl font-bold text-slate-900 mb-3">{title}</h3>
        <p className="text-slate-500 leading-relaxed">{description}</p>
      </div>
    </ElectricBorder>
  </motion.div>
);

const Step = ({ number, icon: Icon, title, description }) => (
  <div className="flex flex-col items-center text-center relative px-4">
    <div className="w-16 h-16 bg-white border-2 border-medical-100 rounded-full flex items-center justify-center mb-6 relative z-10 shadow-sm">
      <Icon className="w-8 h-8 text-medical-600" />
      <div className="absolute -top-1 -right-1 w-6 h-6 bg-medical-600 text-white text-xs font-bold rounded-full flex items-center justify-center">
        {number}
      </div>
    </div>
    <h4 className="font-bold text-slate-900 mb-2">{title}</h4>
    <p className="text-sm text-slate-500 leading-relaxed max-w-[200px]">{description}</p>
  </div>
);

const LandingPage = () => {
  return (
    <div className="overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative min-h-[80vh] flex items-center overflow-hidden bg-slate-950">
        {/* Background Effect */}
        <div className="absolute inset-0 z-0 opacity-40">
          <GradientBlinds
            gradientColors={['#0ea5e9', '#0369a1', '#0c4a6e']}
            angle={45}
            noise={0.2}
            blindCount={20}
            blindMinWidth={40}
            spotlightRadius={0.6}
            spotlightSoftness={0.8}
            spotlightOpacity={0.8}
            mouseDampening={0.1}
            distortAmount={0.5}
            shineDirection="right"
            mixBlendMode="screen"
          />
        </div>
        
        <div className="section-container relative z-10 text-center">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <span className="inline-block px-4 py-1.5 bg-medical-500/10 text-medical-400 text-sm font-bold rounded-full mb-8 border border-medical-500/20 backdrop-blur-sm">
              Revolutionizing Skin Health with AI
            </span>
            <h1 className="text-6xl md:text-8xl font-extrabold text-white mb-8 tracking-tight leading-none">
              AI Skin <span className="text-medical-500 italic">Triage</span> Assistant
            </h1>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto mb-12 leading-relaxed">
              Assess skin risk levels instantly using advanced neural networks. A powerful clinical-grade triage tool designed to support early detection and guidance.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-6">
              <StarBorder
                as={Link}
                to="/upload"
                color="#ffffff"
                speed="3s"
                thickness={2}
              >
                Start Analysis <ArrowRight className="w-6 h-6" />
              </StarBorder>
              <Link to="/how-it-works" className="px-10 py-5 bg-white/5 hover:bg-white/10 text-white border border-white/10 rounded-xl font-semibold transition-all active:scale-95 flex items-center justify-center gap-2 text-xl backdrop-blur-sm">
                Learn More
              </Link>
            </div>
          </motion.div>
        </div>
        
        {/* Scroll Indicator */}
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-slate-500">
          <span className="text-xs font-bold uppercase tracking-widest">Scroll to Explore</span>
          <div className="w-1 h-12 bg-gradient-to-b from-medical-500 to-transparent rounded-full"></div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-white relative">
        <div className="section-container">
          <ScrollReveal>
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-5xl font-bold text-slate-900 mb-4 tracking-tight">Advanced Triage Capabilities</h2>
              <p className="text-slate-500 max-w-2xl mx-auto text-lg">Our system leverages state-of-the-art computer vision to provide comprehensive skin analysis.</p>
            </div>
          </ScrollReveal>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard 
              icon={Brain} 
              title="AI Risk Analysis" 
              description="Deep learning models trained on thousands of dermatological images to identify subtle risk patterns."
              delay={0.1}
            />
            <FeatureCard 
              icon={Flame} 
              title="Heatmap Explainability" 
              description="Grad-CAM technology highlights the exact regions that influenced the AI decision for transparency."
              delay={0.2}
            />
            <FeatureCard 
              icon={ShieldAlert} 
              title="Confidence-Based Triage" 
              description="Not just a result, but a confidence score that helps prioritize cases based on uncertainty levels."
              delay={0.3}
            />
            <FeatureCard 
              icon={ShieldCheck} 
              title="Safe Medical Guidance" 
              description="Structured next-step recommendations based on detected risk levels to ensure patient safety."
              delay={0.4}
            />
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-medical-600">
        <ScrollReveal>
          <div className="section-container">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-4xl font-black text-white mb-2">94%</div>
                <div className="text-medical-100 text-sm font-bold uppercase tracking-wider">Model Accuracy</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-black text-white mb-2">150k+</div>
                <div className="text-medical-100 text-sm font-bold uppercase tracking-wider">Images Analyzed</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-black text-white mb-2">&lt; 3s</div>
                <div className="text-medical-100 text-sm font-bold uppercase tracking-wider">Analysis Speed</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-black text-white mb-2">24/7</div>
                <div className="text-medical-100 text-sm font-bold uppercase tracking-wider">Availability</div>
              </div>
            </div>
          </div>
        </ScrollReveal>
      </section>

      {/* How It Works Preview */}
      <section className="py-24 bg-slate-50 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-medical-200 to-transparent"></div>
        <div className="section-container">
          <ScrollReveal>
            <div className="text-center mb-20">
              <h2 className="text-3xl font-bold text-slate-900 mb-4">Simple 4-Step Process</h2>
              <p className="text-slate-500">From upload to guidance in seconds.</p>
            </div>
          </ScrollReveal>
          
          <ScrollReveal delay={0.2}>
            <div className="relative">
              {/* Connecting Line */}
              <div className="hidden lg:block absolute top-8 left-1/2 -translate-x-1/2 w-[70%] h-0.5 bg-medical-100 -z-0"></div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-12 lg:gap-4">
                <Step number="1" icon={Upload} title="Upload Image" description="Clear, focused photo of the skin area of concern." />
                <Step number="2" icon={Cpu} title="AI Model" description="EfficientNet-B0 processes features and patterns." />
                <Step number="3" icon={BarChart3} title="Risk Score" description="Instant classification into Low, Medium, or High risk." />
                <Step number="4" icon={Stethoscope} title="Guidance" description="Immediate next steps and medical precautions." />
              </div>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* Why This Matters */}
      <section className="py-24 bg-white">
        <div className="section-container">
          <ScrollReveal direction="left">
            <div className="bg-slate-900 rounded-[32px] p-8 md:p-16 text-white relative overflow-hidden">
              <div className="absolute -right-20 -top-20 w-80 h-80 bg-medical-500/10 rounded-full blur-3xl"></div>
              <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div>
                  <h2 className="text-3xl md:text-4xl font-bold mb-6">Why Early Triage Matters</h2>
                  <div className="space-y-6">
                    <div className="flex gap-4">
                      <div className="w-10 h-10 rounded-lg bg-medical-500/20 flex items-center justify-center flex-shrink-0">
                        <ArrowRight className="w-5 h-5 text-medical-400" />
                      </div>
                      <div>
                        <h4 className="font-bold text-lg mb-1">Early Detection</h4>
                        <p className="text-slate-400">Identifying potential issues early significantly improves clinical outcomes and treatment success rates.</p>
                      </div>
                    </div>
                    <div className="flex gap-4">
                      <div className="w-10 h-10 rounded-lg bg-medical-500/20 flex items-center justify-center flex-shrink-0">
                        <ArrowRight className="w-5 h-5 text-medical-400" />
                      </div>
                      <div>
                        <h4 className="font-bold text-lg mb-1">Assistive AI</h4>
                        <p className="text-slate-400">Our AI acts as a first-line screening tool, reducing the burden on healthcare systems while providing immediate peace of mind.</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="bg-white/5 border border-white/10 p-8 rounded-2xl backdrop-blur-sm">
                  <blockquote className="text-xl italic text-slate-300 leading-relaxed mb-6">
                    "Artificial Intelligence in dermatology is not here to replace doctors, but to ensure that high-risk cases get the attention they need faster than ever before."
                  </blockquote>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-slate-700"></div>
                    <div>
                      <p className="font-bold">Medical AI Research Team</p>
                      <p className="text-sm text-slate-500">Skin Triage Project</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* Partners / Trust Section */}
      <section className="py-20 bg-slate-50 border-y border-slate-100">
        <div className="section-container">
          <p className="text-center text-slate-400 font-bold uppercase tracking-widest text-xs mb-12">Trusted by Leading Institutions (Mock)</p>
          <div className="flex flex-wrap justify-center gap-12 md:gap-24 opacity-40 grayscale hover:grayscale-0 transition-all">
            <div className="text-2xl font-black text-slate-900 flex items-center gap-2 italic">DermSafe</div>
            <div className="text-2xl font-black text-slate-900 flex items-center gap-2 italic">HealthAI</div>
            <div className="text-2xl font-black text-slate-900 flex items-center gap-2 italic">SkinClinic</div>
            <div className="text-2xl font-black text-slate-900 flex items-center gap-2 italic">BioTech</div>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="py-24 bg-slate-50 border-t border-slate-200">
        <div className="section-container">
          <div className="text-center mb-16">
            <h2 className="text-2xl font-bold text-slate-900 mb-2 tracking-tight">Our Technology Stack</h2>
            <p className="text-slate-500 text-sm">Powered by state-of-the-art open source technologies.</p>
          </div>
          
          <LogoLoop 
            logos={[
              { node: <SiReact className="text-sky-400" />, title: "React" },
              { node: <SiVite className="text-purple-500" />, title: "Vite" },
              { node: <SiTailwindcss className="text-sky-500" />, title: "Tailwind CSS" },
              { node: <SiFramer className="text-white bg-black p-1 rounded" />, title: "Framer Motion" },
              { node: <SiThreedotjs className="text-black" />, title: "Three.js" },
              { node: <SiLucide className="text-pink-500" />, title: "Lucide Icons" },
            ]}
            speed={60}
            logoHeight={40}
            gap={60}
            fadeOut={true}
            fadeOutColor="#f8fafc"
            scaleOnHover={true}
          />
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-white border-t border-slate-100">
        <div className="section-container text-center">
          <ScrollReveal>
            <h2 className="text-4xl font-extrabold text-slate-900 mb-6">Ready to assess?</h2>
            <p className="text-xl text-slate-500 mb-10">Start your first analysis in less than 30 seconds.</p>
            <StarBorder
              as={Link}
              to="/upload"
              color="#ffffff"
              speed="3s"
              thickness={2}
            >
              Try Now
            </StarBorder>
          </ScrollReveal>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
