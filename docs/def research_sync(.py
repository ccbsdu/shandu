def research_sync(
    self, 
    query: str, 
    depth: int = 2, 
    breadth: int = 4, 
    progress_callback: Optional[Callable] = None,
    include_objective: bool = False,
    detail_level: str = "high"
) -> ResearchResult