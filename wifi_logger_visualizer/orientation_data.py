"""Read hash-bound saved map orientation without changing the Wi-Fi database.

The map snapshot's recorded YAML path identifies its orientation sidecar. For
portable database copies, the same sidecar basename may instead be placed next
to the SQLite file. Only metadata matching the captured map hash is accepted;
its age is not a freshness gate because it describes a saved map, not live TF.
"""
import math
from pathlib import Path

import yaml


def _finite_number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def _validated_orientation(document, map_data):
    """Validate the sidecar and derive North's clockwise image rotation."""
    if not isinstance(document, dict) or type(document.get('schema_version')) is not int or document['schema_version'] != 1:
        return dict(valid=False, reason='Unsupported orientation file format')
    if not map_data.get('content_hash') or document.get('map_content_hash') != map_data['content_hash']:
        return dict(valid=False, reason='Saved orientation does not match this map')
    orientation = document.get('orientation')
    if not isinstance(orientation, dict) or orientation.get('valid') is not True:
        reason = orientation.get('reason') if isinstance(orientation, dict) else None
        return dict(valid=False, reason=reason if isinstance(reason, str) and reason else 'Saved estimate is unavailable')
    if orientation.get('reference') != 'true_north':
        return dict(valid=False, reason='Saved orientation is not referenced to true North')
    heading = orientation.get('map_x_heading_from_east_deg')
    yaw = map_data.get('origin_yaw', 0.)
    uncertainty = orientation.get('uncertainty_deg')
    if not _finite_number(heading) or not _finite_number(yaw):
        return dict(valid=False, reason='Saved orientation angle is invalid')
    if uncertainty is not None and (not _finite_number(uncertainty) or uncertainty < 0):
        return dict(valid=False, reason='Saved orientation uncertainty is invalid')
    north = (90. - heading) % 360.
    reported_north = orientation.get('north_yaw_in_map_deg')
    if reported_north is not None:
        if not _finite_number(reported_north) or abs((reported_north - north + 180.) % 360. - 180.) > .001:
            return dict(valid=False, reason='Saved orientation angles disagree')
    # Raster +X is rotated by origin_yaw within the map. Screen +Y points
    # downward, so a North-up arrow rotates clockwise by heading + origin_yaw.
    return dict(
        valid=True, reference='true_north',
        map_x_heading_from_east_deg=(heading + 180.) % 360. - 180.,
        north_yaw_in_map_deg=north,
        north_rotation_in_image_deg=(heading + math.degrees(yaw)) % 360.,
        uncertainty_deg=uncertainty,
        saved_at=str(document.get('saved_at', '')),
        source=str(orientation.get('source', '')),
    )


def load_saved_orientation(map_data, db_path=None):
    """Return a validated display summary or a nonfatal unavailable reason.

    Read on each refresh, allowing a sidecar saved after database registration
    to become visible. The captured map hash, not the current on-disk image,
    determines whether the orientation belongs to the displayed snapshot.
    """
    source = map_data.get('source_yaml_path')
    if not isinstance(source, str) or not source:
        return dict(valid=False, reason='No saved map path is available')
    sidecar = Path(source).expanduser().with_suffix('.orientation.yaml')
    candidates = [sidecar]
    if db_path:
        fallback = Path(db_path).expanduser().resolve().parent / sidecar.name
        if fallback != sidecar:
            candidates.append(fallback)
    result = dict(valid=False, reason='No saved orientation file found')
    for candidate in candidates:
        try:
            document = yaml.safe_load(candidate.read_text(encoding='utf-8'))
        except FileNotFoundError:
            continue
        except (OSError, UnicodeError, yaml.YAMLError):
            result = dict(valid=False, reason='Could not read the saved orientation file')
            continue
        result = _validated_orientation(document, map_data)
        if result['valid']:
            return result
    return result
