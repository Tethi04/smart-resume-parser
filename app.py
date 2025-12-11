
import streamlit as st
import re
import json
import base64
from datetime import datetime
from io import StringIO
from pypdf import PdfReader
import pdfplumber

# Page configuration
st.set_page_config(
    page_title="Resume Parser",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #10B981;
        margin: 1rem 0;
    }
    .skill-chip {
        display: inline-block;
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 1rem;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF file using multiple methods for reliability"""
    text = ""
    
    try:
        # Method 1: Try pdfplumber first (better for most PDFs)
        with pdfplumber.open(uploaded_file) as pdf:
            pages_text = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            text = "\n".join(pages_text)
        
        # If pdfplumber returns empty or very little text, try PyPDF2
        if not text or len(text.strip()) < 50:
            uploaded_file.seek(0)  # Reset file pointer
            
            # Method 2: Try PyPDF2
            pdf_reader = PdfReader(uploaded_file)
            pages_text = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            text = "\n".join(pages_text)
    
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None
    
    return text

def main():
    # Header
    st.markdown('<h1 class="main-header">📄 Resume Parser</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background-color: #DBEAFE; padding: 1rem; border-radius: 0.5rem;'>
    <strong>✅ Extract information from resumes</strong><br>
    Works with PDF/TXT files or pasted text
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Options")
        input_method = st.radio("Choose input method:", ["Upload File", "Paste text"])
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        **Features:**
        • Extract emails & phones
        • Detect skills
        • Find education
        • Export as JSON
        • Supports PDF and TXT files
        """)
        st.markdown("---")
        st.markdown("**Deployed on Render** ✅")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📤 Input Resume")
        
        resume_text = ""
        
        if input_method == "Upload File":
            uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.lower().endswith('.pdf'):
                        with st.spinner("Extracting text from PDF..."):
                            resume_text = extract_text_from_pdf(uploaded_file)
                            if resume_text:
                                st.success(f"✅ PDF loaded: {uploaded_file.name}")
                                st.text_area("Preview (first 500 chars):", resume_text[:500], height=150)
                            else:
                                st.error("Could not extract text from PDF. Please try another file.")
                    else:  # TXT file
                        # Try UTF-8 first
                        resume_text = uploaded_file.read().decode("utf-8")
                        # Fallback to latin-1 if UTF-8 fails
                        if not resume_text.strip():
                            uploaded_file.seek(0)
                            resume_text = uploaded_file.read().decode("latin-1")
                        
                        if resume_text:
                            st.success(f"✅ TXT file loaded: {uploaded_file.name}")
                            st.text_area("Preview (first 500 chars):", resume_text[:500], height=150)
                
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        else:  # Paste text
            resume_text = st.text_area("Paste your resume text:", height=300, 
                                      placeholder="""Example:
John Doe
Software Engineer
john.doe@email.com
(123) 456-7890

SKILLS:
Python, JavaScript, React, AWS, SQL

EXPERIENCE:
Software Developer at TechCorp (2020-2023)
- Developed web applications
- Used Python and React

EDUCATION:
Bachelor of Computer Science
Stanford University (2018)""")
        
        if resume_text and st.button("🚀 Parse Resume", type="primary", use_container_width=True):
            with st.spinner("Parsing..."):
                result = parse_resume(resume_text)
                
                if result:
                    display_results(result, col2)
    
    with col2:
        st.markdown("### 📋 Quick Samples")
        samples = {
            "Software Engineer": """John Smith
Senior Software Engineer
john.smith@tech.com
(415) 555-1234

SKILLS: Python, JavaScript, React, Node.js, AWS, Docker

EXPERIENCE:
Google (2020-2023)
- Developed backend services
- Improved performance by 40%

Microsoft (2018-2020)
- Built web applications
- Fixed critical bugs

EDUCATION:
MIT - Computer Science (2018)""",
            
            "Data Scientist": """Sarah Johnson
Data Scientist
sarah.j@data.com
(212) 555-9876

SKILLS: Python, Machine Learning, SQL, TensorFlow, Pandas

EXPERIENCE:
DataCorp (2021-2023)
- Built ML models with 95% accuracy
- Analyzed large datasets

Analytics Inc. (2019-2021)
- Created dashboards
- Performed statistical analysis

EDUCATION:
Harvard - Data Science (2019)""",
            
            "Product Manager": """Mike Williams
Product Manager
mike.w@pm.com
(512) 555-4567

SKILLS: Product Management, Agile, Scrum, JIRA, UX

EXPERIENCE:
TechVision (2020-2023)
- Led product development
- Increased user engagement

Digital Co. (2018-2020)
- Managed mobile app
- Conducted user research

EDUCATION:
Stanford - MBA (2018)"""
        }
        
        sample_choice = st.selectbox("Choose sample:", list(samples.keys()))
        if st.button("Load Sample", use_container_width=True):
            st.session_state.sample_text = samples[sample_choice]
            st.rerun()
        
        if 'sample_text' in st.session_state:
            st.text_area("Sample loaded:", st.session_state.sample_text, height=200)

def parse_resume(text):
    """Parse resume text and extract information"""
    
    # Extract emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    
    # Extract phones
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    
    # Extract name (first line usually)
    lines = text.strip().split('\n')
    name = ""
    for line in lines[:5]:
        line = line.strip()
        if line and not any(x in line.lower() for x in ['@', 'http', 'linkedin', 'github']):
            words = line.split()
            if 2 <= len(words) <= 4:
                name = line
                break
    
    if not name and lines:
        name = lines[0].strip()
    
    # Extract skills
    skill_categories = {
        'Programming': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'HTML', 'CSS'],
        'Web': ['React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask'],
        'Databases': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB'],
        'Cloud': ['AWS', 'Azure', 'Docker', 'Kubernetes'],
        'Tools': ['Git', 'GitHub', 'JIRA', 'Linux']
    }
    
    found_skills = []
    for category, skills in skill_categories.items():
        for skill in skills:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text.lower()):
                found_skills.append(skill)
    
    # Extract education
    education = []
    edu_keywords = ['university', 'college', 'institute', 'bachelor', 'master', 'phd', 'mba', 'degree']
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in edu_keywords):
            education_entry = {'text': line.strip()}
            
            # Look for year
            year_match = re.search(r'\b(19|20)\d{2}\b', line)
            if year_match:
                education_entry['year'] = year_match.group()
            
            education.append(education_entry)
    
    # Extract experience
    experience = []
    exp_keywords = ['experience', 'work', 'employment', 'internship', 'developer', 'engineer', 'manager']
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in exp_keywords):
            exp_entry = {'text': line.strip()}
            
            # Look for company
            company_patterns = [' at ', '|', '-', '–']
            for pattern in company_patterns:
                if pattern in line:
                    parts = line.split(pattern)
                    if len(parts) >= 2:
                        exp_entry['title'] = parts[0].strip()
                        exp_entry['company'] = parts[1].strip()
                        break
            
            experience.append(exp_entry)
    
    # LinkedIn
    linkedin_pattern = r'linkedin\.com/[^\s]+'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    linkedin = linkedin_match.group() if linkedin_match else ""
    
    result = {
        'name': name,
        'email': emails[0] if emails else "",
        'emails_all': emails,
        'phone': phones[0] if phones else "",
        'phones_all': phones,
        'linkedin': linkedin,
        'skills': found_skills,
        'education': education[:3],  # Max 3
        'experience': experience[:3],  # Max 3
        'text_preview': text[:300] + "..." if len(text) > 300 else text,
        'parsed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'word_count': len(text.split())
    }
    
    return result

def display_results(result, col):
    """Display parsing results"""
    
    st.markdown("---")
    st.markdown('<div class="success-box"><strong>✅ Parsing Complete!</strong></div>', unsafe_allow_html=True)
    
    # Create tabs
    tabs = st.tabs(["👤 Personal", "🛠️ Skills", "🎓 Education", "💼 Experience"])
    
    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {result['name']}")
            if result['email']:
                st.write(f"**Email:** {result['email']}")
            if result['phone']:
                st.write(f"**Phone:** {result['phone']}")
            if result['linkedin']:
                st.write(f"**LinkedIn:** {result['linkedin']}")
        with col2:
            st.write(f"**Parsed:** {result['parsed_date']}")
            st.write(f"**Word count:** {result['word_count']}")
            st.write(f"**Skills found:** {len(result['skills'])}")
            st.write(f"**Education entries:** {len(result['education'])}")
    
    with tabs[1]:
        skills = result['skills']
        if skills:
            st.write(f"**Found {len(skills)} skills:**")
            cols = st.columns(3)
            skills_per_col = (len(skills) + 2) // 3
            
            for i in range(3):
                with cols[i]:
                    start = i * skills_per_col
                    end = min((i + 1) * skills_per_col, len(skills))
                    for skill in skills[start:end]:
                        st.markdown(f'<span class="skill-chip">{skill}</span>', unsafe_allow_html=True)
        else:
            st.info("No skills detected")
    
    with tabs[2]:
        education = result['education']
        if education:
            for edu in education:
                st.write(f"• {edu['text']}")
        else:
            st.info("No education information found")
    
    with tabs[3]:
        experience = result['experience']
        if experience:
            for exp in experience:
                st.write(f"• {exp['text']}")
        else:
            st.info("No experience information found")
    
    # Export options
    st.markdown("---")
    st.markdown("### 📤 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Download JSON", use_container_width=True):
            download_json(result)
    
    with col2:
        if st.button("📄 Download TXT", use_container_width=True):
            download_txt(result)
    
    with col3:
        if st.button("🔄 Parse Another", use_container_width=True):
            st.rerun()

def download_json(data):
    """Download as JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resume_data_{timestamp}.json"
    
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    b64 = base64.b64encode(json_str.encode()).decode()
    
    href = f'<a href="data:application/json;base64,{b64}" download="{filename}">⬇️ Click here to download JSON</a>'
    st.markdown(href, unsafe_allow_html=True)

def download_txt(data):
    """Download as TXT report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resume_report_{timestamp}.txt"
    
    txt_content = f"""RESUME PARSING REPORT
======================

Name: {data['name']}
Email: {data['email']}
Phone: {data['phone']}
LinkedIn: {data['linkedin']}

SKILLS ({len(data['skills'])} found):
{', '.join(data['skills'])}

EDUCATION:
"""
    
    for edu in data['education']:
        txt_content += f"- {edu['text']}\n"
    
    txt_content += f"\nEXPERIENCE:\n"
    
    for exp in data['experience']:
        txt_content += f"- {exp['text']}\n"
    
    txt_content += f"\nParsed on: {data['parsed_date']}"
    txt_content += f"\nWord count: {data['word_count']}"
    
    b64 = base64.b64encode(txt_content.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}">⬇️ Click here to download TXT</a>'
    st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
