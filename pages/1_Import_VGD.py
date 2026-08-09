"""Projects & multi-spectrum Import page."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.services.import_service import list_spectrum_labels, load_spectrum, spectrum_from_vgd, load_vgd
from src.services import project_service
from src.ui.components.help import labeled_help
from src.ui.components.sidebar import render_sidebar
from src.ui.components.spectrum_viewer import render_spectrum_viewer
from src.ui.project_state import get_project, persist_session_to_active, set_project, sync_active_to_session
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("projects_spectra", lang))
labeled_help("What is a project?", "project", lang)

# --- Create / load project ---
st.subheader(t("project_section", lang))
rows = project_service.list_projects()
c1, c2 = st.columns(2)
with c1:
    new_name = st.text_input(t("new_project_name", lang), value="Мой XPS проект")
    if st.button(t("create_project", lang), type="primary"):
        proj = project_service.create_project(new_name)
        set_project(proj)
        st.success(f"Created {proj.name}")
        st.rerun()
with c2:
    if rows:
        labels = {r["id"]: f"{r['name']} ({r['n_spectra']} spectra) — {r['updated_at'][:19]}" for r in rows}
        pid = st.selectbox(t("load_existing", lang), options=list(labels.keys()), format_func=lambda i: labels[i])
        b1, b2 = st.columns(2)
        with b1:
            if st.button(t("load_project", lang)):
                set_project(project_service.load_project(pid))
                st.success("Project loaded")
                st.rerun()
        with b2:
            if st.button(t("delete_project", lang)):
                project_service.delete_project(pid)
                if get_project() and get_project().id == pid:
                    st.session_state["project"] = None
                st.warning("Deleted")
                st.rerun()
    else:
        st.caption(t("no_projects", lang))

project = get_project()
if project is None:
    st.info(t("need_project", lang))
    st.stop()

st.success(f"Active project: **{project.name}** (`{project.id}`) — {len(project.spectra)} spectra")
notes = st.text_area(t("project_notes", lang), value=project.notes)
if st.button(t("save_notes", lang)):
    project.notes = notes
    project_service.save_project(project)
    st.toast("Saved")

# --- Upload many VGDs ---
st.subheader(t("upload_section", lang))
uploads = st.file_uploader(t("vgd_files", lang), type=["vgd", "VGD"], accept_multiple_files=True)
path_blob = st.text_area(t("or_paths", lang))
if st.button(t("add_files", lang)):
    added = 0
    errors = []
    paths: list[Path] = []
    if uploads:
        tmpdir = Path(tempfile.mkdtemp(prefix="xps_vgd_"))
        for up in uploads:
            p = tmpdir / up.name
            p.write_bytes(up.getvalue())
            paths.append(p)
    for line in path_blob.splitlines():
        line = line.strip()
        if line:
            paths.append(Path(line))
    for path in paths:
        try:
            vgd = load_vgd(path)
            for idx in range(len(vgd.spectra)):
                sp = spectrum_from_vgd(vgd, idx)
                label = f"{path.name} :: {list_spectrum_labels(vgd)[idx]}"
                project_service.add_spectrum_to_project(project, sp, label=label)
                added += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: {exc}")
    set_project(project_service.load_project(project.id))
    st.success(f"Added {added} spectrum(s)")
    for e in errors:
        st.error(e)
    st.rerun()

project = get_project()
assert project is not None

# --- Choose active spectrum ---
st.subheader("3. Choose spectrum to analyse")
if not project.spectra:
    st.warning("No spectra in this project yet.")
    st.stop()

options = {s.id: s.label for s in project.spectra}
active_id = project.active_spectrum_id or project.spectra[0].id
idx = list(options.keys()).index(active_id) if active_id in options else 0
chosen = st.selectbox(
    "Active spectrum",
    options=list(options.keys()),
    format_func=lambda i: options[i],
    index=idx,
)
if st.button("Set as active for analysis", type="primary"):
    persist_session_to_active(save_disk=True)
    project_service.set_active_spectrum(project, chosen)
    set_project(project_service.load_project(project.id))
    sync_active_to_session()
    st.success("Active spectrum set — continue on Region / Baseline / Deconvolution / Workspace")
    st.rerun()

entry = next(s for s in project.spectra if s.id == (project.active_spectrum_id or chosen))
if entry.spectrum is not None:
    render_spectrum_viewer(
        entry.spectrum.binding_energy,
        entry.spectrum.intensity,
        viewer_key="import_active",
        title=entry.label,
        lang=lang,
        show_trace_toggles=False,
    )
