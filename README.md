# 📄 AI Resume Screening Tool

A powerful Streamlit application that automatically screens and scores resumes against job descriptions using keyword matching and intelligent scoring algorithms.

## 🌟 Features

- **Unlimited Text Input**: No character limit for job descriptions
- **Bulk Resume Upload**: Support for PDF, DOCX, and TXT files
- **Intelligent Scoring**: 100-point scoring system based on:
  - Keyword Match (50%)
  - Education (20%)
  - Experience (15%)
  - Technical Skills (15%)
- **Visual Analytics**: Interactive charts and graphs
- **Export Options**: Download results as Excel or PDF
- **Detailed Breakdown**: See exactly how each resume was scored

## 🚀 Deployment Instructions (No Installation Required!)

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click the **+** button (top right) → **New repository**
3. Name it (e.g., `resume-screener`)
4. Make it **Public**
5. Click **Create repository**

### Step 2: Upload Files to GitHub

1. On your new repository page, click **Add file** → **Upload files**
2. Download these 3 files from this chat and upload them:
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Click **Commit changes**

### Step 3: Deploy on Streamlit Cloud (FREE!)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **New app**
4. Fill in:
   - **Repository**: `your-username/resume-screener`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click **Deploy!**

Wait 2-3 minutes for deployment to complete. You'll get a URL like:
`https://your-app.streamlit.app`

## 📖 How to Use

1. **Enter Job Description**: Paste the complete JD (no character limit)
2. **Upload Resumes**: Drag and drop or browse for PDF/DOCX/TXT files
3. **Click "Analyze Resumes"**: Wait for processing
4. **View Results**: 
   - Summary tab shows ranked candidates
   - Visualizations show score distributions
   - Details tab explains scoring for each resume
5. **Export**: Download Excel or PDF reports

## 📊 Scoring Logic

### Keyword Match (50%)
- Extracts all meaningful keywords from JD
- Counts how many appear in each resume
- Score = (Matched Keywords / Total Keywords) × 100

### Education (20%)
- Looks for: bachelor, master, PhD, degree, certification, etc.
- Max score: 20 points

### Experience (15%)
- Looks for: years, worked, led, managed, developed, etc.
- Max score: 15 points

### Technical Skills (15%)
- Looks for: Python, Java, AWS, Docker, React, etc.
- Max score: 15 points

**Final Score** = Weighted average of all components (capped at 100)

## 📥 Export Formats

### Excel Report Includes:
- **Summary Sheet**: Ranked candidates with scores
- **Detailed Breakdown**: All scoring parameters
- **Statistics**: Average, min, max scores
- **Job Description**: Copy of the JD used

### PDF Report Includes:
- Summary statistics
- Top 10 candidates table
- Detailed analysis for each resume
- Matched keywords list

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas
- **Visualization**: Plotly
- **PDF Generation**: ReportLab
- **Document Parsing**: PyPDF2, python-docx

## 💡 Tips for Best Results

1. **Write Detailed JDs**: Include specific technologies, skills, and qualifications
2. **Use Standard Formats**: Ensure resumes are properly formatted
3. **Check File Types**: Use PDF, DOCX, or TXT only
4. **Review Matched Keywords**: Check the details tab to see what matched

## 🔒 Privacy

- No data is stored permanently
- All processing happens in-session
- Files are deleted after analysis
- No third-party data sharing

## 🐛 Troubleshooting

**App not loading?**
- Check if all files are uploaded to GitHub
- Ensure `requirements.txt` is present
- Wait 2-3 minutes for initial deployment

**Can't read resume?**
- Try converting to PDF
- Ensure text is not in image format
- Check file isn't password-protected

**Low scores for good resumes?**
- Add more specific keywords to JD
- Check matched keywords in details tab
- Scores are relative to JD content

## 📝 License

Free to use for personal and commercial purposes.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the scoring logic
3. Ensure files are in correct format

---

**Made with ❤️ using Streamlit**
