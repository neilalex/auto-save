'''
AutoSave - Sublime Text Plugin

Provides a convenient way to turn on and turn off
automatically saving the current file after every modification.
'''

import os, sys
import sublime
import sublime_plugin
from threading import Timer


settings_filename = "auto_save.sublime-settings"
delay_field = "auto_save_delay_in_seconds"
backup_field = "auto_save_backup"
backup_suffix_field = "auto_save_backup_suffix"

class AutoSaveListener(sublime_plugin.EventListener):

  save_queue = [] # Save queue for on_modified events.

  @staticmethod
  def generate_backup_filename(filename, backup_suffix):
    dirname, basename = [os.path.dirname(filename),
      os.path.basename(filename).split('.')]
    if len(basename) > 1:
      basename.insert(-1, backup_suffix)
    else:
      basename.append(backup_suffix)
    return dirname + '/' + '.'.join(basename)


  def on_modified(self, view):
    settings = sublime.load_settings(settings_filename)

    # Only use autosave with todo.md, todo-personal.md, and distractions.md
    if (view.file_name() is None) or not ('todo.md' in view.file_name() or 'todo-personal.md' in view.file_name() or 'Distractions.md' in view.file_name()):
      return

    delay = settings.get(delay_field)
    backup = settings.get(backup_field)
    backup_suffix = settings.get(backup_suffix_field)

    def callback():
      '''
      Must use this callback for ST2 compatibility
      '''
      if view.is_dirty() and not view.is_loading():
        if not backup: # Save file
          view.run_command("save")
        else: # Save backup file
          content = view.substr(sublime.Region(0, view.size()))
          try:
            with open(AutoSaveListener.generate_backup_filename(
              view.file_name(), backup_suffix), 'w', encoding='utf-8') as f:
              f.write(content)
          except Exception as e:
            sublime.status_message(e)
            raise e

      else:
        print("Auto-save callback invoked, but view is",
              "currently loading." if view.is_loading() else "unchanged from disk.")


    def debounce_save():
      '''
      If the queue is longer than 1, pop the last item off,
      Otherwise save and reset the queue.
      '''
      if len(AutoSaveListener.save_queue) > 1:
        AutoSaveListener.save_queue.pop()
      else:
        sublime.set_timeout(callback, 0)
        AutoSaveListener.save_queue = []


    AutoSaveListener.save_queue.append(0) # Append to queue for every on_modified event.
    Timer(delay, debounce_save).start() # Debounce save by the specified delay.
