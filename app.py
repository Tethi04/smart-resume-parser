"""
ULTRA SIMPLE Resume Parser
Works 100% on Render - No external dependencies
"""
import streamlit as st
import re
import json
import base64
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Resume Parser",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Simple Resume Parser")
st.markdown("Upload a TXT file to extract information")

# File upload
uploaded_file = st.file_uploader("Choose a TXT file", type=["txt"])

if uploaded_file is not None:
    # Read the file
    text = uploaded_file.read().decode("utf-8")
    
    # Extract email
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    
    # Extract phone
    phones = re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    
    # Extract skills (simple list)
    skills_list = ["Python", "Java", "JavaScript", "React", "SQL", "AWS", "Docker", "Git"]
    found_skills = []
    for skill in skills_list:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text.lower()):
            found_skills.append(skill)
    
    # Simple name extraction (first line)
    lines = text.split('\n')
    name = lines[0].strip() if lines else "Unknown"
    
    # Display results
    st.success("✅ Resume parsed successfully!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Contact Info")
        if name:
            st.write(f"**Name:** {name}")
        if emails:
            st.write(f"**Email:** {emails[0]}")
        if phones:
            st.write(f"**Phone:** {phones[0]}")
    
    with col2:
        st.subheader("Skills Found")
        if found_skills:
            for skill in found_skills:
                st.code(skill)
        else:
            st.info("No skills detected")
    
    # Download as JSON
    st.subheader("📥 Download Results")
    
    result = {
        "name": name,
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "skills": found_skills,
        "parsed_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    json_str = json.dumps(result, indent=2)
    b64 = base64.b64encode(json_str.encode()).decode()
    
    href = f'<a href="data:application/json;base64,{b64}" download="resume_result.json">⬇️ Download as JSON</a>'
    st.markdown(href, unsafe_allow_html=True)

# Add sample text
with st.expander("📝 Don't have a resume? Try this sample:"):
    sample_text = """John Doe
Software Engineer
john.doe@email.com
(123) 456-7890

SKILLS:
Python, JavaScript, React, AWS, Docker, Git

EXPERIENCE:
Software Developer at TechCorp (2020-2023)
- Developed web applications
- Used Python and React

EDUCATION:
Bachelor of Computer Science
Stanford University"""
    
    st.code(sample_text)
    
    if st.button("Parse Sample Resume"):
        # Extract from sample
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', sample_text)
        phones = re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', sample_text)
        
        skills_list = ["Python", "Java", "JavaScript", "React", "SQL", "AWS", "Docker", "Git"]
        found_skills = []
        for skill in skills_list:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', sample_text.lower()):
                found_skills.append(skill)
        
        st.success("Sample parsed!")
        st.write(f"**Name:** John Doe")
        st.write(f"**Email:** {emails[0] if emails else ''}")
        st.write(f"**Phone:** {phones[0] if phones else ''}")
        st.write(f"**Skills:** {', '.join(found_skills)}")

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | Deployed on Render")
