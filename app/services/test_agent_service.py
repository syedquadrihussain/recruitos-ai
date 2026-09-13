from types import SimpleNamespace

import app.services.agent_service as agent_service


def test_run_agent_without_tool_call(monkeypatch):

    class FakeCompletions:

        def create(self, **kwargs):

            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=(
                                "No candidate search was "
                                "required for this request."
                            ),
                            tool_calls=None
                        )
                    )
                ]
            )

    class FakeClient:

        def __init__(self):
            self.chat = SimpleNamespace(
                completions=FakeCompletions()
            )

    # Replace the real Groq client with our fake client
    monkeypatch.setattr(
        agent_service,
        "client",
        FakeClient()
    )

    request = """
    Explain what RecruitOS AI does.
    """

    result = agent_service.run_agent(
        request
    )

    # Verify that the agent returned a response
    assert result is not None

    # Verify that the response is text
    assert isinstance(
        result,
        str
    )

    # Verify the expected response
    assert (
        result
        == "No candidate search was required "
           "for this request."
    )