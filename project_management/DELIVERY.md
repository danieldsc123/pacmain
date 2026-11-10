# Platform delivery

Status: uploaded to Itch.io with restricted access; cross-machine validation
remains incomplete.

Project URL: https://danda-si.itch.io/pacman-42
Reviewer access: password configured on Itch.io; share separately.

Artifact: `dist/pac-man-native.zip` after `make package`.
Target: native build for the OS on which packaging is executed.

Before submission, upload a tested build to a free restricted/unlisted game page,
then record the platform URL, target OS, upload date, build checksum and reviewer
access instructions here. Account credentials must not be committed.

## Build prepared on 2026-11-09

- Platform: Linux native.
- Archive: `dist/pac-man-native.zip` (approximately 25 MB).
- SHA-256: `7d6a8ca36b6decb91b42060573f26acb080e853af9a2d9776d520984568d83f0`.
- Included configuration: level time 130 seconds, player speed 6, ghost speed 2.
- Checks: flake8, mypy and six acceptance tests passed. ZIP integrity and
  extracted executable usage handling passed.
- Historical build record: this archive was prepared before the later
  configuration change to 200 seconds.
- Platform upload subsequently completed; the user reports that the downloaded
  game opens on their machine. A full gameplay acceptance run is not confirmed.
- The user reports a launch failure on a friend's machine; OS and error output
  are still needed to diagnose it. Cross-machine compatibility remains pending.
- Page text and upload checklist: [ITCH_PAGE.md](ITCH_PAGE.md).
