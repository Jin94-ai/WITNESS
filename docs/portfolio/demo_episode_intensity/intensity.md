# Phase 3.1 Episode Intensity — 회차 단위 장르 시그니처

> **🧪 Fictional fixture-only demo** — 이 demo는 `tests/fixtures/annotation_public_safe/`의 *가공된 가상 인물* 5 episode × 2 annotators 기반이며 실제 방송 회차 데이터가 아니다. Operating Guide §9 deploy 카테고리: `fixture-only`.

> **schema**: `episode_intensity_v1`  
> **n_records**: 10 / **n_genres**: 2  
> **kept_features_used** (4): cliffhanger_strength, conflict_intensity_peak, relationship_pressure, silence_or_avoidance
> **model**: weighted_rule_score (trained=False, data_source=phase3_pilot)
> **audit**: raw_text_used=False / evidence_preserved=True

---

## Title × Genre 별 Episode Arc

### `km_titleA` × `japanese_quiet_drama`

- arc: 0.625 → 0.750 → 0.750 → 0.850 → 0.900
- fit: moderate_fit · strong_fit · strong_fit · strong_fit · strong_fit

### `km_titleA` × `korean_morning_melodrama`

- arc: 0.625 → 0.750 → 0.750 → 0.850 → 0.900
- fit: moderate_fit · strong_fit · strong_fit · strong_fit · strong_fit

### `km_titleB` × `japanese_quiet_drama`

- arc: 0.575 → 0.600 → 0.700 → 0.700 → 0.675
- fit: moderate_fit · moderate_fit · strong_fit · strong_fit · moderate_fit

### `km_titleB` × `korean_morning_melodrama`

- arc: 0.575 → 0.600 → 0.700 → 0.700 → 0.675
- fit: moderate_fit · moderate_fit · strong_fit · strong_fit · moderate_fit

---

## 전체 Intensity Matrix

| record | genre | intensity | fit | top contribution |
|---|---|---|---|---|
| `km_titleA_ep001` | `korean_morning_melodrama` | 0.625 | moderate_fit | silence_or_avoidance |
| `km_titleA_ep001` | `japanese_quiet_drama` | 0.625 | moderate_fit | silence_or_avoidance |
| `km_titleA_ep002` | `korean_morning_melodrama` | 0.750 | strong_fit | silence_or_avoidance |
| `km_titleA_ep002` | `japanese_quiet_drama` | 0.750 | strong_fit | silence_or_avoidance |
| `km_titleA_ep003` | `korean_morning_melodrama` | 0.750 | strong_fit | silence_or_avoidance |
| `km_titleA_ep003` | `japanese_quiet_drama` | 0.750 | strong_fit | silence_or_avoidance |
| `km_titleA_ep004` | `korean_morning_melodrama` | 0.850 | strong_fit | cliffhanger_strength |
| `km_titleA_ep004` | `japanese_quiet_drama` | 0.850 | strong_fit | cliffhanger_strength |
| `km_titleA_ep005` | `korean_morning_melodrama` | 0.900 | strong_fit | conflict_intensity_peak |
| `km_titleA_ep005` | `japanese_quiet_drama` | 0.900 | strong_fit | conflict_intensity_peak |
| `km_titleB_ep001` | `korean_morning_melodrama` | 0.575 | moderate_fit | silence_or_avoidance |
| `km_titleB_ep001` | `japanese_quiet_drama` | 0.575 | moderate_fit | silence_or_avoidance |
| `km_titleB_ep002` | `korean_morning_melodrama` | 0.600 | moderate_fit | cliffhanger_strength |
| `km_titleB_ep002` | `japanese_quiet_drama` | 0.600 | moderate_fit | cliffhanger_strength |
| `km_titleB_ep003` | `korean_morning_melodrama` | 0.700 | strong_fit | silence_or_avoidance |
| `km_titleB_ep003` | `japanese_quiet_drama` | 0.700 | strong_fit | silence_or_avoidance |
| `km_titleB_ep004` | `korean_morning_melodrama` | 0.700 | strong_fit | conflict_intensity_peak |
| `km_titleB_ep004` | `japanese_quiet_drama` | 0.700 | strong_fit | conflict_intensity_peak |
| `km_titleB_ep005` | `korean_morning_melodrama` | 0.675 | moderate_fit | silence_or_avoidance |
| `km_titleB_ep005` | `japanese_quiet_drama` | 0.675 | moderate_fit | silence_or_avoidance |

---

## Audit

- raw_text_used: `False`
- evidence_preserved: `True`
- model_trained: `False`
- model_type: `weighted_rule_score`
- data_source: `phase3_pilot`
