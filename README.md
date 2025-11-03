# Glazing PM AI

Automate commercial glazing project management from contract receipt to final retention billing.

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Your Claude API Key

**Windows:**
```cmd
set ANTHROPIC_API_KEY=your-key-here
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY=your-key-here
```

### 3. Process Your First Project

1. Create a folder in `Input/` with your project name
2. Add PDF files (contract, specifications, drawings, schedule, proposal)
3. Run the processor:

```bash
python main.py process
```

The system will:
- ✅ Organize files into project folder
- ✅ Analyze contract documents with AI
- ✅ Generate Schedule of Values (SOV)
- ✅ Create draft emails ready to send

## How It Works

### Workflow

```
Input Folder → File Organization → Contract Analysis → SOV Generation → Draft Emails
```

### What You Get

**Organized Project Folder:**
```
Projects/
  P001-Your-Project/
    ├── 01-Contract-Documents/    (PDFs moved here)
    ├── 02-Generated-SOV/          (SOV files)
    ├── 03-Purchase-Orders/        (for future use)
    ├── 04-Shop-Drawings/          (for future use)
    └── 05-Correspondence/         (for future use)
```

**AI-Generated Outputs:**
- `Output/Reports/` - Contract analysis (JSON & Markdown)
- `Output/Draft_SOV/` - Schedule of Values (CSV & JSON)
- `Output/Draft_Emails/` - Ready-to-send email drafts

**Logs (CSV format - open in Excel):**
- `Logs/project_registry.csv` - All projects and status
- `Logs/agent_activity.csv` - All AI agent actions
- `Logs/email_intake.csv` - Email tracking (future use)

## Commands

### Process a New Project

```bash
# Auto-detect project in Input/ folder
python main.py process

# Specify project name
python main.py process "Microsoft Building A"
```

### List All Projects

```bash
python main.py list
```

### Run Individual Agents

```bash
# Just organize files (no AI)
python scripts/file_mover.py "Project Name"

# Just analyze contract
python scripts/contract_processor.py P001

# Just generate SOV
python scripts/sov_generator.py P001

# Just generate emails
python scripts/email_generator.py P001
```

## Project Structure

```
Glazing PM Ai/
├── Input/                      # Drop project folders here
├── Projects/                   # AI-managed project folders
├── Archive/                    # Processed input folders
├── Output/                     # AI-generated outputs
│   ├── Draft_Emails/
│   ├── Draft_SOV/
│   └── Reports/
├── Logs/                       # CSV logs of all activity
├── scripts/                    # Python agents
│   ├── logger.py              # CSV logging system
│   ├── file_mover.py          # File organization
│   ├── contract_processor.py  # AI contract analysis
│   ├── sov_generator.py       # AI SOV generation
│   └── email_generator.py     # Draft email creation
├── Claude_Prompts/            # AI system prompts
├── main.py                    # Main orchestrator
└── README.md                  # This file
```

## What the AI Does

### Contract Analysis
- Extracts project info (name, location, client)
- Identifies financial details (contract value, payment terms)
- Analyzes scope of work (spec sections, materials)
- Extracts schedule (start, completion dates)
- Flags key requirements and risks

### SOV Generation
- Creates line items optimized for early billing
- Breaks down by: General Conditions, Materials, Labor, Retention
- Includes billing strategies and triggers
- Follows industry best practices for glazing

### Draft Emails
- **Internal kickoff** - Team notification with project details
- **Client SOV submission** - Professional SOV delivery email
- **Vendor quote requests** - Template emails for glass, framing, hardware

## Review & Send Process

1. **Review Reports** - Check `Output/Reports/` for contract analysis
2. **Review SOV** - Open CSV in Excel, verify line items and totals
3. **Review Emails** - Check `Output/Draft_Emails/` for all drafts
4. **Fill Placeholders** - Replace `[BRACKETS]` with actual info
5. **Copy/Paste** - Copy email text into Gmail
6. **Attach Files** - Attach SOV CSV to client emails
7. **Send** - You control when emails go out

## Tips

- **Multiple Projects**: Process one at a time for best results
- **API Costs**: Claude API calls cost ~$0.50-2.00 per project
- **Edit SOV**: Open CSV in Excel, modify as needed
- **Logs**: Check `Logs/*.csv` to see everything the AI did
- **Errors**: AI will continue even if one step fails

## Next Steps

After MVP is working:
- Add email watching (Gmail API integration)
- Add shop drawing management
- Add PO generation
- Add vendor catalog processing
- Migrate to Make.com if desired

## Support

For issues or questions, refer to:
- `CLAUDE.md` - Full system documentation
- `PROJECT_OVERVIEW.md` - Detailed project requirements
- `Claude_Prompts/` - AI prompt library

## Requirements

- Python 3.8+
- Anthropic API key (get at: https://console.anthropic.com/)
- PDF files for processing
