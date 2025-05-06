from ._anvil_designer import TranscriptionPractice as TranscriptionPracticeTemplate
from anvil import *
import anvil.server
import anvil.users

class TranscriptionPractice(TranscriptionPracticeTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def search_button_click(self, **event_args):
    query = self.search_input.text.strip()
    self.search_results_panel.clear()
    if not query:
      Notification("Please enter a search query.", timeout=3).show()
      return
    try:
      results = anvil.server.call('search_youtube_videos', query)
      if not results:
        self.search_results_panel.add_component(Label(text="No results found."))
        return
      for video in results:
        card = self._make_video_result_card(video)
        self.search_results_panel.add_component(card)
    except Exception as e:
      Notification(f"Error searching videos: {e}", style="danger", timeout=5).show()

  def _make_video_result_card(self, video):
    card = ColumnPanel()
    card.add_component(Image(source=video['thumbnail'], width=160, height=90))
    card.add_component(Label(text=video['title'], bold=True))
    card.add_component(Label(text=f"Channel: {video['channel']}", font_size=12))
    button = Button(text="Select", tag=video['id'])
    button.set_event_handler('click', self._video_select_click)
    card.add_component(button)
    return card

  def _video_select_click(self, sender, **event_args):
    video_id = sender.tag
    try:
      data = anvil.server.call('get_video_details_and_transcript', video_id, self.language_dropdown.selected_value.lower())
      details = data['details']
      transcript = data['transcript']
      self.video_title.text = details['title']
      self.video_player_panel.content = f'<iframe width="100%" height="315" src="{details["embed_url"]}" frameborder="0" allowfullscreen></iframe>'
      self.transcription_input.text = ''
      self.transcription_input.placeholder = transcript
      self.video_transcription_card.visible = True
    except Exception as e:
      Notification(f"Error loading video: {e}", style="danger", timeout=5).show()

  def submit_button_click(self, **event_args):
    user_text = self.transcription_input.text.strip()
    actual_text = self.transcription_input.placeholder.strip()
    if not user_text or not actual_text or actual_text.startswith('No transcript'):
      Notification("Please select a video with a transcript and enter your transcription.", timeout=3).show()
      return
    try:
      result = anvil.server.call('compare_transcriptions', user_text, actual_text)
      stats = f"Total words: {result['total_words']}\nYour words: {result['user_words']}\nCorrect: {result['correct_words']}\nAccuracy: {result['accuracy']:.1f}%"
      self.stats_content.text = stats
      diff_html = ''
      for w in result['diff']:
        color = 'green' if w['correct'] else 'red'
        diff_html += f"<span style='color:{color}'>{w['word']}</span> "
      self.result_container.text = diff_html
      self.result_container.visible = True
    except Exception as e:
      Notification(f"Error comparing transcription: {e}", style="danger", timeout=5).show()

  def form_show(self, **event_args):
    user = anvil.users.get_user()
    if not user:
      Notification("Please log in to access transcription practice.", timeout=3).show()
      open_form('LoginPage')
      return
    if not user.get('subscription') or user['subscription'].lower() == 'free':
      Notification("You need an active subscription to access this page.", timeout=3).show()
      open_form('StripePricing')
      return

  def language_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
