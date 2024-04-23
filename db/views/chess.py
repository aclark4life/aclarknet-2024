import chess
import chess.svg
from django.views.generic import TemplateView


class ChessBoardView(TemplateView):
    template_name = "chess_board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = chess.Board()
        html = chess.svg.board(board=board).replace("svg", "svg style='width:100%;'")
        context["chess_board"] = html
        context["chess_nav"] = True
        display_mode = (
            {"bg": "dark", "text": "light"}
            if self.request.user.profile.dark
            else {"bg": "light", "text": "dark"}
        )
        context["display_mode"] = display_mode
        return context
