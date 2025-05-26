class SnippetNotFound(BaseException):
    def __init__(self, snippet_id):
        self.message = f"Snippet ID: {snippet_id} not found"
        super().__init__(self.message)


class SnippetExists(BaseException):
    def __init__(self, snippet_id):
        self.message = f"Snippet ID: {snippet_id} already exists"
        super().__init__(self.message)
