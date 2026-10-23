"""Local web interface for the document analyzer. Run with python app.py."""

from flask import Flask, render_template, request

from analyzer import AnalysisError, ask_ai

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
MAX_DOCUMENT_LENGTH = 50_000


@app.route("/", methods=["GET", "POST"])
def index():
    document = ""
    result = None
    error = None
    status = 200
    if request.method == "POST":
        document = request.form.get("document", "")
        try:
            upload = request.files.get("file")
            if upload and upload.filename:
                if document.strip():
                    raise AnalysisError("Choose one source: pasted text or a text file.")
                if not upload.filename.lower().endswith(".txt"):
                    raise AnalysisError("Please upload a .txt file.")
                try:
                    document = upload.read().decode("utf-8-sig")
                except UnicodeDecodeError:
                    raise AnalysisError("Please save your text file with UTF-8 encoding.") from None
            if len(document) > MAX_DOCUMENT_LENGTH:
                raise AnalysisError("Please use a document with 50,000 characters or fewer.")
            result = ask_ai(document)
        except AnalysisError as exc:
            error = str(exc)
            status = 400
        except Exception:
            app.logger.exception("Document analysis failed")
            error = "Something went wrong while analyzing the document. Please try again."
            status = 500
    return render_template("index.html", document=document, result=result, error=error), status


@app.errorhandler(413)
def too_large(_error):
    return render_template(
        "index.html", document="", result=None,
        error="This upload is too large. Use a text file smaller than 1 MB.",
    ), 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
