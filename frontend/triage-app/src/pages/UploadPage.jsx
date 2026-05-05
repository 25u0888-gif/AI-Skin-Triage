import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Image as ImageIcon, CheckCircle2, AlertCircle, Info, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ScrollReveal from '../components/ScrollReveal';

const UploadPage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const navigate = useNavigate();

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleSampleImage = async () => {
    // Fetch sample image and convert to File
    try {
      const imageUrl = 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&q=80&w=800';
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const file = new File([blob], 'sample-skin.jpg', { type: 'image/jpeg' });
      
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(blob));
    } catch (error) {
      console.error('Failed to load sample image:', error);
      alert('Failed to load sample image');
    }
  };

  const handleAnalyze = async () => {
    if (!selectedImage) return;
    
    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('image', selectedImage);

      console.log('📤 Sending image to backend...');
      const response = await fetch('https://ai-skin-triage.onrender.com/analyze', {
        method: 'POST',
        body: formData, // FormData automatically sets the correct Content-Type header
      });

      console.log('📥 Response received from backend', response.status);
      const data = await response.json();
      
      console.log('✓ Response data:', {
        prediction: data.prediction,
        confidence: data.confidence,
        risk_level: data.risk_level,
        top_k_count: data.top_k?.length || 0,
        has_error: !!data.error
      });
      
      if (data.error) {
        console.error('❌ API returned error:', data.error);
        alert('Analysis failed: ' + data.error);
        setIsAnalyzing(false);
        return;
      }
      
      // Save results to localStorage (with image preview)
      const resultWithImage = {
        ...data,
        uploadedImagePreview: previewUrl
      };
      localStorage.setItem('analysisResult', JSON.stringify(resultWithImage));
      console.log('💾 Results saved to localStorage');
      
      setIsAnalyzing(false);
      navigate('/results');
    } catch (error) {
      console.error('❌ Analysis failed:', error);
      setIsAnalyzing(false);
      alert('Analysis failed. Please check if both backend and ML service are running.');
    }
  };



  return (
    <div className="section-container min-h-[calc(100vh-200px)] pt-12">
      <div className="mb-12">
        <h1 className="text-4xl font-extrabold text-slate-900 mb-2">New Analysis</h1>
        <p className="text-slate-500">Upload a clear photo of the skin area you wish to assess.</p>
      </div>

      <ScrollReveal>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 items-start">
          {/* Left: Upload Section */}
          <div className="lg:col-span-2 space-y-8">
            <div 
              className={`relative group border-2 border-dashed rounded-3xl p-12 text-center transition-all ${
                previewUrl ? 'border-medical-500 bg-medical-50/30' : 'border-slate-300 hover:border-medical-400 bg-white'
              }`}
            >
              {!previewUrl ? (
                <div className="flex flex-col items-center">
                  <div className="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <Upload className="w-10 h-10 text-slate-400 group-hover:text-medical-600" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2">Drag & Drop Image</h3>
                  <p className="text-slate-500 mb-8 max-w-xs">Supports JPG, PNG (Max 10MB). Ensure the area is well-lit.</p>
                  <div className="flex gap-4">
                    <label className="btn-primary cursor-pointer">
                      Browse Files
                      <input type="file" className="hidden" onChange={handleImageChange} accept="image/*" />
                    </label>
                    <button 
                      onClick={handleSampleImage}
                      className="btn-secondary flex items-center gap-2"
                    >
                      <ImageIcon className="w-5 h-5" />
                      Use Sample
                    </button>
                  </div>
                </div>
              ) : (
                <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                  <img src={previewUrl} alt="Preview" className="w-full h-[400px] object-cover" />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <button 
                      onClick={() => {setPreviewUrl(null); setSelectedImage(null);}}
                      className="bg-red-500 text-white px-4 py-2 rounded-lg font-bold hover:bg-red-600 transition-colors"
                    >
                      Remove & Change
                    </button>
                  </div>
                </div>
              )}
            </div>

            <AnimatePresence>
              {previewUrl && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  className="flex flex-col items-center gap-6"
                >
                  <div className="flex items-center gap-2 text-green-600 font-medium">
                    <CheckCircle2 className="w-5 h-5" />
                    Image ready for analysis
                  </div>
                  <button 
                    onClick={handleAnalyze}
                    disabled={isAnalyzing}
                    className={`btn-primary text-xl px-12 py-4 w-full md:w-auto min-w-[300px] flex items-center justify-center gap-3 ${
                      isAnalyzing ? 'opacity-80 cursor-not-allowed' : ''
                    }`}
                  >
                    {isAnalyzing ? (
                      <>
                        <Loader2 className="w-6 h-6 animate-spin" />
                        Analyzing Image...
                      </>
                    ) : (
                      <>Analyze Image Now</>
                    )}
                  </button>
                  
                  {isAnalyzing && (
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: "100%" }}
                      className="w-full max-w-md h-1.5 bg-slate-100 rounded-full overflow-hidden"
                    >
                      <motion.div 
                        className="h-full bg-medical-600"
                        initial={{ width: "0%" }}
                        animate={{ width: "100%" }}
                        transition={{ duration: 3, ease: "easeInOut" }}
                      />
                    </motion.div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Right: Instructions Section */}
          <div className="space-y-6">
            <ScrollReveal direction="right" delay={0.2}>
              <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm">
                <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
                  <Info className="w-5 h-5 text-medical-600" />
                  Upload Guidelines
                </h3>
                <ul className="space-y-6">
                  <li className="flex gap-4">
                    <div className="w-6 h-6 rounded-full bg-medical-100 flex items-center justify-center flex-shrink-0 text-medical-700 font-bold text-xs">1</div>
                    <p className="text-sm text-slate-600"><span className="font-bold text-slate-900">Good Lighting:</span> Avoid shadows or harsh flashes. Indirect sunlight is best.</p>
                  </li>
                  <li className="flex gap-4">
                    <div className="w-6 h-6 rounded-full bg-medical-100 flex items-center justify-center flex-shrink-0 text-medical-700 font-bold text-xs">2</div>
                    <p className="text-sm text-slate-600"><span className="font-bold text-slate-900">High Resolution:</span> Ensure the image is sharp and not blurry. Tap to focus before capturing.</p>
                  </li>
                  <li className="flex gap-4">
                    <div className="w-6 h-6 rounded-full bg-medical-100 flex items-center justify-center flex-shrink-0 text-medical-700 font-bold text-xs">3</div>
                    <p className="text-sm text-slate-600"><span className="font-bold text-slate-900">Focus:</span> Capture the area of concern in the center of the frame.</p>
                  </li>
                  <li className="flex gap-4">
                    <div className="w-6 h-6 rounded-full bg-medical-100 flex items-center justify-center flex-shrink-0 text-medical-700 font-bold text-xs">4</div>
                    <p className="text-sm text-slate-600"><span className="font-bold text-slate-900">Cleanliness:</span> Ensure the skin is clean and free of makeup or creams if possible.</p>
                  </li>
                </ul>
              </div>
            </ScrollReveal>

            <ScrollReveal direction="right" delay={0.4}>
              <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6">
                <div className="flex gap-3 items-start">
                  <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-bold text-amber-900 mb-1">Privacy Notice</h4>
                    <p className="text-xs text-amber-700 leading-relaxed">
                      Your images are processed securely and are NOT stored on our servers permanently. We value your data privacy and medical confidentiality.
                    </p>
                  </div>
                </div>
              </div>
            </ScrollReveal>
          </div>
        </div>
      </ScrollReveal>
    </div>
  );
};

export default UploadPage;
