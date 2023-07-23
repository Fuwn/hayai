from flask import Flask, flash, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
import shutil
import subprocess

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 16 * 1000 * 1000
app.add_url_rule("/uploads/<name>", endpoint="download_file", build_only=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "txt",
        "epub",
        "pdf",
    }


@app.route("/uploads/<name>")
def download_file(name):
    return send_from_directory("../uploads", f"hayai_{name}")


@app.route("/", methods=["GET", "POST"])
def upload_file():
    # Clean old EPUBs
    if os.path.exists("./uploads"):
        shutil.rmtree("uploads")

    os.makedirs("./uploads")

    if request.method == "POST":
        if "file" not in request.files:
            flash("no file part")

            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("no selected file")

            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(str(file.filename))

            file.save(os.path.join("./uploads", filename))
            # Convert EPUB to "bionic" EPUB
            os.system(f"python hayai/brec.py ./uploads/{filename}")
            # Remove brec's unused artifacts folder
            shutil.rmtree(f"{filename}_zip")
            # Move "bionic" EPUB to uploads folder
            shutil.move(f"hayai_{filename}", f"./uploads/hayai_{filename}")

            # Prompt user to download "bionic" EPUB
            return redirect(url_for("download_file", name=filename))

    return page(
        '<blockquote>Upload an EPUB, receive a <b>"bi</b>onic" <b>EP</b>UB.</blockquote>',
        '<a href="/reader">Want to read an EPUB?</a>',
    )


@app.route("/reader", methods=["GET", "POST"])
def reader():
    # Clean old EPUBs
    if os.path.exists("./uploads"):
        shutil.rmtree("uploads")

    os.makedirs("./uploads")

    if request.method == "POST":
        if "file" not in request.files:
            flash("no file part")

            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("no selected file")

            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(str(file.filename))

            file.save(os.path.join("./uploads", filename))

            output = (
                subprocess.run(
                    ["epr", "-d", f"./uploads/{filename}"], stdout=subprocess.PIPE
                )
                .stdout.decode("utf-8")
                .replace("\n\n\n", "\n")
                .replace("\n", "<br>")
            )

            return page(output, '<a href="/">Want to read another EPUB?</a>')

    return page(
        "<blockquote>Upload an EPUB, read it in plain-text.</blockquote>",
        '<a href="/">Want to convert an EPUB?</a>',
    )


def page(main_content: str, footer: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
    <head>
        <title>はやい</title>

        <link rel="stylesheet" type="text/css" href="https://latex.now.sh/style.css">
        <link rel="stylesheet" type="text/css" href="https://skybox.sh/css/palettes/base16-light.css">
        <link rel="stylesheet" type="text/css" href="https://skybox.sh/css/risotto.css">
        <link rel="stylesheet" type="text/css" href="https://skybox.sh/css/custom.css">
        <link rel="icon" type="image/png" href="https://ps.fuwn.me/-wLj4vfbxrc/favicon.png">
    </head>

    <body>
        <style>text-align: center;</style>

        <h1>はやい</h1>

        {main_content}

        <form method=post enctype=multipart/form-data>
          <input type="file" name="file">
          <input type="submit" value="アップロード">
        </form>

        <br>

        <hr>

        <p>{footer}</p>
    </body>
</html>
"""
