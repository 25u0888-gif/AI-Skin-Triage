import express from "express";
import axios from "axios";
import cors from "cors";
import dotenv from "dotenv";
import multer from "multer";
import Groq from "groq-sdk";
import path from "path";

dotenv.config();

const app = express();
const upload = multer({ dest: "uploads/" });
const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

app.use(cors());
app.use(express.json());

app.post("/analyze", upload.single("image"), async (req, res) => {
  try {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`STEP 1: IMAGE RECEIVED`);
    console.log(`${'='.repeat(60)}`);
    
    if (!req.file) {
      console.error("❌ No image file in request");
      return res.status(400).json({ error: "No image uploaded" });
    }

    console.log(`✓ Image received: ${req.file.originalname}`);
    console.log(`✓ File size: ${req.file.size} bytes`);
    console.log(`✓ MIME type: ${req.file.mimetype}`);
    console.log(`✓ Temp path: ${req.file.path}`);

    // 1. Call the ML service (FastAPI)
    const absolutePath = path.resolve(req.file.path);
    console.log(`✓ Absolute path: ${absolutePath}`);
    
    console.log(`\nSTEP 2: SEND TO ML SERVICE`);
    console.log(`Calling ML service at http://127.0.0.1:8000/predict`);
    
    const predictionResponse = await axios.post("http://127.0.0.1:8000/predict", {
      image_path: absolutePath
    });
    const predictionData = predictionResponse.data;

    console.log(`\n${'='.repeat(60)}`);
    console.log(`STEP 3: ML SERVICE RESPONSE RECEIVED`);
    console.log(`${'='.repeat(60)}`);
    console.log(`✓ Prediction: ${predictionData.prediction}`);
    console.log(`✓ Full name: ${predictionData.prediction_full_name}`);
    console.log(`✓ Confidence: ${predictionData.confidence}`);
    console.log(`✓ Top predictions:`, JSON.stringify(predictionData.top_k, null, 2));

    // Check if there was an error in prediction
    if (predictionData.error) {
      console.error(`❌ Prediction error: ${predictionData.error}`);
      return res.status(400).json({
        error: predictionData.error,
        warning: predictionData.warning || "Failed to analyze image."
      });
    }

    // 2. Use Groq for medical interpretation (optional but adds value)
    let interpretation = null;
    let risk_level = "Low";

    console.log(`\nSTEP 4: DETERMINE RISK LEVEL`);
    
    if (predictionData.prediction === "Uncertain - Low Confidence") {
      risk_level = "Requires Professional Review";
    } else if (predictionData.prediction === "mel" || predictionData.prediction === "Melanoma") {
      risk_level = predictionData.confidence > 0.8 ? "High" : "Medium";
    } else if (predictionData.prediction === "bcc" || predictionData.prediction === "Basal Cell Carcinoma") {
      risk_level = "Medium";
    } else if (predictionData.prediction === "akiec" || predictionData.prediction === "Actinic Keratosis") {
      risk_level = "Medium";
    } else {
      risk_level = "Low";
    }
    
    console.log(`✓ Risk level: ${risk_level}`);

    if (process.env.GROQ_API_KEY) {
      try {
        console.log(`\nSTEP 5: GENERATE MEDICAL INTERPRETATION`);
        
        const groqPrompt = `You are a professional medical assistant. Based on the following AI skin analysis results, provide:
1. A brief clinical interpretation (2-3 sentences)
2. Recommended next steps
3. When to seek professional care

Analysis Results:
- Prediction: ${predictionData.prediction_full_name || predictionData.prediction}
- AI Confidence: ${(predictionData.confidence * 100).toFixed(1)}%
- Risk Level: ${risk_level}
- Top Predictions: ${predictionData.top_k.map(p => `${p.full_name || p.label} (${(p.confidence * 100).toFixed(1)}%)`).join(', ')}

Important: Remind the user this is AI-assisted analysis, not a diagnosis.`;

        const chatCompletion = await groq.chat.completions.create({
          messages: [
            {
              role: "system",
              content: "You are a professional medical assistant specializing in dermatology. Provide accurate, helpful medical guidance based on AI analysis results."
            },
            {
              role: "user",
              content: groqPrompt
            }
          ],
          model: "llama-3.3-70b-versatile",
          max_tokens: 500
        });
        
        interpretation = chatCompletion.choices[0]?.message?.content || null;
        console.log(`✓ Interpretation generated successfully`);
        console.log(`Interpretation preview: ${interpretation?.substring(0, 100)}...`);
        
      } catch (groqError) {
        console.error("⚠️ Groq error:", groqError.message);
        // Continue without interpretation if Groq fails
      }
    } else {
      console.log(`⚠️ GROQ_API_KEY not set - skipping interpretation generation`);
    }

    // 3. Prepare comprehensive response
    console.log(`\nSTEP 6: BUILD RESPONSE`);
    const analysisResponse = {
      prediction: predictionData.prediction,
      prediction_full_name: predictionData.prediction_full_name || predictionData.prediction,
      confidence: predictionData.confidence,
      is_valid_skin: predictionData.is_valid_skin || false,
      is_confident: predictionData.is_confident || false,
      heatmap: predictionData.heatmap || null,
      top_k: predictionData.top_k || [],
      risk_level: risk_level,
      interpretation: interpretation,
      warning: predictionData.warning || "This is an AI-assisted prediction and not a medical diagnosis. Always consult a healthcare professional.",
      debug_info: process.env.NODE_ENV === 'development' ? predictionData.debug_info : undefined
    };

    console.log(`\n${'='.repeat(60)}`);
    console.log(`ANALYSIS COMPLETE - SENDING RESPONSE TO FRONTEND`);
    console.log(`${'='.repeat(60)}`);
    console.log(`Final prediction: ${analysisResponse.prediction}`);
    console.log(`Final confidence: ${analysisResponse.confidence}`);
    console.log(`Is valid skin: ${analysisResponse.is_valid_skin}`);
    console.log(`Has heatmap: ${analysisResponse.heatmap !== null}`);
    console.log(`Risk level: ${risk_level}`);
    console.log(`Response size: ${JSON.stringify(analysisResponse).length} bytes`);

    res.json(analysisResponse);

  } catch (error) {
    console.error(`\n${'='.repeat(60)}`);
    console.error(`❌ BACKEND ERROR`);
    console.error(`${'='.repeat(60)}`);
    console.error("Error message:", error.message);
    console.error("Error details:", error.response?.data || error.toString());
    console.error(`${'='.repeat(60)}\n`);
    
    res.status(500).json({ 
      error: "Failed to analyze image",
      details: error.message,
      warning: "This is an AI-assisted prediction and not a medical diagnosis. Please consult a healthcare professional."
    });
  }
});

// Endpoint to trigger dataset download in the ml-service
app.post("/download-dataset", async (req, res) => {
  try {
    if (!process.env.KAGGLE_API_TOKEN) {
      return res.status(500).json({ error: "KAGGLE_API_TOKEN is not configured in the backend" });
    }
    
    // Using child_process to run the download script
    import('child_process').then(({ exec }) => {
      exec("python download_dataset.py", { cwd: "../ml-service", env: { ...process.env } }, (error, stdout, stderr) => {
        if (error) {
          console.error(`exec error: ${error}`);
          return;
        }
        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);
      });
    });

    res.json({ message: "Dataset download started in the background. Check backend console for progress." });
  } catch (error) {
    console.error("Dataset download error:", error.message);
    res.status(500).json({ error: "Failed to start dataset download" });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Backend server running on port ${PORT}`));