# What This System Does NOT See

> **A Plain-Language Statement for the Public, Lawmakers, and Civil Liberties Reviewers**  
> **Version:** 1.0  
> **Status:** Final  

---

## The One-Sentence Summary

**CHILD GUARDIANS does not watch people. It matches fingerprints of files that courts have already ruled illegal.**

---

## What This System Sees

| What It Sees | Why |
|--------------|-----|
| **Digital fingerprints** (hashes) of files | To check if a file matches known illegal material |
| **Metadata** about when/where a match occurred | To preserve evidence chain |
| **Officer actions** within the system | For audit and oversight |

That's it.

---

## What This System Does NOT See

| What It Never Sees | Why Not |
|--------------------|---------|
| ❌ **Your private messages** | No access to encrypted communications |
| ❌ **Your emails** | Not scanned, not accessed |
| ❌ **Your photos** | Unless law enforcement has a warrant for your device |
| ❌ **Your browsing history** | Not collected, not stored |
| ❌ **Your location** | Not tracked |
| ❌ **Your social media** | Not monitored |
| ❌ **Your cloud storage** | Not accessed without legal authority |
| ❌ **Your identity** | System tracks material, not people |

---

## How Hash Matching Works (Plain English)

Think of it like this:

1. A court convicts someone for possessing an illegal image
2. That image gets a unique digital fingerprint — like a barcode
3. The fingerprint goes into a database of known illegal material
4. If law enforcement later finds a file with the same fingerprint, they know it's the same illegal content

**The system never "looks at" images. It compares barcodes.**

You cannot reverse a fingerprint back into an image. The fingerprint is just a string of numbers.

---

## What Triggers System Activity

| Trigger | NOT a Trigger |
|---------|---------------|
| ✅ Law enforcement submits a hash from a seized device | ❌ Someone uploads a photo to social media |
| ✅ Officer queries the system with a warrant | ❌ Someone sends a private message |
| ✅ Known illegal hash appears on dark web forum | ❌ Someone browses the internet |

**The system responds to law enforcement queries. It does not scan the public.**

---

## The Surveillance Question, Answered Directly

**Q: Is this mass surveillance?**

No.

Mass surveillance means watching everyone to find wrongdoing.

This system does the opposite:
- It starts with **already-identified illegal material**
- It checks if that material reappears
- It only activates when **law enforcement asks a question**

It's a library catalog, not a security camera.

---

**Q: Could this be turned into surveillance?**

The design prevents it:

| Safeguard | How It Works |
|-----------|--------------|
| **No content storage** | Can't surveil what you don't have |
| **Pull-only architecture** | System responds; it doesn't watch |
| **Scope lock** | Charter prohibits expansion beyond CSAM |
| **Watchdog oversight** | Independent body monitors for misuse |
| **Public transparency reports** | Aggregate statistics published quarterly |
| **Open specifications** | Anyone can audit the design |

If someone tried to add surveillance capabilities, it would require:
- Charter amendment (public, supermajority vote)
- Technical redesign (visible in open specs)
- Watchdog approval (independent body)

**Surveillance cannot be added quietly. The architecture prevents it.**

---

## What About the "Dark Web Monitoring"?

The Industrial Magnet component monitors dark web forums. Here's what that means:

| What It Does | What It Doesn't Do |
|--------------|-------------------|
| Connects to public dark web forums (read-only) | Does not interact with anyone |
| Computes hashes of files posted | Does not download or store illegal content |
| Checks hashes against known illegal material | Does not identify users |
| Logs matches for law enforcement | Does not conduct investigations |

**It's a tripwire, not a spy.**

If known illegal material surfaces, the system notes "this fingerprint appeared here at this time." That's all.

---

## The Privacy Commitment

This system was designed by someone who believes:

> **A tool that protects children but destroys privacy is not a solution — it's a different problem.**

Every design decision was tested against this question:

> "Could this be misused for surveillance?"

If yes, the feature was redesigned or removed.

---

## How to Verify This

You don't have to trust this statement. You can verify it.

1. **Read the specifications** — they're public
2. **Check the architecture** — pull-based, hash-only, no content storage
3. **Review the Watchdog design** — independent oversight with public reporting
4. **Examine the Charter** — scope is locked to CSAM only

If you find a surveillance capability we haven't disclosed, that would be a design failure. Report it.

---

## Summary

| Claim | Verification |
|-------|--------------|
| "No mass surveillance" | Pull-based design; no scanning of public |
| "No content storage" | Hash-only architecture; payloads discarded |
| "No identity tracking" | System tracks material, not people |
| "No scope creep" | Charter-locked; amendment requires supermajority |
| "No hidden capabilities" | Open specifications; public audit |

---

**This system exists to protect children, not to watch citizens.**

If it ever becomes a surveillance tool, it will have failed its mission — and should be shut down.

---

*Surveillance Exclusion Statement v1.0 — CHILD GUARDIANS*
