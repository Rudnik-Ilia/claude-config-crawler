class AgentProcessingError(Exception):
    def __init__(self, github_url: str, cause: Exception) -> None:
        self.github_url = github_url
        self.cause = cause
        super().__init__(f"Skipped {github_url}: {type(cause).__name__}: {cause}")
