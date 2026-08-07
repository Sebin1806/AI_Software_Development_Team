## Project Name

**AI Software Development Team**

Version: **1.0**

Status: **Planning**

---

# 1. Overview

The database stores all application data required for managing users, projects, AI agent execution, generated outputs, documents, and system activities.

The database is designed to support:

- Multiple users
- Multiple projects
- Multi-agent workflow
- Agent execution tracking
- Project history
- Generated files
- AI memory

---

# 2. Database Technology

## Primary Database

**PostgreSQL**

Used for:

- User management
- Project management
- Agent data
- Workflow tracking
- Application logs

---

## Vector Database

**ChromaDB**

Used for:

- Document embeddings
- AI knowledge retrieval
- RAG context storage

---

# 3. Database Architecture

```
                 Application
                      |
                      |
                 FastAPI Backend
                      |
        --------------------------------
        |                              |
        v                              v
 PostgreSQL Database              ChromaDB
        |                              |
 Structured Data              Vector Data

```

---

# 4. Entity Relationship Diagram (ERD)

```
Users
 |
 |
 +------ Projects
             |
             |
       Agent Executions
             |
             |
       AI Agents
             |
             |
       Generated Files


Projects
 |
 |
 +------ Chat Sessions
             |
             |
       Chat Messages


Projects
 |
 |
 +------ Uploaded Documents


Projects
 |
 |
 +------ Project Logs

```

---

# 5. Database Tables

---

# 5.1 Users Table

Stores application users.

## Table Name

`users`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| username | VARCHAR | User name |
| email | VARCHAR | User email |
| password_hash | TEXT | Encrypted password |
| role | VARCHAR | User role |
| created_at | TIMESTAMP | Account creation |
| updated_at | TIMESTAMP | Last update |

---

# 5.2 Projects Table

Stores user-created software projects.

## Table Name

`projects`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| user_id | UUID | User reference |
| name | VARCHAR | Project name |
| description | TEXT | Project description |
| status | VARCHAR | Project status |
| technology_stack | JSON | Technologies used |
| created_at | TIMESTAMP | Creation date |
| updated_at | TIMESTAMP | Update date |

---

# 5.3 AI Agents Table

Stores available AI agents.

## Table Name

`agents`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| name | VARCHAR | Agent name |
| type | VARCHAR | Agent role |
| description | TEXT | Agent purpose |
| status | VARCHAR | Active/Inactive |
| created_at | TIMESTAMP | Creation date |

---

# 5.4 Agent Executions Table

Tracks every agent execution.

## Table Name

`agent_executions`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| project_id | UUID | Project reference |
| agent_id | UUID | Agent reference |
| input_data | JSON | Agent input |
| output_data | JSON | Agent output |
| status | VARCHAR | Execution status |
| started_at | TIMESTAMP | Start time |
| completed_at | TIMESTAMP | End time |
| error_message | TEXT | Error details |

---

# 5.5 Project Files Table

Stores generated project files.

## Table Name

`project_files`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| project_id | UUID | Project reference |
| file_name | VARCHAR | File name |
| file_path | TEXT | Storage location |
| file_type | VARCHAR | File extension |
| generated_by | UUID | Agent reference |
| created_at | TIMESTAMP | Creation date |

---

# 5.6 Chat Sessions Table

Stores user conversations.

## Table Name

`chat_sessions`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| user_id | UUID | User reference |
| project_id | UUID | Project reference |
| title | VARCHAR | Session title |
| created_at | TIMESTAMP | Creation date |

---

# 5.7 Chat Messages Table

Stores chat messages.

## Table Name

`chat_messages`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| session_id | UUID | Session reference |
| sender | VARCHAR | User/AI |
| message | TEXT | Message content |
| created_at | TIMESTAMP | Message time |

---

# 5.8 Uploaded Documents Table

Stores user uploaded documents.

## Table Name

`uploaded_documents`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| project_id | UUID | Project reference |
| file_name | VARCHAR | Document name |
| file_path | TEXT | File location |
| file_type | VARCHAR | PDF/DOCX/TXT |
| uploaded_at | TIMESTAMP | Upload time |

---

# 5.9 Generated Files Table

Stores final generated outputs.

## Table Name

`generated_files`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| project_id | UUID | Project reference |
| file_name | VARCHAR | Generated file |
| download_path | TEXT | File location |
| size | INTEGER | File size |
| created_at | TIMESTAMP | Creation date |

---

# 5.10 Project Logs Table

Stores system activities.

## Table Name

`project_logs`

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary Key |
| project_id | UUID | Project reference |
| action | VARCHAR | Activity name |
| details | JSON | Log data |
| created_at | TIMESTAMP | Log time |

---

# 6. Table Relationships

## User → Projects

One user can create multiple projects.

```
users.id

     |

     |

projects.user_id
```

---

## Project → Agent Executions

One project has multiple agent executions.

```
projects.id

     |

agent_executions.project_id
```

---

## Agent → Agent Executions

One agent can execute many tasks.

```
agents.id

     |

agent_executions.agent_id
```

---

## Project → Files

One project can contain many files.

```
projects.id

     |

project_files.project_id
```

---

# 7. Database Indexes

Indexes improve query performance.

Recommended indexes:

```
users.email

projects.user_id

agent_executions.project_id

agent_executions.agent_id

chat_messages.session_id

project_files.project_id
```

---

# 8. Database Constraints

## Primary Keys

Every table uses UUID primary keys.

---

## Foreign Keys

Maintain relationships between tables.

Example:

```
projects.user_id

references

users.id
```

---

## Unique Constraints

Examples:

```
users.email

projects.name + user_id
```

---

## Validation

- Required fields cannot be empty
- Email format validation
- File type validation
- Project ownership validation

---

# 9. Database Security

Security measures:

- Password hashing using bcrypt
- SQL injection protection
- Prepared queries
- Role-based access control
- Database user permissions
- Environment variable storage

---

# 10. Backup Strategy

Database backup:

- Daily automatic backup
- Project export backup
- Migration support using Alembic

---

# 11. Future Tables

Possible future additions:

## Teams

For multiple developers.

## Organizations

For company accounts.

## Billing

For subscription management.

## API Keys

For external AI models.

## Agent Memory

For long-term AI learning.

## Templates

For reusable project structures.

---

# 12. Database Migration

Technology:

**Alembic**

Used for:

- Creating tables
- Updating schema
- Version control
- Database migration

---

# 13. Database Summary

| Component | Technology |
|---|---|
| Main Database | PostgreSQL |
| Vector Database | ChromaDB |
| ORM | SQLAlchemy |
| Migration | Alembic |
| Authentication | JWT |
| Data Format | JSON + Relational Data |

---

# Database Design Status

**Version:** 1.0

**Status:** Approved

**Last Updated:** August 2026