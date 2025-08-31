"""
Seed script to create demo data in the database and vector store.
Run this after setting up the database with `make migrate`.
"""

import asyncio
import uuid
from datetime import datetime
import os
import sys

# Add the parent directory to the sys path to import from the application
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from services.database import async_session, save_note
from services.retriever import process_and_index_note
from services.graph import link_related_notes

# Sample notes for seeding
SAMPLE_NOTES = [
    {
        "title": "Hospital Operations Meeting Notes",
        "body": """
# Hospital Operations Meeting - August 15, 2023

## Attendees
- Dr. Sarah Johnson (Chief Medical Officer)
- John Smith (Operations Director)
- Maria Rodriguez (Nursing Director)
- David Chen (IT Department)

## Key Discussion Points

1. **Emergency Department Wait Times**
   - Current average wait time: 45 minutes
   - Target wait time: 30 minutes
   - Implemented new triage process last month

2. **Staffing Challenges**
   - Nursing shortage in ICU continuing
   - Three new nurses scheduled to start next month
   - Need to develop better retention strategies

3. **Equipment Upgrades**
   - New MRI machine installation scheduled for September
   - Training sessions for staff planned for last week of August
   - Old equipment to be donated to community clinic

## Decisions Made

- Approve budget for two additional triage nurses
- Proceed with telemedicine pilot in outpatient clinic
- Implement new scheduling software in Q4

## Action Items

- John to finalize nursing recruitment plan by August 30
- Maria to develop new staff retention proposal by next meeting
- David to evaluate vendors for scheduling software by September 15
- All department heads to submit Q4 budget requests by September 1
        """
    },
    {
        "title": "DSAT Customer Support Triage Process",
        "body": """
# DSAT Support Ticket Triage Process

## Overview
This document outlines our updated process for triaging customer support tickets using the DSAT (Dissatisfaction) framework.

## Ticket Priority Levels

### P0 - Critical
- Service completely unavailable
- Data loss or security breach
- Affects >50% of customers
- SLA: 1 hour response, 4 hour resolution target

### P1 - High
- Major feature unavailable
- Workaround exists but is cumbersome
- Affects 10-50% of customers
- SLA: 4 hour response, 24 hour resolution target

### P2 - Medium
- Minor feature issues
- Good workaround available
- Affects <10% of customers
- SLA: 24 hour response, 72 hour resolution target

### P3 - Low
- Cosmetic issues
- Feature requests
- Documentation issues
- SLA: 48 hour response, no fixed resolution time

## Triage Process

1. Initial assessment by Level 1 support
2. DSAT score calculation based on:
   - Customer impact (1-5)
   - Frequency of issue (1-5)
   - Business impact (1-5)
3. Automatic escalation for DSAT scores >10
4. Daily triage meeting for all P0/P1 tickets

## Reporting

- Weekly DSAT report to be sent to all team leads
- Monthly trend analysis presented to leadership
- Quarterly review of triage effectiveness

## Action Items

- Update support dashboard to include DSAT scores
- Train all support staff on new process by end of month
- Implement automatic alerts for high DSAT tickets
- Review effectiveness after 30 days and adjust as needed
        """
    },
    {
        "title": "Machine Learning Study Plan",
        "body": """
# Machine Learning Study Plan - Fall 2023

## Learning Objectives
By the end of this study plan, I will:
- Understand core ML concepts and algorithms
- Implement basic models using Python and key libraries
- Complete at least one end-to-end ML project
- Prepare for ML engineer interviews

## Schedule

### Week 1-2: Foundations
- Linear algebra refresher
- Statistics and probability review
- Python programming practice
- Setting up development environment

### Week 3-4: Supervised Learning
- Linear and logistic regression
- Decision trees and random forests
- Support vector machines
- Evaluation metrics

### Week 5-6: Neural Networks
- Perceptrons and multilayer networks
- Backpropagation
- Convolutional neural networks
- Recurrent neural networks

### Week 7-8: Practical ML
- Feature engineering
- Hyperparameter tuning
- Cross-validation strategies
- Model deployment basics

## Resources
- Coursera: Machine Learning by Andrew Ng
- Book: Hands-On Machine Learning with Scikit-Learn & TensorFlow
- YouTube: StatQuest with Josh Starmer
- Dataset practice: Kaggle competitions

## Projects
1. Predictive model for house price estimation
2. Image classification using CNNs
3. Text sentiment analysis

## Action Items
- Sign up for Coursera course by Sunday
- Set up GitHub repository for projects
- Schedule 2 hours of daily study time
- Find study group for accountability
        """
    }
]


async def seed_database():
    """Seed the database with sample notes"""
    print("Seeding database with sample notes...")
    
    async with async_session() as session:
        # Create notes
        note_ids = []
        for note_data in SAMPLE_NOTES:
            note = await save_note(session, {
                "title": note_data["title"],
                "body": note_data["body"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            note_ids.append(note.id)
            print(f"Created note: {note.title} (ID: {note.id})")
        
        # Index notes in vector store
        for i, note_id in enumerate(note_ids):
            print(f"Indexing note {i+1}/{len(note_ids)} in vector store...")
            chunks = await process_and_index_note(
                text=SAMPLE_NOTES[i]["body"],
                note_id=str(note_id),
                metadata={"title": SAMPLE_NOTES[i]["title"]}
            )
            print(f"  Indexed {chunks} chunks")
            
            # Generate links
            links = await link_related_notes(session, note_id)
            print(f"  Created {len(links)} semantic links")
            
    print("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
