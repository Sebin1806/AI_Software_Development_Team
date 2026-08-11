import pytest
from app.agents.project_manager_agent import ProjectManagerAgent
from app.agents.database_engineer_agent import DatabaseEngineerAgent
from app.agents.backend_developer_agent import BackendDeveloperAgent


def test_agents_mock_execution():
    pm_agent = ProjectManagerAgent(mock_mode=True)
    res_pm = pm_agent.run(
        user_prompt="Build a SaaS blog",
        project_context={"name": "Blog Platform", "description": "SaaS app"},
        previous_outputs={}
    )
    assert res_pm["status"] == "success"
    assert res_pm["agent_name"] == "Project Manager"

    db_agent = DatabaseEngineerAgent(mock_mode=True)
    res_db = db_agent.run(
        user_prompt="Build a SaaS blog",
        project_context={"name": "Blog Platform", "description": "SaaS app"},
        previous_outputs={"Project Manager": res_pm}
    )
    assert res_db["status"] == "success"

    be_agent = BackendDeveloperAgent(mock_mode=True)
    res_be = be_agent.run(
        user_prompt="Build a SaaS blog",
        project_context={"name": "Blog Platform", "description": "SaaS app"},
        previous_outputs={"Project Manager": res_pm, "Database Engineer": res_db}
    )
    assert res_be["status"] == "success"
