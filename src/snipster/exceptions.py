class SnippetNotFound(BaseException):
    def __init__(self, snippet_id):
        self.message = f"Snippet ID: {snippet_id} not found"
        super().__init__(self.message)


class SnippetExists(BaseException):
    def __init__(self, snippet_id):
        self.message = f"Snippet ID: {snippet_id} already exists"
        super().__init__(self.message)


class TagExists(BaseException):
    def __init__(self, snippet_id, tag):
        self.message = f"Tag {tag} already exists for Snippet ID: {snippet_id}"
        super().__init__(self.message)


class TagNotFound(BaseException):
    def __init__(self, snippet_id, tag):
        self.message = f"Tag {tag} does not exist for Snippet ID: {snippet_id}"
        super().__init__(self.message)


class NoTagsPresent(BaseException):
    def __init__(self, snippet_id, tag):
        self.message = "Please add a tag before trying to remove tags"
        super().__init__(self.message)
