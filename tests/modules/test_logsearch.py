"""test_logsearch.py
    tests for logsearch
    by Annika"""

import dummies
import logsearch

# We can't really test logsearch very well
# TODO: figure out a way to test things that rely on files on disk

class TestLogsearch():
    """Test the logsearch module
    """
    module = logsearch.Module()

    def testLogsearch(self) -> None:
        """Tests the logsearch command
        """
        message = dummies.DummyMessage(
            arguments=["~logsearch", "testroom", "testuser", "testquery"],
            sender=dummies.DummyUser(isAdmin=True),
            connection=dummies.DummyConnection(logchat=True)
        )
        self.module.logsearch(message)
        assert not message.response
        assert message.HTMLResponse and len(message.HTMLResponse) > 1