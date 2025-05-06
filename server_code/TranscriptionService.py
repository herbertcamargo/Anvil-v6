import anvil.server
import re

def normalize_words(text):
  return text.lower().replace(".", "").replace(",", "").replace("!", "").replace("?", "").split()

class SmartComparer:
  def __init__(self, user_input, official_transcript):
    self.user_words = normalize_words(user_input)
    self.official_words = normalize_words(official_transcript)
    self.result = ""
    self.correct = 0
    self.incorrect = 0
    self.missing = 0

  def compare(self):
    i, j = 0, 0
    while j < len(self.official_words) or i < len(self.user_words):
      if i < len(self.user_words) and j < len(self.official_words) and self.user_words[i] == self.official_words[j]:
        self.result += f"<span style='color: lightgreen'>{self.official_words[j]}</span> "
        self.correct += 1
        i += 1
        j += 1
        continue

      # Tentativa de realinhamento leve
      realigned = False
      for offset in range(1, 4):
        if i + offset < len(self.user_words) and j + offset < len(self.official_words):
          if self.user_words[i + offset] == self.official_words[j + offset]:
            for k in range(offset):
              if j + k < len(self.official_words):
                self.result += f"<span style='color: lightblue'>{self.official_words[j + k]}</span> "
                self.missing += 1
            i += offset
            j += offset
            realigned = True
            break
      if realigned:
        continue

      if i < len(self.user_words):
        self.result += f"<span style='color: lightcoral'>{self.user_words[i]}</span> "
        self.incorrect += 1
        i += 1

      if j < len(self.official_words):
        self.result += f"<span style='color: lightblue'>{self.official_words[j]}</span> "
        self.missing += 1
        j += 1

    total = self.correct + self.incorrect + self.missing
    accuracy = round((self.correct / total) * 100, 1) if total else 0
    return {
      "html": self.result.strip(),
      "stats": {
        "accuracy": accuracy,
        "correct": self.correct,
        "incorrect": self.incorrect,
        "missing": self.missing,
        "total": total
      }
    }

@anvil.server.callable
def compare_transcriptions_simple(user_text, official_text):
  return SmartComparer(user_text, official_text).compare()
