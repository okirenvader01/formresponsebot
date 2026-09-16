# FormResponseBot 🤖📋

**FormResponseBot** is an automated Google Forms response generator designed for **synthetic survey data generation, form testing, research prototyping, and academic projects**.

It allows you to automatically generate a configurable number of responses and control the **percentage distribution of answers for individual questions**. For open-ended questions, it can use a local Ollama model to generate varied, natural-language responses.

> **Important:** FormResponseBot generates **synthetic/fabricated survey data**. It should be used for testing forms, demonstrations, prototypes, statistical exercises, research methodology practice, and academic work where synthetic data is permitted. Synthetic responses should not be presented as responses collected from real participants.

---

## ✨ Features

### 📊 Custom Response Distribution

Control how frequently each option should appear.

For example:

```text
Question: How satisfied are you with the service?

Very Satisfied     → 20%
Satisfied          → 40%
Neutral            → 25%
Dissatisfied       → 10%
Very Dissatisfied  → 5%
```

The bot automatically generates responses according to the distribution you specify.

---

### 🔢 Generate Any Number of Responses

Choose the number of synthetic responses you want to generate:

```text
How many responses do you want to generate?
> 500
```

The bot will generate and submit the requested number of responses.

---

### 📝 Supports Multiple Question Types

FormResponseBot is designed to work with common Google Forms question types, including:

* Multiple Choice
* Linear Scale
* Checkboxes
* Dropdown
* Short Answer
* Paragraph
* Multi-page forms

---

### 🧠 AI-Generated Open-Ended Responses

For text-based questions, FormResponseBot can connect to **Ollama** and use a locally running language model to generate varied responses.

For example:

```text
What did you like most about our product?

→ "I liked the overall quality and the fact that it was easy to use."

→ "The product was convenient and worked well for my daily needs."

→ "The pricing was reasonable and I particularly liked the packaging."
```

The goal is to avoid generating the exact same sentence repeatedly.

---

### 👤 Synthetic Respondent Names

Where a form asks for a name, the generator can create synthetic names rather than repeatedly entering the same identity.

Example:

```text
Rahul Mohanty
Ananya Das
Sambit Jena
Priyanka Sahu
Arjun Patnaik
```

These are **synthetic identities** and should not be treated as real respondents.

---

### 🌐 Multi-Page Form Support

FormResponseBot can navigate through forms containing multiple pages/sections.

It detects the questions on each page and moves through the form automatically.

---

### 🔄 Fresh Browser Session

Each synthetic respondent can be processed using a fresh Chrome session.

This helps prevent one generated respondent's browser state from unintentionally carrying over into the next response.

---

### 📈 Submission Logging

The bot maintains a submission log containing information such as:

```text
Respondent ID
Submission status
Confirmation status
Error information
```

This makes it easier to identify failed submissions during large runs.

---

## 🛠️ How It Works

The basic workflow is:

```text
             ┌─────────────────┐
             │   Google Form   │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │  Form Scanner   │
             │                 │
             │ Detect questions│
             │ Detect options  │
             │ Detect sections │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Distribution    │
             │ Configuration   │
             │                 │
             │ 40% Option A    │
             │ 35% Option B    │
             │ 25% Option C    │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Respondent      │
             │ Generator       │
             └────────┬────────┘
                      │
             ┌────────┴────────┐
             ▼                 ▼
      Structured Answers   AI Text Answers
             │                 │
             └────────┬────────┘
                      ▼
             ┌─────────────────┐
             │ Selenium /      │
             │ Chrome          │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Google Form     │
             │ Submission      │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Submission Log  │
             └─────────────────┘
```

---

# 🚀 Installation

## Option 1 — Install from the GitHub repository

Clone the repository:

```bash
git clone https://github.com/okirenvader01/formresponsebot.git
```

Move into the project directory:

```bash
cd formresponsebot
```

Install the package:

```bash
pip install .
```

The required Python dependencies will be installed automatically.

---

## Option 2 — Developer Installation

If you want to modify the source code:

```bash
git clone https://github.com/okirenvader01/formresponsebot.git
cd formresponsebot
pip install -e .
```

The `-e` option installs the project in editable mode, so changes to the source code can be tested without reinstalling the package.

---

# 📦 Requirements

FormResponseBot requires:

* Python 3.10+
* Google Chrome
* Internet connection
* Selenium
* Requests
* Pandas

For AI-generated open-ended responses:

* Ollama
* A compatible Ollama model

The Python dependencies are installed automatically when installing the package.

---

# 🧠 Ollama Setup

FormResponseBot can use Ollama to generate responses to open-ended questions.

Install Ollama from:

https://ollama.com/

After installing Ollama, download a model.

For example:

```bash
ollama pull llama3.2:3b
```

Make sure Ollama is running locally.

The default endpoint is:

```text
http://localhost:11434
```

The default model used by the project is:

```text
llama3.2:3b
```

You can change the model configuration in the project settings.

---

# ▶️ Usage

Start FormResponseBot:

```bash
formresponsebot
```

The program will guide you through the process.

You will be asked for information such as:

```text
Google Form URL:
>

Number of responses:
> 100
```

The program will then scan the form and identify its questions.

For questions with selectable options, you can specify the desired distribution.

For example:

```text
Question:
How often do you purchase online?

Every day
Every week
Every month
Rarely
```

You could configure:

```text
Every day    → 10%
Every week   → 35%
Every month  → 40%
Rarely       → 15%
```

The generated responses will approximately follow the specified distribution.

---

# 📊 Distribution Examples

## Multiple Choice

For:

```text
Which platform do you use most?

Instagram
YouTube
Facebook
LinkedIn
```

You could specify:

```text
Instagram → 40%
YouTube   → 35%
Facebook  → 15%
LinkedIn  → 10%
```

Total:

```text
40 + 35 + 15 + 10 = 100%
```

---

## Linear Scale

For a 1–5 satisfaction question:

```text
1 → 5%
2 → 10%
3 → 25%
4 → 40%
5 → 20%
```

The bot will use these probabilities when generating responses.

---

## Checkboxes

Checkbox questions work differently because respondents can select multiple options.

For example:

```text
Which features do you use?

☐ Price comparison
☐ Reviews
☐ Discounts
☐ Recommendations
```

Each option can have its own selection probability.

Therefore, checkbox percentages **do not necessarily need to add up to 100%**.

---

# 🧪 Example Use Cases

FormResponseBot can be useful for:

### Academic Projects

Generate synthetic datasets for:

* Statistical analysis
* Regression exercises
* Correlation analysis
* Data visualization
* Machine learning demonstrations
* Survey methodology projects
* Business research assignments

### Form Testing

Test whether a Google Form behaves correctly with:

* Large numbers of responses
* Different answer combinations
* Required questions
* Multiple pages
* Different question types

### Research Prototyping

Create a synthetic dataset before collecting actual responses to test:

* Questionnaire design
* Statistical methods
* Data-cleaning pipelines
* Visualization dashboards
* Analysis scripts

### Demonstrations

Useful for demonstrating survey-analysis workflows without exposing real participant information.

---

# ⚠️ Responsible Use

FormResponseBot generates **synthetic responses**.

Do not use generated responses to falsely claim that:

* real people participated in a survey;
* a survey was conducted when it was not;
* participants provided opinions they never provided;
* fabricated data represents real-world respondents.

If synthetic data is used in an academic report, research project, presentation, or publication, clearly identify it as **synthetic/generated data** whenever disclosure is required.

Only automate forms that you own or have explicit permission to test.

The developer is not responsible for misuse of the software.

---

# 🔐 Privacy

FormResponseBot is designed to generate synthetic responses locally.

When Ollama is used, text generation is performed through the local Ollama service rather than requiring survey answers to be sent to a remote AI API.

However, Selenium still interacts with the Google Form through your browser and internet connection.

Do not enter real people's private or sensitive information into synthetic-data generation workflows.

---

# 🏗️ Project Structure

The project is organized into separate components:

```text
formresponsebot/
│
├── src/
│   └── formresponsebot/
│       │
│       ├── cli.py
│       │
│       ├── scanner/
│       │   └── form_scanner.py
│       │
│       ├── generator/
│       │   ├── ollama.py
│       │   ├── names.py
│       │   └── respondent.py
│       │
│       └── submission/
│           ├── browser.py
│           ├── form_filler.py
│           └── submitter.py
│
├── tests/
│
├── README.md
├── pyproject.toml
└── LICENSE
```

---

# 🔮 Planned Features

Future versions may include:

* [ ] Conditional question / branching support
* [ ] Automatic dropdown option detection
* [ ] Better Google Forms question detection
* [ ] CSV-based response generation
* [ ] Import distributions from CSV/Excel
* [ ] Export generated datasets before submission
* [ ] Dry-run mode
* [ ] Preview generated responses
* [ ] Custom respondent profiles
* [ ] Custom demographic distributions
* [ ] More Ollama model configuration
* [ ] Improved error recovery
* [ ] GUI interface
* [ ] Configuration files
* [ ] Automated statistical validation of generated distributions
* [ ] PyPI distribution

---

# 🤝 Contributing

Contributions are welcome.

If you find a bug or have an idea for a feature:

1. Fork the repository.
2. Create a new branch.

```bash
git checkout -b feature/my-feature
```

3. Make your changes.
4. Test them.
5. Commit your changes.

```bash
git commit -m "Add my feature"
```

6. Push the branch.

```bash
git push origin feature/my-feature
```

7. Open a Pull Request.

---

# 🐛 Reporting Issues

If you encounter a problem, please include:

* Operating system
* Python version
* Browser version
* Form question type causing the problem
* Error message
* Steps to reproduce the issue

Do **not** include private Google Forms, personal information, authentication credentials, or private survey responses in an issue.

---

# 📄 License

This project is distributed under the terms of the license included in this repository.

See:

```text
LICENSE
```

for details.

---

# 👨‍💻 Author

**Amrit Mohanty**

GitHub:

https://github.com/okirenvader01

Project:

https://github.com/okirenvader01/formresponsebot

---

## ⭐ Support the Project

If you find FormResponseBot useful for testing, synthetic-data generation, or academic experimentation, consider giving the repository a ⭐ on GitHub.

Contributions, bug reports, feature requests, and improvements are welcome.

```

I would use this version rather than describing the tool as making fabricated surveys "look organic." That wording makes the project sound like it's intended to deceive. The README can still clearly explain that it generates **realistic synthetic data**, while making the legitimate research/testing purpose explicit.
```
