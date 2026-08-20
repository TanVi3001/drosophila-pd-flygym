"""Declarative parameter-space definitions for future calibration methods."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Any, Callable, Iterable, Mapping


class ParameterSpaceError(ValueError):
    """Raised when a parameter-space declaration is invalid."""


@dataclass(frozen=True)
class ParameterDefinition:
    """One continuous, discrete, or categorical parameter."""

    name: str
    kind: str
    bounds: tuple[float, float] | None = None
    values: tuple[Any, ...] = ()
    default: Any = None

    def __post_init__(self) -> None:
        if not str(self.name).strip():
            raise ParameterSpaceError("Parameter names must be non-empty.")
        if self.kind not in {"continuous", "discrete", "categorical"}:
            raise ParameterSpaceError(
                "Parameter kind must be continuous, discrete, or categorical."
            )
        if self.kind == "continuous":
            if self.bounds is None or len(self.bounds) != 2:
                raise ParameterSpaceError(f"{self.name}: continuous parameters need bounds.")
            lower, upper = map(float, self.bounds)
            if not all(math.isfinite(item) for item in (lower, upper)) or lower > upper:
                raise ParameterSpaceError(f"{self.name}: invalid finite bounds.")
            object.__setattr__(self, "bounds", (lower, upper))
        elif not self.values:
            raise ParameterSpaceError(f"{self.name}: discrete/categorical values are required.")
        if self.default is not None and not self.contains(self.default):
            raise ParameterSpaceError(f"{self.name}: default is outside the declaration.")

    def contains(self, value: Any) -> bool:
        if self.kind == "continuous":
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                return False
            assert self.bounds is not None
            return math.isfinite(numeric) and self.bounds[0] <= numeric <= self.bounds[1]
        return value in self.values

    def sample(self, rng: random.Random) -> Any:
        if self.kind == "continuous":
            assert self.bounds is not None
            return rng.uniform(*self.bounds)
        return rng.choice(self.values)

    def to_mapping(self) -> dict[str, Any]:
        result: dict[str, Any] = {"name": self.name, "kind": self.kind}
        if self.bounds is not None:
            result["bounds"] = list(self.bounds)
        if self.values:
            result["values"] = list(self.values)
        if self.default is not None:
            result["default"] = self.default
        return result


class ParameterSpace:
    """Validated parameter declarations with deterministic sampling."""

    def __init__(
        self,
        definitions: Iterable[ParameterDefinition],
        *,
        constraints: Iterable[Callable[[Mapping[str, Any]], bool]] = (),
    ) -> None:
        self.definitions = tuple(definitions)
        names = [item.name for item in self.definitions]
        if len(names) != len(set(names)):
            raise ParameterSpaceError("Parameter names must be unique.")
        self.constraints = tuple(constraints)

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Mapping[str, Any]]) -> "ParameterSpace":
        definitions = []
        for name, data in mapping.items():
            if not isinstance(data, Mapping):
                raise ParameterSpaceError(f"Parameter {name!r} must be a mapping.")
            bounds = data.get("bounds")
            definitions.append(
                ParameterDefinition(
                    name=str(name),
                    kind=str(data.get("kind", "continuous")),
                    bounds=None if bounds is None else tuple(bounds),
                    values=tuple(data.get("values", ())),
                    default=data.get("default"),
                )
            )
        return cls(definitions)

    def validate(self, parameters: Mapping[str, Any]) -> dict[str, Any]:
        expected = {item.name for item in self.definitions}
        actual = set(parameters)
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        errors = [f"missing parameters: {missing}" if missing else ""]
        errors.append(f"unknown parameters: {unknown}" if unknown else "")
        for definition in self.definitions:
            if definition.name in parameters and not definition.contains(parameters[definition.name]):
                errors.append(f"{definition.name} is outside its declaration")
        candidate = dict(parameters)
        for constraint in self.constraints:
            try:
                passed = bool(constraint(candidate))
            except Exception as error:  # noqa: BLE001 - report invalid constraints
                errors.append(f"constraint raised {type(error).__name__}: {error}")
            else:
                if not passed:
                    errors.append("constraint rejected candidate")
        clean_errors = [error for error in errors if error]
        return {"valid": not clean_errors, "errors": clean_errors}

    def defaults(self) -> dict[str, Any]:
        missing = [item.name for item in self.definitions if item.default is None]
        if missing:
            raise ParameterSpaceError(f"Defaults are missing for: {missing}")
        return {item.name: item.default for item in self.definitions}

    def sample(self, count: int, *, random_seed: int = 0) -> tuple[dict[str, Any], ...]:
        if count < 0:
            raise ParameterSpaceError("count must be non-negative.")
        rng = random.Random(random_seed)
        samples: list[dict[str, Any]] = []
        attempts = 0
        while len(samples) < count and attempts < max(100, count * 100):
            attempts += 1
            candidate = {item.name: item.sample(rng) for item in self.definitions}
            if self.validate(candidate)["valid"]:
                samples.append(candidate)
        if len(samples) != count:
            raise ParameterSpaceError("Could not satisfy constraints for requested samples.")
        return tuple(samples)

    def grid(self) -> tuple[dict[str, Any], ...]:
        """Return a finite grid for discrete/categorical declarations only."""

        import itertools

        if any(item.kind == "continuous" for item in self.definitions):
            raise ParameterSpaceError("A continuous parameter needs an explicit grid.")
        candidates = []
        for values in itertools.product(*(item.values for item in self.definitions)):
            candidate = {item.name: value for item, value in zip(self.definitions, values)}
            if self.validate(candidate)["valid"]:
                candidates.append(candidate)
        return tuple(candidates)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "parameters": [item.to_mapping() for item in self.definitions],
            "constraint_count": len(self.constraints),
        }


__all__ = ["ParameterDefinition", "ParameterSpace", "ParameterSpaceError"]
