# Panel export CI

Every PR and default-branch push validates the repository's 253 panel exports,
all tracked JSON/YAML data, unique JSON keys, required export fields, environment
variable uniqueness and embedded installation-script syntax. The validator accepts
the actual PTDL/PLCN versions present here, including native Pelican YAML. It is a
focused repository contract, not a replacement for a real panel import test.

Run `uv run --no-project --with-requirements .github/requirements.txt python .github/scripts/check-eggs.py`
locally with Python, uv 0.12.10, Bash and BusyBox. PyYAML is versioned in the CI
requirements file and maintained by Renovate. Embedded CRLF is normalized exactly
as Wings does before execution; Bash parses with extglob enabled, and ash scripts
use BusyBox ash. Parsing never downloads or installs a game server.

The shared `ci / required` gate rejects failed, cancelled, missing or skipped
prerequisites and checks explicit PR dispatch identities before and after checks.
Tokens are read-only and action references use full version tags. Shared changes
arrive as version updates from `engels74/automation`; repository checks remain
local so panel-specific behavior can evolve independently.

No application formatter or fake test suite is imposed on panel-generated data.
Real panel imports, container availability and game-server installation/startup
remain manual checks. Generated export corrections must also be reflected in the
source panel to survive re-export. Upstream paths and container choices remain
unchanged by CI adoption.

Require strict up-to-date `ci / required` from GitHub Actions on the configured
default branch, enforce administrators, prohibit force pushes/deletions and use
zero mandatory reviews. Renovate inherits the versioned shared base preset;
automerge remains off until protection and shared-policy readiness are verified.

The baseline removes a duplicate WINDOWS_INSTALL variable from both Mordhau
exports, retaining the existing required fixed value of 1. Fork processing is
explicitly enabled for dependency maintenance.
