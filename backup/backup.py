# app.py
from flask import Flask, request, render_template
from tga_cli.app_factory import create_app, create_processor_router
from tga_cli.domain.models import RunInputs

app = Flask(__name__)

INI_PATH = "MLSA_GapAnalysisRefDB.ini"  # <-- your DB INI

# Wire app services once
ctx = create_app(ini_path=INI_PATH)
preset_repo = ctx["preset_repo"]
router = create_processor_router(ini_path=INI_PATH)

@app.get("/")
def index():
    # 1) Load dropdown presets (DB)
    try:
        presets = preset_repo.get_active_presets()
    except Exception as e:
        presets = []
        # Keep the page usable even if DB is down
        db_error = f"Failed to load presets from database: {e}"
    else:
        db_error = None

    # 2) Read selected preset_id from query string
    preset_id_raw = (request.args.get("preset_id") or "").strip()
    preset_id = int(preset_id_raw) if preset_id_raw.isdigit() else None

    # 3) Defaults (manual)
    page_model = {
        "presets": presets,
        "preset_id": preset_id,
        "preset_name": None,
        "preset_web": None,
        "preset_processor": None,
        "competitor": "",
        "baseline": "",
        "instruction_preset": "",
        "extra_instructions": "",
        "file": "",
        "error": db_error,
    }

    # 4) If preset selected, fetch from DB and prefill
    if preset_id is not None and db_error is None:
        try:
            p = preset_repo.get_preset(preset_id)
        except Exception as e:
            page_model["error"] = f"Failed to load preset {preset_id}: {e}"
            p = None

        if p is None and page_model["error"] is None:
            page_model["error"] = f"Preset id {preset_id} not found or inactive."
        elif p is not None:
            # Note: p is your domain Preset object
            page_model.update(
                {
                    "preset_name": getattr(p, "name", None),
                    "preset_web": getattr(p, "web", None),
                    "preset_processor": getattr(p, "processor", None),
                    "competitor": getattr(p, "competitor", "") or "",
                    "baseline": getattr(p, "baseline", "") or "",
                    "instruction_preset": getattr(p, "instruction_preset", "") or "",
                    "extra_instructions": getattr(p, "extra_instructions", "") or "",
                    # Your domain model may call this "file" even if DB column is source_file_path
                    "file": getattr(p, "file", "") or "",
                }
            )

    return render_template("index.html", **page_model)


@app.post("/run")
def run():
    preset_id_raw = (request.form.get("preset_id") or "").strip()
    preset_id = int(preset_id_raw) if preset_id_raw.isdigit() else None

    inputs = RunInputs(
        competitor=(request.form.get("competitor") or "").strip(),
        baseline=(request.form.get("baseline") or "").strip(),
        instruction_preset=(request.form.get("instruction_preset") or "").strip(),
        extra_instructions=(request.form.get("extra_instructions") or "").strip(),
        file=(request.form.get("file") or "").strip(),
        preset_id=preset_id,
    )

    # IMPORTANT: router.run() should re-read the preset from DB using preset_id
    result = router.run(inputs)

    return {
        "mode": result.mode,
        "summary": result.summary,
        "context": result.context,
        "competitor": result.competitor,
        "baseline": result.baseline,
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)















# from flask import Flask, request, render_template
# from tga_cli.app_factory import create_app, create_processor_router
# from tga_cli.domain.models import RunInputs
#
# app = Flask(__name__)
#
# # Wire app services once
# ctx = create_app(ini_path="TitaniumTechnologyGapAnalysisRef.ini")
# preset_repo = ctx["preset_repo"]
#
# router = create_processor_router(ini_path="TitaniumTechnologyGapAnalysisRef.ini")
#
#
# @app.get("/")
# def index():
#     # 1) Load dropdown presets
#     presets = preset_repo.get_active_presets()
#
#     # 2) Read selected preset_id from query string
#     preset_id_raw = request.args.get("preset_id", "").strip()
#     preset_id = int(preset_id_raw) if preset_id_raw.isdigit() else None
#
#     # 3) Defaults (manual)
#     page_model = {
#         "presets": presets,
#         "preset_id": preset_id,
#         "preset_name": None,
#         "preset_web": None,
#         "preset_processor": None,
#         "competitor": "",
#         "baseline": "",
#         "instruction_preset": "",
#         "extra_instructions": "",
#         "file": "",
#         "error": None,
#     }
#
#     # 4) If preset selected, fetch from DB and prefill
#     if preset_id is not None:
#         p = preset_repo.get_preset(preset_id)
#         if p is None:
#             page_model["error"] = f"Preset id {preset_id} not found or inactive."
#         else:
#             page_model.update({
#                 "preset_name": getattr(p, "name", None),
#                 "preset_web": getattr(p, "web", None),
#                 "preset_processor": getattr(p, "processor", None),
#                 "competitor": p.competitor or "",
#                 "baseline": p.baseline or "",
#                 "instruction_preset": p.instruction_preset or "",
#                 "extra_instructions": p.extra_instructions or "",
#                 "file": getattr(p, "file", "") or "",
#             })
#
#     return render_template("index.html", **page_model)
#
#
# @app.post("/run")
# def run():
#     preset_id_raw = request.form.get("preset_id", "").strip()
#     preset_id = int(preset_id_raw) if preset_id_raw.isdigit() else None
#
#     inputs = RunInputs(
#         competitor=request.form.get("competitor", "").strip(),
#         baseline=request.form.get("baseline", "").strip(),
#         instruction_preset=request.form.get("instruction_preset", "").strip(),
#         extra_instructions=request.form.get("extra_instructions", "").strip(),
#         file=request.form.get("file", "").strip(),
#         preset_id=preset_id,
#     )
#
#     result = router.run(inputs)
#
#     return {
#         "mode": result.mode,
#         "summary": result.summary,
#         "context": result.context,
#         "competitor": result.competitor,
#         "baseline": result.baseline,
#     }
#
#










# from __future__ import annotations
#
# from flask import Flask, request, jsonify, render_template
#
# from tga_cli.app_factory import create_app  # composition root
# from tga_cli.domain.models import Inputs
#
# print("WEB_CONTROLLER LOADED:", __file__)
#
#
# def create_flask_app(ini_path: str = "TitaniumTechnologyGapAnalysisRef.ini") -> Flask:
#     """
#     HTTP delivery adapter.
#
#     Responsibilities:
#     - Parse HTTP request inputs (form fields)
#     - Translate into domain Inputs
#     - Invoke the application service (analysis_service) wired by app_factory
#     - Return JSON or render templates
#
#     No workflow logic belongs here.
#     """
#     app = Flask(__name__)
#
#     # Get wired application services from the composition root
#     ctx = create_app(ini_path=ini_path)
#     analysis_service = ctx["analysis_service"]
#
#     # Optional: presets repository for dropdown + defaulting
#     preset_repo = ctx.get("preset_repo")
#
#     @app.get("/")
#     def index():
#         presets = preset_repo.get_active_presets() if preset_repo else []
#         preset_id = request.args.get("preset_id", "").strip()
#
#         selected = None
#         if preset_repo and preset_id.isdigit():
#             selected = preset_repo.get_preset(int(preset_id))
#
#         return render_template(
#             "index.html",
#             presets=presets,
#             preset_id=preset_id,
#             competitor=(selected.competitor if selected else ""),
#             baseline=(selected.baseline if selected and selected.baseline else ""),
#             instruction_preset=(selected.instruction_preset if selected and selected.instruction_preset else ""),
#             extra_instructions=(selected.extra_instructions if selected and selected.extra_instructions else ""),
#             file=(selected.file if selected and selected.file else ""),
#             preset_name=(selected.name if selected else ""),
#             preset_web=(selected.web if selected and selected.web else ""),
#             preset_processor=(selected.processor if selected and selected.processor else ""),
#             error=None,
#         )
#
#     @app.post("/run")
#     def run():
#         preset_id_raw = request.form.get("preset_id", "").strip()
#         preset_id = int(preset_id_raw) if preset_id_raw.isdigit() else None
#
#         # Re-read preset from DB (do not trust hidden fields)
#         preset = preset_repo.get_preset(preset_id) if (preset_repo and preset_id is not None) else None
#
#         competitor = request.form.get("competitor", "").strip() or (preset.competitor if preset else "")
#         baseline = request.form.get("baseline", "").strip() or (preset.baseline or "" if preset else "")
#         instruction_preset = request.form.get("instruction_preset", "").strip() or (preset.instruction_preset or "" if preset else "")
#         extra_instructions = request.form.get("extra_instructions", "").strip() or (preset.extra_instructions or "" if preset else "")
#         file = request.form.get("file", "").strip() or (preset.file or "" if preset else "")
#
#         inputs = Inputs(
#             competitor=competitor,
#             baseline=baseline,
#             instruction_preset=instruction_preset,
#             extra_instructions=extra_instructions,
#             file=file,
#             preset_id=preset_id,
#         )
#
#         result = analysis_service.run(inputs)
#         return jsonify(result)
#
#     return app
#
#
# if __name__ == "__main__":
#     app = create_flask_app()
#     app.run(host="0.0.0.0", port=5000, debug=True)




# from __future__ import annotations
#
# from flask import Flask, request, jsonify, render_template
#
# from tga_cli.app_factory import create_app  # composition root
# from tga_cli.domain.models import Inputs
#
# print("WEB_CONTROLLER LOADED:", __file__)
#
#
# def create_flask_app(ini_path: str = "TitaniumTechnologyGapAnalysisRef.ini") -> Flask:
#     """
#     HTTP delivery adapter.
#
#     Responsibilities:
#     - Parse HTTP request inputs (form fields)
#     - Translate into domain Inputs
#     - Invoke the application service (analysis_service) wired by app_factory
#     - Return JSON or render templates
#
#     No workflow logic belongs here.
#     """
#     app = Flask(__name__)
#
#     # Get wired application services from the composition root
#     ctx = create_app(ini_path=ini_path)
#     analysis_service = ctx["analysis_service"]
#
#     # Optional: presets repository for dropdown + defaulting
#     preset_repo = ctx.get("preset_repo")
#
#     @app.get("/")
#     def index():
#         presets = preset_repo.get_active_presets() if preset_repo else []
#         preset_id = request.args.get("preset_id", "").strip()
#
#         selected = None
#         if preset_repo and preset_id.isdigit():
#             selected = preset_repo.get_preset(int(preset_id))
#
#         return render_template(
#             "index.html",
#             presets=presets,
#             preset_id=preset_id,
#             competitor=(selected.competitor if selected else ""),
#             baseline=(selected.baseline if selected and selected.baseline else ""),
#             instruction_preset=(selected.instruction_preset if selected and selected.instruction_preset else ""),
#             extra_instructions=(selected.extra_instructions if selected and selected.extra_instructions else ""),
#             file=(selected.file if selected and selected.file else ""),
#             preset_name=(selected.name if selected else ""),
#             preset_web=(selected.web if selected and selected.web else ""),
#             preset_processor=(selected.processor if selected and selected.processor else ""),
#             error=None,
#         )
#
#     @app.post("/run")
#     def run():
#         preset_id_raw = request.form.get("preset_id", "").strip()
#         preset_id = int(preset_id_raw) if preset_id_raw.isdigit() else None
#
#         # Re-read preset from DB (do not trust hidden fields)
#         preset = preset_repo.get_preset(preset_id) if (preset_repo and preset_id is not None) else None
#
#         competitor = request.form.get("competitor", "").strip() or (preset.competitor if preset else "")
#         baseline = request.form.get("baseline", "").strip() or (preset.baseline or "" if preset else "")
#         instruction_preset = request.form.get("instruction_preset", "").strip() or (preset.instruction_preset or "" if preset else "")
#         extra_instructions = request.form.get("extra_instructions", "").strip() or (preset.extra_instructions or "" if preset else "")
#         file = request.form.get("file", "").strip() or (preset.file or "" if preset else "")
#
#         inputs = Inputs(
#             competitor=competitor,
#             baseline=baseline,
#             instruction_preset=instruction_preset,
#             extra_instructions=extra_instructions,
#             file=file,
#             preset_id=preset_id,
#         )
#
#         result = analysis_service.run(inputs)
#         return jsonify(result)
#
#     return app
#
#
# if __name__ == "__main__":
#     app = create_flask_app()
#     app.run(host="0.0.0.0", port=5000, debug=True)
