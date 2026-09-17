# FormResponseBot

FormResponseBot is an automated Google Forms response generator designed for **synthetic survey data generation, form testing, research prototyping, and academic projects**.

It can scan a Google Form, detect supported question types, configure response distributions, generate synthetic respondents, and submit responses through a fresh Chrome browser session.

For open-ended questions, FormResponseBot can use a locally running Ollama model to generate varied natural-language responses.

> **Important:** FormResponseBot generates synthetic/fabricated survey data. Synthetic responses must not be presented as responses collected from real participants.

---

## Features

### Custom Response Distribution

Control how frequently each option should appear.

Example:

```text
Question: How satisfied are you with the service?

Very Satisfied     -> 20%
Satisfied          -> 40%
Neutral            -> 25%
Dissatisfied       -> 10%
Very Dissatisfied  -> 5%