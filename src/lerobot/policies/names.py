"""Canonical policy names."""

TBOT_SA1 = "TBot_SA1"
TBOT_SA1_WAN = "TBot_SA1_Wan"

TBOT_SA1_LEGACY_ALIASES = frozenset()
TBOT_SA1_WAN_LEGACY_ALIASES = frozenset()

TBOT_SA1_ALIASES = frozenset({TBOT_SA1, "tbot_sa1"})
TBOT_SA1_WAN_ALIASES = frozenset({TBOT_SA1_WAN, "tbot_sa1_wan"})

_LOGGED_LEGACY_POLICY_TYPES: set[str] = set()


def is_tbot_sa1(policy_type: str | None) -> bool:
    return policy_type in TBOT_SA1_ALIASES


def is_tbot_sa1_wan(policy_type: str | None) -> bool:
    return policy_type in TBOT_SA1_WAN_ALIASES


def legacy_policy_target(policy_type: str | None) -> str | None:
    return None


def log_legacy_policy_name(policy_type: str | None) -> None:
    return


def canonical_policy_type(policy_type: str | None) -> str | None:
    if is_tbot_sa1(policy_type):
        log_legacy_policy_name(policy_type)
        return TBOT_SA1
    if is_tbot_sa1_wan(policy_type):
        log_legacy_policy_name(policy_type)
        return TBOT_SA1_WAN
    return policy_type
