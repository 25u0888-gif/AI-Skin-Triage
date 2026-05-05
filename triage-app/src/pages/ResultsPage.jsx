import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, AlertTriangle, Eye, EyeOff, Info, ArrowRight, RotateCcw, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';
import ScrollReveal from '../components/ScrollReveal';

const ResultsPage = () => {
  const navigate = useNavigate();
  const [showHeatmap, setShowHeatmap] = useState(false);
  
  // Retrieve result from localStorage
  const storedResult = JSON.parse(localStorage.getItem('analysisResult') || '{}');
  
  // Redirect to upload if no result is available
  useEffect(() => {
    if (!storedResult || Object.keys(storedResult).length === 0) {
      navigate('/upload');
    }
  }, [storedResult, navigate]);
  
  // Check if this is a valid skin disease prediction (not "No skin" or "Uncertain")
  const isValidSkinDisease = storedResult.is_valid_skin === true;
  const hasHeatmap = storedResult.heatmap && storedResult.heatmap.image;
  
  // Determine if this is an "uncertain" or "no skin" prediction
  const isUncertainOrNoSkin = 
    storedResult.prediction === 'Uncertain / Not a clear skin condition' ||
    storedResult.prediction === 'No skin detected' ||
    !isValidSkinDisease;

  // Disease class mapping for display
  const classNameMap = {
    'mel': 'Melanoma',
    'nv': 'Melanocytic Nevus',
    'bcc': 'Basal Cell Carcinoma',
    'akiec': 'Actinic Keratosis',
    'bkl': 'Benign Keratosis',
    'df': 'Dermatofibroma',
    'vasc': 'Vascular Lesions'
  };

  // Map API data to UI structure
  const results = {
    prediction: storedResult.prediction_full_name || classNameMap[storedResult.prediction] || storedResult.prediction || "Uncertain",
    prediction_code: storedResult.prediction || "unknown",
    confidence: storedResult.confidence ? (storedResult.confidence * 100) : 0,
    riskLevel: storedResult.risk_level || "Low",
    riskColor: storedResult.risk_level === "High" ? "bg-red-600" : 
              storedResult.risk_level === "Medium" ? "bg-amber-500" : 
              storedResult.risk_level === "Requires Professional Review" ? "bg-orange-600" :
              "bg-green-600",
    riskText: storedResult.risk_level === "High" ? "text-red-600" : 
             storedResult.risk_level === "Medium" ? "text-amber-600" : 
             storedResult.risk_level === "Requires Professional Review" ? "text-orange-600" :
             "text-green-600",
    explanation: storedResult.interpretation || "Analysis complete. Please consult with a healthcare professional for diagnosis.",
    nextSteps: storedResult.nextSteps || [
      "Monitor for any changes in size, shape, color, or symptoms.",
      "Consult a dermatologist for professional clinical evaluation.",
      "Practice sun protection and skin care best practices."
    ],
    topPredictions: storedResult.top_k || [],
    warning: storedResult.warning || "This is an AI-assisted prediction and not a medical diagnosis."
  };

  // Extract just the abbreviation for styling
  const predictionAbbr = results.prediction_code;

  return (
    <div className="section-container pt-12 pb-32">
      <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-4xl font-extrabold text-slate-900 mb-2">Analysis Results</h1>
          <p className="text-slate-500">Based on our advanced AI triage model.</p>
        </div>
        <div className="flex gap-3">
          <Link to="/upload" className="btn-secondary py-2 flex items-center gap-2">
            <RotateCcw className="w-4 h-4" />
            Analyze Another
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Left: Image & Heatmap */}
        <ScrollReveal direction="left">
          <div className="space-y-6">
            {/* Only show heatmap section if prediction is valid and heatmap exists */}
            {isValidSkinDisease && hasHeatmap ? (
              <>
                <div className="relative group rounded-3xl overflow-hidden shadow-2xl border-4 border-white bg-slate-200 aspect-[4/3]">
                  {/* Show heatmap when toggled on */}
                  {showHeatmap ? (
                    <img 
                      src={`data:image/jpeg;base64,${storedResult.heatmap.image}`}
                      alt="Grad-CAM Heatmap" 
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                    />
                  ) : (
                    <img 
                      src={storedResult.uploadedImagePreview || "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&q=80&w=800"} 
                      alt="Analyzed Skin" 
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                    />
                  )}

                  <button 
                    onClick={() => setShowHeatmap(!showHeatmap)}
                    className="absolute bottom-6 right-6 bg-white/90 backdrop-blur-md px-6 py-3 rounded-xl shadow-xl flex items-center gap-2 font-bold text-slate-900 hover:bg-white transition-colors"
                  >
                    {showHeatmap ? (
                      <><EyeOff className="w-5 h-5 text-medical-600" /> Hide Heatmap</>
                    ) : (
                      <><Eye className="w-5 h-5 text-medical-600" /> Show Heatmap</>
                    )}
                  </button>
                </div>

                <div className="bg-medical-50 p-6 rounded-2xl border border-medical-100">
                  <div className="flex gap-3">
                    <Info className="w-5 h-5 text-medical-600 flex-shrink-0" />
                    <p className="text-sm text-medical-800 leading-relaxed">
                      <span className="font-bold">Explainability:</span> The heatmap shows areas the AI focused on. <span className="text-red-600 font-semibold">Red zones</span> had the most influence on the diagnosis, while cooler colors had less.
                    </p>
                  </div>
                </div>
              </>
            ) : (
              // Show message when heatmap is not available (Uncertain or No skin)
              <div className="rounded-3xl overflow-hidden shadow-2xl border-4 border-white bg-slate-200 aspect-[4/3] flex items-center justify-center">
                <div className="text-center p-6">
                  <AlertTriangle className="w-16 h-16 text-amber-500 mx-auto mb-3" />
                  <p className="text-slate-700 font-semibold">
                    {isUncertainOrNoSkin 
                      ? storedResult.prediction === 'No skin detected'
                        ? "No skin detected in this image"
                        : "Unable to make a clear diagnosis"
                      : "Analysis in progress..."}
                  </p>
                  <p className="text-slate-600 text-sm mt-2">
                    {isUncertainOrNoSkin
                      ? "Heatmap is only available for clear skin condition predictions"
                      : "Please try another image"}
                  </p>
                </div>
              </div>
            )}
          </div>
        </ScrollReveal>

        {/* Right: Results Detail */}
        <div className="space-y-6">
          {/* Risk Level Badge */}
          <ScrollReveal direction="right" delay={0.2}>
            <div className={`p-8 rounded-[32px] text-white shadow-xl ${results.riskColor} relative overflow-hidden`}>
              <div className="relative z-10">
                <span className="text-white/80 font-bold uppercase tracking-widest text-xs mb-2 block">Risk Level</span>
                <div className="flex items-center justify-between">
                  <h2 className="text-5xl font-black">{results.riskLevel}</h2>
                  <AlertTriangle className="w-16 h-16 text-white/20" />
                </div>
              </div>
              <div className="absolute -right-8 -bottom-8 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
            </div>
          </ScrollReveal>

          {/* Prediction Card */}
          <ScrollReveal direction="right" delay={0.4}>
            <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-6">
              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">Top Prediction</label>
                <h3 className="text-2xl font-bold text-slate-900">{results.prediction}</h3>
              </div>

              <div>
                <div className="flex justify-between items-end mb-2">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">AI Confidence</label>
                  <span className="text-lg font-bold text-medical-600">{results.confidence.toFixed(1)}%</span>
                </div>
                <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(results.confidence, 100)}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className="h-full bg-medical-600 rounded-full"
                  />
                </div>
              </div>

              {/* Top-K Predictions */}
              {results.topPredictions && results.topPredictions.length > 0 && (
                <div className="pt-6 border-t border-slate-100">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 block">Top 3 Predictions</label>
                  <div className="space-y-2">
                    {results.topPredictions.map((pred, idx) => (
                      <div key={idx} className="flex items-center justify-between">
                        <div className="flex items-center gap-2 flex-1">
                          <span className="text-xs font-bold text-slate-500 w-6">{idx + 1}.</span>
                          <span className="text-sm font-medium text-slate-700">{pred.full_name || classNameMap[pred.label] || pred.label}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-2 bg-slate-100 rounded-full overflow-hidden">
                            <motion.div 
                              initial={{ width: 0 }}
                              animate={{ width: `${Math.min(pred.confidence * 100, 100)}%` }}
                              transition={{ duration: 0.8, delay: idx * 0.1 }}
                              className="h-full bg-blue-500 rounded-full"
                            />
                          </div>
                          <span className="text-xs font-bold text-slate-600 w-10 text-right">{(pred.confidence * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="pt-6 border-t border-slate-100">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 block">Analysis Explanation</label>
                <p className="text-slate-600 leading-relaxed italic font-medium">
                  "{results.explanation}"
                </p>
              </div>
            </div>
          </ScrollReveal>

          {/* Next Steps */}
          <ScrollReveal direction="up" delay={0.6}>
            <div className="bg-slate-900 rounded-3xl p-8 text-white">
              <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                <ShieldCheck className="w-6 h-6 text-medical-400" />
                Recommended Next Steps
              </h3>
              <ul className="space-y-4">
                {results.nextSteps.map((step, idx) => (
                  <li key={idx} className="flex gap-4 items-start group">
                    <div className="mt-1.5 w-2 h-2 rounded-full bg-medical-500 group-hover:scale-150 transition-transform"></div>
                    <p className="text-slate-300 text-sm leading-relaxed">{step}</p>
                  </li>
                ))}
              </ul>
              <button className="mt-8 w-full bg-white text-slate-900 py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-medical-50 transition-colors">
                Find a Dermatologist Near Me <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </ScrollReveal>

          {/* Warning Banner */}
          <ScrollReveal direction="up" delay={0.8}>
            <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-lg">
              <p className="text-sm text-amber-800">
                <span className="font-bold">⚠️ Important:</span> {results.warning}
              </p>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
