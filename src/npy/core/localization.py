# localization.py
import builtins
import gettext
import os

class TranslationManager:
    def __init__(self, locale_dir="locale", default_lang="en", save_config_callback=None):
        self.locale_dir = locale_dir
        self.current_lang = default_lang
        self.ui_update_callbacks = []
        # Save a reference to your existing config saving mechanism
        self.save_config_callback = save_config_callback 
        self.apply_language(default_lang)

    def apply_language(self, lang_code):
        """Loads the language files and injects the _ function globally."""
        self.current_lang = lang_code
        
        # Load translation catalog
        translation = gettext.translation(
            domain='app',
            localedir=self.locale_dir,
            languages=[lang_code],
            fallback=True
        )
        
        # Inject standard and plural tools into builtins
        builtins._ = translation.gettext
        builtins.ngettext = translation.ngettext

        # 1. AUTOMATICALLY SAVE CONFIG
        # If a config callback was given, trigger it to save the choice to JSON
        if self.save_config_callback:
            self.save_config_callback(lang_code)

        # 2. UPDATE STATIC ACTIVE UI ELEMENTS
        self.refresh_all_uis()

    def register_ui(self, callback):
        self.ui_update_callbacks.append(callback)

    def refresh_all_uis(self):
        for callback in self.ui_update_callbacks:
            try:
                callback()
            except Exception:
                pass