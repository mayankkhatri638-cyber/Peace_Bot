import sqlite3
from pathlib import Path


# ============================================================
# DATABASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "pfp.db"


# ============================================================
# PFP CONSTANTS
# ============================================================

CLAN_RANKS = {
    "Peace Leader",
    "Co-Leader",
    "Captain",
    "Peace Chief",
}

DIVISION_RANKS = {
    "Squad Leader",
    "Vice Leader",
    "Member",
}

ALL_RANKS = CLAN_RANKS | DIVISION_RANKS

DIVISIONS = {
    "Peacekeepers",
    "Harmony",
    "Serenity",
    "Silent Diplomats",
    "Zenith",
}

ROSTER_TYPES = {
    "discord",
    "non_discord",
}


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    with get_connection() as connection:

        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                discord_id INTEGER UNIQUE,

                discord_username TEXT,
                discord_nickname TEXT,

                roblox_username TEXT NOT NULL,
                roblox_ign TEXT NOT NULL,

                rank TEXT NOT NULL,

                roster_type TEXT NOT NULL
                    CHECK (
                        roster_type IN (
                            'discord',
                            'non_discord'
                        )
                    ),

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS division_members (
                member_id INTEGER PRIMARY KEY,

                division TEXT NOT NULL,

                FOREIGN KEY (member_id)
                    REFERENCES members(id)
                    ON DELETE CASCADE
            );


            CREATE INDEX IF NOT EXISTS idx_members_discord_id
            ON members(discord_id);


            CREATE INDEX IF NOT EXISTS idx_members_roster_type
            ON members(roster_type);


            CREATE INDEX IF NOT EXISTS idx_members_rank
            ON members(rank);


            CREATE INDEX IF NOT EXISTS idx_members_roblox_username
            ON members(roblox_username);


            CREATE INDEX IF NOT EXISTS idx_division_members_division
            ON division_members(division);
            """
        )


# ============================================================
# VALIDATION
# ============================================================

def validate_member_data(
    roster_type,
    rank=None,
    division=None,
    discord_id=None,
    roblox_username=None,
    roblox_ign=None,
):

    if roster_type not in ROSTER_TYPES:
        raise ValueError(
            "Roster type must be 'discord' or 'non_discord'."
        )

    if not roblox_username:
        raise ValueError(
            "Roblox username is required."
        )

    if not roblox_ign:
        raise ValueError(
            "Roblox IGN is required."
        )

    # --------------------------------------------------------
    # NON-DISCORD
    # --------------------------------------------------------

    if roster_type == "non_discord":

        if discord_id is not None:
            raise ValueError(
                "A non-Discord member cannot have a Discord ID."
            )

        if rank != "Member":
            raise ValueError(
                "Non-Discord members must have the rank 'Member'."
            )

        if division is not None:
            raise ValueError(
                "Non-Discord members cannot have a division."
            )

        return

    # --------------------------------------------------------
    # DISCORD
    # --------------------------------------------------------

    if roster_type == "discord":

        if discord_id is None:
            raise ValueError(
                "A Discord member must have a Discord ID."
            )

        if rank not in ALL_RANKS:
            raise ValueError(
                "Invalid PFP rank."
            )

        # Clan-level ranks MUST NOT have a division
        if rank in CLAN_RANKS:

            if division is not None:
                raise ValueError(
                    f"{rank} cannot have a division."
                )

        # Division-level ranks MUST have a division
        elif rank in DIVISION_RANKS:

            if division not in DIVISIONS:
                raise ValueError(
                    "A valid division is required for this rank."
                )


# ============================================================
# ADD MEMBER
# ============================================================

def add_member(
    roster_type,
    roblox_username,
    roblox_ign,
    rank=None,
    division=None,
    discord_id=None,
    discord_username=None,
    discord_nickname=None,
):

    # Non-Discord members are ALWAYS Member
    if roster_type == "non_discord":
        rank = "Member"
        division = None

        discord_id = None
        discord_username = None
        discord_nickname = None

    validate_member_data(
        roster_type=roster_type,
        rank=rank,
        division=division,
        discord_id=discord_id,
        roblox_username=roblox_username,
        roblox_ign=roblox_ign,
    )

    with get_connection() as connection:

        # ----------------------------------------------------
        # Check Discord duplicate
        # ----------------------------------------------------

        if discord_id is not None:

            existing = connection.execute(
                """
                SELECT id
                FROM members
                WHERE discord_id = ?
                """,
                (discord_id,),
            ).fetchone()

            if existing:
                raise ValueError(
                    "This Discord member is already registered."
                )

        # ----------------------------------------------------
        # Check Non-Discord duplicate
        # ----------------------------------------------------

        if roster_type == "non_discord":

            existing = connection.execute(
                """
                SELECT id
                FROM members
                WHERE LOWER(roblox_username) = LOWER(?)
                AND roster_type = 'non_discord'
                """,
                (roblox_username,),
            ).fetchone()

            if existing:
                raise ValueError(
                    "This Non-Discord member is already registered."
                )

        # ----------------------------------------------------
        # Division leadership limit
        # ----------------------------------------------------

        if rank in {"Squad Leader", "Vice Leader"}:

            existing_leader = connection.execute(
                """
                SELECT m.id
                FROM members m
                INNER JOIN division_members d
                    ON m.id = d.member_id
                WHERE m.rank = ?
                AND d.division = ?
                """,
                (rank, division),
            ).fetchone()

            if existing_leader:
                raise ValueError(
                    f"{division} already has a {rank}."
                )

        # ----------------------------------------------------
        # Insert member
        # ----------------------------------------------------

        cursor = connection.execute(
            """
            INSERT INTO members (
                discord_id,
                discord_username,
                discord_nickname,
                roblox_username,
                roblox_ign,
                rank,
                roster_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                discord_id,
                discord_username,
                discord_nickname,
                roblox_username,
                roblox_ign,
                rank,
                roster_type,
            ),
        )

        member_id = cursor.lastrowid

        # ----------------------------------------------------
        # Add division if needed
        # ----------------------------------------------------

        if division is not None:

            connection.execute(
                """
                INSERT INTO division_members (
                    member_id,
                    division
                )
                VALUES (?, ?)
                """,
                (
                    member_id,
                    division,
                ),
            )

        return member_id


# ============================================================
# GET MEMBER BY ID
# ============================================================

def get_member_by_id(member_id):

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT
                m.*,
                d.division
            FROM members m
            LEFT JOIN division_members d
                ON m.id = d.member_id
            WHERE m.id = ?
            """,
            (member_id,),
        ).fetchone()

        return dict(row) if row else None


# ============================================================
# GET MEMBER BY DISCORD ID
# ============================================================

def get_member_by_discord_id(discord_id):

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT
                m.*,
                d.division
            FROM members m
            LEFT JOIN division_members d
                ON m.id = d.member_id
            WHERE m.discord_id = ?
            AND m.roster_type = 'discord'
            """,
            (discord_id,),
        ).fetchone()

        return dict(row) if row else None


# ============================================================
# GET MEMBER BY ROBLOX USERNAME
# ============================================================

def get_member_by_roblox_username(roblox_username):

    if not roblox_username:
        return None

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT
                m.*,
                d.division
            FROM members m
            LEFT JOIN division_members d
                ON m.id = d.member_id
            WHERE LOWER(m.roblox_username) = LOWER(?)
            AND m.roster_type = 'non_discord'
            LIMIT 1
            """,
            (roblox_username,),
        ).fetchone()

        return dict(row) if row else None


# ============================================================
# GET ALL DISCORD MEMBERS
# ============================================================

def get_discord_members():

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                m.*,
                d.division
            FROM members m
            LEFT JOIN division_members d
                ON m.id = d.member_id
            WHERE m.roster_type = 'discord'
            ORDER BY
                CASE m.rank
                    WHEN 'Peace Leader' THEN 1
                    WHEN 'Co-Leader' THEN 2
                    WHEN 'Captain' THEN 3
                    WHEN 'Peace Chief' THEN 4
                    WHEN 'Squad Leader' THEN 5
                    WHEN 'Vice Leader' THEN 6
                    WHEN 'Member' THEN 7
                    ELSE 99
                END,
                m.roblox_username
            """
        ).fetchall()

        return [dict(row) for row in rows]


# ============================================================
# GET ALL NON-DISCORD MEMBERS
# ============================================================

def get_non_discord_members():

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                m.*,
                NULL AS division
            FROM members m
            WHERE m.roster_type = 'non_discord'
            ORDER BY m.roblox_username
            """
        ).fetchall()

        return [dict(row) for row in rows]


# ============================================================
# GET ALL MEMBERS
# ============================================================

def get_all_members():

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                m.*,
                d.division
            FROM members m
            LEFT JOIN division_members d
                ON m.id = d.member_id
            ORDER BY m.id
            """
        ).fetchall()

        return [dict(row) for row in rows]


# ============================================================
# GET MEMBERS BY DIVISION
# ============================================================

def get_members_by_division(division):

    if division not in DIVISIONS:
        raise ValueError("Invalid division.")

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                m.*,
                d.division
            FROM members m
            INNER JOIN division_members d
                ON m.id = d.member_id
            WHERE d.division = ?
            ORDER BY
                CASE m.rank
                    WHEN 'Squad Leader' THEN 1
                    WHEN 'Vice Leader' THEN 2
                    WHEN 'Member' THEN 3
                    ELSE 99
                END,
                m.roblox_username
            """,
            (division,),
        ).fetchall()

        return [dict(row) for row in rows]


# ============================================================
# UPDATE MEMBER
# ============================================================

def update_member(
    member_id,
    roblox_username=None,
    roblox_ign=None,
    rank=None,
    division=None,
    discord_username=None,
    discord_nickname=None,
):

    with get_connection() as connection:

        member = connection.execute(
            """
            SELECT *
            FROM members
            WHERE id = ?
            """,
            (member_id,),
        ).fetchone()

        if not member:
            raise ValueError("Member not found.")

        member = dict(member)

        # ====================================================
        # NON-DISCORD
        # ====================================================

        if member["roster_type"] == "non_discord":

            # Non-Discord members are permanently:
            # Rank = Member
            # Division = None

            if rank is not None and rank != "Member":
                raise ValueError(
                    "Non-Discord members must have the rank 'Member'."
                )

            if division is not None:
                raise ValueError(
                    "Non-Discord members cannot have a division."
                )

            new_roblox_username = (
                roblox_username
                if roblox_username is not None
                else member["roblox_username"]
            )

            new_roblox_ign = (
                roblox_ign
                if roblox_ign is not None
                else member["roblox_ign"]
            )

            connection.execute(
                """
                UPDATE members
                SET
                    roblox_username = ?,
                    roblox_ign = ?,
                    rank = 'Member',
                    discord_username = NULL,
                    discord_nickname = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    new_roblox_username,
                    new_roblox_ign,
                    member_id,
                ),
            )

            return

        # ====================================================
        # DISCORD
        # ====================================================

        new_rank = (
            rank
            if rank is not None
            else member["rank"]
        )

        # ----------------------------------------------------
        # Determine new division
        # ----------------------------------------------------

        current_division_row = connection.execute(
            """
            SELECT division
            FROM division_members
            WHERE member_id = ?
            """,
            (member_id,),
        ).fetchone()

        current_division = (
            current_division_row["division"]
            if current_division_row
            else None
        )

        new_division = (
            division
            if division is not None
            else current_division
        )

        # ----------------------------------------------------
        # Validate rank/division combination
        # ----------------------------------------------------

        if new_rank not in ALL_RANKS:
            raise ValueError("Invalid PFP rank.")

        if new_rank in CLAN_RANKS:

            new_division = None

        elif new_rank in DIVISION_RANKS:

            if new_division not in DIVISIONS:
                raise ValueError(
                    "A valid division is required."
                )

        # ----------------------------------------------------
        # Check division leadership limit
        # ----------------------------------------------------

        if new_rank in {"Squad Leader", "Vice Leader"}:

            existing = connection.execute(
                """
                SELECT m.id
                FROM members m
                INNER JOIN division_members d
                    ON m.id = d.member_id
                WHERE m.rank = ?
                AND d.division = ?
                AND m.id != ?
                """,
                (
                    new_rank,
                    new_division,
                    member_id,
                ),
            ).fetchone()

            if existing:
                raise ValueError(
                    f"{new_division} already has a {new_rank}."
                )

        # ----------------------------------------------------
        # Update main member data
        # ----------------------------------------------------

        connection.execute(
            """
            UPDATE members
            SET
                roblox_username = ?,
                roblox_ign = ?,
                rank = ?,
                discord_username = ?,
                discord_nickname = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                roblox_username
                if roblox_username is not None
                else member["roblox_username"],

                roblox_ign
                if roblox_ign is not None
                else member["roblox_ign"],

                new_rank,

                discord_username
                if discord_username is not None
                else member["discord_username"],

                discord_nickname
                if discord_nickname is not None
                else member["discord_nickname"],

                member_id,
            ),
        )

        # ----------------------------------------------------
        # Update division
        # ----------------------------------------------------

        connection.execute(
            """
            DELETE FROM division_members
            WHERE member_id = ?
            """,
            (member_id,),
        )

        if new_division is not None:

            connection.execute(
                """
                INSERT INTO division_members (
                    member_id,
                    division
                )
                VALUES (?, ?)
                """,
                (
                    member_id,
                    new_division,
                ),
            )


# ============================================================
# UPDATE DISCORD INFORMATION
# ============================================================

def update_discord_info(
    discord_id,
    discord_username,
    discord_nickname,
):

    with get_connection() as connection:

        connection.execute(
            """
            UPDATE members
            SET
                discord_username = ?,
                discord_nickname = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE discord_id = ?
            AND roster_type = 'discord'
            """,
            (
                discord_username,
                discord_nickname,
                discord_id,
            ),
        )


# ============================================================
# REMOVE MEMBER
# ============================================================

def remove_member(member_id):

    with get_connection() as connection:

        cursor = connection.execute(
            """
            DELETE FROM members
            WHERE id = ?
            """,
            (member_id,),
        )

        return cursor.rowcount > 0


# ============================================================
# REMOVE MEMBER BY DISCORD ID
# ============================================================

def remove_member_by_discord_id(discord_id):

    with get_connection() as connection:

        cursor = connection.execute(
            """
            DELETE FROM members
            WHERE discord_id = ?
            AND roster_type = 'discord'
            """,
            (discord_id,),
        )

        return cursor.rowcount > 0


# ============================================================
# CHECK PFP MEMBERSHIP
# ============================================================

def is_pfp_member(discord_id):

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT id
            FROM members
            WHERE discord_id = ?
            AND roster_type = 'discord'
            """,
            (discord_id,),
        ).fetchone()

        return row is not None


# ============================================================
# CLOSE / RESET DATABASE
# ============================================================

def delete_database():

    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()