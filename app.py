import gradio as gr
from pypdf import PdfReader
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

resume_text = ""


def extract_text(pdf_file):
    reader = PdfReader(pdf_file.name)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def process_resume(pdf_file):
    global resume_text

    if pdf_file is None:
        return "❌ Please upload a resume first."

    resume_text = extract_text(pdf_file)

    if resume_text.strip() == "":
        return "❌ Could not extract text from the PDF."

    return "✅ Resume uploaded and processed successfully!"


def chat_with_resume(message, history):
    global resume_text

    if resume_text.strip() == "":
        return "Please upload and process your resume first."

    prompt = f"""
You are an AI Resume Q&A Bot.
Answer only based on the resume content.

Resume:
{resume_text}

User question:
{message}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def ats_score():
    global resume_text

    if resume_text.strip() == "":
        return "❌ Please upload and process your resume first."

    prompt = f"""
You are an ATS Resume Evaluator.

Analyze the resume and give a practical ATS-style score out of 100.

Use this format exactly:

## ATS Score: __/100

## Reason for Score
Explain why this score was given.

## Strengths
- point 1
- point 2
- point 3

## Weaknesses
- point 1
- point 2
- point 3

## Improvements Needed
- point 1
- point 2
- point 3

## Best Suitable Roles
- role 1
- role 2
- role 3

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


custom_css = """
.gradio-container {
    background: linear-gradient(135deg, #020617, #0f172a, #1e293b);
    color: white;
}

/* Quote Banner */
#quote-banner {
    max-width: 760px;
    margin: 18px auto 22px auto;
    padding: 18px 22px;
    text-align: center;
    background: linear-gradient(135deg, #ec4899, #8b5cf6);
    color: white;
    border-radius: 18px;
    font-size: 1rem;
    font-style: italic;
    font-weight: 600;
    box-shadow: 0 0 25px rgba(236, 72, 153, 0.35);
    overflow: hidden;
    animation: fadeIn 1s ease, hideBanner 15s forwards;
}

/* Title */
#title {
    text-align: center;
    animation: titleDrop 1s ease;
    margin-bottom: 25px;
}

#title h1 {
    font-size: 2.4rem;
    margin-bottom: 8px;
}

#title p {
    color: #cbd5e1;
    font-size: 1rem;
}

/* Main Card */
#upload-section {
    max-width: 760px;
    margin: auto;
    padding: 28px;
    border-radius: 22px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(56,189,248,0.35);
    box-shadow: 0 0 25px rgba(56,189,248,0.18);
    animation: cardPop 1.2s ease;
}

/* Main Button */
#process-btn {
    background: linear-gradient(135deg, #06b6d4, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
}

/* ATS Button */
#ats-btn {
    background: linear-gradient(135deg, #f97316, #ec4899) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
}

#process-btn:hover,
#ats-btn:hover {
    transform: scale(1.03);
    box-shadow: 0 0 22px rgba(59,130,246,0.65) !important;
}

/* General Buttons */
button {
    transition: all 0.3s ease !important;
}

button:hover {
    transform: translateY(-2px);
}

/* Status */
#status-text {
    color: #4ade80 !important;
    font-weight: 700 !important;
}

/* ATS Output */
#ats-output {
    border-radius: 14px !important;
    border: 1px solid rgba(236,72,153,0.35) !important;
}

/* Chatbot Box */
.chatbot {
    border-radius: 14px !important;
    border: 1px solid rgba(148,163,184,0.3) !important;
}

/* Textbox */
textarea {
    border-radius: 12px !important;
}

/* Animations */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(-12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes hideBanner {
    0%, 93% {
        opacity: 1;
        max-height: 120px;
        padding: 18px 22px;
        margin: 18px auto 22px auto;
    }
    100% {
        opacity: 0;
        max-height: 0;
        padding: 0 22px;
        margin: 0 auto;
    }
}

@keyframes titleDrop {
    from {
        opacity: 0;
        transform: translateY(-35px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes cardPop {
    from {
        opacity: 0;
        transform: scale(0.92);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}
"""


with gr.Blocks() as app:

    gr.Markdown(
        """
        <div id="quote-banner">
            💡 “A resume is not a history of your life; it's a story of your value.”
        </div>
        """
    )

    gr.Markdown(
        """
        <div id="title">
            <h1>📄 AI Resume Analyzer</h1>
            <p>Upload your resume PDF and ask questions about your skills, projects, and experience.</p>
        </div>
        """
    )

    with gr.Column(elem_id="upload-section"):
        pdf = gr.File(
            label="📄 Upload Resume PDF",
            file_types=[".pdf"]
        )

        process_btn = gr.Button(
            "🚀 Process Resume",
            elem_id="process-btn"
        )

        status = gr.Markdown(
            "No resume uploaded yet.",
            elem_id="status-text"
        )

        process_btn.click(
            fn=process_resume,
            inputs=pdf,
            outputs=status
        )

        ats_btn = gr.Button(
            "📊 Generate ATS Score",
            elem_id="ats-btn"
        )

        ats_output = gr.Markdown(
            "",
            elem_id="ats-output"
        )

        ats_btn.click(
            fn=ats_score,
            inputs=[],
            outputs=ats_output
        )

        gr.ChatInterface(
            fn=chat_with_resume,
            chatbot=gr.Chatbot(
                height=500,
                elem_classes="chatbot"
            ),
            textbox=gr.Textbox(
                placeholder="Ask about skills, projects, experience...",
                label="Chatbot"
            ),
            examples=[
                "What are my key skills?",
                "Summarize this resume.",
                "What projects are mentioned?",
                "What job role suits this resume?",
                "What are the weak points in this resume?",
                "Give interview questions from this resume."
            ]
        )

app.launch(css=custom_css)