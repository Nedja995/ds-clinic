"""
brand.py — BrandConfig model and loader.

Owns all identity and commercial configuration for a deployed DSClinic instance.
Loaded from brand.json adjacent to the executable (or project root in dev).
Falls back to built-in defaults when brand.json is absent — the app is always
fully functional without it (generic "MedAI - ViTec" branding).

Deliberately separate from AppSettings: AppSettings governs AI and user
preferences; BrandConfig governs visual identity and subscription tier.
Neither model imports the other (AD-20).
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Literal

from pydantic import BaseModel, Field

from npy.core.utils import get_base_dir_path

logger = logging.getLogger(__name__)

_BRAND_FILENAME = "brand.json"

SubscriptionTier = Literal["trial", "standard", "enterprise"]

# Features gated per tier. Enterprise is a superset of standard.
_TIER_FEATURES: Dict[SubscriptionTier, set[str]] = {
    "trial": set(),
    "standard": {"unlimited_sessions", "no_watermark", "full_reports"},
    "enterprise": {"unlimited_sessions", "no_watermark", "full_reports", "multi_user", "custom_models", "advanced_analytics"},
}


class BrandConfig(BaseModel):
    """
    Identity and commercial configuration for one deployed clinic instance.

    All string fields are used verbatim in PDF output and GUI labels —
    keep them short enough to fit in headers (< 80 chars recommended).
    logo_path is resolved relative to the executable directory at render time.
    """

    clinic_name: str = "MedAI - ViTec"
    clinic_subtitle: str = "Medical AI Analysis Platform"
    clinic_address: str = ""

    # Asset path — relative to executable root (AD-09) or absolute.
    # Empty string means no logo is rendered.
    logo_path: str = "resources/logo.png"

    # PDF color scheme — hex strings, e.g. "#003366"
    primary_color: str = "#003366"
    secondary_color: str = "#ebebeb"

    # PDF header/footer text
    report_header_text: str = ""
    report_footer_text: str = (
        "NAPOMENA: Rezultati su holistički uvid. "
        "Za medicinske dijagnoze konsultujte svog lekara."
    )
    report_consent_text: str = (
        "SAGLASNOST: Pacijent je upoznat sa metodom, "
        "preporučenom terapijom i istu u potpunosti prihvata."
    )

    subscription_tier: SubscriptionTier = "standard"

    # ── Persistence ───────────────────────────────────────────────────────────

    @classmethod
    def load(cls) -> "BrandConfig":
        """
        Load brand.json from the executable root. Returns defaults silently
        when the file is absent — white-label deployments supply the file;
        generic SaaS builds omit it and use the built-in defaults.
        """
        brand_path = Path(get_base_dir_path()) / _BRAND_FILENAME
        if not brand_path.exists():
            logger.debug("brand.json not found — using BrandConfig defaults (generic branding).")
            return cls()

        try:
            with open(brand_path, "r", encoding="utf-8") as f:
                raw: Dict[str, Any] = json.load(f)
            instance = cls(**raw)
            logger.info(f"BrandConfig loaded: {instance.clinic_name!r} tier={instance.subscription_tier!r}")
            return instance
        except Exception as exc:
            logger.error(f"Failed to parse brand.json — falling back to defaults: {exc}")
            return cls()

    def save(self) -> None:
        """
        Persist current BrandConfig to brand.json at the executable root.
        Used by the Clinic Profile settings section (v2.11.4) when the user
        edits their brand profile via the Settings UI.
        """
        brand_path = Path(get_base_dir_path()) / _BRAND_FILENAME
        tmp_path = brand_path.with_suffix(".tmp")
        try:
            payload = self.model_dump()
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            tmp_path.replace(brand_path)
            logger.info(f"BrandConfig saved to {brand_path}")
        except OSError as exc:
            logger.error(f"Failed to save brand.json: {exc}")
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise

    # ── Resolved paths ────────────────────────────────────────────────────────

    def resolved_logo_path(self) -> str:
        """
        Returns an absolute path to the logo file, resolving relative paths
        against the executable root (AD-09). Returns empty string if the
        resolved path does not exist so callers can skip logo rendering safely.
        """
        if not self.logo_path:
            return ""
        p = Path(self.logo_path)
        if not p.is_absolute():
            p = Path(get_base_dir_path()) / p
        return str(p) if p.exists() else ""

    # ── Subscription gate ─────────────────────────────────────────────────────

    def is_feature_allowed(self, feature: str) -> bool:
        """
        Returns True when the current subscription_tier grants access to
        the named feature. Unknown features default to False so new gated
        features are safe by default.

        Enterprise is a superset of standard; trial has no gated features.
        """
        allowed = _TIER_FEATURES.get(self.subscription_tier, set())
        result = feature in allowed
        if not result:
            logger.debug(
                f"Feature '{feature}' denied — tier={self.subscription_tier!r} "
                f"(allowed={sorted(allowed) or 'none'})"
            )
        return result

    # ── Color helpers ─────────────────────────────────────────────────────────

    def primary_color_rgb(self) -> tuple[int, int, int]:
        """Parse primary_color hex string to (R, G, B) tuple for FPDF."""
        return _hex_to_rgb(self.primary_color)

    def secondary_color_rgb(self) -> tuple[int, int, int]:
        """Parse secondary_color hex string to (R, G, B) tuple for FPDF."""
        return _hex_to_rgb(self.secondary_color)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert a CSS hex color string (#RRGGBB or #RGB) to an (R, G, B) int tuple.
    Falls back to (0, 51, 102) — the original DSClinic dark blue — on parse error.
    """
    _fallback = (0, 51, 102)
    raw = hex_color.lstrip("#")
    try:
        if len(raw) == 3:
            raw = "".join(c * 2 for c in raw)
        if len(raw) != 6:
            raise ValueError(f"Unexpected hex length: {len(raw)}")
        r = int(raw[0:2], 16)
        g = int(raw[2:4], 16)
        b = int(raw[4:6], 16)
        return r, g, b
    except (ValueError, AttributeError) as exc:
        logger.warning(f"Invalid hex color {hex_color!r} — using fallback: {exc}")
        return _fallback


# ── Single Global Instance Initialized on Import ──────────────────────────────
brand_config = BrandConfig.load()
