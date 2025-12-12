import streamlit as st
import pandas as pd
import pdfplumber
import docx
import io
import re
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

st.set_page_config(page_title="Resume Screening Tool", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📄 AI Resume Screening Tool</p>', unsafe_allow_html=True)

def extract_text_from_pdf(file):
    try:
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return ""

def extract_text_from_txt(file):
    try:
        return file.read().decode('utf-8')
    except Exception as e:
        st.error(f"Error reading TXT: {str(e)}")
        return ""

def extract_keywords(text):
    text_lower = text.lower()
    text_clean = re.sub(r'[^a-z0-9\s\+\#\.]', ' ', text_lower)
    words = text_clean.split()
    
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                  'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                  'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
                  'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                  'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
                  'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
                  'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
                  'very', 'just', 'also', 'years', 'year', 'experience', 'work', 'working'}
    
    keywords = []
    for i, word in enumerate(words):
        if len(word) > 2 and word not in stop_words:
            if i < len(words) - 1:
                two_word = f"{word} {words[i+1]}"
                if len(two_word) > 5:
                    keywords.append(two_word)
            keywords.append(word)
    
    return list(set(keywords))

def calculate_keyword_match(jd_keywords, resume_text):
    resume_lower = resume_text.lower()
    return [keyword for keyword in jd_keywords if keyword.lower() in resume_lower]

def score_resume(jd_text, resume_text, resume_name):
    jd_keywords = extract_keywords(jd_text)
    matched_keywords = calculate_keyword_match(jd_keywords, resume_text)
    
    keyword_match_score = (len(matched_keywords) / len(jd_keywords) * 100) if jd_keywords else 0
    
    resume_lower = resume_text.lower()
    
    education_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma', 'certification', 
                         'university', 'college', 'mba', 'btech', 'mtech', 'engineering']
    education_score = min(sum(1 for edu in education_keywords if edu in resume_lower) * 5, 20)
    
    experience_keywords = ['years', 'experience', 'worked', 'led', 'managed', 'developed',
                          'implemented', 'achieved', 'delivered', 'coordinated']
    experience_score = min(sum(1 for exp in experience_keywords if exp in resume_lower) * 2, 15)
    
    tech_keywords = ['python', 'java', 'javascript', 'sql', 'aws', 'azure', 'docker',
                    'kubernetes', 'react', 'node', 'angular', 'machine learning', 'ai',
                    'data', 'analytics', 'agile', 'scrum', 'git', 'api']
    tech_score = min(sum(1 for tech in tech_keywords if tech in resume_lower) * 2, 15)
    
    final_score = min(round(
        keyword_match_score * 0.50 +
        education_score * 0.20 / 20 * 100 +
        experience_score * 0.15 / 15 * 100 +
        tech_score * 0.15 / 15 * 100, 2), 100)
    
    return {
        'Resume Name': resume_name,
        'Overall Score': final_score,
        'Keyword Match Score': round(keyword_match_score, 2),
        'Keywords Matched': len(matched_keywords),
        'Total Keywords in JD': len(jd_keywords),
        'Education Score': round(education_score, 2),
        'Experience Score': round(experience_score, 2),
        'Technical Skills Score': round(tech_score, 2),
        'Matched Keywords': ', '.join(matched_keywords[:20]) if matched_keywords else 'None',
        'Resume Length (chars)': len(resume_text)
    }

def create_excel_report(results_df, jd_text):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        summary_df = results_df[['Resume Name', 'Overall Score', 'Keywords Matched', 
                                'Total Keywords in JD', 'Keyword Match Score']].sort_values('Overall Score', ascending=False)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        results_df.to_excel(writer, sheet_name='Detailed Breakdown', index=False)
        
        stats_df = pd.DataFrame({
            'Metric': ['Total Resumes', 'Average Score', 'Highest Score', 'Lowest Score',
                      'Resumes > 70', 'Resumes 50-70', 'Resumes < 50'],
            'Value': [len(results_df), round(results_df['Overall Score'].mean(), 2),
                     results_df['Overall Score'].max(), results_df['Overall Score'].min(),
                     len(results_df[results_df['Overall Score'] >= 70]),
                     len(results_df[(results_df['Overall Score'] >= 50) & (results_df['Overall Score'] < 70)]),
                     len(results_df[results_df['Overall Score'] < 50])]
        })
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        pd.DataFrame({'Job Description': [jd_text]}).to_excel(writer, sheet_name='Job Description', index=False)
    
    output.seek(0)
    return output

def create_pdf_report(results_df, jd_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24,
                                textColor=colors.HexColor('#1f77b4'), spaceAfter=30, alignment=1)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14,
                                   textColor=colors.HexColor('#2c3e50'), spaceAfter=12)
    
    story.append(Paragraph("Resume Screening Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Summary Statistics", heading_style))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Resumes Analyzed', str(len(results_df))],
        ['Average Score', f"{results_df['Overall Score'].mean():.2f}"],
        ['Highest Score', f"{results_df['Overall Score'].max():.2f}"],
        ['Lowest Score', f"{results_df['Overall Score'].min():.2f}"],
        ['Resumes Scored > 70', str(len(results_df[results_df['Overall Score'] >= 70]))],
        ['Resumes Scored 50-70', str(len(results_df[(results_df['Overall Score'] >= 50) & (results_df['Overall Score'] < 70)]))],
        ['Resumes Scored < 50', str(len(results_df[results_df['Overall Score'] < 50]))]
    ]
    
    summary_table = Table(summary_data, colWidths=[3.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Top 10 Candidates", heading_style))
    top_candidates = results_df.nlargest(10, 'Overall Score')[['Resume Name', 'Overall Score', 
                                                                'Keywords Matched', 'Keyword Match Score']]
    
    table_data = [['Rank', 'Resume Name', 'Score', 'Keywords', 'Match %']]
    for idx, row in enumerate(top_candidates.itertuples(), 1):
        table_data.append([str(idx), str(row._1)[:40], f"{row._2:.2f}", str(row._3), f"{row._4:.2f}"])
    
    top_table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 0.8*inch, 1*inch, 0.8*inch])
    top_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(top_table)
    story.append(PageBreak())
    
    story.append(Paragraph("Detailed Candidate Analysis", heading_style))
    for idx, row in results_df.sort_values('Overall Score', ascending=False).iterrows():
        story.append(Paragraph(f"<b>{row['Resume Name']}</b>", styles['Heading3']))
        detail_data = [
            ['Metric', 'Score/Value'],
            ['Overall Score', f"{row['Overall Score']:.2f}/100"],
            ['Keyword Match Score', f"{row['Keyword Match Score']:.2f}%"],
            ['Keywords Matched', f"{row['Keywords Matched']}/{row['Total Keywords in JD']}"],
            ['Education Score', f"{row['Education Score']:.2f}/20"],
            ['Experience Score', f"{row['Experience Score']:.2f}/15"],
            ['Technical Skills Score', f"{row['Technical Skills Score']:.2f}/15"],
        ]
        detail_table = Table(detail_data, colWidths=[2.5*inch, 2*inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(detail_table)
        if row['Matched Keywords'] != 'None':
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(f"<b>Keywords:</b> {row['Matched Keywords'][:200]}...", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. Enter Job Description
    2. Upload Resumes (PDF, DOCX, TXT)
    3. Click 'Analyze Resumes'
    4. Download Results
    
    ---
    
    ### Scoring Criteria:
    - **Keyword Match (50%)**
    - **Education (20%)**
    - **Experience (15%)**
    - **Technical Skills (15%)**
    """)
    st.info("💡 Include specific skills in JD for better matching")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Job Description")
    jd_text = st.text_area("Paste the complete job description here", height=300,
                          placeholder="Enter job description...")
    if jd_text:
        st.caption(f"✅ Characters: {len(jd_text):,} | Words: {len(jd_text.split()):,}")

with col2:
    st.subheader("📤 Upload Resumes")
    uploaded_files = st.file_uploader("Upload resume files", type=['pdf', 'docx', 'txt'],
                                     accept_multiple_files=True)
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        with st.expander("View files"):
            for file in uploaded_files:
                st.text(f"📄 {file.name}")

st.markdown("---")

if st.button("🔍 Analyze Resumes", type="primary", use_container_width=True):
    if not jd_text:
        st.error("⚠️ Please enter a job description!")
    elif not uploaded_files:
        st.error("⚠️ Please upload at least one resume!")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        
        for idx, file in enumerate(uploaded_files):
            status_text.text(f"Processing: {file.name} ({idx + 1}/{len(uploaded_files)})")
            progress_bar.progress((idx + 1) / len(uploaded_files))
            
            if file.name.endswith('.pdf'):
                resume_text = extract_text_from_pdf(file)
            elif file.name.endswith('.docx'):
                resume_text = extract_text_from_docx(file)
            elif file.name.endswith('.txt'):
                resume_text = extract_text_from_txt(file)
            else:
                continue
            
            if resume_text:
                results.append(score_resume(jd_text, resume_text, file.name))
        
        progress_bar.empty()
        status_text.empty()
        
        if results:
            results_df = pd.DataFrame(results).sort_values('Overall Score', ascending=False).reset_index(drop=True)
            st.session_state['results_df'] = results_df
            st.session_state['jd_text'] = jd_text
            st.success(f"✅ Successfully analyzed {len(results)} resumes!")
        else:
            st.error("❌ No valid resumes processed.")

if 'results_df' in st.session_state:
    results_df = st.session_state['results_df']
    jd_text = st.session_state['jd_text']
    
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Resumes", len(results_df))
    col2.metric("Average Score", f"{results_df['Overall Score'].mean():.2f}")
    col3.metric("Highest Score", f"{results_df['Overall Score'].max():.2f}")
    col4.metric("Lowest Score", f"{results_df['Overall Score'].min():.2f}")
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "📊 Visualizations", "🔍 Details", "📥 Export"])
    
    with tab1:
        st.subheader("Top Candidates Summary")
        def color_score(val):
            color = '#28a745' if val >= 70 else '#ffc107' if val >= 50 else '#dc3545'
            return f'background-color: {color}; color: white; font-weight: bold'
        
        display_df = results_df[['Resume Name', 'Overall Score', 'Keywords Matched', 
                                'Total Keywords in JD', 'Keyword Match Score']]
        st.dataframe(display_df.style.applymap(color_score, subset=['Overall Score']),
                    use_container_width=True, height=400)
    
    with tab2:
        st.subheader("Score Distribution")
        fig_hist = px.histogram(results_df, x='Overall Score', nbins=20,
                               title='Distribution of Resume Scores',
                               color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig_hist, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            score_categories = pd.cut(results_df['Overall Score'], bins=[0, 50, 70, 100],
                                     labels=['Below 50', '50-70', 'Above 70'])
            fig_pie = px.pie(values=score_categories.value_counts().values,
                           names=score_categories.value_counts().index,
                           title='Candidates by Score Range',
                           color_discrete_sequence=['#dc3545', '#ffc107', '#28a745'])
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            top_10 = results_df.nlargest(10, 'Overall Score')
            fig_bar = px.bar(top_10, x='Overall Score', y='Resume Name', orientation='h',
                           title='Top 10 Candidates', color='Overall Score',
                           color_continuous_scale='Blues')
            fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab3:
        st.subheader("Detailed Scoring Breakdown")
        selected_resume = st.selectbox("Select resume:", results_df['Resume Name'].tolist())
        
        if selected_resume:
            resume_data = results_df[results_df['Resume Name'] == selected_resume].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Score Components")
                components = {
                    'Keyword Match': resume_data['Keyword Match Score'],
                    'Education': resume_data['Education Score'] / 20 * 100,
                    'Experience': resume_data['Experience Score'] / 15 * 100,
                    'Technical Skills': resume_data['Technical Skills Score'] / 15 * 100
                }
                fig = go.Figure(data=[go.Bar(x=list(components.keys()), y=list(components.values()),
                                            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])])
                fig.update_layout(title='Score Breakdown', yaxis_title='Score (%)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### Metrics")
                st.metric("Overall Score", f"{resume_data['Overall Score']:.2f}/100")
                st.metric("Keywords Matched", f"{resume_data['Keywords Matched']}/{resume_data['Total Keywords in JD']}")
                st.metric("Match Percentage", f"{resume_data['Keyword Match Score']:.2f}%")
                st.metric("Resume Length", f"{resume_data['Resume Length (chars)']:,} chars")
            
            st.markdown("### Matched Keywords")
            if resume_data['Matched Keywords'] != 'None':
                st.info(f"**Keywords:** {resume_data['Matched Keywords']}")
            else:
                st.warning("No keywords matched")
    
    with tab4:
        st.subheader("Export Results")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Excel Export")
            excel_file = create_excel_report(results_df, jd_text)
            st.download_button("📥 Download Excel Report", data=excel_file,
                             file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             use_container_width=True)
        
        with col2:
            st.markdown("### 📄 PDF Export")
            pdf_file = create_pdf_report(results_df, jd_text)
            st.download_button("📥 Download PDF Report", data=pdf_file,
                             file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                             mime="application/pdf", use_container_width=True)
        
        st.info("💡 Excel includes: Summary, Detailed Breakdown, Statistics, and Job Description")
