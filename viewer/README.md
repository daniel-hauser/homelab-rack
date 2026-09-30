# Homelab Rack 3D Viewer

Focused Vite + TypeScript + Three.js viewer for the validated ten-part homelab
rack production set. Dependencies and STL assets are local; the deployed site
makes no CDN requests.

## Local development

```powershell
npm ci
npm run dev
```

Production build:

```powershell
npm run build
```

The output is written to `dist`. Vite uses `base: "./"`, so scripts, images, and models resolve beneath any GitHub Pages repository subpath.

## GitHub Pages integration

The repository workflow at `.github/workflows/pages.yml` builds this directory
with Node 22 and publishes `viewer/dist` through GitHub's OIDC-backed Pages
deployment. It uses no repository secrets.

No repository name or fixed `/repo/` base path is embedded. Relative Vite paths
allow the site to run at `https://daniel-hauser.github.io/homelab-rack/`.

## Production data

- Printer: Bambu Lab A1, 0.4 mm nozzle
- Profile: 0.20 mm layers, four walls, five top/bottom layers, 20% gyroid
- Supports/brim/skirt: none
- Candidate total: 538.12 g, 180.42200 m, 433.96577 cm³, 23h24m33s
- Magnets: universal 6 × 2 mm discs
- Module depth: 150 mm

Dimensions shown in the viewer are calculated STL bounding boxes. Release
totals are loaded from `public/estimate.json`, which `..\export.ps1`
synchronizes with `slicer/release/estimate.json`.
