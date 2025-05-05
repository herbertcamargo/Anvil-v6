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

    if not user_text or not official_text:
      alert("Please fill in both fields.")
      return

    result = anvil.server.call("compare_transcriptions", user_text, official_text)
    self.comparison_output.content = result["html"]
    self.accuracy_label.text = (
      f"Accuracy: {result['stats']['accuracy']}% — "
      f"{result['stats']['correct']} correct, "
      f"{result['stats']['incorrect']} wrong, "
      f"{result['stats']['missing']} missing"
    )
