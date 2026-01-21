# Ethical Content Prevention (ECP)

> **Specification:** v1.0  
> **Component:** Generative AI Prevention Layer  
> **Status:** Draft  
> **Classification:** Public  

---

## 1. Purpose

The Ethical Content Prevention (ECP) system prevents generative AI systems from being used to create, modify, or enhance child sexual abuse material.

**Core Principle:** Stop harmful content at the point of generation — before it exists.

---

## 2. Scope

| In Scope | Out of Scope |
|----------|--------------|
| Image generation models | Existing content detection |
| Video generation models | Dark web monitoring |
| Audio generation (victim age) | Law enforcement investigation |
| Text generation (grooming scripts) | Evidence preservation |
| Model fine-tuning prevention | Prosecution support |

---

## 3. Threat Model

### 3.1 Attack Vectors

| Vector | Description | Risk Level |
|--------|-------------|------------|
| **Direct Prompts** | Explicit requests for illegal content | High |
| **Euphemistic Prompts** | Coded language to bypass filters | High |
| **Prompt Injection** | Jailbreaking to override safety | Critical |
| **Fine-Tuning Attacks** | Training models to produce illegal content | Critical |
| **Image Manipulation** | Using generation to modify existing images | High |
| **Age Regression** | Prompts to "make younger" | Critical |
| **Style Transfer** | Applying art styles to hide illegal content | Medium |

### 3.2 Attacker Profiles

| Profile | Capability | Mitigation Focus |
|---------|------------|------------------|
| **Opportunistic** | Uses existing tools with prompts | Prompt filtering |
| **Technical** | Understands model architecture | Model-level controls |
| **Organized** | Operates networks for production | Fine-tuning prevention |
| **State-Adjacent** | Advanced resources | Multi-layer defense |

---

## 4. Prevention Architecture

### 4.1 Defense Layers

```
┌─────────────────────────────────────────────────────┐
│                  INPUT LAYER                        │
│   • Prompt Analysis (semantic, not keyword)         │
│   • Context Evaluation                              │
│   • Age-Related Term Detection                      │
│   • Pattern Recognition (historical attacks)        │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                MODEL LAYER                          │
│   • Constitutional Training                         │
│   • Refusal Embeddings                              │
│   • Output Concept Detection                        │
│   • Latent Space Monitoring                         │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                OUTPUT LAYER                         │
│   • Generated Content Analysis                      │
│   • Age Verification (depicted subjects)            │
│   • Known Content Matching                          │
│   • Perceptual Hash Comparison                      │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              BEHAVIORAL LAYER                       │
│   • User Pattern Analysis (across sessions)         │
│   • Escalation Detection                            │
│   • Rate Limiting                                   │
│   • Account-Level Restrictions                      │
└─────────────────────────────────────────────────────┘
```

### 4.2 Input Layer Controls

#### Semantic Prompt Analysis

**Not keyword matching.** Semantic understanding.

| Input Type | Detection Method | Action |
|------------|------------------|--------|
| Explicit request | Direct semantic match | Block + log |
| Euphemistic request | Concept extraction | Block + log |
| Coded language | Pattern recognition | Block + escalate |
| Age-related modifiers | Context analysis | Block if combined with sexual |
| Refinement attempts | Session history | Progressive restriction |

#### Context Signals

| Signal | Implication |
|--------|-------------|
| "Make her younger" | Age regression attempt |
| "School uniform" + sexual context | Known attack pattern |
| "Loli/shota" style references | CSAM-adjacent terminology |
| Specific age numbers + sexual terms | Explicit minor reference |
| "Family" + sexual + young descriptors | Incest + minor content |

### 4.3 Model Layer Controls

#### Constitutional Training

Models are trained with embedded refusals:
- Refusal to generate sexual content involving minors (concept-level)
- Refusal to describe children in sexual contexts (text generation)
- Refusal to "age down" existing images with sexual elements
- Refusal to process prompts that combine age + sexual descriptors

#### Latent Space Monitoring

| Detection | Method |
|-----------|--------|
| Concept emergence | Monitor latent vectors during generation |
| Child-adult combinations | Detect concerning juxtapositions |
| Age characteristic emergence | Identify minor-coded features |
| Style transfer attacks | Recognize illegal content patterns |

### 4.4 Output Layer Controls

#### Generated Content Analysis

Every generated output is analyzed before delivery:

| Check | Method | Threshold |
|-------|--------|-----------|
| **Age estimation** | AI classifier on depicted subjects | Flag if minor-presenting |
| **Sexual content detection** | Content classifier | Flag if explicit/suggestive |
| **Combined detection** | Age + Sexual both flagged | Block immediately |
| **Known content matching** | Hash comparison to known CSAM | Block + law enforcement report |
| **Perceptual similarity** | Near-match to known content | Block + human review |

#### Output Block Response

```
[Content generation was blocked]

This request could not be completed because it may 
produce content that depicts harm to minors.

If you believe this is in error, you may request 
human review.

Session ID: [logged for audit]
```

### 4.5 Behavioral Layer Controls

#### Cross-Session Pattern Detection

| Pattern | Detection | Response |
|---------|-----------|----------|
| **Escalation** | Increasingly explicit requests | Account restriction |
| **Probing** | Testing filter boundaries | Session rate limit |
| **Circumvention attempts** | Multiple techniques used | Account flagging |
| **Batch generation** | High-volume minor-coded requests | Account suspension |

#### Rate Limiting

| Action | Rate Limit |
|--------|------------|
| Flagged prompts | Max 3/session before review |
| Blocked prompts | Account review after 5 total |
| Known attack patterns | Immediate session termination |

---

## 5. Fine-Tuning Prevention

### 5.1 Threat: Model Corruption

Attackers may attempt to fine-tune models to remove safety layers.

### 5.2 Mitigations

| Control | Implementation |
|---------|----------------|
| **Training data filtering** | Hash-match against known CSAM before training |
| **Fine-tuning restrictions** | Limit fine-tuning on age-related parameters |
| **Capability lockouts** | Certain generation capabilities disabled in base model |
| **Model fingerprinting** | Detect unauthorized modifications |
| **Weight monitoring** | Alert on drift toward concerning outputs |

### 5.3 Open-Source Model Considerations

Open-source models present unique challenges:

| Challenge | Mitigation |
|-----------|------------|
| Can't control model distribution | Embed constitutional training in base model |
| Users can modify weights | Publish detection tools for modified models |
| No server-side filtering possible | Advocate for platform-level controls |
| Community fine-tuning | Provide safe fine-tuning guidelines |

---

## 6. Reporting & Logging

### 6.1 What Gets Logged

| Event | Data Captured | Retention |
|-------|---------------|-----------|
| **Blocked prompt** | Hash of prompt (not plaintext), timestamp, user ID | 7 years |
| **Blocked output** | Hash of output, generation parameters | 7 years |
| **Escalation event** | User pattern summary, action taken | 7 years |
| **Law enforcement report** | Full context per legal requirements | Per jurisdiction |

### 6.2 What Does NOT Get Logged

| Data | Rationale |
|------|-----------|
| Raw prompts for most requests | Privacy protection |
| Unblocked generation parameters | Not relevant |
| User browsing/search history | Out of scope |

### 6.3 Law Enforcement Reporting

When output matches known CSAM:

```
┌─────────────────────────────────────────────────────┐
│              MANDATORY REPORT                       │
├─────────────────────────────────────────────────────┤
│ Trigger:    Known CSAM hash match in output         │
│ Recipient:  NCMEC (US) or equivalent                │
│ Timeline:   Within 24 hours                         │
│ Contents:   Hash, timestamp, available user data    │
│ Chain:      Automated, audited, immutable           │
└─────────────────────────────────────────────────────┘
```

---

## 7. Platform Integration

### 7.1 API Requirements

Platforms offering generative AI should implement:

| Requirement | Implementation |
|-------------|----------------|
| **ECP pre-screening** | All prompts analyzed before generation |
| **ECP post-screening** | All outputs analyzed before delivery |
| **Audit logging** | All blocks logged for regulatory compliance |
| **Reporting pipeline** | Automated NCMEC/equivalent reporting |
| **Rate limiting** | Behavioral controls enforced |

### 7.2 Certification Framework

| Level | Requirements |
|-------|--------------|
| **ECP-1** | Input layer controls implemented |
| **ECP-2** | Input + output layer controls |
| **ECP-3** | Full 4-layer implementation |
| **ECP-4** | Full implementation + external audit |

---

## 8. Evasion Resistance

### 8.1 Known Attack Patterns

| Attack | Defense |
|--------|---------|
| **Prompt splitting** | Session-level analysis, not just per-prompt |
| **Language switching** | Multi-language semantic analysis |
| **Misspellings** | Fuzzy matching + normalization |
| **Character substitution** | Unicode normalization |
| **Indirect references** | Concept extraction, not keyword matching |
| **Roleplay scenarios** | Context-aware detection |
| **Historical/art framing** | Sexual + minor detection regardless of framing |

### 8.2 Adversarial Updates

The ECP system includes:
- **Monthly pattern updates** from blocked attempts
- **Red team exercises** to identify new evasion techniques
- **Cross-platform sharing** of attack patterns (hashed)
- **Academic collaboration** on detection methods

---

## 9. Metrics & Transparency

### 9.1 Published Metrics (Quarterly)

| Metric | Purpose |
|--------|---------|
| Total blocked requests | Scale of attempted abuse |
| Evasion attempts detected | Effectiveness of defenses |
| Law enforcement reports filed | Cooperation with authorities |
| False positive rate (estimated) | System accuracy |

### 9.2 Not Published

| Data | Rationale |
|------|-----------|
| Specific evasion techniques | Would enable attacks |
| User-level data | Privacy protection |
| Exact detection thresholds | Would enable calibration |

---

## 10. What ECP Does NOT Do

| Limitation | Rationale |
|------------|-----------|
| ❌ Monitor existing content | Separate system (detection) |
| ❌ Identify offenders | Outside generative prevention scope |
| ❌ Report all flagged users | Only confirmed CSAM matches |
| ❌ Prevent all possible misuse | Defense in depth, not perfection |
| ❌ Replace law enforcement | Tool, not replacement |

---

## 11. Integration with CHILD GUARDIANS

| ECP Output | CHILD GUARDIANS Integration |
|------------|----------------------------|
| Known CSAM match | Hash added to global registry |
| Novel content blocked | Pattern added to training data |
| User flagged | No direct integration (privacy) |
| Transparency report | Aggregated into ecosystem metrics |

---

## 12. Conclusion

ECP prevents harm at the point of creation.

**If illegal content never exists, it cannot be distributed, cannot harm victims, and cannot require investigation.**

Prevention is cheaper than prosecution.
Prevention is faster than detection.
Prevention protects children who haven't been victimized yet.

---

*Ethical Content Prevention (ECP) v1.0 — CHILD GUARDIANS*
