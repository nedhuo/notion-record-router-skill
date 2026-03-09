# Mature Skill Design

## Purpose

This document defines what a mature Codex skill should look like, how it should guide execution, and which failure patterns to avoid. It is intended as a working design reference for improving existing skills and creating new ones.

## What a Skill Is

A skill is not a single task. A skill is a reusable execution method for a class of tasks.

A mature skill should provide:

- a clear trigger boundary
- a decision path for different scenarios
- a stable workflow
- explicit failure handling
- reusable resources such as scripts, templates, or references

The best test is simple:

- a task is one request
- a skill is the repeatable method for handling similar requests well

## Goals of a Mature Skill

A mature skill should make another Codex instance:

- start in the correct place
- avoid common mistakes
- know what to check before acting
- know what to do when something fails
- know when to stop instead of guessing

## Core Design Principles

### 1. Separate Decision From Execution

Do not start with commands or scripts.

Start with a short decision layer:

- what kind of situation is this
- which path should be used
- is the input ready
- should the skill proceed or stop

### 2. Keep Entry Light

The first read should answer:

- when to use the skill
- what the minimum inputs are
- what the next action is

If a user or another Codex instance needs to read the whole skill before acting, the skill is too heavy.

### 3. Make Preconditions Explicit

Before execution, the skill should list a short preflight checklist.

Examples:

- required credentials exist
- required files exist
- target system permissions are granted
- config values are real, not placeholders
- output destination is known

### 4. Define the Smallest Safe Input

A mature skill should define the smallest usable input shape.

If inputs are often raw and messy, the skill should say how to convert them into the structured form required for execution.

### 5. Prefer Safe Failure Over Clever Guessing

If the skill cannot route confidently, it should stop.

Wrong writes, wrong edits, and wrong destinations are more expensive than asking for one more field.

### 6. Support Expansion Without Rewriting Logic

If a skill is meant to handle multiple variants, it should explain how to extend them without changing the core execution path.

Examples:

- add one new route
- add one new template
- add one new property mapping
- add one new validation step

### 7. Treat Failure Modes as First-Class Design

The skill should not only describe the happy path.

It should explain:

- likely failure classes
- how to diagnose each one
- whether to retry, patch config, or stop

## Recommended Structure for a Mature Skill

This is the structure that most execution-oriented skills should follow.

### 1. Trigger and Scope

- what this skill does
- when to use it
- when not to use it

### 2. Quick Decision

Short branching guidance such as:

- use path A for first-time setup
- use path B for daily use
- use path C for debugging

### 3. Preflight Checklist

Short checklist before any action.

### 4. Input Contract

- minimum required fields
- optional fields
- examples of valid input

### 5. Core Workflow

The normal path from input to result.

### 6. Failure Handling

- common failures
- likely cause
- next action

### 7. Extension Workflow

How to add support for another variant without changing the whole skill.

### 8. Files and Responsibilities

Explain what each file does so the skill does not become a black box.

## Failure Case: Notion Record Router V1

This repository's first version of `notion-record-router` is a useful example of a skill that worked, but was not yet mature.

### What Worked

- the script could route content by type
- the script could render markdown templates
- the script could build a valid Notion request body
- the skill documented the basic upload flow

### What Failed at the Skill Design Level

#### 1. It started with execution, not decision

The original skill quickly moved into:

- read config
- check token
- prepare JSON
- run dry-run
- upload

It did not first explain which path to use for:

- first-time setup
- daily uploads
- route extension
- debugging

#### 2. It assumed structured input already existed

The first version assumed the user already had a valid JSON record.

In real use, the usual inputs are often:

- a raw article link
- a bug summary
- a short idea
- a block of copied notes

This meant the skill only described the back half of the workflow:

`structured record -> route -> upload`

It did not describe:

`raw material -> structured record -> route -> upload`

#### 3. It lacked a real preflight checklist

The original version mentioned token, config, and permissions, but not as an explicit checklist.

This made first-time usage weaker and more error-prone.

#### 4. It treated failures too generically

The original version did not clearly separate:

- missing token
- missing route target
- no route match
- property mismatch
- Notion permission failure

That made troubleshooting slower than it needed to be.

#### 5. It did not make route extension explicit enough

The first version supported multiple content types, but did not clearly state the exact steps for adding a new type safely.

### Lessons From This Failure

- a working script is not the same thing as a mature skill
- the skill must cover decision, input shaping, safe execution, and failure recovery
- if users can misuse the skill by taking the wrong path, the pathing must be rewritten

## Practical Review Checklist

Use this checklist when reviewing a skill:

- Can a first-time user tell which path to take in under 30 seconds
- Does the skill define a minimum safe input
- Does it include a preflight checklist
- Does it explain what happens when routing or execution fails
- Does it tell the user when to stop instead of guessing
- Does it explain how to extend the supported variants
- Does it separate resource responsibilities clearly

If two or more answers are "no", the skill is probably still immature.

## Standard to Aim For

A mature skill should feel like:

- a small operating manual
- a safe execution framework
- a repeatable method with recovery paths

It should not feel like:

- a loose prompt
- a script README with missing failure handling
- a happy-path-only demo
