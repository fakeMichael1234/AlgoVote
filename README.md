# AlgoVote

AlgoVote is a simple, beginner-friendly anonymous voting web application built with Flask and SQLite.

Features
- Create polls with multiple options (admin)
- Anonymous voting (no names, emails, phones stored)
- Simple admin panel to create, activate, and close polls
- Results page with counts and percentage bars

Getting started

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Create `.env`

Copy `.env.example` to `.env` and set secure values:

```
ADMIN_PASSWORD=your-admin-password
SECRET_KEY=some-random-secret
```

3. Create the database

Run the app once; it will create `algovote.db` automatically from `schema.sql`:

```bash
python app.py
```

4. Use the app
- Visit `http://127.0.0.1:5000` for the home page
- Visit `http://127.0.0.1:5000/admin` to log in (use `ADMIN_PASSWORD` from `.env`)

Creating and closing polls
- In the admin panel add a question and options (one per line)
- Create the poll, then click `Activate` to open voting
- Click `Close` to stop voting and view final results

Testing voting
- Open the home page and click `Vote Now` to submit a vote
- After submitting, a confirmation is shown
- Results are available via admin or results link

Security notes
- Admin password and `SECRET_KEY` must be stored in `.env` (not committed)
- Votes are stored without personal identifiers. Standard web logs (server, proxy) may still record technical metadata.
- Database queries are parameterized to prevent SQL injection.

This is a minimal first version; blockchain or extra features can be added later.
# AlgoVote
A simple blockchain-based voting system using Algorand.
# AlgoVote

## About the Project

AlgoVote is a simple blockchain-based voting system built using the Algorand blockchain.

The project aims to provide a secure and transparent way to conduct digital voting and record voting transactions on the blockchain.

## Objectives

- Create a simple digital voting system
- Record votes using Algorand
- Provide transparent voting records
- Improve the security of the voting process

## Technologies

- Algorand
- Python
- Algorand SDK

## Future Scope

- User authentication
- Algorand wallet integration
- Smart contract integration
- Voting results dashboard
- Real-time vote tracking
