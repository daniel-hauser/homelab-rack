// SPDX-License-Identifier: MIT

import "./style.css";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import { models, type RackModel } from "./models";

const base = import.meta.env.BASE_URL;

document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
  <main class="viewer-app" id="viewer">
    <header class="toolbar">
      <div class="title">
        <span class="mark" aria-hidden="true">HR</span>
        <h1>Homelab rack</h1>
      </div>

      <label class="model-picker" for="model-select">
        <span>Model</span>
        <select id="model-select">
          <option value="assembly" selected>Full rack assembly</option>
          ${models.filter((model) => !model.assemblyOnly).map((model) => `<option value="${model.id}">${model.label}</option>`).join("")}
        </select>
      </label>

      <div class="controls" aria-label="Viewer controls">
        <button id="reset-view" type="button" title="Reset view (R)">Reset</button>
        <button id="auto-rotate" type="button" aria-pressed="false" title="Toggle auto-rotate (A)">Auto-rotate</button>
        <button id="explode" type="button" aria-pressed="false" title="Toggle exploded view (E)">Explode</button>
        <button id="wireframe" type="button" aria-pressed="false" title="Toggle wireframe (W)">Wireframe</button>
      </div>
    </header>

    <section class="viewport-shell" aria-label="3D model viewer">
      <div id="webgl-error" class="webgl-error" hidden role="alert">
        <strong>3D viewer unavailable.</strong>
        <span>WebGL could not start in this browser or graphics configuration.</span>
      </div>
      <div
        id="viewport"
        tabindex="0"
        role="application"
        aria-label="Interactive 3D rack model. Drag to orbit, right-drag to pan, and scroll or pinch to zoom. Keyboard shortcuts: R reset, A rotate, E explode, W wireframe, and arrow keys pan."
      ></div>
      <div id="selected-meta" class="model-meta"></div>
      <div id="status" class="status" role="status" aria-live="polite">Preparing viewer…</div>
    </section>
  </main>
`;

const viewport = document.querySelector<HTMLDivElement>("#viewport")!;
const status = document.querySelector<HTMLDivElement>("#status")!;
const errorPanel = document.querySelector<HTMLDivElement>("#webgl-error")!;
const select = document.querySelector<HTMLSelectElement>("#model-select")!;
const meta = document.querySelector<HTMLDivElement>("#selected-meta")!;
const resetButton = document.querySelector<HTMLButtonElement>("#reset-view")!;
const rotateButton = document.querySelector<HTMLButtonElement>("#auto-rotate")!;
const explodeButton = document.querySelector<HTMLButtonElement>("#explode")!;
const wireButton = document.querySelector<HTMLButtonElement>("#wireframe")!;

let renderer: THREE.WebGLRenderer;
let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let controls: OrbitControls;
let currentSelection = "assembly";
let exploded = false;
let wireframe = false;
let animationId = 0;
let releaseSummary = "529.43 g · 177.51173 m · 426.96577 cm³ · 23h04m49s";
const visibleGroup = new THREE.Group();
const loaded = new Map<string, THREE.Mesh>();
const loader = new STLLoader();

function cssColor(name: string) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function setPressed(button: HTMLButtonElement, pressed: boolean) {
  button.setAttribute("aria-pressed", String(pressed));
}

function setStatus(message: string, state: "loading" | "ready" | "error" = "ready") {
  status.textContent = message;
  status.dataset.state = state;
}

function updateMeta() {
  if (currentSelection === "assembly") {
    meta.innerHTML = `<strong>Full rack assembly</strong><span>244.5 × 152 × 197.6 mm · 6 plates · ${releaseSummary}</span>`;
    explodeButton.disabled = false;
    return;
  }

  const model = models.find((entry) => entry.id === currentSelection)!;
  meta.innerHTML = `<strong>${model.label}</strong><span>${model.dimensions.join(" × ")} mm · plate ${model.plate}</span>`;
  explodeButton.disabled = true;
  exploded = false;
  setPressed(explodeButton, false);
  explodeButton.textContent = "Explode";
}

async function loadReleaseSummary() {
  try {
    const response = await fetch(`${base}estimate.json`);
    if (!response.ok) throw new Error(`Estimate request failed: ${response.status}`);
    const estimate = await response.json();
    const totals = estimate.totals;
    const serialTime = String(totals.serial_time).replace(
      /^(\d+)h\s*(\d+)m\s*(\d+)s$/,
      (_, hours, minutes, seconds) =>
        `${hours}h${String(minutes).padStart(2, "0")}m${String(seconds).padStart(2, "0")}s`
    );
    releaseSummary =
      `${Number(totals.grams).toFixed(2)} g · ` +
      `${Number(totals.length_m).toFixed(5)} m · ` +
      `${Number(totals.volume_cm3).toFixed(5)} cm³ · ${serialTime}`;
    updateMeta();
  } catch (error) {
    console.warn("Using embedded release estimate fallback", error);
  }
}

function makeMaterial(index: number) {
  const colors = ["--cp-accent", "--cp-text-soft", "--cp-border-strong", "--cp-text-muted"];
  return new THREE.MeshStandardMaterial({
    color: new THREE.Color(cssColor(colors[index % colors.length])),
    roughness: 0.72,
    metalness: 0.04,
    wireframe
  });
}

function loadModel(model: RackModel, index: number): Promise<THREE.Mesh> {
  const existing = loaded.get(model.id);
  if (existing) return Promise.resolve(existing);

  return new Promise((resolve, reject) => {
    loader.load(
      `${base}models/${model.file}`,
      (geometry) => {
        geometry.computeVertexNormals();
        geometry.center();
        const mesh = new THREE.Mesh(geometry, makeMaterial(index));
        mesh.name = model.id;
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        loaded.set(model.id, mesh);
        resolve(mesh);
      },
      undefined,
      reject
    );
  });
}

function placeMesh(mesh: THREE.Mesh, model: RackModel, assembly: boolean) {
  mesh.position.set(0, 0, 0);
  mesh.rotation.set(0, 0, 0);
  if (!assembly) return;

  mesh.position.set(...(exploded ? model.exploded : model.position));
  if (model.rotation) mesh.rotation.set(...model.rotation);
}

function fitView() {
  const box = new THREE.Box3().setFromObject(visibleGroup);
  if (box.isEmpty()) return;

  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  const maxSize = Math.max(size.x, size.y, size.z);
  const distance = maxSize / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2))) * 1.7;
  camera.position.set(center.x + distance * 0.72, center.y - distance, center.z + distance * 0.55);
  camera.near = Math.max(distance / 100, 0.1);
  camera.far = distance * 20;
  camera.updateProjectionMatrix();
  controls.target.copy(center);
  controls.update();
}

async function showSelection(id: string) {
  currentSelection = id;
  visibleGroup.clear();
  updateMeta();
  const requested = id === "assembly" ? models : models.filter((model) => model.id === id);
  setStatus(`Loading ${id === "assembly" ? "assembly" : requested[0].label}…`, "loading");

  try {
    const meshes = await Promise.all(requested.map((model) => loadModel(model, models.indexOf(model))));
    meshes.forEach((mesh, index) => {
      placeMesh(mesh, requested[index], id === "assembly");
      visibleGroup.add(mesh);
    });
    fitView();
    setStatus("Ready");
  } catch (error) {
    console.error(error);
    setStatus("Model failed to load", "error");
  }
}

function initViewer() {
  try {
    const probe = document.createElement("canvas");
    if (!probe.getContext("webgl2") && !probe.getContext("webgl")) throw new Error("WebGL unavailable");

    scene = new THREE.Scene();
    scene.background = new THREE.Color(cssColor("--cp-surface-soft"));
    camera = new THREE.PerspectiveCamera(38, 1, 0.1, 5000);
    camera.up.set(0, 0, 1);

    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    viewport.appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.07;
    controls.screenSpacePanning = true;
    controls.minDistance = 60;
    controls.maxDistance = 1400;

    scene.add(visibleGroup);
    const ambient = new THREE.HemisphereLight(
      new THREE.Color(cssColor("--cp-surface")),
      new THREE.Color(cssColor("--cp-border-strong")),
      2.2
    );
    const key = new THREE.DirectionalLight(new THREE.Color(cssColor("--cp-surface")), 4);
    key.position.set(300, -240, 400);
    key.castShadow = true;
    scene.add(ambient, key);

    const floor = new THREE.Mesh(
      new THREE.PlaneGeometry(1200, 1200),
      new THREE.ShadowMaterial({ color: new THREE.Color(cssColor("--cp-text")), opacity: 0.12 })
    );
    floor.position.z = -45;
    floor.receiveShadow = true;
    scene.add(floor);

    const resize = () => {
      const { width, height } = viewport.getBoundingClientRect();
      renderer.setSize(width, height, false);
      camera.aspect = width / Math.max(height, 1);
      camera.updateProjectionMatrix();
    };
    new ResizeObserver(resize).observe(viewport);
    resize();

    const animate = () => {
      controls.update();
      renderer.render(scene, camera);
      animationId = requestAnimationFrame(animate);
    };
    animate();
    showSelection("assembly");
  } catch (error) {
    console.error(error);
    errorPanel.hidden = false;
    viewport.hidden = true;
    status.hidden = true;
    select.disabled = true;
    [resetButton, rotateButton, explodeButton, wireButton].forEach((button) => {
      button.disabled = true;
    });
  }
}

select.addEventListener("change", () => showSelection(select.value));
resetButton.addEventListener("click", fitView);
rotateButton.addEventListener("click", () => {
  controls.autoRotate = !controls.autoRotate;
  controls.autoRotateSpeed = 1.4;
  setPressed(rotateButton, controls.autoRotate);
});
explodeButton.addEventListener("click", () => {
  if (currentSelection !== "assembly") return;
  exploded = !exploded;
  setPressed(explodeButton, exploded);
  explodeButton.textContent = exploded ? "Assemble" : "Explode";
  models.forEach((model) => {
    const mesh = loaded.get(model.id);
    if (mesh) placeMesh(mesh, model, true);
  });
  fitView();
});
wireButton.addEventListener("click", () => {
  wireframe = !wireframe;
  setPressed(wireButton, wireframe);
  loaded.forEach((mesh) => {
    (mesh.material as THREE.MeshStandardMaterial).wireframe = wireframe;
  });
});

viewport.addEventListener("keydown", (event) => {
  const step = 8;
  if (event.key === "Home" || event.key.toLowerCase() === "r") fitView();
  if (event.key.toLowerCase() === "a") rotateButton.click();
  if (event.key.toLowerCase() === "e" && !explodeButton.disabled) explodeButton.click();
  if (event.key.toLowerCase() === "w") wireButton.click();
  if (event.key === "ArrowLeft") controls.target.x -= step;
  if (event.key === "ArrowRight") controls.target.x += step;
  if (event.key === "ArrowUp") controls.target.z += step;
  if (event.key === "ArrowDown") controls.target.z -= step;
  if (event.key.startsWith("Arrow")) {
    controls.update();
    event.preventDefault();
  }
});

window.addEventListener("beforeunload", () => cancelAnimationFrame(animationId));
updateMeta();
loadReleaseSummary();
initViewer();
