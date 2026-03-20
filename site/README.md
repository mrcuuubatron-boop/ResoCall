# Site (Frontend)

This file contains site-specific installation and recommended libraries. All frontend setup and library recommendations live here — the repository root contains only a brief project description.

## System requirements
- Node.js (>=18 recommended)
- pnpm (recommended package manager)
- Optional: `ffmpeg` if working with audio files locally for previews

## Install Node + pnpm (Fedora example)
```bash
sudo dnf install -y nodejs npm
sudo npm install -g pnpm
```

## Install site dependencies
```bash
cd site
pnpm install
```

## Run dev server
```bash
cd site
pnpm dev
```

## Recommended frontend libraries (already in package.json)
- next
- react, react-dom
- @hookform/resolvers, react-hook-form
- @radix-ui/* (UI primitives used in the project)
- tailwindcss, @tailwindcss/postcss
- lucide-react, recharts, sonner

These libraries are frontend-only and should be managed via the `site/package.json` and installed with `pnpm`.

See `site/requirements.txt` for a concise, site-local list of required tools and the main frontend packages.

## Useful checks
```bash
cd site
pnpm -v
pnpm list --depth 0
```

## Notes
- Backend/ASR dependencies and venv setup are intentionally kept outside `site/` and are documented in their respective folders.
- If you want, I can create a small `site/start.sh` to automate `pnpm install && pnpm dev`.
