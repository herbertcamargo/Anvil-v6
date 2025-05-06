from ._anvil_designer import VideoResultCardTemplate
from anvil import *
import anvil.server
import anvil.users


class VideoResultCard(VideoResultCardTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def set_item(self, item):
    self.thumbnail_image.source = item['thumbnail']
    self.title_label.content = item['title']

  def form_show(self, **event_args):
    """This method is called when the form is shown on the page"""
    pass

  def click(self, **event_args):
    open_form("CompareTranscription", video_id=self.item["video_id"])
