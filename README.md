# Destroyer Wordlist Generator

A targeted wordlist and passphrase generation utility engineered for authorized penetration testing, security auditing, and password policy validation.

---

## 1. Technical Architecture

Destroyer operates as a pipeline consisting of four primary phases:

```
+-------------------------------------------------------------+
|                     Reconnaissance Input                    |
|  - JSON Target Profile (profiles/*.json)                    |
|  - Interactive CLI Questionnaire                            |
|  - HTTP Keyword Harvester (CeWL-style web spider)           |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                  TargetProfile Data Layer                   |
|  - Normalizes demographic, associative, and corporate data  |
|  - Extracts numeric calendar substrings & phone fragments   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|             Combinatorial Engine (PCFG Models)              |
|  - Multi-token Passphrase Synthesis                         |
|  - Organizational Directory Rollovers (Seasons/Months/Qtrs) |
|  - Temporal Token Injection (1950 - 2030, Short Years)      |
|  - Selective and Light Leetspeak Mutations                  |
|  - Keyboard Walk Sequences                                  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|              Filtering, Metrics & Output Stream             |
|  - Length Shaping (wcfrom to wcto / NIST SP 800-63B)        |
|  - In-Memory Bounded Set Deduplication (Memory-Safe)        |
|  - Shannon Keyspace Entropy Computation                     |
|  - Plaintext Candidate Dictionary (*.txt)                   |
|  - Hashcat / John the Ripper Rules (*.rule) & Masks (*.hcmask)
+-------------------------------------------------------------+
```

### 1.1 Combinatorial Strategy & PCFG Production Templates

Instead of unconstrained Cartesian expansion, Destroyer generates candidates using Probabilistic Context-Free Grammar (PCFG) templates reflecting observed password structural distributions:

* **Template 1 (Word + Year + Punctuation):** $S \rightarrow \text{Token}_{\text{case}} \cdot \text{Year} \cdot \text{Symbol}$ (e.g., `Shadow2026!`, `Mercer2027@`)
* **Template 2 (Prefix Punctuation + Word + Year):** $S \rightarrow \text{Symbol} \cdot \text{Token}_{\text{case}} \cdot \text{Year}$ (e.g., `@Shadow2027`, `!Mercer2026`)
* **Template 3 (Word + Inner Punctuation + Year):** $S \rightarrow \text{Token}_{\text{case}} \cdot \text{Symbol} \cdot \text{Year}$ (e.g., `Shadow@2027`, `Mercer#2026`)
* **Template 4 (Word + Sequence + Punctuation):** $S \rightarrow \text{Token}_{\text{case}} \cdot \text{Sequence} \cdot \text{Symbol}$ (e.g., `Shadow123!`, `Alex123456@`)
* **Template 5 (Organizational Rollover):** $S \rightarrow \text{CorporateToken} \cdot \text{Year} \cdot \text{Symbol}$ (e.g., `CyberCorp2027!`, `Welcome2026#`)
* **Template 6 (Directory Cycle Rollover):** $S \rightarrow \text{Season/Month/Quarter} \cdot \text{Year} \cdot \text{Symbol}$ (e.g., `Spring2027!`, `October2026!`, `Q12027#`)
* **Template 7 (Multi-Token Passphrase):** $S \rightarrow \text{Token}_1 \cdot \text{Delimiter} \cdot \text{Token}_2 \cdot \text{Delimiter} \cdot \text{Year} \cdot \text{Symbol}$ (e.g., `Mercer-Alexpwns-2027!`)
* **Template 8 (Date & Calendar Suffixes):** $S \rightarrow \text{Token}_{\text{case}} \cdot \text{DateSubstr}$ (e.g., `Alex14051996`, `Shadow96!`)
* **Template 9 (Keyboard Walk Patterns):** $S \rightarrow \text{Token}_{\text{case}} \cdot \text{Walk}$ (e.g., `Shadow123456`, `Alex!@#$%^`)

### 1.2 Keyspace Entropy Measurement

The generator computes theoretical keyspace entropy in bits for each candidate:

$$H = L \cdot \log_2(|R|)$$

Where:
* $L$ = Length of the candidate string.
* $|R|$ = Cardinality of the active character set pool:
  * Lowercase letters: $26$
  * Uppercase letters: $26$
  * Digits: $10$
  * Punctuation / Symbols: $33$

Mean entropy is reported in the final execution summary to evaluate candidate strength against NIST SP 800-63B standards.

### 1.3 Memory-Bounded Streaming Architecture

To prevent Out-Of-Memory (OOM) conditions during large permutations, candidates are yielded via Python generators and written to disk through a 64 KB I/O buffer. In-memory deduplication uses a hash set capped at $1.5 \times 10^6$ entries, maintaining predictable memory consumption under 100 MB even when generating millions of candidates.

---

## 2. Installation & Requirements

Destroyer requires Python 3.8 or newer and uses the standard library by default.

```bash
git clone https://github.com/Destroyer-official/Destroyer-wordlist-generator.git
cd Destroyer-wordlist-generator
```

### Optional UI Dependency
To enable enhanced terminal tables, install `rich`:
```bash
pip install -r requirements.txt
```
If `rich` is not installed, the tool automatically falls back to standard ANSI formatting.

---

## 3. Configuration Reference (`destroyer.cfg`)

The application loads configuration parameters from `destroyer.cfg` via `configparser.ConfigParser(interpolation=None)`.

| Section | Key | Description | Default Values |
| :--- | :--- | :--- | :--- |
| `[years]` | `years` | 4-digit calendar years for temporal tokens | `1950,1951,...,2030` |
| `[years]` | `short_years` | 2-digit year representations | `24,25,26,27,28,29,30,95..23` |
| `[corporate_cycles]` | `seasons` | Seasonal tokens for rotation policies | `Spring,Summer,Autumn,Fall,Winter` |
| `[corporate_cycles]` | `quarters` | Fiscal quarter identifiers | `Q1,Q2,Q3,Q4,H1,H2,FY24..FY28` |
| `[corporate_cycles]` | `months` | Full month names for reset policies | `January,February,...,December` |
| `[corporate_cycles]` | `short_months` | Abbreviated month names | `Jan,Feb,Mar,...,Dec` |
| `[keyboard_walks]` | `walks` | Spatial keyboard sequences | `123456,12345678,qweasd,asdfgh,zaq12wsx,!@#$,!@#$%^` |
| `[leet]` | `<letter>` | Substitution mapping for leetspeak | `a=4, i=1, e=3, t=7, o=0, s=5, g=9, z=2, b=8` |
| `[specialchars]` | `chars` | Punctuation for prefix/suffix injection | `!,@,#,$,%,&,*,-,_,=,+,?,~,<,>` |
| `[separators]` | `separators` | Delimiters for multi-token passphrases | `-,_,.,@,#,$,!,&` |
| `[nums]` | `from`, `to` | Numeric range for deep-mode suffix padding | `0` to `100` |
| `[shaping]` | `wcfrom`, `wcto` | Length filter bounds in characters | `8` to `64` |
| `[nist]` | `min_passphrase_length` | Minimum bound for NIST SP 800-63B | `15` |
| `[scraper]` | `user_agent`, `timeout` | HTTP harvesting parameters | Chrome UA, `10`s timeout, max 60 words |

---

## 4. Command-Line Interface (CLI)

```
usage: wordlist_generator.py [-h] [-i] [-p PROFILE] [-u URL] [-o OUTPUT]
                             [-m {fast,standard,deep,passphrase}]
                             [--min-len MIN_LEN] [--max-len MAX_LEN] [--nist]
                             [--leet {off,light,standard}] [--no-corporate]
                             [--hashcat-rules HASHCAT_RULES]
                             [--hashcat-masks HASHCAT_MASKS]
                             [--save-profile SAVE_PROFILE] [--no-banner]
                             [--inspect]
```

### Argument Reference

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `-i, --interactive` | Flag | `False` | Launch interactive terminal questionnaire. |
| `-p, --profile` | `FILE` | `None` | Path to target reconnaissance JSON file. |
| `-u, --url` | `URL` | `None` | Target HTTP/HTTPS endpoint to crawl for keywords. |
| `-o, --output` | `FILE` | `passwords.txt` | Filepath for compiled candidate output. |
| `-m, --mode` | `STRING` | `standard` | Generation depth: `fast`, `standard`, `deep`, or `passphrase`. |
| `--min-len` | `INT` | `8` | Minimum candidate length filter. |
| `--max-len` | `INT` | `64` | Maximum candidate length filter. |
| `--nist` | Flag | `False` | Enforce NIST SP 800-63B minimum length bound of 15 characters. |
| `--leet` | `STRING` | `light` | Leetspeak strategy: `off`, `light` (selective), or `standard`. |
| `--no-corporate` | Flag | `False` | Disable organizational and directory rotation patterns. |
| `--hashcat-rules` | `FILE` | `None` | Filepath to export a targeted Hashcat `.rule` file. |
| `--hashcat-masks` | `FILE` | `None` | Filepath to export a targeted Hashcat `.hcmask` file. |
| `--save-profile` | `FILE` | `None` | Save questionnaire inputs to a JSON profile. |
| `--no-banner` | Flag | `False` | Suppress terminal banner for UNIX pipeline integration. |
| `--inspect` | Flag | `False` | Print top 50 generated entries to stdout upon completion. |

---

## 5. Target Profile Schema (`profile.json`)

Target attributes can be structured into a JSON file for automated pipelines:

```json
{
    "name": "alex",
    "surname": "mercer",
    "nick": "shadow",
    "handles": ["alexpwns", "shadow_m"],
    "email": "alex.mercer@cybercorp.internal",
    "birthdate": "14051996",
    "mobile": "9876543210",
    "partner_name": "elena",
    "partner_nick": "ellie",
    "partner_birthdate": "22081998",
    "guardian_name": "robert",
    "guardian_nick": "bob",
    "guardian_birthdate": "10021968",
    "children_names": ["leo"],
    "pet_names": ["thor", "luna"],
    "company": "cybercorp",
    "company_acronym": "ccorp",
    "department": "devops",
    "domain": "cybercorp.internal",
    "project_names": ["apollo", "titan"],
    "target_url": "https://cybercorp.internal",
    "city": "seattle",
    "sports_team": "seahawks",
    "keywords": ["hacker", "crypto", "matrix", "cloud"]
}
```

---

## 6. Execution Examples

### 6.1 Automated Generation via Profile
```bash
python wordlist_generator.py -p profiles/target_example.json -o wordlist.txt
```

### 6.2 Profile Generation with Web Crawling
```bash
python wordlist_generator.py -p profiles/target_example.json --url https://cybercorp.internal -o corp_wordlist.txt
```

### 6.3 Dedicated NIST SP 800-63B Passphrase Generation
```bash
python wordlist_generator.py -p profiles/target_example.json --nist -m passphrase -o passphrases.txt
```

### 6.4 Exporting Hashcat Rules and Masks
```bash
python wordlist_generator.py -p profiles/target_example.json -o base_words.txt --hashcat-rules custom.rule --hashcat-masks custom.hcmask
```

Pipeline execution with Hashcat:
```bash
# Rule-based dictionary attack (Mode 0):
hashcat -a 0 -m 1000 ntlm_hashes.txt base_words.txt -r custom.rule

# Mask attack using generated structural lengths (Mode 3):
hashcat -a 3 -m 1000 ntlm_hashes.txt custom.hcmask
```

---

## 7. Compliance & Standards Context

* **NIST SP 800-63B (Section 5.1.1.2):**
  * Specifies minimum password lengths of 8 characters for human-chosen passwords, recommending 15+ characters for higher security assurance.
  * Explicitly discourages periodic forced resets and arbitrary composition rules (e.g. requiring a mix of uppercase, digits, and symbols), favoring long multi-token passphrases.
* Destroyer's `--nist` mode enforces these length constraints, filtering out short strings while synthesizing high-entropy multi-token passphrases using target context.

---

## 8. License & Ethical Disclaimer

### License
This project is licensed under the [MIT License](LICENSE).

### Disclaimer
This utility is intended exclusively for authorized security audits, vulnerability assessments, and penetration testing engagements conducted under explicit, written authorization. Unauthorized use of this tool against systems without prior consent is illegal and strictly prohibited. The author assumes no liability for misuse of this software.
