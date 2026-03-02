import json
import logging
import subprocess
import uuid

logger = logging.getLogger("acp")


def connect():
    """Spawn kiro-cli and return a Client connected to it."""
    # Start kiro-cli in ACP mode with pipes for stdin/stdout communication
    process = subprocess.Popen(
        ["kiro-cli", "acp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return Client(process)


class Client:
    """Manages JSON-RPC communication with kiro-cli over ACP protocol."""

    def __init__(self, process):
        self._process = process
        # Initialize the ACP connection with protocol version and client info
        self._send_request("initialize", {
            "protocolVersion": 1,
            "clientInfo": {"name": "acp-orchestrator", "version": "1.0"},
        })

    def new_session(self, system_prompt=None):
        # Create a new session with kiro-cli
        result, _ = self._send_request("session/new", {"cwd": ".", "mcpServers": []})
        return Session(self, result["sessionId"], system_prompt)

    def close(self):
        self._process.terminate()

    def _send(self, message):
        # Serialize and send JSON-RPC message to kiro-cli
        logger.debug(f"OUTGOING: {json.dumps(message)}")
        self._process.stdin.write(json.dumps(message).encode() + b"\n")
        self._process.stdin.flush()

    def _read_message(self):
        # Read and parse a JSON-RPC message from kiro-cli
        line = self._process.stdout.readline()
        if not line:
            return None
        message = json.loads(line.decode().strip())
        logger.debug(f"INCOMING: {json.dumps(message)}")
        return message

    def _send_request(self, method, params):
        # Send a JSON-RPC request and wait for response, collecting agent message chunks
        request_id = str(uuid.uuid4())
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        agent_text = ""
        line_buffer = ""
        while True:
            msg = self._read_message()
            if not msg:
                raise Exception("Connection closed")
            # Check if this is the response to our request
            if msg.get("id") == request_id:
                if line_buffer:
                    logger.info(f"kiro-cli: {line_buffer}")
                if "error" in msg:
                    raise Exception(msg["error"])
                return msg.get("result"), agent_text
            # Handle notifications (messages without id) - collect agent message chunks
            if "method" in msg and "id" not in msg:
                update = msg.get("params", {}).get("update", {})
                if update.get("sessionUpdate") == "agent_message_chunk":
                    text = update.get("content", {}).get("text", "")
                    if text:
                        agent_text += text
                        line_buffer += text
                        # Log complete lines as they arrive
                        while "\n" in line_buffer:
                            line, line_buffer = line_buffer.split("\n", 1)
                            logger.info(f"kiro-cli: {line}")


class Session:
    """Represents a conversation session with kiro-cli."""

    def __init__(self, client, session_id, system_prompt):
        self._client = client
        self._session_id = session_id
        self._system_prompt = system_prompt
        self._first = True  # Track if this is the first prompt to inject system prompt

    def prompt(self, text):
        # Build message list, injecting system prompt on first call if provided
        messages = []
        if self._first and self._system_prompt:
            messages.append({"type": "text", "text": self._system_prompt})
            self._first = False
        messages.append({"type": "text", "text": text})
        for m in messages:
            logger.info(f"acp-client: {m['text']}")
        # Send prompt and return agent's response
        _, agent_text = self._client._send_request("session/prompt", {
            "sessionId": self._session_id,
            "prompt": messages,
        })
        return agent_text
