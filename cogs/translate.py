import asyncio

import aiohttp
import discord
from discord.ext import commands
from langdetect import detect


# =========================================================
# FREE MYMEMORY TRANSLATION API
# =========================================================

MYMEMORY_URL = (
    "https://api.mymemory.translated.net/get"
)


# =========================================================
# LANGUAGE CODES
# =========================================================

LANGUAGE_CODES = {
    "en": "en",
    "ko": "ko",
    "ja": "ja",
    "zh-cn": "zh-CN",
    "zh-tw": "zh-TW",
    "hi": "hi",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "it": "it",
    "pt": "pt",
    "ru": "ru",
    "ar": "ar",
    "tr": "tr",
    "nl": "nl",
    "pl": "pl",
    "uk": "uk",
    "vi": "vi",
    "id": "id",
    "th": "th",
    "bn": "bn",
    "ta": "ta",
    "te": "te",
    "mr": "mr",
    "gu": "gu",
    "pa": "pa",
    "ur": "ur",
    "ne": "ne",
    "da": "da",
    "sv": "sv",
    "no": "no",
    "fi": "fi",
    "cs": "cs",
    "el": "el",
    "ro": "ro",
    "bg": "bg",
    "hu": "hu",
    "sk": "sk",
    "sl": "sl",
    "ca": "ca",
    "he": "he",
    "iw": "he",
}


# =========================================================
# TARGET LANGUAGES
# =========================================================

TARGET_LANGUAGES = {

    # -----------------------------------------------------
    # English
    # -----------------------------------------------------

    "en": ("en", "English", "🇬🇧"),
    "english": ("en", "English", "🇬🇧"),

    # -----------------------------------------------------
    # Korean
    # -----------------------------------------------------

    "ko": ("ko", "Korean", "🇰🇷"),
    "kor": ("ko", "Korean", "🇰🇷"),
    "korean": ("ko", "Korean", "🇰🇷"),

    # -----------------------------------------------------
    # Japanese
    # -----------------------------------------------------

    "ja": ("ja", "Japanese", "🇯🇵"),
    "jpn": ("ja", "Japanese", "🇯🇵"),
    "japanese": ("ja", "Japanese", "🇯🇵"),

    # -----------------------------------------------------
    # Chinese
    # -----------------------------------------------------

    "zh": ("zh-CN", "Chinese (Simplified)", "🇨🇳"),
    "zh-cn": ("zh-CN", "Chinese (Simplified)", "🇨🇳"),
    "cn": ("zh-CN", "Chinese (Simplified)", "🇨🇳"),
    "chinese": ("zh-CN", "Chinese (Simplified)", "🇨🇳"),
    "simplified chinese": (
        "zh-CN",
        "Chinese (Simplified)",
        "🇨🇳",
    ),
    "chinese simplified": (
        "zh-CN",
        "Chinese (Simplified)",
        "🇨🇳",
    ),

    "zh-tw": (
        "zh-TW",
        "Chinese (Traditional)",
        "🇹🇼",
    ),
    "tw": (
        "zh-TW",
        "Chinese (Traditional)",
        "🇹🇼",
    ),
    "traditional chinese": (
        "zh-TW",
        "Chinese (Traditional)",
        "🇹🇼",
    ),

    # -----------------------------------------------------
    # Indian Languages
    # -----------------------------------------------------

    "hi": ("hi", "Hindi", "🇮🇳"),
    "hindi": ("hi", "Hindi", "🇮🇳"),

    "bn": ("bn", "Bengali", "🇮🇳"),
    "bengali": ("bn", "Bengali", "🇮🇳"),

    "ta": ("ta", "Tamil", "🇮🇳"),
    "tamil": ("ta", "Tamil", "🇮🇳"),

    "te": ("te", "Telugu", "🇮🇳"),
    "telugu": ("te", "Telugu", "🇮🇳"),

    "mr": ("mr", "Marathi", "🇮🇳"),
    "marathi": ("mr", "Marathi", "🇮🇳"),

    "gu": ("gu", "Gujarati", "🇮🇳"),
    "gujarati": ("gu", "Gujarati", "🇮🇳"),

    "pa": ("pa", "Punjabi", "🇮🇳"),
    "punjabi": ("pa", "Punjabi", "🇮🇳"),

    "ur": ("ur", "Urdu", "🇵🇰"),
    "urdu": ("ur", "Urdu", "🇵🇰"),

    "ne": ("ne", "Nepali", "🇳🇵"),
    "nepali": ("ne", "Nepali", "🇳🇵"),

    # -----------------------------------------------------
    # European Languages
    # -----------------------------------------------------

    "es": ("es", "Spanish", "🇪🇸"),
    "spanish": ("es", "Spanish", "🇪🇸"),

    "fr": ("fr", "French", "🇫🇷"),
    "french": ("fr", "French", "🇫🇷"),

    "de": ("de", "German", "🇩🇪"),
    "german": ("de", "German", "🇩🇪"),

    "it": ("it", "Italian", "🇮🇹"),
    "italian": ("it", "Italian", "🇮🇹"),

    "pt": ("pt", "Portuguese", "🇵🇹"),
    "portuguese": ("pt", "Portuguese", "🇵🇹"),

    "ru": ("ru", "Russian", "🇷🇺"),
    "russian": ("ru", "Russian", "🇷🇺"),

    "uk": ("uk", "Ukrainian", "🇺🇦"),
    "ukrainian": ("uk", "Ukrainian", "🇺🇦"),

    "pl": ("pl", "Polish", "🇵🇱"),
    "polish": ("pl", "Polish", "🇵🇱"),

    "nl": ("nl", "Dutch", "🇳🇱"),
    "dutch": ("nl", "Dutch", "🇳🇱"),

    "tr": ("tr", "Turkish", "🇹🇷"),
    "turkish": ("tr", "Turkish", "🇹🇷"),

    # -----------------------------------------------------
    # Middle East
    # -----------------------------------------------------

    "ar": ("ar", "Arabic", "🇸🇦"),
    "arabic": ("ar", "Arabic", "🇸🇦"),

    "he": ("he", "Hebrew", "🇮🇱"),
    "hebrew": ("he", "Hebrew", "🇮🇱"),

    # -----------------------------------------------------
    # Southeast Asia
    # -----------------------------------------------------

    "vi": ("vi", "Vietnamese", "🇻🇳"),
    "vietnamese": ("vi", "Vietnamese", "🇻🇳"),

    "id": ("id", "Indonesian", "🇮🇩"),
    "indonesian": ("id", "Indonesian", "🇮🇩"),

    "th": ("th", "Thai", "🇹🇭"),
    "thai": ("th", "Thai", "🇹🇭"),

    # -----------------------------------------------------
    # Other Languages
    # -----------------------------------------------------

    "da": ("da", "Danish", "🇩🇰"),
    "danish": ("da", "Danish", "🇩🇰"),

    "sv": ("sv", "Swedish", "🇸🇪"),
    "swedish": ("sv", "Swedish", "🇸🇪"),

    "no": ("no", "Norwegian", "🇳🇴"),
    "norwegian": ("no", "Norwegian", "🇳🇴"),

    "fi": ("fi", "Finnish", "🇫🇮"),
    "finnish": ("fi", "Finnish", "🇫🇮"),

    "cs": ("cs", "Czech", "🇨🇿"),
    "czech": ("cs", "Czech", "🇨🇿"),

    "el": ("el", "Greek", "🇬🇷"),
    "greek": ("el", "Greek", "🇬🇷"),

    "ro": ("ro", "Romanian", "🇷🇴"),
    "romanian": ("ro", "Romanian", "🇷🇴"),

    "bg": ("bg", "Bulgarian", "🇧🇬"),
    "bulgarian": ("bg", "Bulgarian", "🇧🇬"),

    "hu": ("hu", "Hungarian", "🇭🇺"),
    "hungarian": ("hu", "Hungarian", "🇭🇺"),

    "sk": ("sk", "Slovak", "🇸🇰"),
    "slovak": ("sk", "Slovak", "🇸🇰"),

    "sl": ("sl", "Slovenian", "🇸🇮"),
    "slovenian": ("sl", "Slovenian", "🇸🇮"),

    "ca": ("ca", "Catalan", "🇪🇸"),
    "catalan": ("ca", "Catalan", "🇪🇸"),
}


# =========================================================
# RESOLVE TARGET LANGUAGE
# =========================================================

def resolve_target_language(language: str):
    """
    Return:

        (service_code, display_name, flag)

    """

    normalized = " ".join(
        language.lower().strip().split()
    )

    if normalized in TARGET_LANGUAGES:
        return TARGET_LANGUAGES[normalized]

    # Allow raw two-letter language codes.
    if (
        len(normalized) == 2
        and normalized.isalpha()
    ):
        return (
            normalized,
            normalized.upper(),
            "🌐",
        )

    return None


# =========================================================
# LANGUAGE DETECTION
# =========================================================

GERMAN_WORDS = {
    "danke",
    "heute",
    "ist",
    "freitag",
    "ich",
    "du",
    "wir",
    "ihr",
    "nicht",
    "kein",
    "keine",
    "der",
    "die",
    "das",
    "und",
    "oder",
    "aber",
    "ein",
    "eine",
    "einen",
    "mit",
    "für",
    "auf",
    "von",
    "zu",
    "den",
    "dem",
    "des",
    "wie",
    "was",
    "warum",
    "bitte",
    "morgen",
    "gestern",
    "guten",
    "tag",
    "abend",
    "nacht",
}


# =========================================================
# SPANISH SHORT-TEXT DETECTION
# =========================================================

# langdetect can sometimes misidentify very short Spanish
# messages such as "Vete a dormir", so we use a small
# vocabulary safeguard before falling back to langdetect.
SPANISH_WORDS = {
    "hola",
    "adios",
    "adiós",
    "gracias",
    "por",
    "favor",
    "que",
    "qué",
    "como",
    "cómo",
    "estas",
    "estás",
    "estoy",
    "eres",
    "es",
    "son",
    "una",
    "uno",
    "el",
    "la",
    "los",
    "las",
    "de",
    "del",
    "para",
    "con",
    "sin",
    "no",
    "si",
    "sí",
    "quiero",
    "puedo",
    "puedes",
    "dormir",
    "vete",
    "ven",
    "tengo",
    "tienes",
    "muy",
    "bien",
    "mal",
}


def detect_language_for_translation(
    text: str,
):
    """
    Detect the source language.

    A small German vocabulary check is kept
    from the original system because langdetect
    can sometimes confuse short German messages.
    """

    words = {
        word.strip(
            ".,!?;:'\"()[]{}"
            "，。！？；："
        ).lower()
        for word in text.split()
    }

    words.discard("")

    german_matches = len(
        words & GERMAN_WORDS
    )

    if german_matches >= 2:
        return "de"

    # Spanish safeguard for short messages.
    spanish_matches = len(
        words & SPANISH_WORDS
    )

    if spanish_matches >= 1:
        return "es"

    return detect(text)


# =========================================================
# TRANSLATION
# =========================================================

async def translate_with_retry(
    source: str,
    target: str,
    text: str,
    attempts: int = 3,
):
    """
    Translate using MyMemory's free API.

    This uses the API directly instead of
    deep-translator, so we don't depend on
    Google's unofficial endpoint.
    """

    last_error = None

    # MyMemory expects normal language codes.
    source = LANGUAGE_CODES.get(
        source.lower(),
        source,
    )

    target = LANGUAGE_CODES.get(
        target.lower(),
        target,
    )

    # Keep Chinese regional codes.
    if source.lower() == "zh-cn":
        source = "zh-CN"

    if source.lower() == "zh-tw":
        source = "zh-TW"

    if target.lower() == "zh-cn":
        target = "zh-CN"

    if target.lower() == "zh-tw":
        target = "zh-TW"

    # If source and target are the same,
    # there is no reason to call the API.
    source_base = source.split("-")[0].lower()
    target_base = target.split("-")[0].lower()

    if source_base == target_base:
        return text

    params = {
        "q": text,
        "langpair": f"{source}|{target}",
    }

    timeout = aiohttp.ClientTimeout(
        total=20
    )

    for attempt in range(
        1,
        attempts + 1,
    ):

        try:

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    MYMEMORY_URL,
                    params=params,
                ) as response:

                    if response.status != 200:
                        raise RuntimeError(
                            f"MyMemory returned HTTP "
                            f"{response.status}"
                        )

                    data = await response.json(
                        content_type=None
                    )

            response_data = data.get(
                "responseData",
                {},
            )

            translated = response_data.get(
                "translatedText"
            )

            if (
                translated
                and translated.strip()
            ):
                return translated.strip()

            raise RuntimeError(
                "MyMemory returned an empty "
                "translation."
            )

        except Exception as error:

            last_error = error

            print(
                f"[translate] Attempt "
                f"{attempt}/{attempts} failed: "
                f"{type(error).__name__}: "
                f"{error}"
            )

            if attempt < attempts:

                await asyncio.sleep(
                    1.5 * attempt
                )

    raise last_error


# =========================================================
# TRANSLATE COG
# =========================================================

class Translate(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot,
    ):
        self.bot = bot

    # =====================================================
    # !translate
    # =====================================================

    @commands.command(
        name="translate",
    )
    @commands.cooldown(
        3,
        10,
        commands.BucketType.user,
    )
    async def translate(
        self,
        ctx: commands.Context,
        target_language: str = "en",
    ):
        """
        Translate the message being replied to.

        Examples:

            !translate

            !translate Korean

            !translate ko

            !translate Hindi

            !translate Japanese

            !translate Spanish
        """

        # -------------------------------------------------
        # Resolve target language
        # -------------------------------------------------

        target_info = resolve_target_language(
            target_language
        )

        if target_info is None:

            await ctx.send(
                "❌ I don't recognize that "
                "language.\n\n"
                "Examples:\n"
                "`!translate Korean`\n"
                "`!translate ko`\n"
                "`!translate Hindi`\n"
                "`!translate Spanish`\n"
                "`!translate Japanese`"
            )

            return

        (
            target_code,
            target_name,
            target_flag,
        ) = target_info

        # -------------------------------------------------
        # Check whether command is a reply
        # -------------------------------------------------

        if ctx.message.reference is None:

            await ctx.send(
                "🌐 **Reply to the message you "
                "want to translate.**\n\n"
                "Then use:\n"
                "`!translate` → English\n"
                "`!translate Korean`\n"
                "`!translate Hindi`\n"
                "`!translate Japanese`\n"
                "`!translate Spanish`"
            )

            return

        # -------------------------------------------------
        # Get referenced message
        # -------------------------------------------------

        try:

            referenced_message = (
                await ctx.channel.fetch_message(
                    ctx.message.reference.message_id
                )
            )

        except discord.NotFound:

            await ctx.send(
                "❌ I couldn't find the message "
                "you're replying to."
            )

            return

        except discord.HTTPException as error:

            print(
                "[translate] Discord error:",
                error,
            )

            await ctx.send(
                "❌ I couldn't access that message."
            )

            return

        # -------------------------------------------------
        # Check message content
        # -------------------------------------------------

        if not referenced_message.content:

            await ctx.send(
                "❌ That message doesn't contain "
                "any text to translate."
            )

            return

        original_text = (
            referenced_message.content.strip()
        )

        # -------------------------------------------------
        # Message length protection
        # -------------------------------------------------

        if len(original_text) > 4500:

            await ctx.send(
                "❌ That message is too long "
                "to translate."
            )

            return

        # -------------------------------------------------
        # Detect language
        # -------------------------------------------------

        try:

            detected_language = (
                detect_language_for_translation(
                    original_text
                )
            )

        except Exception as error:

            print(
                "[translate] Language detection "
                "failed:",
                error,
            )

            await ctx.send(
                "❌ I couldn't detect the language "
                "of that message."
            )

            return

        # -------------------------------------------------
        # Debug information
        # -------------------------------------------------

        print(
            "------------------------------------"
        )

        print(
            "[translate] Original:",
            original_text,
        )

        print(
            "[translate] Detected:",
            detected_language,
        )

        print(
            "[translate] Target:",
            target_name,
            target_code,
        )

        print(
            "------------------------------------"
        )

        # -------------------------------------------------
        # Translate
        # -------------------------------------------------

        async with ctx.typing():

            try:

                translated_text = (
                    await translate_with_retry(
                        source=detected_language,
                        target=target_code,
                        text=original_text,
                    )
                )

            except Exception as error:

                print(
                    "\n===================================="
                )

                print(
                    "❌ TRANSLATION ERROR"
                )

                print(
                    "===================================="
                )

                print(
                    "Original text:",
                    original_text,
                )

                print(
                    "Detected language:",
                    detected_language,
                )

                print(
                    "Target language:",
                    target_name,
                )

                print(
                    "Target code:",
                    target_code,
                )

                print(
                    "Error type:",
                    type(error).__name__,
                )

                print(
                    "Error:",
                    error,
                )

                print(
                    "====================================\n"
                )

                await ctx.send(
                    f"❌ I couldn't translate "
                    f"that message into "
                    f"**{target_name}**."
                )

                return

        # -------------------------------------------------
        # Discord message limit
        # -------------------------------------------------

        if len(translated_text) > 1900:

            translated_text = (
                translated_text[:1900]
                .rstrip()
                + "…"
            )

        # -------------------------------------------------
        # Send translation
        # -------------------------------------------------

        await ctx.send(
            translated_text
        )

    # =====================================================
    # COMMAND ERROR HANDLER
    # =====================================================

    @translate.error
    async def translate_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError,
    ):

        if isinstance(
            error,
            commands.CommandOnCooldown,
        ):

            await ctx.send(
                f"⏳ Slow down. Try again in "
                f"**{error.retry_after:.1f}s**."
            )

            return

        print(
            "[translate] Command error:",
            type(error).__name__,
            error,
        )


# =========================================================
# EXTENSION SETUP
# =========================================================

async def setup(
    bot: commands.Bot,
):

    await bot.add_cog(
        Translate(bot)
    )