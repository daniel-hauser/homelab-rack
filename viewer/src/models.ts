// SPDX-License-Identifier: MIT

export type RackModel = {
  id: string;
  label: string;
  file: string;
  dimensions: [number, number, number];
  plate: number;
  position: [number, number, number];
  exploded: [number, number, number];
  rotation?: [number, number, number];
  assemblyOnly?: boolean;
};

export const models: RackModel[] = [
  { id: "ucg", label: "UCG-Ultra module", file: "01_UCG_Ultra.stl", dimensions: [244.5, 152, 46.7], plate: 2, position: [0, 0, 23.35], exploded: [0, 0, -24] },
  { id: "usw-right", label: "USW-Ultra right", file: "03_USW_Ultra_Right.stl", dimensions: [241.3, 152, 46.7], plate: 5, position: [-1.6, 0, 67.8], exploded: [82, 0, 38] },
  { id: "usw-left", label: "USW-Ultra left", file: "02_USW_Ultra_Left.stl", dimensions: [244.5, 152, 46.7], plate: 3, position: [0, 0, 112.25], exploded: [-82, 0, 76] },
  { id: "pi-chassis", label: "Dual-Pi chassis", file: "04_Dual_Pi_Chassis.stl", dimensions: [244.5, 152, 46.7], plate: 4, position: [0, 0, 156.7], exploded: [0, 0, 140] },
  { id: "drawer-1", label: "Pi drawer 1", file: "05_Pi_Drawer_1.stl", dimensions: [64.5, 114.4, 30], plate: 6, position: [-67.6, -19.2, 154.35], exploded: [-145, -24, 152] },
  { id: "drawer-2", label: "Pi drawer 2", file: "06_Pi_Drawer_2.stl", dimensions: [64.5, 114.4, 30], plate: 5, position: [64.4, -19.2, 154.35], exploded: [145, -24, 152] },
  { id: "vent", label: "Vent insert", file: "07_Vent_Insert.stl", dimensions: [64.5, 30, 6], plate: 1, position: [-1.6, -73.7, 154.35], exploded: [0, -130, 170], rotation: [Math.PI / 2, 0, 0] },
  { id: "uk-top", label: "UK-Ultra top", file: "08_UK_Ultra_Top.stl", dimensions: [241.3, 150, 14], plate: 6, position: [-1.6, 1, 184.8], exploded: [0, 0, 224] },
  { id: "spine-a", label: "Rear spine A", file: "09_Rear_Spine_A.stl", dimensions: [14, 177.05, 8], plate: 1, position: [-104.25, 77, 88.525], exploded: [-158, 102, 92], rotation: [Math.PI / 2, 0, 0] },
  { id: "spine-b", label: "Rear spine B", file: "10_Rear_Spine_B.stl", dimensions: [14, 177.05, 8], plate: 1, position: [101.05, 77, 88.525], exploded: [158, 102, 92], rotation: [Math.PI / 2, 0, 0] },
  { id: "feet", label: "Installed desktop feet", file: "desktop_feet_installed.stl", dimensions: [241.3, 150, 9], plate: 1, position: [-1.6, 1, -1.3], exploded: [0, 0, -42], assemblyOnly: true }
];
