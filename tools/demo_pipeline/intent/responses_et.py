from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

import requests

DEFAULT_WEATHER_LOCATION = os.getenv("KRATT_WEATHER_LOCATION", "Tallinn")
WEATHER_SESSION = requests.Session()

_HOUR_NOMINATIVE = {
    1: "üks",
    2: "kaks",
    3: "kolm",
    4: "neli",
    5: "viis",
    6: "kuus",
    7: "seitse",
    8: "kaheksa",
    9: "üheksa",
    10: "kümme",
    11: "üksteist",
    12: "kaksteist",
}

_HOUR_GENITIVE = {
    1: "ühe",
    2: "kahe",
    3: "kolme",
    4: "nelja",
    5: "viie",
    6: "kuue",
    7: "seitsme",
    8: "kaheksa",
    9: "üheksa",
    10: "kümne",
    11: "üheteistkümne",
    12: "kaheteistkümne",
}

_NUMBER_NOMINATIVE = {
    1: "üks",
    2: "kaks",
    3: "kolm",
    4: "neli",
    5: "viis",
    6: "kuus",
    7: "seitse",
    8: "kaheksa",
    9: "üheksa",
    10: "kümme",
    11: "üksteist",
    12: "kaksteist",
    13: "kolmteist",
    14: "neliteist",
    15: "viisteist",
    16: "kuusteist",
    17: "seitseteist",
    18: "kaheksateist",
    19: "üheksateist",
    20: "kakskümmend",
}

_NUMBER_GENITIVE = {
    1: "ühe",
    2: "kahe",
    3: "kolme",
    4: "nelja",
    5: "viie",
    6: "kuue",
    7: "seitsme",
    8: "kaheksa",
    9: "üheksa",
    10: "kümne",
    11: "üheteistkümne",
    12: "kaheteistkümne",
    13: "kolmeteistkümne",
    14: "neljateistkümne",
    15: "viieteistkümne",
    16: "kuueteistkümne",
    17: "seitsmeteistkümne",
    18: "kaheksateistkümne",
    19: "üheksateistkümne",
    20: "kahekümne",
}

def number_nom_et(n: int) -> str:
    if n <= 20:
        return _NUMBER_NOMINATIVE.get(n, str(n))
    if n < 30:
        return f"kakskümmend {_NUMBER_NOMINATIVE[n - 20]}"
    return str(n)

def number_gen_et(n: int) -> str:
    if n <= 20:
        return _NUMBER_GENITIVE.get(n, str(n))
    if n < 30:
        return f"kahekümne {_NUMBER_GENITIVE[n - 20]}"
    return str(n)

def natural_time_et(now: datetime | None = None) -> str:
    """Return a TTS-friendly Estonian time phrase for the supplied/current minute."""
    now = now or datetime.now().astimezone()
    hour = now.hour % 12 or 12
    minute = now.minute
    next_hour = (hour % 12) + 1

    if minute == 0:
        return f"Kell on {_HOUR_NOMINATIVE[hour]}."
    if minute == 15:
        return f"Kell on veerand {_HOUR_NOMINATIVE[next_hour]}."
    if minute == 30:
        return f"Kell on pool {_HOUR_NOMINATIVE[next_hour]}."
    if minute == 45:
        return f"Kell on kolmveerand {_HOUR_NOMINATIVE[next_hour]}."
    if minute < 30:
        minute_word = number_nom_et(minute)
        unit = "minut" if minute == 1 else "minutit"
        return f"Kell on {minute_word} {unit} üle {_HOUR_GENITIVE[hour]}."

    minutes_to_next = 60 - minute
    minute_word = number_gen_et(minutes_to_next)
    return f"Kell on {minute_word} minuti pärast {_HOUR_NOMINATIVE[next_hour]}."

def time_response_et(offset_minutes: int = 0) -> str:
    target = datetime.now().astimezone() + timedelta(minutes=offset_minutes)
    phrase = natural_time_et(target)
    if offset_minutes == 0:
        return phrase
    prefix = "Kell on "
    if phrase.startswith(prefix):
        verb = "oli" if offset_minutes < 0 else "on"
        return f"Siis {verb} kell " + phrase[len(prefix):]
    return phrase

_DATE_ORDINAL = {
    1: "esimene",
    2: "teine",
    3: "kolmas",
    4: "neljas",
    5: "viies",
    6: "kuues",
    7: "seitsmes",
    8: "kaheksas",
    9: "üheksas",
    10: "kümnes",
    11: "üheteistkümnes",
    12: "kaheteistkümnes",
    13: "kolmeteistkümnes",
    14: "neljateistkümnes",
    15: "viieteistkümnes",
    16: "kuueteistkümnes",
    17: "seitsmeteistkümnes",
    18: "kaheksateistkümnes",
    19: "üheksateistkümnes",
    20: "kahekümnes",
    21: "kahekümne esimene",
    22: "kahekümne teine",
    23: "kahekümne kolmas",
    24: "kahekümne neljas",
    25: "kahekümne viies",
    26: "kahekümne kuues",
    27: "kahekümne seitsmes",
    28: "kahekümne kaheksas",
    29: "kahekümne üheksas",
    30: "kolmekümnes",
    31: "kolmekümne esimene",
}

_MONTH_ET = {
    1: "jaanuar",
    2: "veebruar",
    3: "märts",
    4: "aprill",
    5: "mai",
    6: "juuni",
    7: "juuli",
    8: "august",
    9: "september",
    10: "oktoober",
    11: "november",
    12: "detsember",
}

_WEEKDAY_ET = {
    0: "esmaspäev",
    1: "teisipäev",
    2: "kolmapäev",
    3: "neljapäev",
    4: "reede",
    5: "laupäev",
    6: "pühapäev",
}

def natural_date_et(offset_days: int = 0, now: datetime | None = None) -> str:
    target = (now or datetime.now().astimezone()) + timedelta(days=offset_days)
    day = _DATE_ORDINAL.get(target.day, str(target.day))
    month = _MONTH_ET[target.month]
    weekday = _WEEKDAY_ET[target.weekday()]
    if offset_days == 0:
        return f"Täna on {weekday}, {day} {month}."
    return f"Siis on {weekday}, {day} {month}."

_WEATHER_CODE_ET = {
    0: "selge",
    1: "peamiselt selge",
    2: "osaliselt pilves",
    3: "pilves",
    45: "udune",
    48: "härmase uduga",
    51: "kerge uduvihm",
    53: "uduvihm",
    55: "tugev uduvihm",
    61: "kerge vihm",
    63: "vihmane",
    65: "tugev vihm",
    71: "kerge lumesadu",
    73: "lumesadu",
    75: "tugev lumesadu",
    80: "hoovihm",
    81: "tugev hoovihm",
    82: "väga tugev hoovihm",
    95: "äike",
    96: "äike ja rahe",
    99: "tugev äike ja rahe",
}

def _weather_code_et(code: int | None) -> str:
    if code is None:
        return "ilm teadmata"
    return _WEATHER_CODE_ET.get(int(code), "ilm teadmata")

def place_inessive_et(place: str) -> str:
    name = (place or "").strip()
    lower = name.lower()
    if lower == "tallinn":
        return "Tallinnas"
    if lower in ("tartu", "pärnu", "parnu", "võru", "voru"):
        return f"{name}s"
    if lower.endswith("s"):
        return name
    return f"{name}s"

def normalize_place_et(place: str | None) -> str:
    name = (place or "").strip()
    lower = name.lower()
    known = {
        "tallinnas": "Tallinn",
        "tallinn": "Tallinn",
        "tartus": "Tartu",
        "tartu": "Tartu",
        "pärnus": "Pärnu",
        "parnus": "Pärnu",
        "pärnu": "Pärnu",
        "parnu": "Pärnu",
    }
    return known.get(lower, name)

def relative_day_phrase_et(offset_days: int) -> str:
    if offset_days == 0:
        return "täna"
    if offset_days == 1:
        return "homme"
    if offset_days == 2:
        return "ülehomme"
    if offset_days == -1:
        return "eile"
    if offset_days > 0:
        return f"{offset_days} päeva pärast"
    return f"{abs(offset_days)} päeva tagasi"


def _daily_value(daily: dict[str, Any], key: str, index: int, default: Any = None) -> Any:
    values = daily.get(key) or []
    if not values or index < 0 or index >= len(values):
        return default
    value = values[index]
    return default if value is None else value


def _format_temp_range_et(temp_min: int, temp_max: int) -> str:
    if temp_min == temp_max:
        return f"{temp_max} kraadi"
    return f"{temp_min} kuni {temp_max} kraadi"


def _weather_window_limit(offset_days: int) -> str | None:
    if offset_days > 15:
        return "Saan ilmaennustust vaadata kuni 15 päeva ette."
    if offset_days < -7:
        return "Saan hiljutist ilma vaadata kuni 7 päeva tagasi."
    return None


def weather_response_et(place: str | None = None, mode: str = "current", offset_days: int = 0) -> str:
    """Fetch current weather or a relative-day forecast via Open-Meteo, no API key required."""
    place = normalize_place_et(place or DEFAULT_WEATHER_LOCATION) or DEFAULT_WEATHER_LOCATION
    mode = (mode or "current").strip().lower()
    try:
        offset_days = int(offset_days or 0)
    except (TypeError, ValueError):
        offset_days = 0

    limit_message = _weather_window_limit(offset_days)
    if limit_message:
        return limit_message

    try:
        geo = WEATHER_SESSION.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": place, "count": 1, "language": "et", "format": "json"},
            timeout=4,
        )
        geo.raise_for_status()
        results = geo.json().get("results") or []
        if not results:
            return f"Ma ei leidnud ilma asukoha {place} kohta."
        loc = results[0]
        loc_name = loc.get("name") or place
        loc_phrase = place_inessive_et(loc_name)
        forecast_days = max(1, offset_days + 1) if offset_days >= 0 else 1
        past_days = max(0, -offset_days)
        forecast_params: dict[str, Any] = {
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "current": "temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "daily": (
                "weather_code,temperature_2m_max,temperature_2m_min,"
                "apparent_temperature_max,apparent_temperature_min,"
                "precipitation_probability_max,precipitation_sum,wind_speed_10m_max"
            ),
            "forecast_days": forecast_days,
            "timezone": "auto",
        }
        if past_days:
            forecast_params["past_days"] = past_days
        forecast = WEATHER_SESSION.get(
            "https://api.open-meteo.com/v1/forecast",
            params=forecast_params,
            timeout=4,
        )
        forecast.raise_for_status()
        data = forecast.json()
        current = data.get("current") or {}
        daily = data.get("daily") or {}
        target_date = (datetime.now().astimezone().date() + timedelta(days=offset_days)).isoformat()
        dates = daily.get("time") or []
        try:
            daily_index = dates.index(target_date)
        except ValueError:
            daily_index = min(max(offset_days + past_days, 0), max(len(dates) - 1, 0))

        rain_prob_raw = _daily_value(daily, "precipitation_probability_max", daily_index)
        rain_prob = int(round(float(rain_prob_raw))) if rain_prob_raw is not None else None
        rain_mm = float(_daily_value(daily, "precipitation_sum", daily_index, 0.0) or 0.0)

        if offset_days == 0:
            temp = round(float(current.get("temperature_2m")))
            apparent = round(float(current.get("apparent_temperature", temp)))
            wind_kmh = float(current.get("wind_speed_10m", 0) or 0)
            wind_ms = round(wind_kmh / 3.6, 1)
            precipitation = float(current.get("precipitation", 0) or 0)
            description = _weather_code_et(current.get("weather_code"))

            if mode == "rain":
                if rain_prob is not None:
                    return f"{loc_phrase} on täna vihma tõenäosus umbes {rain_prob} protsenti ja sademeid {rain_mm:g} millimeetrit."
                rain_now = "Praegu sajab." if precipitation > 0 else "Praegu sademeid ei ole."
                return f"{loc_phrase}: {rain_now}"

            if mode == "clothing":
                rain_hint = rain_prob is not None and rain_prob >= 40
                if apparent <= 5:
                    advice = "Pane soe jope."
                elif apparent <= 13:
                    advice = "Pane kerge jope või paksem pusa."
                elif apparent <= 20:
                    advice = "Pusa või õhuke jakk on hea mõte."
                else:
                    advice = "Kerge riietus sobib."
                if rain_hint:
                    advice += " Võta vihmavari ka."
                return f"{loc_phrase} on {temp} kraadi, tundub nagu {apparent}. {advice}"

            rain_part = " Sajab." if precipitation > 0 else " Sademeid hetkel ei ole."
            return (
                f"{loc_phrase} on {temp} kraadi ja {description}. "
                f"Tundub nagu {apparent}. Tuul {wind_ms:g} meetrit sekundis."
                f"{rain_part}"
            )

        day_phrase = relative_day_phrase_et(offset_days)
        verb = "oli" if offset_days < 0 else "on"
        temp_max = round(float(_daily_value(daily, "temperature_2m_max", daily_index, 0)))
        temp_min = round(float(_daily_value(daily, "temperature_2m_min", daily_index, temp_max)))
        apparent_max = round(float(_daily_value(daily, "apparent_temperature_max", daily_index, temp_max)))
        apparent_min = round(float(_daily_value(daily, "apparent_temperature_min", daily_index, temp_min)))
        wind_kmh = float(_daily_value(daily, "wind_speed_10m_max", daily_index, 0) or 0)
        wind_ms = round(wind_kmh / 3.6, 1)
        description = _weather_code_et(_daily_value(daily, "weather_code", daily_index))
        temp_range = _format_temp_range_et(temp_min, temp_max)
        apparent_range = _format_temp_range_et(apparent_min, apparent_max)

        if mode == "rain":
            if rain_prob is not None:
                return f"{loc_phrase} {verb} {day_phrase} vihma tõenäosus umbes {rain_prob} protsenti ja sademeid {rain_mm:g} millimeetrit."
            return f"{loc_phrase} {verb} {day_phrase} sademeid umbes {rain_mm:g} millimeetrit."

        if mode == "clothing":
            rain_hint = rain_prob is not None and rain_prob >= 40
            if apparent_max <= 5:
                advice = "Soe jope sobib."
            elif apparent_max <= 13:
                advice = "Kerge jope või paksem pusa sobib."
            elif apparent_max <= 20:
                advice = "Pusa või õhuke jakk on hea mõte."
            else:
                advice = "Kerge riietus sobib."
            if apparent_min <= 5 and apparent_max > 5:
                advice += " Jahedamaks osaks võta lisakiht."
            if rain_hint:
                advice += " Vihmavari tasub kaasa võtta."
            return f"{loc_phrase} {verb} {day_phrase} {temp_range}, tundub nagu {apparent_range}. {advice}"

        rain_part = ""
        if rain_prob is not None:
            rain_part = f" Vihma tõenäosus umbes {rain_prob} protsenti."
        elif rain_mm > 0:
            rain_part = f" Sademeid umbes {rain_mm:g} millimeetrit."
        return (
            f"{loc_phrase} {verb} {day_phrase} {temp_range} ja {description}. "
            f"Tuul kuni {wind_ms:g} meetrit sekundis."
            f"{rain_part}"
        )
    except Exception:
        return "Ilmateadet ei saanud praegu kätte."

def demo_response_for_action(action_name: str, action: dict[str, Any] | None = None) -> str:
    action = action or {}
    if action_name == "turn_off":
        return "Tuli on kustutatud."
    if action_name == "turn_on":
        return "Tuli põleb."
    if action_name == "set_color":
        color = str(action.get("color", "")).strip()
        return f"Tuli on {color}." if color else "Värv muudetud."
    if action_name == "set_brightness":
        return "Heledus muudetud."
    if action_name == "get_state":
        return "Vaatan olekut."
    if action_name == "list_devices":
        return "Vaatan seadmeid."
    if action_name == "get_capabilities":
        return "Ma oskan lampi juhtida, ilma ja kellaaega öelda ning üldküsimuste jaoks abi küsida."
    if action_name == "run_effect":
        effect = str(action.get("effect", "")).strip()
        if effect == "disco":
            return "Teen diskot."
        if effect == "color_cycle":
            return "Näitan värve."
        if effect == "pulse":
            return "Vilgutan tuld."
    return "Tehtud."
