from ._anvil_designer import CompareTranscriptionTemplate
from anvil import *
import anvil.server
import anvil.users


class CompareTranscription(CompareTranscriptionTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def compare_button_click(self, **event_args):
    user_text = self.user_input_box.text
    official_text = self.official_input_box.text
    selected_lang = self.language_dropdown.selected_value or 'en'

    if not user_text or not official_text:
      alert("Please fill in both fields.")
      return

    # Passa o idioma selecionado, se necessário no futuro
    result = anvil.server.call("compare_transcriptions", user_text, official_text)

    self.comparison_output.content = result["html"]
    self.accuracy_label.text = (
      f"Accuracy: {result['stats']['accuracy']}% — "
      f"{result['stats']['correct']} correct, "
      f"{result['stats']['incorrect']} wrong, "
      f"{result['stats']['missing']} missing"
    )

  def search_button_click(self, **event_args):
    query = self.search_box.text
    if not query:
      alert("Please enter a search term.")
      return

    results = anvil.server.call('search_youtube_videos', query)
    self.results_repeater.items = results

  def user_input_box_change(self, **event_args):
    """This method is called when the text in this text area is edited"""
    pass

  def language_dropdown_change(self, **event_args):
    """Called when the language is changed"""
    selected = self.language_dropdown.selected_value
    Notification(f"Language set to: {selected}", timeout=2).show()
