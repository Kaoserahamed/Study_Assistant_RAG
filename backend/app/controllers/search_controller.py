# app/controllers/search_controller.py
from app.services.search_service import search_service
from app.schemas.search_schema import SearchRequest, SearchResponse


class SearchController:
    
    @staticmethod
    def search_documents(query_request: SearchRequest, user_id: int) -> SearchResponse:
        """Search user's documents"""
        results = search_service.search_documents(
            query=query_request.query,
            user_id=user_id,
            top_k=query_request.top_k
        )
        
        return SearchResponse(
            results=results,
            total_results=len(results)
        )


search_controller = SearchController()
