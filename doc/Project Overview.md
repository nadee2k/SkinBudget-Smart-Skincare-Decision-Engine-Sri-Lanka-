# **Project Overview Document**
## Project Title

**SkinBudget – Budget-Aware Skincare Decision System**

## Objective

To develop a system that recommends cost-effective skincare routines based on user skin type, concerns, and ingredient compatibility using structured data and decision logic.

## Problem Statement

Users struggle to:

select suitable skincare products
understand ingredient effects
stay within a fixed budget

This results in ineffective purchases and wasted money.

## Proposed Solution

A data-driven decision system that:

maps skin concerns → ingredients
maps ingredients → products
filters products based on:
suitability
budget
outputs an optimized skincare routine

# Functional Requirements
## Input Requirements
- Skin type (oily, dry, combination)
- Skin concerns (acne, dryness, pigmentation)
- Budget (numeric value)

## Processing Requirements
- Identify suitable ingredients for each concern
- Identify harmful ingredients for each concern
- Match products with ingredient profiles
- Filter products based on:
    -  suitability
    - budget constraints
## Output Requirements
- Recommended skincare routine:

    - cleanser
    - moisturizer
    - sunscreen
- Product details:
    - price
    - ingredients
    - reason for recommendation
- Total cost summary

## User Stories
### ___User: Skincare Consumer___
Story 1

>As a user, I want to input my skin concerns so that I receive relevant recommendations.

Story 2

>As a user, I want to set a budget so that I only see affordable products.

Story 3

>As a user, I want to understand why a product is recommended so that I can trust the system.

Story 4

>As a user, I want to avoid harmful ingredients so that I don’t damage my skin.

Story 5

>As a user, I want a complete skincare routine so that I don’t need to research multiple products.