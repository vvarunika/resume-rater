
<h1 align="center">SkillMatch – Resume Rater</h1>

<p align="center">
  <strong>A Resume Analysis Tool for Smarter Job Applications</strong>
</p>

<p align="center">
  A Python-based web application that analyzes resumes against job descriptions
  and helps job seekers understand how well their skills align with job requirements.
</p>

<hr>

<h2>📌 Overview</h2>

<p>
  Applying for jobs without understanding whether your resume matches the
  job requirements can reduce your chances of getting noticed.
</p>

<p>
  SkillMatch aims to simplify this process by comparing resume content with
  job descriptions, identifying matching keywords, and generating a match
  score to help users evaluate their resume.
</p>

<h2>✨ Features</h2>

<ul>
  <li><strong>Resume Upload:</strong> Upload your resume for automated analysis.</li>
  <li><strong>Job Description Analysis:</strong> Process job descriptions to identify relevant requirements.</li>
  <li><strong>Resume Parsing:</strong> Extract text and relevant information from uploaded resumes.</li>
  <li><strong>Match Score:</strong> Calculate similarity between the resume and job description.</li>
  <li><strong>Keyword Matching:</strong> Identify matching terms between both documents.</li>
  <li><strong>Visual Results:</strong> Display analysis results through charts and keyword insights.</li>
</ul>

<h2>🛠️ Tech Stack</h2>

<table>
  <tr>
    <th>Technology</th>
    <th>Purpose</th>
  </tr>
  <tr>
    <td>Python</td>
    <td>Core application logic</td>
  </tr>
  <tr>
    <td>Flask</td>
    <td>Web application framework</td>
  </tr>
  <tr>
    <td>HTML</td>
    <td>Frontend structure</td>
  </tr>
  <tr>
    <td>CSS</td>
    <td>Frontend styling</td>
  </tr>
  <tr>
    <td>JavaScript</td>
    <td>Frontend interactions</td>
  </tr>
  <tr>
    <td>TF-IDF</td>
    <td>Text feature extraction</td>
  </tr>
  <tr>
    <td>Scikit-learn</td>
    <td>Text similarity analysis</td>
  </tr>
  <tr>
    <td>PyMuPDF</td>
    <td>PDF text extraction</td>
  </tr>
</table>

<h2>⚙️ How It Works</h2>

<ol>
  <li><strong>Upload Resume:</strong> The user uploads a resume.</li>
  <li><strong>Enter Job Description:</strong> The user provides a job description for comparison.</li>
  <li><strong>Text Extraction:</strong> Resume content is extracted using the PDF parsing module.</li>
  <li><strong>Text Processing:</strong> Both documents are processed for comparison.</li>
  <li><strong>Similarity Calculation:</strong> TF-IDF and cosine similarity are used to calculate textual similarity.</li>
  <li><strong>Results:</strong> The application displays the match score and relevant keyword insights.</li>
</ol>

<h2>📂 Project Structure</h2>

<pre>
resume-rater/
│
├── app.py
├── analyzer.py
├── parser.py
├── requirements.txt
├── README.md
│
├── static/
├── templates/
│
└── .gitignore
</pre>

<h2>🔮 Future Improvements</h2>

<ul>
  <li>Improve resume analysis accuracy.</li>
  <li>Expand skill and keyword identification.</li>
  <li>Improve the user interface and responsive design.</li>
  <li>Add support for additional resume formats.</li>
  <li>Provide more detailed suggestions for improving resume-job alignment.</li>
</ul>

<h2>📌 Project Status</h2>

<p>
  <strong>Currently under development.</strong>
</p>

<p>
  SkillMatch is an ongoing project. New improvements, refinements,
  and features will be added as development progresses.
</p>

<h2>👩‍💻 Author</h2>

<p>
  <strong>Varunika Vats</strong><br>
  B.Tech – Computer Science and Engineering
</p>

<p>
  GitHub:
  <a href="https://github.com/vvarunika">
    @vvarunika
  </a>
</p>

<hr>

<p align="center">
  Built to explore Python-based text processing, resume analysis,
  and job description matching.
</p>
