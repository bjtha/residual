def url_maker(base_url: str):

    def join_url(*args) -> str:
        return '/'.join(str(item) for item in [base_url, *args])

    return join_url