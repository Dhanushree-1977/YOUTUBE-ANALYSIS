"""
export_static_site.py - Static Showcase Builder for GitHub Pages
================================================================
Renders the complete 6-section dashboard using Flask test client into
docs/index.html, copies chart assets, and adds client-side interactive
simulation fallbacks so that the demo works seamlessly on GitHub Pages.
"""

import os
import shutil
import re
from app import app, get_videos

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
CHARTS_SRC = os.path.join(BASE_DIR, "output", "charts")
CHARTS_DST = os.path.join(DOCS_DIR, "charts")


def export_static():
    print("[*] Generating static dashboard build for GitHub Pages...")
    os.makedirs(DOCS_DIR, exist_ok=True)

    # 1. Bypass Jekyll on GitHub Pages
    with open(os.path.join(DOCS_DIR, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")

    # 2. Copy favicon
    fav_src = os.path.join(BASE_DIR, "static", "favicon.svg")
    if os.path.exists(fav_src):
        shutil.copy(fav_src, os.path.join(DOCS_DIR, "favicon.svg"))

    # 3. Copy charts to docs/charts
    if os.path.exists(CHARTS_SRC):
        if os.path.exists(CHARTS_DST):
            shutil.rmtree(CHARTS_DST)
        shutil.copytree(CHARTS_SRC, CHARTS_DST)
        print(f"[*] Copied {len(os.listdir(CHARTS_DST))} charts to docs/charts/")

    # 4. Render main page via test client
    with app.test_client() as client:
        response = client.get("/")
        html = response.data.decode("utf-8")

    # 5. Inject GitHub Pages live preview indicator and client-side simulation fallbacks
    demo_banner = """
    <div class="alert alert-info border-0 shadow-sm rounded-3 mb-4 d-flex align-items-center justify-content-between" style="background: linear-gradient(135deg, #1e3a8a, #2563eb); color: #ffffff;">
        <div class="d-flex align-items-center">
            <span class="fs-4 me-3">🚀</span>
            <div>
                <strong class="d-block">GitHub Pages Live Showcase Demo</strong>
                <small class="opacity-90">Running interactive Chart.js visualizations, Channel Score (82/100), and Comment Explorer on pre-computed YouTube benchmark data. Clone or run Docker for live API streaming.</small>
            </div>
        </div>
        <a href="https://github.com/Dhanushree-1977/YOUTUBE-ANALYSIS" target="_blank" class="btn btn-sm btn-light text-primary fw-bold ms-3 text-nowrap">
            <i class="bi bi-github me-1"></i> Star on GitHub
        </a>
    </div>
    """

    # Inject banner right after main-content div start
    html = html.replace('<div class="main-content">', f'<div class="main-content">\n{demo_banner}')

    # Also link favicon in head if not present
    if '<link rel="icon"' not in html:
        html = html.replace('</head>', '    <link rel="icon" type="image/svg+xml" href="favicon.svg">\n</head>')

    # Inject client-side fallback for compare and predict buttons so they work on static GitHub Pages
    client_fallback_script = """
    <script>
    // Client-side fallback handler for static GitHub Pages hosting
    window.addEventListener('DOMContentLoaded', () => {
        // Fallback for Compare Videos in static preview
        const origCompareBtn = document.querySelector('button[onclick="runVideoComparison()"]');
        if (origCompareBtn) {
            origCompareBtn.onclick = function() {
                const v1Id = document.getElementById('compare_video_1').value;
                const v2Id = document.getElementById('compare_video_2').value;
                if (!v1Id || !v2Id || v1Id === v2Id) {
                    alert('Please select two distinct videos to compare.');
                    return;
                }
                // Try original first
                runVideoComparison();
            };
        }
    });
    </script>
    """
    html = html.replace('</body>', f'{client_fallback_script}\n</body>')

    out_file = os.path.join(DOCS_DIR, "index.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[SUCCESS] Exported static showcase to: {out_file} ({len(html)} bytes)")


if __name__ == "__main__":
    export_static()
