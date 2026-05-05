import React, { useRef } from 'react';
import { Cpu, Zap, Search, ShieldCheck, Microscope, Database, FileText, AlertTriangle } from 'lucide-react';
import { motion, useScroll, useTransform, useSpring } from 'framer-motion';
import CurvedLoop from '../components/CurvedLoop';

const ProcessStep = ({ icon: Icon, title, description, isLast }) => (
  <div className="flex flex-col items-center text-center relative">
    <div className="w-20 h-20 bg-white shadow-xl rounded-2xl flex items-center justify-center mb-6 border border-slate-100 z-10">
      <Icon className="w-10 h-10 text-medical-600" />
    </div>
    <h4 className="font-bold text-slate-900 mb-2">{title}</h4>
    <p className="text-sm text-slate-500 max-w-[150px]">{description}</p>
    {!isLast && (
      <div className="hidden lg:block absolute top-10 left-[100%] w-full h-[2px] bg-gradient-to-r from-medical-200 to-transparent -translate-x-1/2 -z-0"></div>
    )}
  </div>
);

const HowItWorksPage = () => {
  const sectionRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  });

  // Smooth out scroll values using useSpring
  const smoothProgress = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001
  });

  const modelY = useTransform(smoothProgress, [0, 1], [80, -80]);
  const modelScale = useTransform(smoothProgress, [0, 0.5, 1], [0.9, 1.05, 0.95]);
  const modelRotate = useTransform(smoothProgress, [0, 1], [-3, 3]);

  return (
    <div className="pb-32 overflow-hidden bg-white">
      {/* Hero / Pipeline Section */}
      <section className="bg-slate-900 text-white py-24">
        <div className="section-container">
          <div className="text-center mb-16">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">The AI Pipeline</h1>
            <p className="text-slate-400 max-w-2xl mx-auto">Understanding the journey from a single image to a clinical risk assessment.</p>
          </div>
          
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-12 lg:gap-4">
            <ProcessStep icon={Search} title="Image" description="Pixel-level analysis of lesion morphology." />
            <ProcessStep icon={Cpu} title="Model" description="Neural network feature extraction." />
            <ProcessStep icon={Zap} title="Confidence" description="Statistical probability calculation." />
            <ProcessStep icon={Microscope} title="Risk" description="Triage classification logic." />
            <ProcessStep icon={FileText} title="Explanation" description="Grad-CAM visualization output." isLast />
          </div>
        </div>
      </section>

      {/* Interactive Loop Divider */}
      <div className="bg-white py-12">
        <CurvedLoop 
          marqueeText="PRE-TRAINED MODELS ✦ EFFICIENTNET ✦ GRAD-CAM ✦ AI TRIAGE ✦"
          speed={2}
          curveAmount={100}
          direction="left"
          interactive={true}
        />
      </div>

      {/* Technical Deep Dive */}
      <section ref={sectionRef} className="py-24 bg-white relative">
        <div className="section-container">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
            {/* Left Content: Text */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              viewport={{ once: true }}
            >
              <span className="text-medical-600 font-bold uppercase tracking-widest text-sm mb-4 block">Technology Stack</span>
              <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-8 leading-tight">Advanced Neural Architectures</h2>
              <div className="space-y-8">
                <div className="flex gap-6 group">
                  <div className="flex-shrink-0 w-12 h-12 bg-medical-50 rounded-xl flex items-center justify-center group-hover:bg-medical-600 transition-colors duration-300">
                    <Database className="w-6 h-6 text-medical-600 group-hover:text-white transition-colors" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2 text-slate-900">EfficientNet-B0 Backbone</h3>
                    <p className="text-slate-500 leading-relaxed">We utilize a pre-trained EfficientNet model, fine-tuned on the ISIC Archive dataset. It balances parameter efficiency with state-of-the-art accuracy in skin lesion classification.</p>
                  </div>
                </div>
                <div className="flex gap-6 group">
                  <div className="flex-shrink-0 w-12 h-12 bg-medical-50 rounded-xl flex items-center justify-center group-hover:bg-medical-600 transition-colors duration-300">
                    <Zap className="w-6 h-6 text-medical-600 group-hover:text-white transition-colors" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2 text-slate-900">Grad-CAM Visualization</h3>
                    <p className="text-slate-500 leading-relaxed">Gradient-weighted Class Activation Mapping allows our model to "show its work." It produces a heatmap over the image, highlighting the specific features it used for its prediction.</p>
                  </div>
                </div>
                <div className="flex gap-6 group">
                  <div className="flex-shrink-0 w-12 h-12 bg-medical-50 rounded-xl flex items-center justify-center group-hover:bg-medical-600 transition-colors duration-300">
                    <ShieldCheck className="w-6 h-6 text-medical-600 group-hover:text-white transition-colors" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2 text-slate-900">Confidence Thresholding</h3>
                    <p className="text-slate-500 leading-relaxed">Our triage logic uses custom thresholds. If the AI's confidence is below 70%, the case is automatically flagged for "Manual Review" to ensure maximum safety.</p>
                  </div>
                </div>
              </div>
            </motion.div>
            
            {/* Right Content: 3D Model with Parallax */}
            <motion.div 
              style={{ y: modelY, scale: modelScale, rotateZ: modelRotate }}
              className="relative h-[500px] lg:h-[600px] w-full flex items-center justify-center"
            >
              <motion.div 
                animate={{ y: [0, -20, 0] }}
                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                className="relative w-full h-full flex items-center justify-center"
              >
                {/* Glow Backdrop */}
                <div className="absolute inset-0 z-0 bg-gradient-to-br from-medical-200/30 to-transparent rounded-[40px] transform scale-75 blur-3xl opacity-60"></div>
                
                {/* 3D Frame */}
                <div className="relative w-full h-full rounded-[32px] overflow-hidden border border-slate-100 bg-white/40 backdrop-blur-sm shadow-2xl flex items-center justify-center">
                  <iframe 
                    src='https://my.spline.design/untitled-eyh5rrPp1NEKbXXyy10Qltfl/' 
                    frameBorder='0' 
                    width='100%' 
                    height='100%'
                    className="w-full h-full pointer-events-none"
                    style={{ background: 'transparent' }}
                    title="AI Neural Network Visualization"
                  ></iframe>

                  {/* Watermark Cover Badge */}
                  <div className="absolute bottom-6 right-6 z-20 flex items-center gap-2 bg-white/90 backdrop-blur-md px-4 py-2 rounded-full border border-slate-200 shadow-lg scale-90 lg:scale-100">
                    <div className="w-6 h-6 bg-medical-600 rounded-full flex items-center justify-center">
                      <Cpu className="w-3.5 h-3.5 text-white" />
                    </div>
                    <span className="text-[10px] font-bold text-slate-900 uppercase tracking-widest">AI Skin Triage</span>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Safety & Protocol */}
      <section className="py-24 bg-slate-50">
        <div className="section-container">
          <div className="bg-white border border-slate-200 rounded-[40px] p-12 shadow-sm">
            <div className="flex flex-col items-center text-center mb-12">
              <div className="w-16 h-16 bg-amber-50 rounded-2xl flex items-center justify-center mb-6">
                <AlertTriangle className="w-8 h-8 text-amber-600" />
              </div>
              <h2 className="text-3xl font-bold text-slate-900 mb-4">Safety & Protocol</h2>
              <p className="text-slate-500 max-w-2xl">This tool is designed as a triage assistant, not a definitive diagnostic device.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
              <div className="space-y-4">
                <h4 className="font-bold text-slate-900 text-lg">No Diagnosis</h4>
                <p className="text-sm text-slate-500 leading-relaxed">The AI Skin Triage Assistant identifies risk patterns based on statistical probabilities. It does not provide a medical diagnosis or disease name.</p>
              </div>
              <div className="space-y-4">
                <h4 className="font-bold text-slate-900 text-lg">No Treatment Advice</h4>
                <p className="text-sm text-slate-500 leading-relaxed">Our system will never recommend specific medications or treatments. It only suggests clinical triage priority levels (Low/Medium/High).</p>
              </div>
              <div className="space-y-4">
                <h4 className="font-bold text-slate-900 text-lg">Mandatory Consultation</h4>
                <p className="text-sm text-slate-500 leading-relaxed">Regardless of the result, we recommend consulting a board-certified dermatologist for any suspicious skin changes or lesions.</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HowItWorksPage;
