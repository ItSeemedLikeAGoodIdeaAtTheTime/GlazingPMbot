# Claude API Prompt Library

This directory contains specialized Claude API system prompts for different project management tasks.

## Prompt Categories

### 1. Document Processing
- `contract_extraction.md` - Extract key details from contracts (scope, value, schedule)
- `spec_analysis.md` - Parse specification sections for requirements
- `drawing_analysis.md` - Extract dimensions, materials, details from drawings
- `vendor_quote_parser.md` - Extract pricing and terms from vendor quotes

### 2. Constructibility Reviews
- `caulk_joint_checker.md` - Review shop drawings for proper caulk joint sizing
- `material_compatibility.md` - Verify glass/metal/hardware compatibility
- `code_compliance.md` - Check against building codes and standards
- `installation_feasibility.md` - Flag potential field installation issues

### 3. Financial & Billing
- `sov_generator.md` - Generate Schedule of Values from contract docs
- `budget_builder.md` - Create internal budget with cost codes
- `invoice_matcher.md` - Match vendor invoices to POs

### 4. Communication
- `email_classifier.md` - Categorize incoming emails (vendor, client, RFI, submittal, etc.)
- `email_responder.md` - Generate professional responses to common inquiries
- `rfi_handler.md` - Process Requests for Information
- `submittal_tracker.md` - Track submittal status and responses

### 5. Shop Drawing Management
- `shop_drawing_reviewer.md` - Review shop drawings for completeness
- `revision_tracker.md` - Monitor and minimize revision counts
- `approval_checker.md` - Verify all required approvals received

### 6. Procurement
- `po_generator.md` - Generate purchase orders from approved submittals
- `vendor_comparer.md` - Compare vendor options against specs
- `delivery_tracker.md` - Track material delivery schedules

## Prompt Template Structure

Each prompt file should follow this structure:

```markdown
# [Task Name]

## Purpose
Brief description of what this prompt does

## Input Format
What data the prompt expects

## Output Format
What the prompt should return

## System Prompt
The actual Claude API system prompt

## Example Usage
Sample input and expected output
```

## Usage in Make.com

1. Store prompts as text files in this directory
2. Make.com HTTP module calls Claude API
3. Reference prompt file contents in system message
4. Pass dynamic data in user message
5. Parse JSON response for structured output
