import os
import shutil

from .HTMLandCSS import HTMLforEditor, read_file, front, back, front_cloze, back_cloze, css
from aqt import mw
from anki.hooks import addHook
import anki

MODEL_NAME = "KaTeX and Markdown"
CONF_NAME = "MDKATEX"


def markdownPreview(editor):
    """This function runs when the user opens the editor, creates the markdown preview area"""
    if editor.note.note_type()["name"] in [
        MODEL_NAME + " Basic (Color)",
        MODEL_NAME + " Cloze (Color)",
    ]:
        editor.web.eval(HTMLforEditor)
    else:  # removes the markdown preview
        editor.web.eval(
            """
					var area = document.getElementById('markdown-area');
					if(area) area.remove();
        """
        )


addHook("loadNote", markdownPreview)


def create_model_if_necessacy():
    """
    Runs when the user opens Anki, creates the two card types and also handles updating
    the card types CSS and HTML if the addon has a pending update
    """
    model = mw.col.models.by_name(MODEL_NAME + " Basic (Color)")
    model_cloze = mw.col.models.by_name(MODEL_NAME + " Cloze (Color)")

    if not model:
        create_model()
    if not model_cloze:
        create_model_cloze()

    update()


def create_model():
    """Creates the Basic Card type"""
    m = mw.col.models
    model = m.new(MODEL_NAME + " Basic (Color)")

    field = m.newField("Front")
    m.addField(model, field)

    field = m.newField("Back")
    m.addField(model, field)

    template = m.newTemplate(MODEL_NAME + " Basic (Color)")
    template["qfmt"] = front
    template["afmt"] = back
    model["css"] = css

    m.addTemplate(model, template)
    m.add(model)
    m.save(model)


def create_model_cloze():
    """Creates the Cloze Card type"""
    m = mw.col.models
    model = m.new(MODEL_NAME + " Cloze (Color)")
    model["type"] = anki.consts.MODEL_CLOZE

    field = m.newField("Text")
    m.addField(model, field)

    field = m.newField("Back Extra")
    m.addField(model, field)

    template = m.newTemplate(MODEL_NAME + " Cloze (Color)")
    template["qfmt"] = front_cloze
    template["afmt"] = back_cloze
    model["css"] = css

    m.addTemplate(model, template)
    m.add(model)
    m.save(model)


def update():
    """Updates the card types the addon has a pending update"""
    model = mw.col.models.by_name(MODEL_NAME + " Basic (Color)")
    model_cloze = mw.col.models.by_name(MODEL_NAME + " Cloze (Color)")

    model["tmpls"][0]["qfmt"] = front
    model["tmpls"][0]["afmt"] = back
    model["css"] = css

    model_cloze["tmpls"][0]["qfmt"] = front_cloze
    model_cloze["tmpls"][0]["afmt"] = back_cloze
    model_cloze["css"] = css

    mw.col.models.save(model)
    mw.col.models.save(model_cloze)

    if os.path.isdir(os.path.join(mw.col.media.dir(), "_katex")):
        shutil.rmtree(os.path.join(mw.col.media.dir(), "_katex"))

    if os.path.isdir(os.path.join(mw.col.media.dir(), "_markdown-it")):
        shutil.rmtree(os.path.join(mw.col.media.dir(), "_markdown-it"))

    addon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))

    _write_data("style.css", bytes(read_file("css/style.css"), 'utf-8'))
    _add_file(os.path.join(addon_path, "css",  "user_style.css"), "user_style.css")
    _add_file(os.path.join(addon_path, "_katex.min.js"), "_katex.min.js")
    _add_file(os.path.join(addon_path, "_katex.css"), "_katex.css")
    _add_file(os.path.join(addon_path, "_auto-render.js"), "_auto-render.js")
    _add_file(os.path.join(addon_path, "_markdown-it.min.js"),
              "_markdown-it.min.js")
    _add_file(os.path.join(addon_path, "_highlight.css"), "_highlight.css")
    _add_file(os.path.join(addon_path, "_highlight.js"), "_highlight.js")
    _add_file(os.path.join(addon_path, "_mhchem.js"), "_mhchem.js")
    _add_file(os.path.join(addon_path, "_markdown-it-mark.js"),
              "_markdown-it-mark.js")

    for katex_font in os.listdir(os.path.join(addon_path, "fonts")):
        _add_file(os.path.join(addon_path, "fonts", katex_font), katex_font)


def _add_file(path, filename):
    if not os.path.isfile(os.path.join(mw.col.media.dir(), filename)):
        mw.col.media.add_file(path)


def _write_data(filename, data):
    mw.col.media.trash_files([filename])
    mw.col.media.write_data(filename, data)


addHook("profileLoaded", create_model_if_necessacy)
